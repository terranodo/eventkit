# -*- mode: ruby -*-
# vi: set ft=ruby :
# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "geerlingguy/centos7"
  config.vm.provision :shell, path: "scripts/bootstrap.sh"
  config.vm.hostname = "eventkit.dev"

  ## create a private network visible only to the host machine
  config.vm.network :private_network, ip: "192.168.99.120"

  ## Example of share an additional folder to the guest VM.
  ## This is useful if wanting to do development on your localhost with an IDE/Editor of your choice
  #config.vm.synced_folder "../Eventkit/data", "/var/lib/eventkit/data"
  #config.vm.synced_folder "../mapproxy/mapproxy", "/usr/lib64/python2.7/site-packages/mapproxy"
  #config.vm.synced_folder "../django-osgeo-importer/osgeo_importer", "/usr/lib/python2.7/site-packages/osgeo_importer"

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "8224", "--cpus", "4"]
  end
  
end
