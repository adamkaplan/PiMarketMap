# This is the process used to create distribution
# images of PiMarketMap from a blank SD card.
# Some of these steps are outlined in README.md,
# the intention here is to create distributable
# images quickly.

# Download & Flash Raspbian to new blank SD card
# See: https://www.raspberrypi.org/documentation/installation/installing-images/mac.md
cat 2018-11-13-raspbian-stretch-lite.img | pv -s 1700m | sudo dd of=/dev/rdiskN conv=sync

# Setup Wifi & SSH
# https://medium.com/@mikestreety/use-a-raspberry-pi-with-multiple-wifi-networks-2eda2d39fdd6
touch /Volumes/boot/ssh

echo 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="YOUR_NETWORK_NAME"
	psk="YOUR_PASSWORD"
	id_str="WIFI_LABEL"
	priority=100
	key_mgmt=WPA-PSK
}' > /Volumes/boot/wpa_supplicant.conf

############################
### Create base image    ###
############################

# Boot Pi, ssh in, and install PiMarketMap
scp -r /code/PiMarketMap pi@172.20.10.2:/home/pi/PiMarketMap
ssh pi@172.20.10.2

# Update system
sudo apt-get -y --force-yes update
sudo apt-get -y --force-yes upgrade
sudo apt-get -y --force-yes autoremove --purge
sudo apt-get install --yes --force-yes vim python3-pip

# Use Python 3
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.5 2

# Install Python dependencies
cd PiMarketMap
sudo pip3 install -r requirements.txt

# Enable service
sudo cp etc/systemd/system/marketmap.service /etc/systemd/system/marketmap.service
sudo systemctl daemon-reload && sudo systemctl enable marketmap && sudo systemctl start marketmap

# Install Halt Pin
# https://learn.adafruit.com/read-only-raspberry-pi/
sudo apt-get install -y --force-yes wiringpi
echo "Installing gpio-halt in /usr/local/bin..."
cd /tmp
curl -LO https://github.com/adafruit/Adafruit-GPIO-Halt/archive/master.zip
unzip master.zip
cd Adafruit-GPIO-Halt-master
make
sudo mv gpio-halt /usr/local/bin
cd ..
rm -rf Adafruit-GPIO-Halt-master
# Insert gpio-halt into rc.local before final 'exit 0'
HALT_PIN=21 sudo sed -i "s/^exit 0/\/usr\/local\/bin\/gpio-halt $HALT_PIN \&\\nexit 0/g" /etc/rc.local >/dev/null

############################
### Base image complete! ###
############################

# Shut down raspberry pi, and put SD card into your mac

# TODO: Shrink partition to minimal size to save time
# https://www.raspberrypi.org/forums/viewtopic.php?t=148519

# Image drive (may take 90 minutes for 16GB)
# dd will read the full SD card, 8, 16, etc GB, but only write a ~1GB gzipped file
sudo dd bs=1m if=/dev/disk3 | gzip > pimarketmap-raspbian-stretch-1.img.gz

# To save time and space, trim the image for distribution
docker run -it -v ~/:/images:cached --name ubuntu ubuntu:latest bash
$ apt-get update
$ apt-get install -y gparted parted udev wget
$ cd
$ wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
$ chmod +x pishrink.sh
$ time ./pishrink.sh /images/pimarketmap-raspbian-stretch.img /images/pimarketmap-raspbian-stretch-dist.img
# Takes about 60 seconds for 16GB

