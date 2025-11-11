from django.core.management.base import BaseCommand
# from django.contrib.settings import boto3
from django.conf import settings
import boto3
import os
s3 = boto3.client('s3')


class Command(BaseCommand):
    help = 'run this in order to download the vault file'

    def add_arguments(self, parser):
        parser.add_argument('url', nargs='+')

    def handle(self, *args, **kwargs):
        url = kwargs.pop('url')[0]
        path = os.path.join(settings.BASE_DIR, 'src', "vault.py")
        os.system(f"""wget -O {path} {url}""")
