import sys
from django.core.management.base import BaseCommand, CommandError
from geonode.layers.models import Layer
from geonode.base.models import Link
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import argparse
import uuid

class Command(BaseCommand):
    help = 'Imports mvt layers'

    parser = argparse.ArgumentParser()

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            action='store',
            dest='name',
            default=None,
            help='Name of mvt layer',
        )

        parser.add_argument(
            '--url',
            action='store',
            dest='url',
            default=None,
            help='The z/y/x url of the mvt layer'
        )

        parser.add_argument(
            '--bbox',
            action='store',
            dest='bbox',
            default=[-180, 180, -89.9, 89.9],
            help='The bounding box of the layer in format \n'
                 '[minX, maxX, minY, maxY]',
        )

    def handle(self, *args, **options):
        if options['name'] and options['url']:
            self.create_layer(options['name'], options['url'], options['bbox'])
        else:
            self.stdout.write('Name and Url must be provided')

    def create_layer(self, name, url, bbox=None):
        if not bbox:
            bbox = [-180, 180, -89.9, 89.9]
        layer, created = Layer.objects.get_or_create(
            name = name,
            title = name,
            bbox_x0 = bbox[0],
            bbox_x1 = bbox[1],
            bbox_y0 = bbox[2],
            bbox_y1 = bbox[3],
            uuid = str(uuid.uuid1())
        )
        l, created = Link.objects.get_or_create(
            resource=layer.resourcebase_ptr,
            extension='mvt_tiles',
            name='MVT',
            mime='image/png',
            link_type='mvt',
            url=url
        )
