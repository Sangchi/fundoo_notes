from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoo_notes.settings')

# Create an instance of the Celery class
app = Celery('fundoo_notes')
app.conf.update(
    broker_connection_retry_on_startup=True,  # Maintain retry behavior on startup
    enable_utc=True,                         # Enable UTC for Celery
    timezone='UTC',                         # Set timezone to UTC
)


# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()