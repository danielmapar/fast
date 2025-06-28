#!/bin/bash

echo "---> Installing brew.sh"

sudo apt-get install build-essential

/bin/bash -c "NONINTERACTIVE=1 HOMEBREW_NO_ENV_HINTS=1 HOMEBREW_NO_INSTALL_CLEANUP=1 $(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

(echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/vagrant/.bashrc
(echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/vagrant/.zshrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

echo "---> Finished installing brew.sh"