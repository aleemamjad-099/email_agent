import smtplib
from email.mime.text import MIMEText

def send_email(receiver_email, subject, body):
    # Gmail example (App Password use karein)
    sender_email = "aleemamjad25@gmail.com"
    password = "dyyh ayjm gofc dsnw"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return "Email sent successfully!"
    except Exception as e:
        return f"Error: {str(e)}"