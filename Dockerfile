FROM geonode/django
MAINTAINER Jeff Johnson <jeff@terranodo.io>

# The geonode/django image is pulling most of the Django requirements
# and takes care of copying the current folder onto the container
# and installing it's requirements file.

RUN apt-get update && apt-get install -y \
        gcc \
        gettext \
        postgresql-client libpq-dev \
        sqlite3 \
                python-gdal python-psycopg2 \
                python-imaging python-lxml \
                python-dev libgdal-dev \
                python-ldap \
                libmemcached-dev libsasl2-dev zlib1g-dev \
                libprotobuf-dev protobuf-compiler \
                libtokyocabinet-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*
