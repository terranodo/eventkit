from __future__ import absolute_import
from .celery import app as celery_app # noqa

default_app_config = 'eventkit.apps.EventkitConfig'