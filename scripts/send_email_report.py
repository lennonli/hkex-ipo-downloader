import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# ================= CONFIGURATION =================
# 1. Go to: https://myaccount.google.com/apppasswords
# 2. Add an app named "HKEX Downloader"
# 3. Copy the 16-character password below
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = ""  # Paste the 16-character App Password here
RECEIVER_EMAIL = "your_email@gmail.com"

# The directory where IPO documents are saved
# Prioritize original path, fallback to relative
CUSTOM_PATH = '/Users/licheng/Documents/港股IPO自动文档'
if os.path.exists(CUSTOM_PATH):
    BASE_DIR = CUSTOM_PATH
else:
    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
# =================================================

def get_weekly_summary():
    one_week_ago = datetime.now() - timedelta(days=7)
    summary = []
    
    if not os.path.exists(BASE_DIR):
        return "下载目录不存在。"

    folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    
    for folder in folders:
        folder_path = os.path.join(BASE_DIR, folder)
        mtime = datetime.fromtimestamp(os.path.getmtime(folder_path))
        
        if mtime > one_week_ago:
            files = os.listdir(folder_path)
            summary.append(f"- {folder} (包含 {len(files)} 个文件)")
            
    if not summary:
        return "过去一周没有下载新的 IPO 文档。"
    
    return "本周下载的 IPO 公司如下：\n" + "\n".join(summary)

def send_email(content):
    if SENDER_EMAIL == "your_email@gmail.com":
        print("错误：请先在脚本中配置 SENDER_EMAIL 和 SENDER_PASSWORD。")
        print("邮件内容汇总如下：\n")
        print(content)
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"港股 IPO 自动下载周报 ({datetime.now().strftime('%Y-%m-%d')})"

    msg.attach(MIMEText(content, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    report = get_weekly_summary()
    send_email(report)
