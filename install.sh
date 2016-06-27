#!/bin/bash

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root" 1>&2
   exit 1
fi

echo -e '\nInstalling the required programs...'
sudo apt-get --assume-yes install socat git

cd /tmp

echo -e '\nCloning the github repository...'
git clone https://github.com/bodiroga/zwave-socat-gateway.git
cd zwave-socat-gateway

echo -e '\nMoving the udev rule to the corresponding folder...'
cp -rf udev/* /etc/udev/rules.d/

echo -e '\nMoving the program files to the /root directory...'
cp -rf files/* /root

echo -e '\nAdding the start script file...'
cp -rf init.d/* /etc/init.d/
chmod +x /etc/init.d/zwave-socat
update-rc.d zwave-socat defaults

cd /root
if [ ! -f CONFIGURATION ]; then
	echo -e '\nCreating the CONFIGURATION file, edit the parameters to meet your needs...'
	cp CONFIGURATION_DEFAULT CONFIGURATION
else
	echo -e '\nYour CONFIGURATION file already exists, we will not touch it...'
fi

echo -e '\nRemoving the tmp folder...'
rm -rf /tmp/zwave-socat-gateway

echo -e '\n----------------------------------------------------------------------------'
echo -e 'Go to the /root folder, read the README file and edit the CONFIGURATION file'
echo -e '----------------------------------------------------------------------------'
