# A python implementation of the osm-extract makefile
import sys
import getopt
import os
import urllib
import psycopg2
import subprocess
import zipfile
import yaml
import shutil
from tempfile import mkstemp
from shutil import move
from os import remove, close
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def import_osm_data(dataset_name, dataset_url,
                    data_directory=None, cache_directory=None,
                    kml=False, json=False, shp_zip = False,
                    gpkg=False):
    if not dataset_name or not dataset_url:
        sys.exit("Both a name and url are required")

    database_name = '{}_osm'.format(dataset_name)
    database_user = database_name
    database_password = database_name

    connection = get_connection(database_name, database_user)
    if connection:
        print("User and database have already been created")
    else:
        create_user(database_user)
        create_db(database_name, database_user, database_password)

    input_file_name = '{}.osm.pbf'.format(dataset_name)
    if not data_directory:
        data_directory = '/var/lib/eventkit/{}_data'.format(dataset_name)
    if not cache_directory:
        cache_directory = '/var/lib/eventkit/{}_imposm_cache'.format(dataset_name)
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)
    if os.path.exists(data_directory):
        print("Removing old directory")
        shutil.rmtree(data_directory)
    os.makedirs(data_directory)
    input_file_path = os.path.join(data_directory, input_file_name)

    print("Retrieving data from url ...")
    urllib.urlretrieve(dataset_url, input_file_path)
    print("Original OSM data has been saved to {}".format(input_file_path))
    print("Extracting OSM data to postgis")
    subprocess.call(['sudo', '/var/lib/eventkit/bin/imposm', '--connection',
                     'postgis://{0}:{1}@localhost/{2}'.format(database_user, database_password, database_name),
                     '-m', '/var/lib/eventkit/osm-bright/imposm-mapping.py', '--read', '--write', '--optimize',
                     '--overwrite-cache', '--cache-dir', cache_directory,
                     '--deploy-production-tables', input_file_path])

    tables = get_postgis_tables(database_name)

    if not tables:
        print("No tables found in database")
        quit()

    tables = generate_shp(tables, database_name, data_directory)

    if shp_zip:
        generate_shp_zip(tables, data_directory)

    if json:
        generate_json(tables, data_directory)

    if kml:
        generate_kml(tables, data_directory)

    if gpkg:
        generate_gpkg(tables, data_directory, database_name)

    generate_mapnik_file(database_name)
    tables = get_osm_bright_tables()
    generate_mapproxy_file(tables, database_name)
    from register_service import register_service
    register_service(base_url='http://eventkit.dev/',
                     service_url='http://eventkit.dev/mapproxy/{}/service'.format(database_name),
                     service_name=database_name)


def get_connection(db_name, user):
    try:
        conn = psycopg2.connect("dbname={0} user={1} host=localhost".format(db_name, user))
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    except psycopg2.DatabaseError:
        conn = None
    return conn


def create_user(role_name):
    print("Creating user and database")
    conn = get_connection('postgres', 'postgres')
    cur = conn.cursor()
    try:
        cur.execute('CREATE ROLE {0} SUPERUSER CREATEDB LOGIN'.format(role_name))
    except psycopg2.DatabaseError:
        print("User already exits")
    cur.close()
    conn.close()


def create_db(db_name, db_owner, db_password):
    conn = get_connection('postgres', 'postgres')
    cur = conn.cursor()
    try:
        cur.execute('CREATE DATABASE {0} ENCODING "UTF8" OWNER {1}'.format(db_name, db_owner))
    except psycopg2.DatabaseError:
        print("Database already exists")
    cur.close()
    conn.close()
    conn = get_connection(db_name, 'postgres')
    cur = conn.cursor()
    cur.execute("SELECT datname from pg_database")
    cur.execute("CREATE EXTENSION postgis")
    cur.execute("CREATE EXTENSION hstore")
    cur.execute("ALTER TABLE spatial_ref_sys OWNER to {}".format(db_owner))
    cur.execute("ALTER USER {0} WITH PASSWORD '{1}'".format(db_owner, db_password))
    cur.close()
    conn.close()


def get_postgis_tables(database_name):
    conn = get_connection(database_name, 'postgres')
    cur = conn.cursor()
    cur.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")

    tables = []
    for table in cur.fetchall():
        if table[2].startswith('osm_'):
            if not table[2].startswith('osm_old') or table[2].startswith('osm_new'):
                tables.append(table[2])
    cur.close()
    conn.close()
    return tables


def generate_shp(tables, database_name, data_directory):
    tables_removed = []
    for table in tables:
        try:
            print("Generating shp from postgis table '{}'".format(table))
            subprocess.check_output(['pgsql2shp', '-f', os.path.join(data_directory, table),
                                     '-u', database_name, '-P', database_name, database_name,
                                     'public.{0}'.format(table)])
        except subprocess.CalledProcessError:
            print("The table '{}' could not be converted to shp".format(table))
            tables_removed.append(table)

    if tables_removed:
        for table in tables_removed:
            tables.remove(table)
    return tables


def generate_shp_zip(tables, data_directory):
    for table in tables:
        print("Generating .shp.zip from {}.shp".format(table))
        z = zipfile.ZipFile(os.path.join(data_directory, "{}.shp.zip".format(table)), "w")
        z.write(os.path.join(data_directory, "{}.shp".format(table)))
        z.write(os.path.join(data_directory, "{}.prj".format(table)))
        z.write(os.path.join(data_directory, "{}.dbf".format(table)))
        z.write(os.path.join(data_directory, "{}.shx".format(table)))
        z.close()


def generate_json(tables, data_directory):
    for table in tables:
        print("Generating json from {}.shp".format(table))
        subprocess.call(['ogr2ogr', '-f', 'GeoJSON', '-t_srs', 'crs:84',
                         os.path.join(data_directory, '{}.json'.format(table)),
                         os.path.join(data_directory, '{}.shp'.format(table))])


def generate_kml(tables, data_directory):
    for table in tables:
        print("Generating kml from {}.shp".format(table))
        subprocess.call(['ogr2ogr', '-f', 'KML', '-t_srs', 'crs:84',
                         os.path.join(data_directory, '{}.kml'.format(table)),
                         os.path.join(data_directory, '{}.shp'.format(table))])


def generate_gpkg(tables, data_directory, gpkg_name):
    print("Generating gpkg from layers")
    for table in tables:
        print("Adding {} to gpkg . . .".format(table))
        subprocess.call(['ogr2ogr', '-f', 'GPKG', '-t_srs', 'crs:84', '-append',
                         os.path.join(data_directory, '{}.gpkg'.format(gpkg_name)),
                         os.path.join(data_directory, '{}.shp'.format(table))])
    print("GPGK creation finished")


def generate_mapproxy_file(tables, db_name):
    mapproxy_yaml = {'services': {
        'demo': None,
        'kml': None,
        'wmts': None,
        'tms': {'use_grid_names': True},
        'wms': {
            'srs': ['EPSG:4326', 'EPSG:900913', 'EPSG:3857'],
            'image_formats': ['image/jpeg', 'image/png'],
            'wms_opts': {'featureinfo': True},
            'md': {
                'title': 'EventKit WMS',
                'abstract': 'EventKit WMS',
                'online_resources': 'http://eventkit.org'}}},
        'grids': {
            'default_grid': {
                'origin': 'nw',
                'srs': 'EPSG:3857',
                'tile_size': [256, 256]}}}
    caches = {}
    layers = []
    sources = {}
    for table in tables:
        caches["{}_cache".format(table)] = {
            'cache': {
                'directory': '/cache/mapproxy/layer/{0}_{1}_cache'.format(db_name, table),
                'directory_layout': 'tms',
                'type': 'file'
            },
            'grids': ['default_grid'],
            'sources': [table]
        }
        layers.append({'name': table, 'title': '{0}_{1}'.format(db_name, table), 'sources': ['{}_cache'.format(table)]})
        sources[table] = {'type': 'mapnik', 'mapfile': '{}.xml'.format(db_name), 'layers': [table], 'transparent': True}
    mapproxy_yaml['caches'] = caches
    mapproxy_yaml['layers'] = layers
    mapproxy_yaml['sources'] = sources

    with open('/var/lib/eventkit/mapproxy/apps/{}.yaml'.format(db_name), 'w') as outfile:
        outfile.write(yaml.safe_dump(mapproxy_yaml, default_flow_style=False))


def generate_mapnik_file(db_name):
    file_path = '/var/lib/eventkit/mapproxy/apps/{}.xml'.format(db_name)
    old_cwd = os.getcwd()
    os.chdir('/var/lib/eventkit/osm-bright')
    subprocess.call(['sudo', 'sed', '-i',
                     's/config\["postgis"\]\["dbname"\].*/config\["postgis"\]\["dbname"\]   = "{}"/g'.format(db_name),
                     '/var/lib/eventkit/osm-bright/configure.py'])
    subprocess.call(['sudo', 'python', '/var/lib/eventkit/osm-bright/configure.py'])
    subprocess.call(['sudo', 'python', '/var/lib/eventkit/osm-bright/make.py'])
    xml_output = subprocess.Popen(['sudo', '/var/lib/eventkit/mapproxy/magnacarto/magnacarto', '-mml',
                                   '/var/lib/eventkit/mapproxy/OSMBright/project.mml'], stdout=subprocess.PIPE)
    with open(file_path, 'wb') as xml_file:
        xml_file.write(xml_output.stdout.read())
    subprocess.call(['sudo', 'sed', '-i', 's/background-color="#c4dff6"/background-color="transparent"/g',
                    file_path])
    fix_mangnacarto_xml(file_path)
    os.chdir(old_cwd)


def get_osm_bright_tables():
    return ['land-low', 'land-high', 'landuse_gen0', 'landuse_gen1', 'landuse',
            'waterway_low', 'waterway-med', 'waterway-high', 'water_gen0',
            'water_gen1', 'water', 'landuse_overlays', 'admin', 'buildings',
            'aeroway', 'tunnel', 'turning_circle_case', 'roads_high', 'roads_med',
            'roads_low', 'turning_circle_fill', 'bridge', 'barrier_points',
            'barrier_lines', 'place', 'area_label', 'motorway_label', 'mainroad_label',
            'minorroad_label', 'waterway_label']


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


def fix_mangnacarto_xml(file_path):
    replace(file_path, 'maxzoom', 'maximum-scale-denominator')
    replace(file_path, 'minzoom', 'minimum-scale-denominator')
    replace(file_path, 'unifont', 'Unifont')


def usage():
    print('--name: (required) The name of the dataset\n'
          '--url: (required) The url of the osm pbf dataset\n'
          '--cache-dir: The directory for imposm cache files\n'
          '--data-dir: The directory for any geospatial data files\n'
          '--kml: If you want kml data files generated\n'
          '--json: If you want json data files generated\n'
          '--shp-zip: If you want zipped shps generated\n'
          '--gpkg: If you want a gpkg generated')

try:
    options, remainder = getopt.getopt(
        sys.argv[1:], 'u:n:', ['name=', 'url=', 'cache-dir=', 'data-dir=',
                               'kml', 'json', 'shp-zip', 'gpkg', 'help'])
except getopt.GetoptError as err:
    print (err)
    quit()

name = None
url = None
data_directory = None
cache_directory = None
kml = False
json = False
shp_zip = False
gpkg = False

for opt, arg in options:
    if opt in ('-n', '--name'):
        name = arg
    elif opt in ('-u', '--url'):
        url = arg
    elif opt == '--cache-dir':
        cache_directory = arg
    elif opt == '--data-dir':
        data_directory = arg
    elif opt == '--kml':
        kml = True
    elif opt == '--json':
        json = True
    elif opt == '--shp-zip':
        shp_zip = True
    elif opt == '--gpkg':
        gpkg = True
    elif opt =='--help':
        usage()

import_osm_data(name, url, data_directory=data_directory,
                cache_directory=cache_directory, kml=kml, json=json,
                shp_zip=shp_zip, gpkg=gpkg)
