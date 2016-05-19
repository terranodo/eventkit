from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventkit.settings')

from django.conf import settings  # noqa

app = Celery('eventkit')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
