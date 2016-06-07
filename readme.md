Eventkit is a project aiming to allow data to be conveniently downloaded and served in a locally networked environment.  It is currently in develolpment. To set up the development VM.
- Install Vagrant. 
- Clone this repo. 
- In an elevated shell/prompt, install the hosts updater plugin:
   `vagrant plugin install vagrant-hostsupdater`
- Change into the eventkit directory (where the Vagrantfile is located), and run vagrant:
    `vagrant up`
- After the VM is prepared, open a browser and view the data at http://eventkit.dev.
