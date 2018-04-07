#!/bin/bash

echo Start executing pre_install.linux.sh
echo pwd
pwd

# Print out current python env
python -V

# Upgrade pip
python -m pip install --upgrade pip

#Build for Linux
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip

#Build for Windows

#Install wine from their PPA
# sudo dpkg --add-architecture i386
# sudo apt-get install software-properties-common
# sudo apt-add-repository 'https://dl.winehq.org/wine-builds/ubuntu/'
# wget https://dl.winehq.org/wine-builds/Release.key && sudo apt-key add Release.key
# apt-get install apt-transport-https
# sudo apt-get update
# sudo apt-get install --install-recommends winehq-stable

#Install win32-python+pip within wine
# wget "https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi"
# wine msiexec /i python-3.4.4.msi /quiet

#Install zip for windows deployment
# sudo apt-get install zip
