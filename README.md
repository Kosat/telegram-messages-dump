# Telegram Messages Dump 
[![GitHub version](https://badge.fury.io/gh/Kosat%2Ftelegram-messages-dump.svg)](https://github.com/Kosat/telegram-messages-dump/releases)
[![Build Status](https://travis-ci.org/Kosat/telegram-messages-dump.svg?branch=master)](https://travis-ci.org/Kosat/telegram-messages-dump)

This is a simple console tool for dumping message history from a Telegram chat into a __jsonl__, __csv__ or plain text file. 
## Installation
**From sources:**
Fetch the latest sources with git:
```
git clone https://github.com/Kosat/telegram-messages-dump.git
```
Then run directly from sources
```
cd telegram-messages-dump
python -m telegram_messages_dump
```
Or run after installing locally
```
python setup.py install
telegram-messages-dump
```
**Binaries:**

Binaries for Linux, Windows and MacOS are available in [Releases](https://github.com/Kosat/telegram-messages-dump/releases) section.

## Usage

Mandatory parameters are <chat_name> e.g. @Python or @CSharp and <phone_num> - a telephone number. A phone number is needed for authentication and will not be stored anywhere. After the first successful authorization it will create telegram_chat_dump.session file containing auth token. The information from this file is being reused in next runs. If this is not a desirable behaviour, use -cl flag to delete session file on exit.

```
telegram-messages-dump -c <@chat_name> -p <phone_num> [-l <count>] [-o <file>] [-cl]

Where:
    -c,  --chat     Unique name of a channel/chat. E.g. @python.
    -p,  --phone    Phone number. E.g. +380503211234.
    -l,  --limit    Number of the latest messages to dump, 0 means no limit. (Default: 100)
    -o,  --out      Output file name or full path. (Default: telegram_<chatName>.log)
    -cl, --clean    Clean session sensitive data (e.g. auth token) on exit. (Default: False)
    -e,  --exp      Exporter name. text | jsonl | csv (Default: 'text')
    -v,  --verbose  Verbose mode. (Default: False)
      ,  --addbom   Add BOM to the beginning of the output file. (Default: False)
    -h,  --help     Show this help message and exit.
```
![telegram-dump-gif](https://user-images.githubusercontent.com/153023/36110898-fda2e7f6-102c-11e8-9475-471063004be8.gif)

## Notes

* This tool relies on [Telethon](https://github.com/LonamiWebs/Telethon) - a Telegram client implementation in Python.

## Plugins

Output format is managed by *exporter* plugins. Currently there are two exporters available: **text**,**jsonl** and **csv**.
Exporters reside in `./exporters` subfolder. 
Basically an exporter is a class that implements three methods:
- `format(...)` that extracts all necessary data from a message and stringifies it.
- `begin_final_file(...)` that allows an exporter to write a preamble to a resulting output file.
- `end_final_file(...)` that allows an exporter to write an afterword to a resulting output file.

To use a custom exporter. Place you `.py` file with a class implementing those 3 methods into `./exporters` subfolder and specify its name in `--exp <exporter_name>` setting. 

>Note: the class name **MUST** exactly match the file name of its `.py` file. This very same name is used as an argument for the `--exp` setting.

>Note2: in `.vscode` subfolder you can find the default settings that I use for debugging this project.  

## License

This project is licensed under the [MIT license](LICENSE).
