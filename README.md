# Eventkit-Live

Eventkit-Live is a demonstration live DVD for the Eventkit project. 
It is based on CentOS 7 and it can be used to deploy/install Eventkit on bare metal or on a Virtual Machine.

In order to build Eventkit-Live you need a working CentOS 7 machine or VM to act as a build host.

First you need to install epel:

	sudo yum install epel-release git

Then you need to install livecd tools:

	sudo yum install livecd-tools

Clone the git repository:

	git clone https://github.com/terranodo/eventkit-live.git
	cd geonode-live

And build the iso:

	livecd-creator -c centos-7-livecd.cfg -f eventkit-live --cache=/root/cache 2>&1 | tee /var/log/eventkit-live/build.log

The iso file will be available as eventkit-live.iso at the end of the build process and the build logs will be available at /var/log/eventkit-live/build.log
