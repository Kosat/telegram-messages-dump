#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:

Normal mode:
  telegram-messages-dump -c <chat_name> -p <phone_num> [-l <count>] [-o <file>] [-cl] [...]
  telegram-messages-dump --chat=<chat_name> --phone=<phone_num> [--limit=<count>] [--out <file>]

Continuous mode:
  telegram-messages-dump --continue -p <phone_num> -o <file> [-cl] [...]
  telegram-messages-dump --continue=<MSG_ID> -p <phone_num> -o <file> -e <exporter> -c <chat_name>

Where:
    -c,  --chat      Unique name of a channel/chat. E.g. @python.
    -p,  --phone     Phone number. E.g. +380503211234.
    -o,  --out       Output file name or full path. (Default: telegram_<chatName>.log)
    -e,  --exp       Exporter name. text | jsonl | csv (Default: 'text')
      ,  --continue  Continue previous dump. Supports optional integer param <message_id>.
    -l,  --limit     Number of the latest messages to dump, 0 means no limit. (Default: 100)
    -cl, --clean     Clean session sensitive data (e.g. auth token) on exit. (Default: False)
    -v,  --verbose   Verbose mode. (Default: False)
      ,  --addbom    Add BOM to the beginning of the output file. (Default: False)
    -h,  --help      Show this help message and exit.
"""

import os
import sys
import importlib
import logging
from telegram_messages_dump.telegram_dumper import TelegramDumper
from telegram_messages_dump.chat_dump_settings import ChatDumpSettings
from telegram_messages_dump.chat_dump_metadata import DumpMetadata
from telegram_messages_dump.chat_dump_metadata import MetadataError
from telegram_messages_dump.utils import sprint

def main():
    """ Entry point. """
    settings = ChatDumpSettings(__doc__)

    # define the console output verbosity
    default_format = '%(levelname)s:%(message)s'
    if settings.is_verbose:
        logging.basicConfig(format=default_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=default_format, level=logging.INFO)

    metadata = DumpMetadata(settings.out_file)

    # when user specified --continue
    try:
        if settings.is_incremental_mode and settings.last_message_id == -1:
            metadata.merge_into_settings(settings)
    except MetadataError as ex:
        sprint("ERROR: %s" % ex)
        sys.exit(1)

    exporter = _load_exporter(settings.exporter)

    sys.exit(TelegramDumper(os.path.basename(__file__), settings, metadata, exporter).run())

def _load_exporter(exporter_name):
    """ Loads exporter from file <exporter_name>.py in ./exporters subfolder.
        :param exporter_name:      name of exporter. E.g. 'text' or 'json'

        :return: Exporter instance
    """
    # By convention exporters are located in .\exporters subfolder
    # COMMENT: Don't check file existance. It won't play well with pyinstaller bins
    exporter_file_name = exporter_name + ".py"
    exporter_rel_name = "telegram_messages_dump.exporters." + exporter_name
    # Load exporter from file
    sprint("Try to load exporter '%s'...  " % (exporter_file_name), end='')
    try:
        exporter_module = importlib.import_module(exporter_rel_name)
        sprint("OK!")
    except ModuleNotFoundError:
        sprint("\nERROR: Failed to load exporter './exporters/%s'." % exporter_file_name)
        exit(1)

    try:
        exporterClass = getattr(exporter_module, exporter_name)
    except AttributeError:
        sprint("ERROR: Failed to load class '%s' out of './exporters/%s'." \
               % (exporter_name, exporter_file_name))
        exit(1)

    return exporterClass()
