#!/bin/bash

#Install telethon:
pip3 install -I telethon==0.17
pyinstaller -D -F -n telegram-messages-dump \
-c ./telegram_messages_dump/run.py \
--hidden-import telegram_messages_dump.exporters.text \
--hidden-import telegram_messages_dump.exporters.json

#Package for distribution
cd ./dist
tar -zcvf telegram_messages_dump_darwin.tar.gz ./telegram-messages-dump
