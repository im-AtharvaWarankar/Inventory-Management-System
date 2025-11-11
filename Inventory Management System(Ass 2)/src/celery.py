import os
from celery import Celery
from celery import shared_task
from django.conf import settings
# Set the default Django settings module for the 'celery' program.
ENV = os.getenv('ENV', None)
if ENV is not None and ENV == "prod":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.dev')
app = Celery('src', )
app = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend='rpc://')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.py
app.autodiscover_tasks()


# @app.task(bind=True)
@shared_task
def debug_task(self):
    print("done")
    # print(f'Request: {self.request!r}')
