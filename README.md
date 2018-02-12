# Telegram Messages Dump 
[![GitHub version](https://badge.fury.io/gh/Kosat%2Ftelegram-messages-dump.svg)](https://github.com/Kosat/telegram-messages-dump/releases)
[![Build Status](https://travis-ci.org/Kosat/telegram-messages-dump.svg?branch=master)](https://travis-ci.org/Kosat/telegram-messages-dump)

This is a simple console tool for dumping message history from a Telegram chat into a plain text file. 
## Installation
**From sources:**
```
git clone https://github.com/Kosat/telegram-messages-dump.git
cd telegram-messages-dump
python setup.py install
telegram-messages-dump
or
python -m telegram_messages_dump
```
**Binaries:**

Binaries for Linux, Windows and MacOS are available in [Releases](https://github.com/Kosat/telegram-messages-dump/releases) section.

## Usage

Mandatory parameters are <chat_name> e.g. @Python or @CSharp and <phone_num> - a telephone number. A phone number is needed for authentication and will not be stored anywhere. After the first successful authorization it will create telegram_chat_dump.session file containing auth token. The information from this file is being reused in next runs. If this is not a desirable behaviour, use -cl flag to delete session file on exit.

```
telegram-messages-dump -c <@chat_name> -p <phone_num> [-l <count>] [-o <file>] [-cl]

Where:
    -c,  --chat   Unique name of a channel/chat. E.g. @python.
    -p,  --phone  Phone number. E.g. +380503211234.
    -l,  --limit  Number of the latest messages to dump, 0 means no limit. (Default: 100)
    -o,  --out    Output file name or full path. (Default: telegram_<chatName>.log)
    -cl, --clean  Clean session sensitive data (e.g. auth token) on exit. (Default: False)
    -h,  --help   Show this help message and exit.
```
![telegram-dump-gif](https://user-images.githubusercontent.com/153023/36110898-fda2e7f6-102c-11e8-9475-471063004be8.gif)

## Notes

* This tool relies on [Telethon](https://github.com/LonamiWebs/Telethon) - a Telegram client implementation in Python.


## License

This project is licensed under the [MIT license](LICENSE).
