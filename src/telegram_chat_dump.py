#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:

telegram-messages-dump -c <@chat_name> -p <phone_num> [-l <count>] [-o <file>] [-cl]

Where:
    -c,  --chat   Unique name of a channel/chat. E.g. @python.
    -p,  --phone  Phone number. E.g. +380503211234.
    -l,  --limit  Number of the latest messages to dump, 0 means no limit. (Default: 100)
    -o,  --out    Output file name or full path. (Default: telegram_<chatName>.log)
    -cl, --clean  Clean session sensitive data (e.g. auth token) on exit. (Default: False)
    -h,  --help   Show this help message and exit.

"""

import os
from chat_dump_settings import ChatDumpSettings
from telegram_dumper import TelegramDumper


def main():
    settings = ChatDumpSettings(__doc__)
    TelegramDumper(os.path.basename(__file__), settings).run()


if __name__ == "__main__":
    main()
