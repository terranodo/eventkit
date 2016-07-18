from __future__ import absolute_import

from djmp.models import Tileset
from mapproxy.script.conf.app import config_command
import yaml
from django.core.files.temp import NamedTemporaryFile
import logging
from .voyagersearch import export_voyager_data
from django.db import IntegrityError
from django.conf import settings

log = logging.getLogger(__name__)


def create_conf_from_wms(wms_url, name="Eventkit", bbox=None):
    """

    :param wms_url: A URL for an external service.
    :param name: The name of the service.
    :param bbox: A bounding box as an array (e.g. [-180, -89, 180, 89])(not implemented)
    :return: None
    """
    temp_file = NamedTemporaryFile()
    # wms_url = wms_url.replace('"','')
    params = ['--capabilities', wms_url, '--output', temp_file.name, '--force']
    config_command(params)
    conf_dict = None
    try:
        conf_dict = yaml.load(temp_file)
    except yaml.YAMLError as exc:
        log.error(exc)
    create_tileset_from_conf_dict(conf_dict, name)


def create_confs_from_voyager(base_url, voyager_ids, bbox=None):
    """

    :param base_url: URL of server running voyagersearch
    :param voyager_ids: A list of ids to request relevant metadata from voyager.
    :param bbox: A bounding box to narrow results (e.g. [-180, -89, 180, 89])(not implemented)
    :return: None
    """
    service_list = export_voyager_data(base_url, voyager_ids=voyager_ids)
    if not service_list:
        return None
    for service in service_list:
        if 'wms' in service.get('format'):
            if not service.get('url'):
                continue
            create_conf_from_wms(service.get('url'), name=service.get('title'))


def create_tileset_from_conf_dict(conf_dict, name):
    """

    :param conf_dict: A mapproxy configuration yaml as a dict.
    :param name: The desired name of the new service.
    :return: None
    """

    name = name
    created_by = "Eventkit Service"
    cache_type = 'file'
    directory_layout = 'tms'
    directory = getattr(settings, 'CACHE_DIR', '/cache')
    filename = None
    table_name = None
    server_url = None
    source_type = 'wms'
    mapfile = None
    layer_zoom_stop = 6

    layers = get_layers(conf_dict.get('layers'))
    for layer in layers:
        layer_name = layer.get('name')
        bbox = None
        for source in layer.get('sources'):
            layer_source_data = conf_dict.get('sources').get(source) or conf_dict.get('caches').get(source)
            if layer_source_data.get('cache'):
                cache_type = layer_source_data.get('cache').get('type')
                directory_layout = layer_source_data.get('cache').get('directory_layout')
                directory = layer_source_data.get('cache').get('directory')
                filename = layer_source_data.get('cache').get('filename')
                table_name = layer_source_data.get('cache').get('table_name')

                if layer_source_data.get('cache').get('grids'):
                    for grid in layer_source_data.get('cache').get('grids'):
                        if grid.get('srs').lower() == 'epsg:4326':
                            temp_bbox = conf_dict.get('grids').get(grid).get('bbox')
                            if bbox and temp_bbox:
                                #since we are supporting only one grid, ensure that grid covers all of the grids area.
                                for i in [0, 1]:
                                    bbox[i] = temp_bbox if temp_bbox[i] < bbox[i] else bbox[i]
                                for i in [2, 3]:
                                    bbox[i] = temp_bbox if temp_bbox[i] > bbox[i] else bbox[i]
                            elif temp_bbox:
                                bbox = temp_bbox
            if layer_source_data.get('type', ' ').lower() == 'wms':
                server_url = layer_source_data.get('req').get('url')
                source_type = 'wms'
            if layer_source_data.get('type', ' ').lower() == 'mapnik':
                mapfile = layer_source_data.get('mapfile')
        if not bbox:
            bbox = [-180, -89, 180, 89]
        try:
            Tileset.objects.get_or_create(name=name,
                                          created_by=created_by,
                                          layer_name=layer_name,
                                          cache_type=cache_type,
                                          directory_layout=directory_layout,
                                          directory=directory,
                                          filename=filename,
                                          table_name=table_name,
                                          bbox_x0=bbox[0],
                                          bbox_y0=bbox[1],
                                          bbox_x1=bbox[2],
                                          bbox_y1=bbox[3],
                                          server_url=server_url,
                                          source_type=source_type,
                                          mapfile=mapfile,
                                          layer_zoom_stop=layer_zoom_stop)
        except IntegrityError:
            continue

def get_layers(layers):
    """

    :param layers: A layer dict from the mapproxy configuration.
    :return: A flattened version of the layer dict (i.e. not nested).
    """
    layer_list = []
    for layer in layers:
        if isinstance(layer, dict) and layer.get('layers'):
            layer_list += get_layers(layer.get('layers'))
        else:
            layer_list += [layer]
    return layer_list



