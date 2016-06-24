# A python implementation of the osm-extract makefile
import sys
import os
import urllib
import psycopg2
import subprocess
import zipfile
import yaml
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def import_osm_data(dataset_name, dataset_url):
    if not dataset_name or not dataset_url:
        sys.exit("Both a name and url are required")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print("Current directory is {}".format(current_directory))
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
    data_directory_name = dataset_name
    data_directory_path = os.path.join(current_directory, data_directory_name)
    if not os.path.exists(data_directory_path):
        os.makedirs(data_directory_path)
    input_file_path = os.path.join(data_directory_path, input_file_name)

    if os.path.exists(input_file_path):
        print("Removing old file version")
        os.remove(input_file_path)

    print("Retrieving data from url ...")
    urllib.urlretrieve(dataset_url, input_file_path)
    print("Original OSM data has been saved to {}".format(input_file_path))
    print("Extracting OSM data to postgis")
    subprocess.call(['sudo', 'imposm', '--connection',
                     'postgis://{0}:{1}@localhost/{2}'.format(database_user, database_password, database_name),
                     '-m', '/var/lib/eventkit/osm-bright/imposm-mapping.py', '--read', '--write', '--optimize',
                     '--overwrite-cache', '--deploy-production-tables', input_file_path])
    print("The following tables were imported to postgis")

    conn = get_connection(database_name, 'postgres')
    cur = conn.cursor()
    cur.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")

    tables = []
    for table in cur.fetchall():
        if table[2].startswith('osm_'):
            if not table[2].startswith('osm_old') or table[2].startswith('osm_new'):
                tables.append(table[2])
    print tables
    print("Total table count: {}".format(len(tables)))

    if not tables:
        print("No tables found in database")
        quit()

    tables_removed = []

    for table in tables:
        try:
            print("Generating shp from postgis table '{}'".format(table))
            subprocess.check_output(['pgsql2shp', '-f', os.path.join(data_directory_path, table),
                                     '-u', database_name, '-P', database_name, database_name,
                                     'public.{0}'.format(table)])
        except subprocess.CalledProcessError:
            print("The table '{}' could not be converted to shp".format(table))
            tables_removed.append(table)

    if tables_removed:
        for table in tables_removed:
            tables.remove(table)
        print("Updated list of tables:")
        print tables

    for table in tables:
        print("Generating .shp.zip from {}.shp".format(table))
        z = zipfile.ZipFile(os.path.join(data_directory_path, "{}.shp.zip".format(table)), "w")
        z.write(os.path.join(data_directory_path, "{}.shp".format(table)))
        z.write(os.path.join(data_directory_path, "{}.prj".format(table)))
        z.write(os.path.join(data_directory_path, "{}.dbf".format(table)))
        z.write(os.path.join(data_directory_path, "{}.shx".format(table)))
        z.close()

    for table in tables:
        print("Generating json from {}.shp".format(table))
        subprocess.call(['ogr2ogr', '-f', 'GeoJSON', '-t_srs', 'crs:84',
                         os.path.join(data_directory_path, '{}.json'.format(table)),
                         os.path.join(data_directory_path, '{}.shp'.format(table))])

    for table in tables:
        print("Generating kml from {}.shp".format(table))
        subprocess.call(['ogr2ogr', '-f', 'KML', '-t_srs', 'crs:84',
                         os.path.join(data_directory_path, '{}.kml'.format(table)),
                         os.path.join(data_directory_path, '{}.shp'.format(table))])

    print("Generating gpkg from layers")
    for table in tables:
        print("Adding {} to gpkg . . .".format(table))
        subprocess.call(['ogr2ogr', '-f', 'GPKG', '-t_srs', 'crs:84', '-append',
                         os.path.join(data_directory_path, '{}.gpkg'.format(data_directory_name)),
                         os.path.join(data_directory_path, '{}.shp'.format(table))])
    print("GPGK creation finished")

    generate_mapnik_file(database_name)
    tables = get_osm_bright_tables()
    generate_mapproxy_file(tables, database_name)
    from register_service import register_service
    register_service(base_url='http://eventkit.dev/',
                     service_url='http://eventkit.dev/mapproxy/{}/service'.format(database_name),
                     service_name='eventkit')


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


def generate_mapproxy_file(tables, db_name):
    mapproxy_yaml = {'services': {
        'demo': None,
        'kml': None,
        'wmts': None,
        'tms': None,
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
    old_cwd = os.getcwd()
    os.chdir('/var/lib/eventkit/osm-bright')
    subprocess.call(['sudo', 'sed', '-i',
                     's/config\["postgis"\]\["dbname"\].*/config\["postgis"\]\["dbname"\]   = "{}"/g'.format(db_name),
                     '/var/lib/eventkit/osm-bright/configure.py'])
    subprocess.call(['sudo', 'python', '/var/lib/eventkit/osm-bright/configure.py'])
    subprocess.call(['sudo', 'python', '/var/lib/eventkit/osm-bright/make.py'])
    xml_output = subprocess.Popen(['sudo', '/var/lib/eventkit/mapproxy/magnacarto/magnacarto', '-mml',
                                   '/var/lib/eventkit/mapproxy/OSMBright/project.mml'], stdout=subprocess.PIPE)
    with open('/var/lib/eventkit/mapproxy/apps/{}.xml'.format(db_name), 'wb') as xml_file:
        xml_file.write(xml_output.stdout.read())
    subprocess.call(['sudo', 'sed', '-i', 's/background-color="#c4dff6"/background-color="transparent"/g',
                     '/var/lib/eventkit/mapproxy/apps/{}.xml'.format(db_name)])
    os.chdir(old_cwd)


def get_osm_bright_tables():
    return ['land-low', 'land-high', 'landuse_gen0', 'landuse_gen1', 'landuse',
            'waterway_low', 'waterway-med', 'waterway-high', 'water_gen0',
            'water_gen1', 'water', 'landuse_overlays', 'admin', 'buildings',
            'aeroway', 'tunnel', 'turning_circle_case', 'roads_high', 'roads_med',
            'roads_low', 'turning_circle_fill', 'bridge', 'barrier_points',
            'barrier_lines', 'place', 'area_label', 'motorway_label', 'mainroad_label',
            'minorroad_label', 'waterway_label']


name = sys.argv[1]
url = sys.argv[2]
import_osm_data(name, url)
