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

  # Example of share an additional folder to the guest VM.
  config.vm.synced_folder "../Eventkit", "/var/lib/eventkit"
  config.vm.synced_folder "../mapproxy/mapproxy", "/var/lib64/python2.7/site-packages/mapproxy"
  
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "6144", "--cpus", "2"]
  end
  
end