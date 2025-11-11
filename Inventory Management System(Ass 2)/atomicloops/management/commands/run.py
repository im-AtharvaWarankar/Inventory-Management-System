
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os


# validate-setup
class Command(BaseCommand):
    help = 'run this command in order to run in different mode'

    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('--mode', type=str, help='Define the mode', required=True)

    def handle(self, *args, **kwargs):
        mode = kwargs['mode']
        modes = ['start-dev', 'stop-dev', 'start-prod', 'stop-prod', 'interactive-dev', 'interactive-prod', 'check-syntax', 'start-deploy', "migrate"]

        if mode not in modes:
            raise CommandError("Invalid mode.\n mode must be one of: %s" % modes)

        if mode == 'start-dev':
            os.system(f'''docker-compose -p {settings.PROJECT_NAME}-dev -f docker-compose-dev.yml build''')
            os.system(f'''docker-compose -p {settings.PROJECT_NAME}-dev -f docker-compose-dev.yml up -d''')

        if mode == 'stop-dev':
            os.system(f'''docker-compose -p {settings.PROJECT_NAME}-dev -f docker-compose-dev.yml down''')

        if mode == 'interactive-dev':
            os.system(f'''docker exec -it --user root {settings.PROJECT_NAME}-backend bash''')

        if mode == 'start-prod':
            os.system(f'''docker-compose -p {settings.PROJECT_NAME}-prod build''')
            os.system(f'''docker-compose -p {settings.PROJECT_NAME}-prod up -d''')

        if mode == 'stop-prod':
            os.system(f'''docker-compose -p {settings.PROJECT_NAME}-prod down''')

        if mode == 'interactive-prod':
            os.system(f'''docker exec -it --user root {settings.PROJECT_NAME}-backend bash''')

        if mode == 'check-syntax':
            os.system('''flake8 .''')
            # os.system("""act -p""")

        # if mode == "migrate":
        #     command_run = subprocess.call(["python", "manage.py", "makemigrations", "--check", "--dry-run"])
        #     if command_run == 0:
        #         print("Its worked!!", flush=True)
        #     else:
        #         print("It didn't work")
        #     print(command_run, flush=True)
