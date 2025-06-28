# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
    # The most common configuration options are documented and commented below.
    # For a complete reference, please see the online documentation at
    # https://docs.vagrantup.com.
  
    # Every Vagrant development environment requires a box. You can search for
    # boxes at https://vagrantcloud.com/search.
  
    config.vm.box = "ubuntu/jammy64"

    config.vm.provider :virtualbox do |vb|
      vb.name = "fast"
      # Display the VirtualBox GUI when booting the machine
      vb.gui = true

      # Customize the amount of memory on the VM:
      vb.memory = "16384" # 16GB
      vb.cpus = 4
    end
  
    # Share an additional folder to the guest VM. The first argument is
    # the path on the host to the actual folder. The second argument is
    # the path on the guest to mount the folder. And the optional third
    # argument is a set of non-required options.
    config.vm.synced_folder ".", "/home/vagrant/fast", disabled: false
  
    # Disable the default share of the current code directory. Doing this
    # provides improved isolation between the vagrant box and your host
    # by making sure your Vagrantfile isn't accessable to the vagrant box.
    # If you use this you may want to enable additional shared subfolders as
    # shown above.
    config.vm.synced_folder ".", "/vagrant", disabled: true
  
    class GitHubEmail
        def valid_email?(email)
          # Regular expression for basic email validation
          email_regex = /\A[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\z/
          !!(email =~ email_regex) # Use =~ to check the match and convert to a boolean
        end
        def to_s
            print "-----------------------------------------------------------\n"
            print " Provide your fast email to generate SSH keys.\n"
            print "-----------------------------------------------------------\n"
            print "Email: " 
            email = STDIN.gets.chomp
  
            unless valid_email?(email)
              raise ArgumentError, "Invalid email address!"
            end
            return email
        end
    end
  
    class WaitingGithubSSHKey
        def to_s
          print "-----------------------------------------------------------\n"
          print " Visit https://github.com/settings/keys and set your new SSH Key.\n"
          print " Click ENTER when done.\n"
          print "-----------------------------------------------------------\n"
          return STDIN.gets.chomp
        end 
    end
  
    # Give execution permission to our scripts
    config.vm.provision "file", source: "./scripts", destination: "/home/vagrant/scripts"
    config.vm.provision "shell", inline: <<-SHELL
      su -l vagrant -s "/bin/bash" -c "chmod +x /home/vagrant/scripts/*/*.sh"
    SHELL
    # Install Oh My ZSh
    config.vm.provision "shell", path: "scripts/install/oh_my_zsh.sh"
    # Config Github SSH Keys
    config.vm.provision "shell", env: {"EMAIL" => GitHubEmail.new}, inline: <<-SHELL
      su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/config/github_ssh_key.sh $EMAIL"
    SHELL
    # Install Brew
    config.vm.provision "shell", inline: <<-SHELL
      su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/brew.sh"
    SHELL
    # Install dos2unis
    config.vm.provision "shell", path: "scripts/install/dos2unix.sh"
    # Install Python
    config.vm.provision "shell", inline: <<-SHELL
      su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/python.sh"
    SHELL
    # Install NodeJS
    config.vm.provision "shell", inline: <<-SHELL
      su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/nodejs.sh"
    SHELL
    # Install Java JRE/JDK
    config.vm.provision "shell", path: "scripts/install/java.sh"
    # Install Ubuntu Desktop Environment
    config.vm.provision "shell", path: "scripts/install/ui.sh"
    # Setup Complete message
    config.vm.provision "shell", inline: <<-SHELL
      echo "---> Setup Complete."
    SHELL
  end