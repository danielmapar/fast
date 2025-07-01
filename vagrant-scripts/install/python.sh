#!/bin/bash

echo "---> Installing python.sh"

sudo apt -y update
sudo apt -y install \
    build-essential \
    curl \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    make \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev
curl https://pyenv.run | bash

# Add pyenv to bashrc and zshrc
cat << 'EOF' >> ~/.bashrc
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# https://github.com/pyenv/pyenv-virtualenv/issues/42
# eval "$(pyenv virtualenv-init -)"
EOF
cat << 'EOF' >> ~/.zshrc
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# https://github.com/pyenv/pyenv-virtualenv/issues/42
# eval "$(pyenv virtualenv-init -)"
EOF

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install python 3.13.0
pyenv install --force 3.13.0
pyenv global 3.13.0

# Install poetry
sudo apt -y install pipx
pipx ensurepath
pipx install poetry==1.8.4
pipx ensurepath

echo "---> Finished installing python.sh"