#!/usr/bin/env python3
"""实时盯「有人付到我的收钱码」，一有新到账就通知你自己的程序（webhook）。
在装着模拟器的那台 Mac 上直接跑：
    pip install pillow && brew install tesseract tesseract-lang
    python3 watch-payments.py https://你的服务器/收款到账  [--token 口令]
先在模拟器里把支付宝停在：消息 → 通知(Notifications) → Payments 那一页（最上面一张是最近一笔「收款金额」卡，
下面写着「今日第N笔收入，共计¥X」）。脚本每秒左右：下拉刷新 → 截图 → 裁出那一行 → 认字 → N 变大了就用 X 的差算出这笔多少钱，
POST 给 webhook：{"amount": 0.01, "n": 7, "total": 476.02}。
只看、只刷新，不碰任何跟钱有关的按钮。
为什么要这么绕：支付宝的到账通知在模拟器里推不到系统通知栏（前台后台都试过），那一页又是网页、uiautomator 读不到字，只剩截图认字这条路。"""
import io, json, re, subprocess, sys, time, urllib.request
from PIL import Image

ADB = subprocess.os.path.expanduser('~/Library/Android/sdk/platform-tools/adb')
LINE = re.compile(r'今日第\s*(\d+)\s*笔收入.{0,4}?共计\s*[¥Y￥]?\s*([\d,]+\.\d{2})')
WEBHOOK = sys.argv[1] if len(sys.argv) > 1 else ''
TOKEN = sys.argv[sys.argv.index('--token') + 1] if '--token' in sys.argv else ''
CROP = (0, 560, 1080, 790)          # Pixel 6 分辨率下「经营数据」那一行；别的机型自己量一下

def log(*a): print(time.strftime('%m-%d %H:%M:%S'), *a, flush=True)

def shot():
    subprocess.run([ADB, 'shell', 'input', 'swipe', '540', '700', '540', '1400', '120'], capture_output=True); time.sleep(0.45)
    raw = subprocess.run([ADB, 'exec-out', 'screencap', '-p'], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert('L').crop(CROP)

last = {'img': None, 'text': ''}
def ocr(im):
    small = im.resize((im.width // 2, im.height // 2)).tobytes()
    # 跟上一帧几乎一样就不认字（认字最慢）。★要数「变了的点」，别用平均差——一个数字 8→9 平均下来几乎为零，会漏掉
    changed = last['img'] is None or sum(1 for a, b in zip(small, last['img']) if abs(a - b) > 40) > 3
    if not changed and last['text']: return last['text']
    buf = io.BytesIO(); im.save(buf, 'PNG')
    r = subprocess.run(['tesseract', 'stdin', 'stdout', '-l', 'chi_sim+eng', '--psm', '6'], input=buf.getvalue(), capture_output=True)
    text = r.stdout.decode('utf8', 'ignore')
    last.update(img=small, text=text if LINE.search(text.replace(' ', '')) else '')
    return text

def notify(amount, n, total):
    if not WEBHOOK: return log('（没给 webhook，只打印）')
    req = urllib.request.Request(WEBHOOK, data=json.dumps({'amount': amount, 'n': n, 'total': total}).encode(),
                                 headers={'Content-Type': 'application/json', **({'Authorization': 'Bearer ' + TOKEN} if TOKEN else {})})
    urllib.request.urlopen(req, timeout=15).read()

state = {'date': None, 'n': 0, 'total': 0.0}
while True:
    try:
        m = LINE.search(ocr(shot()).replace(' ', ''))
        if not m: time.sleep(1); continue
        n, total = int(m.group(1)), float(m.group(2).replace(',', ''))
        today = time.strftime('%Y-%m-%d')
        if state['date'] != today:
            state = {'date': today, 'n': n, 'total': total}; log('起点', state); continue
        if n > state['n'] and total > state['total'] + 0.004:
            amount = round(total - state['total'], 2)
            notify(amount, n, total); log(f'到账 第{n}笔 ¥{amount:.2f}')
            state.update(n=n, total=total)
        elif n != state['n'] or abs(total - state['total']) > 0.004:
            log('数对不上，以现在为准'); state.update(n=n, total=total)
    except Exception as e:
        log('出错', repr(e)[:160]); time.sleep(5)
    time.sleep(0.3)
