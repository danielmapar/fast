echo "---> Installing Ubuntu Desktop Environment..."
apt-get update
apt-get install -y ubuntu-desktop-minimal

# Enable graphical login
systemctl set-default graphical.target

# Create a user session for vagrant user
usermod -aG sudo vagrant