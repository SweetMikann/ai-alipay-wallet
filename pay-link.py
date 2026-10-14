#!/usr/bin/env python3
"""把 AI 小号的「收钱码」截图变成一条点了就能付款的链接。
用法：python3 pay-link.py 收钱码截图.png
（截图：模拟器里 支付宝 → 收付款 → 收钱 → 个人收钱码，用 emu.sh shot 截）
需要：pip install zxing-cpp pillow
得到的链接放进你的 App／网页按钮／快捷指令里；人点它 → 支付宝「付款给 AI」页 → 自己填金额、确认。
★不要用「带金额的转账链接」（appId=20000123&actionType=scan&biz_data=…），支付宝会当成诈骗拉款，直接「交易中断」。"""
import sys, urllib.parse
import zxingcpp
from PIL import Image
codes = [b.text for b in zxingcpp.read_barcodes(Image.open(sys.argv[1])) if b.text.startswith('https://qr.alipay.com/')]
if not codes:
    sys.exit('截图里没找到支付宝收钱码')
print('alipays://platformapi/startapp?saId=10000007&qrcode=' + urllib.parse.quote(codes[0], safe=''))
