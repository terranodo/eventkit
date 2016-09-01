FROM geonode/django
MAINTAINER GeoNode development team

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


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

RUN pip install GDAL==1.10 --global-option=build_ext --global-option="-I/usr/include/gdal"

RUN pip install virtualenv
RUN virtualenv /var/lib/eventkit/.virtualenvs/eventkit

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

ONBUILD COPY requirements.txt /usr/src/app/
ONBUILD RUN pip install --no-cache-dir -r requirements.txt
ONBUILD RUN pip install -e .

ONBUILD COPY . /usr/src/app/
ONBUILD RUN pip install --no-deps --no-cache-dir -e /usr/src/app/

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
