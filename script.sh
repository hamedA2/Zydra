#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

sudo apt-get update -y
# sudo apt-get upgrade -y
# Workaround for the grub-config-prompt issue :
DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
# As taken from here :
# https://askubuntu.com/questions/146921/how-do-i-apt-get-y-dist-upgrade-without-a-grub-config-prompt

sudo apt-get install qpdf -y
sudo apt-get install unrar -y
sudo apt-get install python3.7 -y
sudo apt-get install python3-pip -y
pip3 --version

python -m venv .venv
source .venv/bin/activate
pip install pip --upgrade
pip install -r requirements.txt
cd /vagrant/
