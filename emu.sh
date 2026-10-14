#!/bin/bash
# AI 的「手」：只管这台模拟器。
#   start              开机（不开窗口），等到开机完成
#   stop               关机
#   shot               截图 → /tmp/emu.png（输支付密码那页会是黑的，正常）
#   dump               读当前页面上的字和位置（每行：文字 [左,上][右,下]），黑屏的页也读得到
#   tap X Y            点
#   text 字            输入（只能输英文数字）
#   swipe x1 y1 x2 y2 [毫秒]   拖（拼图滑块用）
#   key 码             按键，4＝返回
#   app                打开支付宝
#   open 链接          在模拟器里打开一条链接（试跳转链接用）
NAME="${EMU_NAME:-wallet}"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
A="$ANDROID_HOME/platform-tools/adb"
case "$1" in
  start) pgrep -f "emulator.*-avd $NAME" >/dev/null || (nohup "$ANDROID_HOME/emulator/emulator" -avd "$NAME" -no-window -no-audio -no-boot-anim -memory 4096 >/tmp/emu.log 2>&1 </dev/null &)
         for i in $(seq 1 60); do [ "$("$A" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ] && { echo booted; exit 0; }; sleep 3; done; echo "没等到开机"; exit 1;;
  stop)  "$A" emu kill;;
  shot)  rm -f /tmp/emu.png; "$A" exec-out screencap -p > /tmp/emu.png; [ -s /tmp/emu.png ] && echo /tmp/emu.png || echo "截不到（多半是密码页）";;
  dump)  "$A" shell uiautomator dump /sdcard/u.xml >/dev/null 2>&1; "$A" shell cat /sdcard/u.xml | python3 -c "
import sys,re,html
for t,b in re.findall(r'text=\"([^\"]+)\"[^>]*?bounds=\"([^\"]+)\"', sys.stdin.read()): print(html.unescape(t), b)";;
  tap)   "$A" shell input tap "$2" "$3";;
  text)  "$A" shell input text "$2";;
  swipe) "$A" shell input swipe "$2" "$3" "$4" "$5" "${6:-900}";;
  key)   "$A" shell input keyevent "$2";;
  app)   "$A" shell am start -n com.eg.android.AlipayGphone/.AlipayLogin;;
  open)  "$A" shell am start -a android.intent.action.VIEW -d "'$2'";;
  *) sed -n '2,13p' "$0";;
esac
