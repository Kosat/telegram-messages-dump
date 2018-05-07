# Telegram Messages Dump 
[![GitHub version](https://badge.fury.io/gh/Kosat%2Ftelegram-messages-dump.svg)](https://github.com/Kosat/telegram-messages-dump/releases)
[![Build Status](https://travis-ci.org/Kosat/telegram-messages-dump.svg?branch=master)](https://travis-ci.org/Kosat/telegram-messages-dump)

This is a simple console tool for dumping message history from a Telegram chat into a __jsonl__, __csv__ or plain __text__ file. 
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

Mandatory parameters are <chat_name> e.g. @Python, @CSharp or a title of a dialogue, as seen in the UI, and <phone_num> - a telephone number. A phone number is needed for authentication and will not be stored anywhere. After the first successful authorization it will create telegram_chat_dump.session file containing auth token. The information from this file is being reused in next runs. If this is not a desirable behaviour, use -cl flag to delete session file on exit.
>Note1: You can use telegram dialogue multi-word title like so: `--chat="Telegram Geeks"` with double quotes. However, when using multi-word title (rather than @channel_name), you need to join the channel first. Only then you will be able to dump it. This way you can dump __private__ dialogues which doesn't have @channel_name.

>Note2: For private channels you can also pass an invitation link as chat name. E.g. `--chat="https://t.me/joinchat/XXXXXYYYYZZZZZ"`.
__IMPORTANT__: It only works when you (the logged-in user) has already joined the private chat that the invitation link corresponds to.

```
telegram-messages-dump -c <chat_name> -p <phone_num> [-l <count>] [-o <file>] [-cl]

Where:
    -c,  --chat     Unique name of a channel/chat. E.g. @python.
    -p,  --phone    Phone number. E.g. +380503211234.
    -o,  --out      Output file name or full path. (Default: telegram_<chatName>.log)
    -e,  --exp      Exporter name. text | jsonl | csv (Default: 'text')
      ,  --continue Continue previous dump. Supports optional integer param <message_id>.
    -l,  --limit    Number of the latest messages to dump, 0 means no limit. (Default: 100)
    -cl, --clean    Clean session sensitive data (e.g. auth token) on exit. (Default: False)
    -v,  --verbose  Verbose mode. (Default: False)
      ,  --addbom   Add BOM to the beginning of the output file. (Default: False)
    -h,  --help     Show this help message and exit.
```
![telegram-dump-gif](https://user-images.githubusercontent.com/153023/36110898-fda2e7f6-102c-11e8-9475-471063004be8.gif)

## Increamental/Continuous mode
After dumping messages into an output file, `telegram-messages-dump` also creates a **meta file**
with the latest (biggest) message id that was successfully saved into an output file.
For instance, if messages with ids 10..100 were saved in output file, the metafile will contain the `"latest_message_id": 100` record in it.

- If you want to update an existing dump file use `--continue` option without a parameter value. In this case `telegram-messages-dump` will read the latest message id from a meta file. In the sample below it will be `C:\temp\xyz.txt.meta`:
  ```
  telegram-messages-dump -p... -oC:\temp\xyz.txt  --continue
  ```
  In this case `telegram-messages-dump` will look for `C:\temp\xyz.txt.meta` file and try to incrimentally update the contents of `C:\temp\xyz.txt` with new messages.
>Note: In incremental mode when metafile exists `--exp` and `--chat` will be taken from the meta file and must NOT be specified explicitely as parameters. `--limit` setting has to be omitted.

- Otherwise, if you DON'T have a metafile or want to ignore it, you can still open your dump file and find the last message's id at the bottom of the file and then specify it explicitly as `--continue=<LAST_MSG_ID>` command, along with the correct `--exp` and `--chat` that were used to generate the existing dump file.
  ```
  telegram-messages-dump -p... -oC:\temp\xyz.txt --continue=100500 --exp=jsonl --chat=@geekschat
  ```
In both aforementioned cases, `telegram-messages-dump` will open the existing `C:\temp\xyz.txt` file and append the newer messages that were posted in the telegram chat since the message with the message with id 100500 was created.
>Note1: There must be `=` sign between the `--continue` command name and integer message id.

>Note2: In incremental mode without metafile,  `--out`, `--exp` and `--chat` must be specified explicitely as parameters. `--limit` setting has to be omitted.

## Notes

* This tool relies on [Telethon](https://github.com/LonamiWebs/Telethon) - a Telegram client implementation in Python.

## Plugins

Output format is managed by *exporter* plugins. Currently there are two exporters available: **text**, **jsonl** and **csv**.
Exporters reside in `./exporters` subfolder. 
Basically an exporter is a class that implements three methods:
- `format(...)` that extracts all necessary data from a message and stringifies it.
- `begin_final_file(...)` that allows an exporter to write a preamble to a resulting output file.

To use a custom exporter. Place you `.py` file with a class implementing those 3 methods into `./exporters` subfolder and specify its name in `--exp <exporter_name>` setting. 

>Note1: the class name **MUST** exactly match the file name of its `.py` file. This very same name is used as an argument for the `--exp` setting.

>Note2: in `.vscode` subfolder you can find the default settings that I use for debugging this project.  

## License

This project is licensed under the [MIT license](LICENSE).
