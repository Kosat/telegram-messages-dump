#!/bin/bash

#Install telethon:
pip3 install -I telethon==0.18.3
pyinstaller -n telegram-messages-dump --noconsole --onefile \
--hidden-import telegram_messages_dump.exporters.text \
--hidden-import telegram_messages_dump.exporters.jsonl \
--hidden-import telegram_messages_dump.exporters.csv \
 ./telegram_messages_dump/__main__.py

#Package for distribution
cd ./dist
tar -zcvf telegram_messages_dump_darwin.tar.gz ./telegram-messages-dump
