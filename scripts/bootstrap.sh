#!/usr/bin/env bash

# A bootstrap script for a geerlingguy/centos7 vagrant box

cd /etc/yum.repos.d/
sudo wget  https://yum.boundlessps.com/geoshape.repo
sudo yum install gdal-devel postgis-postgresql95 -y
sudo yum install postgresql95-contrib -y
sudo yum install libpqxx-devel -y
export PATH=$PATH:/usr/pgsql-9.5/bin
sudo echo "PATH=$PATH:/usr/pgsql-9.5/bin" >> /etc/profile.d/path.sh #HAVE TO BE SUDO SU
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
# sudo yum install proj -y
wget http://download.osgeo.org/proj/proj-4.9.2.tar.gz
tar -zxvf proj-4.9.2.tar.gz
cd proj-4.9.2
./configure
sudo make install
cd ..

#wget http://download.osgeo.org/gdal/2.1.0/gdal-2.1.0.tar.gz
#tar -zxvf gdal-2.1.0.tar.gz
#cd gdal-2.1.0
#./configure 
#cd gdal
#./configure --enable-shared --with-python --prefix=/usr/
#make
#make install
#sudo echo "LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH" >> /etc/profile.d/path.sh
#sudo echo "GDAL_DATA=/usr/share/gdal" >> /etc/profile.d/path.sh
#export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
#export GDAL_DATA=/usr/share/gdal
#cd -

#cd swig/python
#python setup.py build
#mkdir -p /usr/lib/python2.7/site-packages (replace python2.7 by appropriate version in all below commands)
#PYTHONPATH=/path/to/install/prefix/lib/python2.7/site-packages setup.py install --prefix=/path/to/install/prefix
## Check that this works with :
#PYTHONPATH=/path/to/install/prefix/lib/python2.7/site-packages:$PYTHONPATH python -c "from osgeo import gdal; print(gdal.__version__)"


# sudo yum groupinstall "development tools" -y
sudo yum install python-pip -y
sudo pip install --upgrade pip
sudo pip install backports.ssl_match_hostname
sudo pip install click
sudo pip install mapproxy
sudo pip install gdal
sudo chown postgres:postgres -R /var/lib/osmosis
#git clone https://github.com/terranodo/osm-extract.git
# using a fork so small changes can be made for use of demonstration
git clone https://github.com/lukerees/osm-extract.git
sudo mv osm-extract /var/lib/osm-extract
sudo chown -R postgres:postgres /var/lib/osm-extract

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
sudo yum install java-1.7.0-openjdk-devel -y 
sudo yum install tomcat -y

# GEONODE SETUP
git clone https://github.com/GeoNode/geonode.git
sudo mv geonode /home/geonode
cd /home
sudo chown -R geonode:geonode geonode
sudo chmod -R 755 geonode
cd /home/geonode/geonode
sudo pip install -e .
cd /home/geonode/geonode/geonode
sudo cp local_settings.py.sample local_settings.py
sudo echo "ALLOWED_HOSTS = ['192.168.99.120', 'localhost', '::1']" | sudo tee --append /home/geonode/geonode/geonode/local_settings.py
sudo echo "PROXY_ALLOWED_HOSTS = ('192.168.99.120', 'localhost', '::1')" | sudo tee --append /home/geonode/geonode/geonode/local_settings.py
sudo echo "POSTGIS_VERSION = (2, 2, 2)" | sudo tee --append /home/geonode/geonode/geonode/local_settings.py
sudo grep -q 'http://localhost:8000/' /home/geonode/geonode/geonode/local_settings.py && sudo sed -i "s/http:\/\/localhost:8000/http:\/\/localhost/g" /home/geonode/geonode/geonode/local_settings.py
sudo grep -q "'ENGINE': ''" /home/geonode/geonode/geonode/local_settings.py && sudo sed -i "s/'ENGINE': ''/# 'ENGINE': ''/g" /home/geonode/geonode/geonode/local_settings.py
sudo grep -q "#'ENGINE'" /home/geonode/geonode/geonode/local_settings.py && sudo sed -i "s/#'ENGINE'/'ENGINE'/g" /home/geonode/geonode/geonode/local_settings.py
sudo sed -i "0,/'NAME': 'geonode'/! s/'NAME': 'geonode'/'NAME': 'geonode_data'/g" /home/geonode/geonode/geonode/local_settings.py
sudo grep -q "'LOCATION' : 'http://localhost:8080/geoserver/'" /home/geonode/geonode/geonode/local_settings.py && sudo sed -i "s/'LOCATION' : 'http:\/\/localhost:8080\/geoserver\/'/'LOCATION' : 'http:\/\/localhost\/geoserver\/'/g" /home/geonode/geonode/geonode/local_settings.py
sudo grep -q "'PUBLIC_LOCATION' : 'http://localhost:8080/geoserver/'" /home/geonode/geonode/geonode/local_settings.py && sudo sed -i "s/'PUBLIC_LOCATION' : 'http:\/\/localhost:8080\/geoserver\/'/'PUBLIC_LOCATION' : 'http:\/\/localhost\/geoserver\/'/g" /home/geonode/geonode/geonode/local_settings.py
sudo chown geonode:geonode local_settings.py
sudo chmod 755 local_settings.py
cd /home/geonode/geonode
sudo chmod 777 /usr/lib/python2.7/site-packages/account
sudo -u geonode python /home/geonode/geonode/manage.py makemigrations sites
sudo -u geonode python /home/geonode/geonode/manage.py migrate sites
sudo -u geonode python /home/geonode/geonode/manage.py makemigrations account
sudo -u geonode python /home/geonode/geonode/manage.py migrate account
# sudo -u geonode python /home/geonode/geonode/manage.py makemigrations
# sudo -u geonode python /home/geonode/geonode/manage.py migrate
sudo -u geonode python /home/geonode/geonode/manage.py syncdb --noinput
sudo -u geonode python /home/geonode/geonode/manage.py collectstatic --noinput
sudo mkdir /home/geonode/geonode/geonode/uploaded/
sudo chmod +X /home/geonode/
sudo chown -R geonode /home/geonode/geonode/
sudo chown apache:apache /home/geonode/geonode/geonode/static/
sudo chown apache:apache /home/geonode/geonode/geonode/uploaded/
sudo chown apache:apache /home/geonode/geonode/geonode/static_root/

# TOMCAT SETUP
sudo mkdir /var/lib/tomcats/base
sudo cp -a /usr/share/tomcat/* /var/lib/tomcats/base/
sudo mkdir /var/lib/tomcats/geoserver
sudo cp -a /usr/share/tomcat/* /var/lib/tomcats/geoserver/
sudo cp /usr/lib/systemd/system/tomcat.service /usr/lib/systemd/system/tomcat\@geoserver.service
sudo grep -q "EnvironmentFile=-/etc/sysconfig/tomcat" /usr/lib/systemd/system/tomcat\@geoserver.service && sudo sed -i "s/EnvironmentFile=-\/etc\/sysconfig\/tomcat/EnvironmentFile=-\/etc\/sysconfig\/tomcat@geoserver/g" /usr/lib/systemd/system/tomcat\@geoserver.service
sudo cp /etc/sysconfig/tomcat /etc/sysconfig/tomcat\@geoserver
sudo grep -q '#CATALINA_BASE' /etc/sysconfig/tomcat\@geoserver && sudo sed -i 's/#CATALINA_BASE/CATALINA_BASE/g' /etc/sysconfig/tomcat\@geoserver
sudo grep -q 'CATALINA_BASE="\/usr\/share\/tomcat"' /etc/sysconfig/tomcat\@geoserver && sudo sed -i 's/CATALINA_BASE="\/usr\/share\/tomcat"/CATALINA_BASE="\/var\/lib\/tomcats\/geoserver"/g' /etc/sysconfig/tomcat\@geoserver
cd /var/lib/tomcats/geoserver/webapps/
sudo wget http://build.geonode.org/geoserver/latest/geoserver.war

sudo chown -R tomcat:tomcat /var/lib/tomcats*
sudo systemctl start tomcat@geoserver
sudo systemctl enable tomcat@geoserver

# APACHE SETUP
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --reload
sudo setsebool -P httpd_can_network_connect_db 1
sudo su -c "echo '
WSGIDaemonProcess geonode python-path=/home/geonode/geonode:/home/geonode/.venvs/geonode/lib/python2.7/site-packages user=apache threads=15 processes=2

<VirtualHost *:80>
    ServerName http://localhost
    ServerAdmin webmaster@localhost
    DocumentRoot /home/geonode/geonode/geonode

    ErrorLog /var/log/httpd/error.log
    LogLevel warn
    CustomLog /var/log/httpd/access.log combined

    WSGIProcessGroup geonode
    WSGIPassAuthorization On
    WSGIScriptAlias / /home/geonode/geonode/geonode/wsgi.py

    Alias /static/ /home/geonode/geonode/geonode/static_root/
    Alias /uploaded/ /home/geonode/geonode/geonode/uploaded/

    <Directory "/home/geonode/geonode/geonode/">
         <Files wsgi.py>
             Order deny,allow
             Allow from all
             Require all granted
         </Files>

        Order allow,deny
        Options Indexes FollowSymLinks
        Allow from all
        IndexOptions FancyIndexing
    </Directory>

    <Directory "/home/geonode/geonode/geonode/static_root/">
        Order allow,deny
        Options Indexes FollowSymLinks
        Allow from all
        Require all granted
        IndexOptions FancyIndexing
    </Directory>

    <Directory "/home/geonode/geonode/geonode/uploaded/thumbs/">
        Order allow,deny
        Options Indexes FollowSymLinks
        Allow from all
        Require all granted
        IndexOptions FancyIndexing
    </Directory>

    <Proxy *>
        Order allow,deny
        Allow from all
    </Proxy>

    ProxyPreserveHost On
    ProxyPass /geoserver http://192.168.99.120:8080/geoserver
    ProxyPassReverse /geoserver http://192.168.99.120:8080/geoserver

</VirtualHost>' >> /etc/httpd/conf.d/geonode.conf"
sudo mkdir -p /home/geonode/geonode/geonode/uploaded/thumbs
sudo mkdir -p /home/geonode/geonode/geonode/uploaded/layers
sudo chown -R geonode /home/geonode/geonode/
sudo chown geonode:apache /home/geonode/geonode/geonode/static/
sudo chown geonode:apache /home/geonode/geonode/geonode/uploaded/
sudo chmod -Rf 777 /home/geonode/geonode/geonode/uploaded/thumbs
sudo chmod -Rf 777 /home/geonode/geonode/geonode/uploaded/layers
sudo chown apache:apache /home/geonode/geonode/geonode/static_root/

sudo systemctl start httpd
sudo systemctl enable httpd

sudo -u geonode python /home/geonode/geonode/manage.py createsuperuser --username admin --email admin@geonode.com

#cd /var/lib/osm-extract
#sudo -u postgres make clean all NAME=guinea_bissau URL=http://download.geofabrik.de/africa/guinea-bissau-latest.osm.pbf
#cd guinea_bissau
#sudo mapproxy-util serve-develop ./mapproxy.yaml -b eventkit.dev:80