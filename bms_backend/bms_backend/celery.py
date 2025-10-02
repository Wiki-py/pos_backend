import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bms_backend.settings')

app = Celery('bms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()