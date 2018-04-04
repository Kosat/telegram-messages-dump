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
    -e,  --exp    Exporter name. text | json (Default: 'text')
    -h,  --help   Show this help message and exit.

"""

import os
import importlib
from telegram_messages_dump.telegram_dumper import TelegramDumper
from telegram_messages_dump.chat_dump_settings import ChatDumpSettings
from telegram_messages_dump.utils import sprint

def main():
    """ Entry point. """
    settings = ChatDumpSettings(__doc__)

    exporter = _load_exporter(settings.exporter)

    TelegramDumper(os.path.basename(__file__), settings, exporter).run()

def _load_exporter(exporter_name):
    """ Loads exporter from file <exporter_name>.py in ./exporters subfolder.
        :param exporter_name:      name of exporter. E.g. 'text' or 'json'

        :return: Exporter instance
    """
    # By convention exporters are located in .\exporters subfolder
    # COMMENT: Don't check file existance. It won't play well with with pyinstaller bins
    exporter_file_name = exporter_name + ".py"
    exporter_rel_name = "telegram_messages_dump.exporters." + exporter_name
    # Load exporter from file
    sprint("Try to load exporter '%s'...  " % (exporter_file_name), end='')
    exporter_module = importlib.import_module(exporter_rel_name)
    sprint("OK!")
    exporterClass = getattr(exporter_module, exporter_name)
    return exporterClass()

if __name__ == "__main__":
    main()
