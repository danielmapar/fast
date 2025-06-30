echo "---> Installing Ubuntu Desktop..."
sudo apt-add-repository multiverse && sudo apt-get update -y
sudo apt upgrade -y

sudo apt-get install -y virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11

# install the desktop.
apt-get install -y --no-install-recommends \
    xorg \
    xserver-xorg-video-qxl \
    xserver-xorg-video-fbdev \
    xserver-xorg-video-vmware \
    xfce4 \
    xfce4-terminal \
    lightdm \
    lightdm-gtk-greeter \
    xfce4-whiskermenu-plugin \
    xfce4-taskmanager \
    menulibre \
    firefox

sudo apt-get install -y virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11

# Add vagrant user to necessary groups for GUI access
sudo usermod -aG sudo,adm,dialout,cdrom,floppy,audio,dip,video,plugdev,netdev vagrant

# Configure LightDM for automatic login (optional - remove if you want manual login)
sudo mkdir -p /etc/lightdm/lightdm.conf.d
sudo tee /etc/lightdm/lightdm.conf.d/50-vagrant.conf > /dev/null <<EOF
[Seat:*]
autologin-user=vagrant
autologin-user-timeout=0
user-session=xfce
EOF

echo "---> Desktop setup complete. User: vagrant, Password: vagrant"