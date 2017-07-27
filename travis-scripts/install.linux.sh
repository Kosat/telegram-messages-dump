#!/bin/bash

echo Start executing install.linux.sh
echo pwd
pwd

#Build for Linux
pip install -I telethon==0.11.5
pyinstaller -D -F -n telegram-chat-dump -c ./telegram_messages_dump/run.py


#Setup build env for Windows: pyinstaller+telethon
wine pip install -I telethon==0.11.5
wine pip install pyinstaller
wine pyinstaller -n telegram-chat-dump.exe --onefile --clean --win-private-assemblies -c --noconfirm --log-level=WARN ./telegram_messages_dump/run.py

#Package for distribution
cd ./dist
tar -zcvf telegram_chat_dump_linux.tar.gz ./telegram-chat-dump
zip -r telegram_chat_dump_windows.zip ./telegram-chat-dump.exe