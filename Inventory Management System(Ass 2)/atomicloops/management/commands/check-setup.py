import yaml
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
from src.vault import credentials


class Command(BaseCommand):
    help = 'run this in order to check the project setup'

    def handle(self, *args, **kwargs):
        counter = 0
        # 1. Change the project name
        settings_file = os.path.join(settings.BASE_DIR, "src", "settings", "base.py")

        with open(settings_file, "r") as f:
            data = f.readlines()

        project_name = [line for line in data if "PROJECT_NAME" in line][0]
        if "*****" in project_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the Project Name in src/settings/base.py\n" + '\n')

        timezone = [line for line in data if "PROJECT_NAME" in line][0]
        if "*****" in timezone:
            counter += 1
            sys.stdout.write(f"{counter}. Please Uncomment TIME_ZONE = UTC in src/settings/base.py\nUpdate the TIME_ZONE as per client zone.\n" + '\n')

        django_secret_key = [line for line in data if "SECRET_KEY" in line][0]

        if "*****" in django_secret_key:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the SECRET_KEY in src/settings/base.py\nTo Generate a key use the following commands in the terminal\n\n{'#'*90}\npython3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'\n{'#'*90}\n" + '\n')
            
        secret_key = [line for line in data if "SIGNING_KEY" in line][0]
        if "*****" in secret_key:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the SIGNING_KEY in SIMPLE_JWT config in src/settings/base.py\nTo Generate a key use the following commands in the terminal\n\n{'#'*90}\npython3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'\n{'#'*90}\n" + '\n')

        # Update Docker-compose dev file
        docker_compose_dev_file = os.path.join(settings.BASE_DIR, "docker-compose-dev.yml")
        conf = yaml.safe_load(Path(docker_compose_dev_file).read_text())

        backend_name = conf['services']['backend']['container_name']
        if "*****" in backend_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the backend service container_name to <project_name>-backend in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        db_name = conf['services']['db']['container_name']
        if "*****" in db_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the db service container_name to <project_name>-db in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        volume_name = conf['services']['db']['volumes'][0]
        if "volume_name" in volume_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the db service <volume_name> to <project_name>-db in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        volume_name = conf['services']['db']['volumes'][0]
        if "volume_name" in volume_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the db service <volume_name> to <project_name>-admin in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        # New Services
        # rabbit-mq service
        rabbit_mq_service_name = conf['services']['rabbit-mq']['container_name']
        if "*****" in rabbit_mq_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the rabbit-mq service container to <project_name>-rabbit-mq in docker--compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        #  celery service
        celery_service_name = conf['services']['celery']['container_name']
        if "*****" in celery_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the celery service container to <project_name>-celery in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + "\n")

        # Redis service
        redis_service_name = conf['services']['redis']['container_name']
        if "*****" in redis_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the redis service container to <project_name>-redis in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + "\n")

        # flower service
        flower_service_name = conf['services']['flower']['container_name']
        if "*****" in flower_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the flower service container to <project_name>-flower in docker-compose-dev.yml\n Please find the PROJECT NAME IN THE README\n" + "\n")

        # Update Docker-compose file
        docker_compose_dev_file = os.path.join(settings.BASE_DIR, "docker-compose.yml")
        conf = yaml.safe_load(Path(docker_compose_dev_file).read_text())

        backend_name = conf['services']['backend']['container_name']
        if "*****" in backend_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the backend service container_name to <project_name>-backend in docker-compose.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        # volume_name = conf['services']['db']['volumes'][0]
        # if "volume_name" in volume_name:
        #     counter += 1
        #     sys.stdout.write(f"{counter}. Please Update the db service <volume_name> to <project_name>-admin in docker-compose.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        # new services

        # rabbit-mq service
        rabbit_mq_service_name = conf['services']['rabbit-mq']['container_name']
        if "*****" in rabbit_mq_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the rabbit-mq service container to <project_name>-rabbit-mq in docker-compose.yml\n Please find the PROJECT NAME IN THE README\n" + '\n')

        #  celery service
        celery_service_name = conf['services']['celery']['container_name']
        if "*****" in celery_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the celery service container to <project_name>-celery in docker-compose.yml\n Please find the PROJECT NAME IN THE README\n" + "\n")

        # Redis service
        redis_service_name = conf['services']['redis']['container_name']
        if "*****" in redis_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the redis service container to <project_name>-redis in docker-compose.yml\n Please find the PROJECT NAME IN THE README\n" + "\n")

        # flower service
        flower_service_name = conf['services']['flower']['container_name']
        if "*****" in flower_service_name:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the flower service container to <project_name>-flower in docker-compose.yml\n Please find the PROJECT NAME IN THE README\n" + "\n")

        # Check vault
        vault_file = os.path.join(settings.BASE_DIR, "src", "vault.py")

        with open(vault_file, "r") as f:
            data = f.readlines()

        # Check S3 Bucket
        s3_bucket = credentials['dev']['S3_BUCKET']

        if "*****" in s3_bucket:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the S3_BUCKET Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # Check AWS KEYS
        AWS_ACCESS_KEY_ID = credentials['dev']['AWS_ACCESS_KEY_ID']

        if "*****" in AWS_ACCESS_KEY_ID:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the AWS_ACCESS_KEY_ID Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # Check AWS SECRET KEY
        AWS_SECRET_ACCESS_KEY = credentials['dev']['AWS_SECRET_ACCESS_KEY']

        if "*****" in AWS_SECRET_ACCESS_KEY:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the AWS_SECRET_ACCESS_KEY Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # CHECK REGION
        region = credentials['dev']['REGION']

        if "*****" in region:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the REGION Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # AWS URL
        aws_url = credentials['dev']['AWS_URL']

        if "*****" in aws_url:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the AWS_URL Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # Check EMAIL
        email = credentials['dev']['EMAIL']

        if "*****" in email:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the EMAIL Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # CHECK Password
        password = credentials['dev']['PASSWORD']

        if "*****" in password:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the PASSWORD Variable in src/vault.py\n Please contact your Manager for the AWS Details\n" + '\n')

        # Check DB Host
        db_host = credentials['dev']['DB_HOST']

        if "*****" in db_host:
            counter += 1
            sys.stdout.write(f"{counter}. Please Update the DB_HOST Variable in src/vault.py\n This must match the docker-compose-dev.yml file container_name in db services\n" + '\n')

        if counter == 0:
            sys.stdout.write("Project Setup Done Successfully.\n" + '\n')

        else:
            sys.stdout.write(f"{'#'*90}\n>>>{counter} configurations are yet to be done\n{'#'*90}\n")
