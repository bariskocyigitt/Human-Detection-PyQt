# utils/alerts.py
import os, smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
MAIL_TO   = os.getenv("MAIL_TO")

def send_mail(subject, body, attachment_path=None):
    """Basit e-posta gönderimi (TLS). Ek dosya varsa ekler."""
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = MAIL_TO
        msg.set_content(body)

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                data = f.read()
            msg.add_attachment(
                data,
                maintype="application",
                subtype="octet-stream",
                filename=os.path.basename(attachment_path),
            )

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)  # Gmail için App Password şart
            s.send_message(msg)

        print(f"[MAIL] E-posta gönderildi: {MAIL_TO}")
        return True
    except Exception as e:
        print("[MAIL] Hata:", e)
        return False
