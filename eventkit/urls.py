from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from geonode.urls import *
from osgeo_importer.urls import urlpatterns as importer_urlpatterns

urlpatterns = patterns('',
   url(r'^/?$',
       TemplateView.as_view(template_name='site_index.html'),
       name='home'),
   url(
        r'^favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('img/favicon.ico'),
            permanent=False),
        name="favicon"
    ),
    (r'^djmp/', include('djmp.urls')),
    url(r'^mvt_example$',
        TemplateView.as_view(template_name='open-layers-example.html'),
        name='mvt_example'),
) + urlpatterns

urlpatterns += importer_urlpatterns
