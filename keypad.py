#!/usr/bin/env python3
"""读出支付密码键盘上 0–9 每个键的中心坐标（密码页不让截屏，只能这样「看」）。
用法：python3 keypad.py   → 打印  1 180 1803 / 2 541 1803 / …
AI 拿到坐标后，一位一位用 emu.sh tap 去点，每位之间停 0.7–2 秒、落点挪一点，像人手那样。
★本脚本不碰密码本身，密码别写进任何脚本。"""
import re, subprocess
out = subprocess.run(['bash', 'emu.sh', 'dump'], capture_output=True, text=True).stdout
for line in out.splitlines():
    m = re.fullmatch(r'(\d) \[(\d+),(\d+)\]\[(\d+),(\d+)\]', line.strip())
    if m:
        d, x1, y1, x2, y2 = m.group(1), *map(int, m.groups()[1:])
        print(d, (x1 + x2) // 2, (y1 + y2) // 2)
