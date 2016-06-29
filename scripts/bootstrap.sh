#!/usr/bin/env bash

# A bootstrap script for a geerlingguy/centos7 vagrant box

cd /etc/yum.repos.d/
sudo wget  https://yum.boundlessps.com/geoshape.repo
sudo yum install gdal-devel postgis-postgresql95 -y
sudo yum install postgresql95-contrib -y
sudo yum install libpqxx-devel -y
export PATH=$PATH:/usr/pgsql-9.5/bin
sudo echo "PATH=$PATH:/usr/pgsql-9.5/bin" >> /etc/profile.d/path.sh
export PG_CONFIG=/usr/pgsql-9.5/bin/pg_config
sudo echo "PG_CONFIG=/usr/pgsql-9.5/bin/pg_config" >> /etc/profile.d/path.sh
sudo /usr/pgsql-9.5/bin/postgresql95-setup initdb
sudo service postgresql-9.5 start
sudo systemctl enable postgresql-9.5

wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
mkdir osmosis
mv osmosis-latest.tgz osmosis
cd osmosis
tar xvfz osmosis-latest.tgz
rm -rf osmosis-latest.tgz
chmod a+x bin/osmosis
cd ..
sudo mv osmosis /var/lib/osmosis
sudo ln -s /var/lib/osmosis/bin/osmosis /usr/bin/osmosis  
sudo ln -s /var/lib/osmosis/bin/osmosis-extract-apidb-0.6 /usr/bin/osmosis-extract-apidb-0.6
sudo ln -s /var/lib/osmosis/bin/osmosis-extract-mysql-0.6 /usr/bin/osmosis-extract-mysql-0.6

sudo yum install scons -y
sudo yum install zip -y
sudo yum install vim -y
sudo yum install git -y
sudo yum install java -y
sudo yum install boost-devel harfbuzz-devel libicu-devel freetype-devel sqlite-devel python-devel libjpeg-devel libpng-devel -y
sudo yum install gcc gcc-c++ -y
sudo yum install mlocate -y
wget http://download.osgeo.org/proj/proj-4.9.2.tar.gz
tar -zxvf proj-4.9.2.tar.gz
cd proj-4.9.2
./configure
sudo make install
cd ..
sudo yum install proj-epsg -y


sudo yum install python-pip -y
sudo pip install --upgrade pip
sudo pip install backports.ssl_match_hostname
sudo pip install click
sudo pip install mapproxy
cd /var/lib/
sudo git clone https://github.com/terranodo/mapproxy.git
cd mapproxy/
sudo git checkout addGeopackageCache
sudo rm -rf /usr/lib64/python2.7/site-packages/mapproxy
sudo ln -s /var/lib/mapproxy/mapproxy /usr/lib64/python2.7/site-packages/

sudo pip install -e git://github.com/terranodo/django-mapproxy.git@registry#egg=django-mapproxy


sudo pip install gdal
sudo pip install uwsgi
sudo pip install numpy
sudo pip install gunicorn
sudo pip install eventlet
sudo chown vagrant:vagrant -R /var/lib/osmosis
git clone https://github.com/terranodo/osm-extract.git
sudo mv osm-extract /var/lib/osm-extract
sudo chown -R vagrant:vagrant /var/lib/osm-extract
sudo -u postgres psql -c 'CREATE ROLE vagrant WITH CREATEDB SUPERUSER LOGIN;'
sudo -u postgres createdb -O vagrant vagrant

sudo git clone https://github.com/mapnik/mapnik.git
cd mapnik
sudo git checkout v3.0.10
sudo git submodule update --init
sudo python scons/scons.py configure PG_CONFIG=/usr/pgsql-9.5/bin/pg_config
sudo make
sudo make install 
cd ..


sudo git clone https://github.com/mapnik/python-mapnik
cd python-mapnik
sudo su -c "echo '/usr/local/lib' >> /etc/ld.so.conf.d/eventkit.conf"
sudo ldconfig
export PATH=$PATH:/usr/local/bin
sudo echo "PATH=$PATH:/usr/local/bin" >> /etc/profile.d/path.sh
sudo env "PATH=$PATH" python setup.py install
cd ..

sudo yum install tokyocabinet-devel protobuf-devel protobuf-compiler spatialindex bzip2-devel -y

sudo pip install rtree
sudo env "PATH=$PATH" pip install imposm

cd /var/lib/eventkit
sudo git clone https://github.com/mapbox/osm-bright.git
cd osm-bright
sudo cp /var/lib/eventkit/osm-bright/osm-bright/fonts/* /usr/local/lib/mapnik/fonts/
sudo cp /var/lib/eventkit/osm-bright/configure.py.sample /var/lib/eventkit/osm-bright/configure.py
sudo yum install unzip -y
sudo grep -q 'config\["importer"\] = "osm2pgsql"' /var/lib/eventkit/osm-bright/configure.py && sudo sed -i 's/config\["importer"\] = "osm2pgsql"/config\["importer"\] = "imposm"/g' /var/lib/eventkit/osm-bright/configure.py
sudo grep -q 'config\["postgis"\]\["user"\]     = ""' /var/lib/eventkit/osm-bright/configure.py && sudo sed -i 's/config\["postgis"\]\["user"\]     = ""/config\["postgis"\]\["user"\]     = "postgres"/g' /var/lib/eventkit/osm-bright/configure.py
sudo grep -q 'config\["postgis"\]\["password"\] = ""' /var/lib/eventkit/osm-bright/configure.py && sudo sed -i 's/config\["postgis"\]\["password"\] = ""/config\["postgis"\]\["password"\] = "postgres"/g' /var/lib/eventkit/osm-bright/configure.py
sudo grep -q  'path\.expanduser("\~\/Documents\/MapBox\/project")' /var/lib/eventkit/osm-bright/configure.py && sudo sed -i 's/path\.expanduser("\~\/Documents\/MapBox\/project")/path\.expanduser("\/var\/lib\/eventkit\/mapproxy")/g' /var/lib/eventkit/osm-bright/configure.py
sudo mkdir /var/lib/eventkit/osm-bright/shp
cd /var/lib/eventkit/osm-bright/shp
sudo wget http://data.openstreetmapdata.com/simplified-land-polygons-complete-3857.zip
sudo unzip simplified-land-polygons-complete-3857
sudo wget http://data.openstreetmapdata.com/land-polygons-split-3857.zip
sudo unzip land-polygons-split-3857
sudo mkdir -p /var/lib/eventkit/mapproxy/apps
cd /var/lib/eventkit/mapproxy
sudo wget http://download.omniscale.de/magnacarto/rel/dev-20160406-012a66a/magnacarto-dev-20160406-012a66a-linux-amd64.tar.gz
sudo tar -xzvf magnacarto-dev-20160406-012a66a-linux-amd64.tar.gz
sudo mv magnacarto-dev-20160406-012a66a-linux-amd64 magnacarto
sudo yum install golang -y
export GOROOT=/usr/lib/golang
sudo echo "GOROOT=/usr/lib/golang" >> /etc/profile.d/path.sh
export GOPATH=/var/lib/eventkit
sudo echo "GOPATH=/var/lib/eventkit" >> /etc/profile.d/path.sh
cd /var/lib/eventkit
go get -d github.com/omniscale/go-mapnik
go generate github.com/omniscale/go-mapnik
go install github.com/omniscale/go-mapnik
cd -

sudo grep -q '   peer' /var/lib/pgsql/9.5/data/pg_hba.conf && sudo sed -i "s/   peer/   trust/g" /var/lib/pgsql/9.5/data/pg_hba.conf
sudo grep -q '   ident' /var/lib/pgsql/9.5/data/pg_hba.conf && sudo sed -i "s/   ident/   trust/g" /var/lib/pgsql/9.5/data/pg_hba.conf
sudo grep -q '127.0.0.1' /var/lib/pgsql/9.5/data/pg_hba.conf && sudo sed -i "s/127.0.0.1\/32     /192.168.99.120\/32/g" /var/lib/pgsql/9.5/data/pg_hba.conf
sudo systemctl restart postgresql-9.5
grep -q '127.0.0.1' /etc/hosts && sed -i "s/127.0.0.1/192.168.99.120/g" /etc/hosts
sudo service network restart

# SETUP USER AND DB
sudo adduser -m geonode
sudo -u postgres psql -c "CREATE USER geonode WITH PASSWORD 'geonode';"
sudo -u postgres createdb -O geonode geonode
sudo -u postgres createdb -O geonode geonode_data
sudo -u postgres psql -d geonode_data -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d geonode_data -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
sudo -u postgres psql -d geonode_data -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'

#INSTALL GEONODE DEPENDENCIES
sudo yum install python-imaging python-virtualenv python-psycopg2 libxml2-devel libxml2-python libxslt-devel libxslt-python -y 
sudo yum install httpd -y
sudo yum install mod_ssl mod_proxy_html mod_wsgi -y
sudo pip install decorator

# GEONODE SETUP
sudo yum install supervisor -y
cd ~
sudo pip install git+https://github.com/ProminentEdge/django-osgeo-importer.git
sudo git clone https://github.com/terranodo/eventkit.git
sudo mv eventkit/* /var/lib/eventkit/
git clone https://github.com/GeoNode/geonode.git
sudo mv geonode/geonode /var/lib/eventkit/
sudo ln -s /var/lib/eventkit/geonode /usr/lib/python2.7/site-packages/
sudo ln -s /var/lib/eventkit/eventkit /usr/lib/python2.7/site-packages/
sudo ln -s /var/lib/osm-extract/osm_extract /usr/lib/python2.7/site-packages/
sudo mkdir /var/log/eventkit
sudo pip install -e ~/geonode/

sudo cp /var/lib/eventkit/geonode/local_settings.py.sample /var/lib/eventkit/geonode/local_settings.py
sudo echo "ALLOWED_HOSTS = ['192.168.99.120', 'localhost', '::1']" | sudo tee --append /var/lib/eventkit/geonode/local_settings.py
sudo echo "PROXY_ALLOWED_HOSTS = ('192.168.99.120', 'localhost', '::1')" | sudo tee --append /var/lib/eventkit/geonode/local_settings.py
sudo echo "POSTGIS_VERSION = (2, 2, 2)" | sudo tee --append /var/lib/eventkit/geonode/local_settings.py
sudo grep -q 'http://localhost:8000/' /var/lib/eventkit/geonode/local_settings.py && sudo sed -i "s/http:\/\/localhost:8000/http:\/\/localhost/g" /var/lib/eventkit/geonode/local_settings.py
sudo grep -q "'ENGINE': ''" /var/lib/eventkit/geonode/local_settings.py && sudo sed -i "s/'ENGINE': ''/# 'ENGINE': ''/g" /var/lib/eventkit/geonode/local_settings.py
sudo grep -q "#'ENGINE'" /var/lib/eventkit/geonode/local_settings.py && sudo sed -i "s/#'ENGINE'/'ENGINE'/g" /var/lib/eventkit/geonode/local_settings.py
sudo sed -i "0,/'NAME': 'geonode'/! s/'NAME': 'geonode'/'NAME': 'geonode_data'/g" /var/lib/eventkit/geonode/local_settings.py
sudo grep -q "'LOCATION' : 'http://localhost:8080/geoserver/'" /var/lib/eventkit/geonode/local_settings.py && sudo sed -i "s/'LOCATION' : 'http:\/\/localhost:8080\/geoserver\/'/'LOCATION' : 'http:\/\/localhost\/geoserver\/'/g" /var/lib/eventkit/geonode/local_settings.py
sudo grep -q "'PUBLIC_LOCATION' : 'http://localhost:8080/geoserver/'" /var/lib/eventkit/geonode/local_settings.py && sudo sed -i "s/'PUBLIC_LOCATION' : 'http:\/\/localhost:8080\/geoserver\/'/'PUBLIC_LOCATION' : 'http:\/\/192.168.99.120\/geoserver\/'/g" /var/lib/eventkit/geonode/local_settings.py
sudo grep -q 'SITEURL = "https://localhost/"' /var/lib/eventkit/geonode/local_settings.py && sudo sed -i 's/SITEURL = "http:\/\/localhost\/"/SITEURL = "http:\/\/192.168.99.120\/"/g' /var/lib/eventkit/geonode/local_settings.py

chown vagrant:vagrant -R /var/lib/eventkit
sudo chmod -R 755 /var/lib/eventkit/geonode
sudo chmod 777 /usr/lib/python2.7/site-packages/account


sudo python /var/lib/eventkit/manage.py makemigrations --noinput
sudo python /var/lib/eventkit/manage.py migrate --noinput
sudo python /var/lib/eventkit/manage.py collectstatic --noinput
sudo mkdir /var/lib/eventkit/geonode/uploaded/
sudo mkdir /cache
sudo chown vagrant:vagrant /cache

sudo echo '[unix_http_server]
file=/var/run/supervisor.sock

[supervisord]
pidfile=/var/run/supervisor.pid
logfile=/var/log/supervisor.log
logfile_backups=1

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[group:eventkit]
programs=gunicorn-geonode,gunicorn-mapproxy
priority=999

[program:gunicorn-geonode]
command =  /bin/gunicorn eventkit.wsgi:application
           --bind eventkit.dev:6443
           --worker-class eventlet
           --workers 2
           --threads 4
           --access-logfile /var/log/eventkit/geonode-access-log.txt
           --error-logfile /var/log/eventkit/geonode-error-log.txt
           --name eventkit
           --user vagrant
           --keyfile /etc/pki/eventkit/key.pem
           --certfile /etc/pki/eventkit/cert.pem
autostart=true
autorestart=true
stdout_logfile=/var/log/eventkit/stdout.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
stderr_logfile=/var/log/eventkit/stderr.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=5
stopsignal=INT

[program:gunicorn-mapproxy]
command =  /bin/gunicorn mapproxy.wsgi:application
           --bind eventkit.dev:7443
           --worker-class eventlet
           --workers 4
           --threads 8
           --access-logfile /var/log/eventkit/mapproxy-access-log.txt
           --error-logfile /var/log/eventkit/mapproxy-error-log.txt
           --name eventkit
           --user vagrant
           --no-sendfile
           --keyfile /etc/pki/eventkit/key.pem
           --certfile /etc/pki/eventkit/cert.pem
autostart=true
autorestart=true
stdout_logfile=/var/log/eventkit/stdout.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
stderr_logfile=/var/log/eventkit/stderr.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=5
stopsignal=INT' > /etc/supervisord.conf

sudo echo 'ServerLimit 16
StartServers 2
MinSpareServers 2
MaxSpareServers 4
<VirtualHost *:443>
    ServerName eventkit.dev
    ServerAdmin webmaster@localhost
    DocumentRoot /var/lib/eventkit/geonode


    ErrorLog /var/log/httpd/error.log
    LogLevel warn
    CustomLog /var/log/httpd/access.log combined

    Alias /static/ /var/lib/eventkit/geonode/static_root/
    Alias /uploaded/ /var/lib/eventkit/geonode/uploaded/
    SSLEngine on
    SSLProxyEngine on
    SSLCertificateFile /etc/pki/eventkit/cert.pem
    SSLCertificateKeyFile /etc/pki/eventkit/key.pem
    ProxyRequests Off
    ProxyPreserveHost On
    <Location /mapproxy>
        ProxyPass https://192.168.99.120:7443
        ProxyPassReverse  https://192.168.99.120:7443
        RequestHeader unset X-Script-Name
        RequestHeader add X-Script-Name "/mapproxy"
    </Location>

    ProxyPass / https://eventkit.dev:6443/
    ProxyPassReverse / https://eventkit.dev:6443/

</VirtualHost>' > /etc/httpd/conf.d/eventkit.conf

echo "from mapproxy.multiapp import make_wsgi_app
application = make_wsgi_app('/var/lib/eventkit/mapproxy/apps', allow_listing=True)" > /usr/lib64/python2.7/site-packages/mapproxy/wsgi.py

sudo chown vagrant:vagrant -R /var/lib/eventkit/
sudo chmod -R 755 /var/lib/eventkit/

sudo mkdir /etc/pki/eventkit
cd /etc/pki/eventkit
sudo openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=eventkit.dev'
sudo cp /etc/pki/eventkit/cert.pem /etc/pki/ca-trust/source/anchors/
sudo cp /etc/pki/eventkit/key.pem /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust extract

sudo systemctl start firewalld
sudo systemctl enable firewalld

sudo firewall-cmd --zone=internal --add-port=6443/tcp --permanent
sudo firewall-cmd --zone=internal --add-port=7443/tcp --permanent
sudo firewall-cmd --zone=public --add-port=5432/tcp --permanent
sudo firewall-cmd --zone=public --add-port=443/tcp --permanent
sudo firewall-cmd --reload
sudo setsebool -P httpd_can_network_connect_db 1

sudo service supervisord start
sudo systemctl enable supervisord

sudo systemctl start httpd
sudo systemctl enable httpd

sudo echo '[
    {
        "pk": 1,
        "model": "people.profile",
        "fields": {
            "profile": null,
            "last_name": "",
            "is_staff": true,
            "user_permissions": [],
            "date_joined": "2016-06-15T14:25:19.000",
            "city": null,
            "first_name": "",
            "area": null,
            "zipcode": null,
            "is_superuser": true,
            "last_login": "2016-06-15T14:25:19.000",
            "email": "admin@geonode.org",
            "username": "admin",
            "fax": null,
            "is_active": true,
            "delivery": null,
            "groups": [
                1
            ],
            "organization": null,
            "password": "pbkdf2_sha256$20000$qH1pQEscvOgy$ypOQA/Ogej//J0218c39CFXobmv14050/hwWHnvhgxg=",
            "country": null,
            "position": null,
            "voice": null
        }
    }
]' > /var/lib/eventkit/geonode/fixtures.json


sudo python /var/lib/eventkit/manage.py loaddata /var/lib/eventkit/geonode/fixtures.json

# python /var/lib/eventkit/scripts/osm_importer.py --name rio --url https://s3.amazonaws.com/metro-extracts.mapzen.com/rio-de-janeiro_brazil.osm.pbf
