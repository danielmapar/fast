#!/bin/bash

echo "---> Installing pre-commit.sh"

eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# Install Pre Commit
NONINTERACTIVE=1 brew install pre-commit

echo "---> Finished installing pre-commit.sh"