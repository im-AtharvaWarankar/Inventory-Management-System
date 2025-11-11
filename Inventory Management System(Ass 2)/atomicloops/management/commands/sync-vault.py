from django.conf import settings
import boto3
import datetime
import os
from src import vault
from django.core.management.base import BaseCommand
import json

s3 = boto3.client("s3", region_name=settings.REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


# validate-setup
class Command(BaseCommand):
    help = 'run this command in order to sync the vault file'

    def handle(self, *args, **kwargs):
        vault_path = os.path.join(settings.BASE_DIR, "src", "vault.py")
        # remove the email credentials
        # read file
        with open(vault_path) as f:
            data = f.readlines()
        # Change credentials
        data = vault.credentials
        data['dev']['EMAIL'] = "*****"
        data['dev']['PASSWORD'] = "*****"

        data['prod']['EMAIL'] = "*****"
        data['prod']['PASSWORD'] = "*****"
        # prettify json
        credentials = json.dumps(data, indent=4)
        # write in a new temporary file
        with open('tmp', 'w') as f:
            content = "credentials = %s" % credentials
            f.write(content)
        time = str(datetime.datetime.now()).split(".")[0].replace(' ', '-')
        s3.upload_file(
            "tmp",
            settings.S3_BUCKET,
            f"vault/vault_{time}.py",
            ExtraArgs={'ACL': 'public-read'})
        url = os.path.join(settings.AWS_URL, f"vault/vault_{time}.py")
        os.remove('tmp')
        print("File uploaded successfully")
        print("This is the new vault url :")
        print(url)
        print("Please update this url in the README in the Latest Section")
