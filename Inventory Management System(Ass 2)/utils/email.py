from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import threading
from django.conf import settings


class SendEmailThread(threading.Thread):
    def __init__(self, receiver, subject, message, cc=""):
        self.email = settings.EMAIL
        self.password = settings.PASSWORD
        self.receiver = receiver
        self.subject = subject
        self.message = message
        self.cc = cc
        threading.Thread.__init__(self)

    def run(self):
        try:
            # stmp setup to send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(0)  # 0 for no debugging
            server.ehlo()  # say hello to the server
            server.starttls()  # start TLS encryption
            server.login(self.email, self.password)

            # Email Configuration
            body = MIMEMultipart("alternative")
            body["Subject"] = self.subject
            body["From"] = self.email
            body["To"] = self.receiver   # send to single email
            body.attach(MIMEText(self.message, 'html'))
            if self.cc != "":
                body['Cc'] = self.cc
                rcpt = [self.receiver] + self.cc.split(',')
            else:
                rcpt = [self.receiver]
            server.sendmail(self.email, rcpt, body.as_string())
            return True
        except:
            return False


def send_email(receiver, subject, message, cc='', *args, **kwargs):
    SendEmailThread(receiver=receiver, subject=subject, message=message, cc=cc).start()
