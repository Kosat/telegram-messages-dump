#!/bin/bash

echo Start executing install.linux.sh
echo pwd
pwd

#Build for Linux
pip install -I telethon==0.11.5
pyinstaller -D -F -n telegram-chat-dump -c ./src/telegram_chat_dump.py


#Build for Windows
wine pip install -I telethon==0.11.5
wine pip install pyinstaller
wine pyinstaller -n telegram-chat-dump.exe --onefile --clean --win-private-assemblies -c --noconfirm --log-level=WARN ./src/telegram_chat_dump.py

#Package for distribution
cd ./dist
tar -zcvf telegram_chat_dump_linux.tar.gz ./telegram-chat-dump
tar -zcvf telegram_chat_dump_windows.tar.gz ./telegram-chat-dump.exe