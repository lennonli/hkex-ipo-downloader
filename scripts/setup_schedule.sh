#!/bin/bash

# ================= CONFIGURATION =================
# Get the absolute path of the current directory (where the script is located)
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)

# Define PLIST names and paths
DOWNLOAD_PLIST="com.user.hkex_download.plist"
EMAIL_PLIST="com.user.hkex_email.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$LAUNCH_AGENTS_DIR"

# 1. Create Download PLIST (Saturday 20:00)
cat <<EOF > "$LAUNCH_AGENTS_DIR/$DOWNLOAD_PLIST"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.hkex_download</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPTS_DIR/download_ipo_files.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>6</integer>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/hkex_download.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hkex_download.err</string>
</dict>
</plist>
EOF

# 2. Create Email PLIST (Monday 10:00)
cat <<EOF > "$LAUNCH_AGENTS_DIR/$EMAIL_PLIST"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.hkex_email</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPTS_DIR/send_email_report.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/hkex_email.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hkex_email.err</string>
</dict>
</plist>
EOF

# Load the tasks
launchctl unload "$LAUNCH_AGENTS_DIR/$DOWNLOAD_PLIST" 2>/dev/null
launchctl load "$LAUNCH_AGENTS_DIR/$DOWNLOAD_PLIST"
launchctl unload "$LAUNCH_AGENTS_DIR/$EMAIL_PLIST" 2>/dev/null
launchctl load "$LAUNCH_AGENTS_DIR/$EMAIL_PLIST"

echo "✅ 定时任务已成功安装到 $LAUNCH_AGENTS_DIR"
echo "📅 下载任务：每周六 20:00"
echo "📅 邮件任务：每周一 10:00"
echo "运行日志将保存在 /tmp/hkex_download.log 和 /tmp/hkex_email.log"
