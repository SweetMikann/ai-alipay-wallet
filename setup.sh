#!/bin/bash
# 在 Mac（Apple 芯片）上装好一台不开窗口的安卓 14 模拟器。跑一次就行，大约 10–20 分钟（要下几个 G）。
# 用法：bash setup.sh [模拟器名字，默认 wallet]
set -e
NAME="${1:-wallet}"
export PATH=/opt/homebrew/bin:$PATH
brew install openjdk
brew install --cask android-commandlinetools
export JAVA_HOME="$(brew --prefix openjdk)/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
export ANDROID_HOME="$HOME/Library/Android/sdk"
mkdir -p "$ANDROID_HOME/cmdline-tools"
# 坑：avdmanager 只认放在 SDK 目录里的命令行工具，brew 装的那份要拷一份进来
cp -R "$(brew --prefix)/share/android-commandlinetools/cmdline-tools/latest" "$ANDROID_HOME/cmdline-tools/" 2>/dev/null || true
SDKM="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
AVDM="$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager"
yes | "$SDKM" --sdk_root="$ANDROID_HOME" --licenses >/dev/null
"$SDKM" --sdk_root="$ANDROID_HOME" "platform-tools" "emulator" "platforms;android-34" "system-images;android-34;google_apis;arm64-v8a"
echo no | "$AVDM" create avd -n "$NAME" -k "system-images;android-34;google_apis;arm64-v8a" -d pixel_6 --force
echo "装好了：模拟器 $NAME。下一步：bash emu.sh start，再 adb install 支付宝安装包。"
