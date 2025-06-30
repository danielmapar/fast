#!/bin/bash

echo "---> Installing java.sh"

sudo apt -y update
sudo apt -y upgrade
sudo apt -y install openjdk-21-jdk openjdk-21-jre

echo "---> Finished installing java.sh"