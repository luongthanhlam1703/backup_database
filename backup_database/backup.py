import os
import shutil
import smtplib
import schedule
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

# Thư mục chứa file database và thư mục backup
DATABASE_FOLDER = 'database'
BACKUP_FOLDER = 'backup'

# Hàm gửi email
def send_email(subject, body):
    try:
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = RECEIVER_EMAIL
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(message)

        print("Đã gửi email thông báo.")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")

# Hàm thực hiện việc backup
def backup_database():
    try:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)

        files = os.listdir(DATABASE_FOLDER)
        backup_count = 0

        for file in files:
            if file.endswith('.sql') or file.endswith('.sqlite3'):
                source = os.path.join(DATABASE_FOLDER, file)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")# Đặt tên file backup có kèm timestamp
                backup_filename = f"{os.path.splitext(file)[0]}_{timestamp}{os.path.splitext(file)[1]}"
                destination = os.path.join(BACKUP_FOLDER, backup_filename)
                shutil.copy2(source, destination)
                backup_count += 1

        if backup_count > 0:
            subject = "Backup Thành Công"
            body = f"Sao lưu {backup_count} file thành công lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        else:
            subject = "Backup Không Có File"
            body = f"Không tìm thấy file .sql hoặc .sqlite3 để sao lưu lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

        send_email(subject, body)

    except Exception as e:
        subject = "Backup Thất Bại"
        body = f"Có lỗi xảy ra trong quá trình backup: {e}"
        send_email(subject, body)
# Backup lúc 00:00 AM hằng ngày
schedule.every().day.at("00:00").do(backup_database)
if __name__ == "__main__":
    print("Quá trình backup đang thực hiện")

    while True:
        schedule.run_pending()
        time.sleep(1)
