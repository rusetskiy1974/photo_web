import smtplib
from email.mime.text import MIMEText
from email.header import Header

# Message
msg = MIMEText("Це тестовий лист, надісланий через SMTP-сервер meta.ua з Python.\nДякуємо!", 'plain', 'utf-8')
msg['Subject'] = Header('Перевірка SMTP через Python', 'utf-8')
msg['From'] = 'sergrus.1974@meta.ua'
msg['To'] = 'sergrus1974@gmail.com'  # ✅ Use a different recipient if possible

try:
    with smtplib.SMTP_SSL('smtp.meta.ua', 465) as server:
        server.login('sergrus.1974@meta.ua', 'Cthtuf_2011')
        server.send_message(msg)
        print("✅ Email надіслано")
except Exception as e:
    print("❌ ПОМИЛКА:", e)
