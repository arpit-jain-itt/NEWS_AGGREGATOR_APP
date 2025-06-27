import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from config.config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM
from server.utils.service_helper import send_email_safely


class EmailService:
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.email_from = EMAIL_FROM

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = formataddr(("NEWS_AGGREGATOR_TEAM", self.email_from))
        msg["To"] = to_email

        def do_send():
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

        return send_email_safely(do_send)
