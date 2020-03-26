Vagrant.configure(2) do |config|
    config.vm.box = "hashicorp/bionic64"
    config.vm.provider "virtualbox" do |vb|
      vb.cpus = 4
      vb.memory = 4096
    end
    config.vm.hostname = "test"
    config.vm.network "forwarded_port", guest: 80, host: 8081
    config.vm.network "forwarded_port", guest: 443, host: 8082
    config.vm.synced_folder ".", "/vagrant"
    config.ssh.extra_args = ["-t", "cd /vagrant; bash --login"]
    config.ssh.forward_agent = true  
    config.vm.provision "shell", path: "script.sh"
end
  