#!/bin/bash

#Install telethon:
pip3 install -I telethon==0.11.5
pyinstaller -n telegram-chat-dump --noconsole --onefile ./telegram_messages_dump/run.py

#Package for distribution
cd ./dist
tar -zcvf telegram_chat_dump_darwin.tar.gz ./telegram-chat-dump