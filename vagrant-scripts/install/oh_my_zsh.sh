#!/bin/bash

echo "---> Installing oh_my_zsh.sh"

sudo apt -y install zsh
sudo chsh -s /bin/zsh vagrant
su -l vagrant -s "/bin/sh" -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

echo "---> Finished installing oh_my_zsh.sh"