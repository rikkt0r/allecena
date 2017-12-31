# coding: utf-8
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

queue = Celery('allecena')
queue.config_from_object('django.conf:settings')
queue.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
