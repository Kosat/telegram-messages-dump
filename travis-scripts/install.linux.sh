#!/bin/bash

echo Start executing install.linux.sh
echo pwd
pwd

#Build for Linux
pip install -I telethon==0.18.3
pyinstaller -F -n telegram-messages-dump \
-c ./telegram_messages_dump/__main__.py \
--hidden-import telegram_messages_dump.exporters.text \
--hidden-import telegram_messages_dump.exporters.jsonl \
--hidden-import telegram_messages_dump.exporters.csv

#Setup build env for Windows: pyinstaller+telethon
# wine pip install -I telethon==0.18
# wine pip install pyinstaller
# wine pyinstaller -n telegram-messages-dump.exe --onefile --clean --win-private-assemblies -c --noconfirm --log-level=WARN ./telegram_messages_dump/__main__.py --hidden-import telegram_messages_dump.exporters.text --hidden-import telegram_messages_dump.exporters.jsonl --hidden-import telegram_messages_dump.exporters.csv

#Package for distribution
cd ./dist
tar -zcvf telegram_messages_dump_linux.tar.gz ./telegram-messages-dump
# zip -r telegram_messages_dump_windows.zip ./telegram-messages-dump.exe
