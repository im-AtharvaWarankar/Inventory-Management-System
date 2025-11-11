from django.core.management.base import BaseCommand
from django.conf import settings
import os
import django.apps


class Command(BaseCommand):
    help = 'run this in order to take backup of all data'

    def handle(self, *args, **kwargs):
        models = django.apps.apps.get_models()
        total = len(models)
        for index, model in enumerate(models, start=1):
            try:
                filePath = os.path.join(settings.BACKUP_DIR, f"{model._meta.app_label}-{model.__name__}.json")
                command = f"python manage.py dumpdata --indent 2 {model._meta.app_label}.{model.__name__} > {filePath}"
                os.system(command)
                print(f"{index}/{total} done")
            except Exception as e:
                print(str(e))
