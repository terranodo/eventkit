from __future__ import absolute_import

from celery import shared_task
from .service_manager import create_confs_from_voyager, cache_tileset

@shared_task(name="eventkit.tasks.task_create_confs_from_voyager")
def task_create_confs_from_voyager(base_url, voyager_ids, bbox=None):
    create_confs_from_voyager(base_url, voyager_ids, bbox=None)

@shared_task(name="eventkit.tasks.task_cache_tileset")
def task_cache_tileset(tileset_id):
    cache_tileset(tileset_id)