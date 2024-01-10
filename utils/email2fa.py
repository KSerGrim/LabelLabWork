import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random


def send_mail(recipient_email: str):
    facode = str(random.randint(10000,90000))
    smtp_server = 'mail.privateemail.com'
    smtp_port = 587
    email_address = 'ppdino@ppdinosaur.com'
    email_password = ''
    to_address = recipient_email
    msg = MIMEMultipart()
    msg['From'] = "LabelLabs 2fa <ppdino@ppdinosaur.com>"
    msg['To'] = to_address
    msg['Subject'] = facode
    msg.attach(MIMEText('', 'html'))
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(msg)
    return facode


if __name__ == "__main__":
    send_mail('bigswaggydude10@gmail.com')
