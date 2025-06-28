#!/bin/bash

email=$1

if [[ "${email}" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    # Extract the user part before '@'
    user="${email%%@*}"

    ssh-keygen -q -t rsa -b 4096 -C "${email}" -N '' -f ~/.ssh/id_rsa <<<y >/dev/null 2>&1
    echo "SSH keys generated, please setup GitHub with: "
    cat ~/.ssh/id_rsa.pub

    git config --global user.name "${user}"
    git config --global user.email "${email}"
    git config --global --add oh-my-zsh.hide-status 1
    git config --global --add oh-my-zsh.hide-dirty 1
else
  echo "Invalid email address!"
fi