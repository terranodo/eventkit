# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Django settings for the GeoNode project.
import os
import geonode
from geonode.settings import *
#
# General Django development settings
#

SITENAME = 'eventkit'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Defines the directory that contains the settings file as the LOCAL_ROOT
# It is used for relative settings elsewhere.
GEONODE_ROOT = os.path.abspath(os.path.abspath(geonode.__file__))
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

WSGI_APPLICATION = "eventkit.wsgi.application"


# Load more settings from a file called local_settings.py if it exists
try:
    from local_settings import *
except ImportError:
    pass

# Additional directories which hold static files
STATICFILES_DIRS.append(
    os.path.join(LOCAL_ROOT, "static"),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'eventkit',
        'USER' : 'eventkit',
        'PASSWORD' : 'eventkit',
        'HOST' : 'localhost',
        'PORT' : '5432',
    },
    # vector datastore for uploads
     'datastore' : {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'eventkit_datastore',
        'USER' : 'eventkit',
        'PASSWORD' : 'eventkit',
        'HOST' : 'localhost',
        'PORT' : '5432',
     }
}

OSGEO_DATASTORE = 'datastore'
OSGEO_IMPORTER_GEONODE_ENABLED = True
LOGGING['loggers']['osgeo_importer'] = {"handlers": ["console"], "level": "DEBUG"}
DATABASE_ROUTERS = ['osgeo_importer_prj.dbrouters.DefaultOnlyMigrations']

# Note that Django automatically includes the "templates" dir in all the
# INSTALLED_APPS, se there is no need to add maps/templates or admin/templates
TEMPLATE_DIRS = (
    os.path.join(LOCAL_ROOT, "templates"),
) + TEMPLATE_DIRS

# Location of url mappings
ROOT_URLCONF = 'eventkit.urls'

# Location of locale files
LOCALE_PATHS = (
    os.path.join(LOCAL_ROOT, 'locale'),
    ) + LOCALE_PATHS

INSTALLED_APPS += ("osgeo_importer", "celery", "kombu.transport.django",)

BROKER_URL = 'django://'
#CELERY_ACCEPT_CONTENT = ['json']
#CELERY_TASK_SERIALIZER = 'json'
#CELERY_RESULT_SERIALIZER = 'json'
#CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True 

LAYER_PREVIEW_LIBRARY="OL3"

USE_DJMP_FOR_ALL_LAYERS = False

IMPORT_HANDLERS = ['osgeo_importer.handlers.geonode.GeoNodePublishHandler',
                           'osgeo_importer.handlers.geonode.GeoNodeMetadataHandler']


