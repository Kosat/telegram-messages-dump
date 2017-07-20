#!/bin/bash

echo Start executing pre_install.linux.sh
echo pwd
pwd

#Build for Linux
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip

#Build for Windows

#Install wine from their PPA
sudo dpkg --add-architecture i386
sudo apt-add-repository 'https://dl.winehq.org/wine-builds/ubuntu/'
wget https://dl.winehq.org/wine-builds/Release.key && sudo apt-key add Release.key
sudo apt update && sudo apt install winehq-stable

#Install win32-python+pip+pyinstaller+telethon within wine
wget "https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi"
wine msiexec /i python-3.4.4.msi /quiet