import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LeaderBoardTPU_Project.settings')

app = Celery('LeaderBoard')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()