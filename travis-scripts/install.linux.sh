#!/bin/bash

echo Start executing install.linux.sh
echo pwd
pwd

#Build for Linux
pip install -I telethon==0.17
pyinstaller -D -F -n telegram-messages-dump \
-c ./telegram_messages_dump/run.py \
--hidden-import telegram_messages_dump.exporters.text \
--hidden-import telegram_messages_dump.exporters.json


#Setup build env for Windows: pyinstaller+telethon
# wine pip install -I telethon==0.17
# wine pip install pyinstaller
# wine pyinstaller -n telegram-chat-dump.exe --onefile --clean --win-private-assemblies -c --noconfirm --log-level=WARN ./telegram_messages_dump/run.py

#Package for distribution
cd ./dist
tar -zcvf telegram_messages_dump_linux.tar.gz ./telegram-messages-dump
# zip -r telegram_chat_dump_windows.zip ./telegram-chat-dump.exe
