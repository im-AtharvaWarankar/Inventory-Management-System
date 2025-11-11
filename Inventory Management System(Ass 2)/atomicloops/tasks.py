from src.celery import app
import os
from django.conf import settings
import csv
from django.apps import apps
import random
import boto3
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from users.serializers import ExportDataSerializer

BASE_DIR = settings.BASE_DIR


@app.task(bind=True)
def export_data(
    self, model, app_name, filename=None, userId=None,
):
    table = apps.get_model('{}.{}'.format(app_name, model))
    qs = table.objects.all()

    keys = list(qs.first().__dict__.keys())
    keys.remove('_state')
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    # Write to file
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, delimiter='\t')
        dict_writer.writeheader()
        for item in qs:
            row = item.__dict__
            del row['_state']
            dict_writer.writerow(item.__dict__)

    # upload to AWS
    file_id = self.request.id
    s3 = boto3.client("s3", region_name=settings.REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    aws_path = "export-data/%s-%s.tsv" % (model, file_id)
    s3.upload_file(
        filename,
        settings.S3_BUCKET,
        aws_path,
        ExtraArgs={'ACL': 'public-read'})
    aws_url = f"{settings.AWS_URL}/{aws_path}"
    data = {
        'id': file_id,
        'userId': userId,
        'modelName': model,
        'fileUrl': aws_url
    }
    serializer = ExportDataSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    os.remove(filename)


@app.task(bind=True)
def send_email(self, receiver, subject, message, cc=''):
    try:
        # stmp setup to send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(0)  # 0 for no debugging
        server.ehlo()  # say hello to the server
        server.starttls()  # start TLS encryption
        server.login(settings.EMAIL, settings.PASSWORD)

        # Email Configuration
        body = MIMEMultipart("alternative")
        body["Subject"] = subject
        body["From"] = settings.EMAIL
        body["To"] = receiver   # send to single email
        body.attach(MIMEText(message, 'html'))
        if cc != "":
            body['Cc'] = cc
            rcpt = [receiver] + cc.split(',')
        else:
            rcpt = [receiver]
        server.sendmail(settings.EMAIL, rcpt, body.as_string())
        return True
    except:
        return False
