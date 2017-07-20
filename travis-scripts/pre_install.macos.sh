#!/bin/bash

brew update

#Use this specific python 3.5.3 version because of 'pyinstaller' compatibility issues
brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/ec545d45d4512ace3570782283df4ecda6bb0044/Formula/python3.rb

#virtualenv env -p python3
#source env/bin/activate

echo Current active python version:
python3 --version

echo Installed pip version:
pip3 --version

#Install pyinstaller
pip3 install pyinstaller

echo Installed pyinstaller version:
pyinstaller --version