#!/bin/zsh

echo "---> Installing nodejs.sh"

sudo apt-get -y update
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

source ~/.bashrc
source ~/.zshrc

nvm install 18
nvm use 18

echo "---> Finished installing nodejs.sh"
