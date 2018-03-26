#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs
import tempfile
from collections import deque
from getpass import getpass
from time import sleep

from telethon import TelegramClient, ConnectionMode
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpc_error_list import FloodWaitError
from telethon.tl.functions.contacts import ResolveUsernameRequest


def sprint(string, *args, **kwargs):
    """Safe Print (handle UnicodeEncodeErrors on some terminals)"""
    try:
        print(string, *args, **kwargs)
    except UnicodeEncodeError:
        string = string.encode('utf-8', errors='ignore') \
            .decode('ascii', errors='ignore')
        print(string, *args, **kwargs)


class TelegramDumper(TelegramClient):
    """ Authenticates and opens new session.
        Retrieves message history for a chat.
    """



    def __init__(self, session_user_id, settings):

        sprint('Initializing session...')
        super().__init__(session_user_id, settings.api_id, settings.api_hash, connection_mode=ConnectionMode.TCP_FULL, proxy=None,     update_workers=1)

        self.settings = settings
        self.init_connect()

    def init_connect(self):

        print('Connecting to Telegram servers...')
        if not self.connect():
            print('Initial connection failed. Retrying...')
            if not self.connect():
                print('Could not connect to Telegram servers.')
                return

        # Then, ensure we're authorized and have access
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            self.send_code_request(self.settings.phone_num)

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = self.sign_in(self.settings.phone_num, code)

                # Two-step verification may be enabled
                except SessionPasswordNeededError:
                    pw = getpass("Two step verification is enabled. "
                                 "Please enter your password: ")

                    self_user = self.sign_in(password=pw)

    def run(self):
        # Resolve chat name into id
        peer = self(ResolveUsernameRequest(self.settings.chat_name))

        if peer.chats is None or len(peer.chats) == 0:
            raise ValueError('Error: failed to resolve chat name into chat_id')

        chat = peer.chats[0]

        sprint('Chat name @{} resolved into channel id={}'.format(self.settings.chat_name, chat.id))

        # Dump history to file
        count = self.dump_messages_in_file(chat)

        if self.settings.is_clean:
            # noinspection PyBroadException
            try:
                self.log_out()
                sprint('Session data cleared.')
            except:
                sprint('Error: failed to log-out.')

        sprint('{} messages were successfully written in resulting file. Done!'.format(count))

    @staticmethod
    def extract_message_data(msg):
        sender = msg.sender
        """ Extracts user name from 'sender', message caption and message content from msg."""
        # Get the name of the sender if any
        if sender:
            name = getattr(sender, 'first_name', None)
            if not name:
                name = getattr(sender, 'title', None)
                if not name:
                    name = '???'
        else:
            name = '???'

        caption = None
        # Format the message content
        if getattr(msg, 'media', None):
            # The media may or may not have a caption
            caption = getattr(msg.media, 'caption', '')
            content = '<{}> {}'.format(
                type(msg.media).__name__, caption)

        elif hasattr(msg, 'message'):
            content = msg.message
        elif hasattr(msg, 'action'):
            content = str(msg.action)
        else:
            # Unknown message, simply print its class name
            content = type(msg).__name__

        return name, caption, content

    def retrieve_message_history(self, peer, msg_count, id_offset, buffer):
        """ Retrieves a number (100) of messages from Telegram's DC and adds them to 'buffer'.
            :param peer:        Chat/Channel object
            :param msg_count:   number of messages to process
            :param id_offset:   current message id to start with
            :param buffer:      buffer where to place retrieved messages

            :return
                msg_count - retrived_msg_count
                id_offset - the id of the last message retrieved
        """
        messages = []
        #senders = []

        # First retrieve the messages and some information
        # make 5 attempts
        for i in range(0, 5):
            try:
                messages = self.get_message_history(
                    peer, limit=100, offset_id=id_offset)

                if messages.total > 0 and len(messages) > 0:
                    print('Processing messages with ids {}-{} ...'.format(messages[0].id, messages[-1].id))
            except FloodWaitError as ex:
                sprint('FloodWaitError detected. Sleep for {} sec before reconnecting! \n'.format(ex.seconds))
                sleep(ex.seconds)
                self.init_connect()
                continue
            break

        # Iterate over all (in reverse order so the latest appear
        # the last in the console) and print them with format:
        # "[yyyy-mm-dd hh:mm] Sender: Message RE:"
        for msg in messages:

            name, caption, content = self.extract_message_data(msg)

            re_id_str = ''
            if hasattr(msg, 'reply_to_msg_id') and msg.reply_to_msg_id is not None:
                re_id_str = 'RID={} '.format(str(msg.reply_to_msg_id))

            # Format a message log record
            msg_dump_str = '[{}-{:02d}-{:02d} {:02d}:{:02d}] ID={} {}{}: {}'.format(
                msg.date.year, msg.date.month, msg.date.day,
                msg.date.hour, msg.date.minute, msg.id, re_id_str, name,
                content)

            buffer.append(msg_dump_str)

            msg_count -= 1
            id_offset = msg.id

            if msg_count == 0:
                break

        return msg_count, id_offset

    def dump_messages_in_file(self, peer):
        """ Retrieves messages in small chunks (Default: 100) and saves them in in-memory 'buffer'.
            When buffer reaches '1000' messages they are saved into intermediate temp file.
            In the end messages from all the temp files are being moved into resulting file in
            ascending order along with the remaining ones in 'buffer'. After all, temp files are deleted.

             :param peer: Chat/Channel object that contains the message history of interest

             :return  Number of files that were saved into resulting file
        """
        history_length = self.settings.limit if self.settings.limit > 0 else sys.maxsize
        file_path = self.settings.out_file

        sprint('Dumping {} messages into "{}" file ...'.format('all' if history_length == sys.maxsize
                                                               else history_length, file_path))

        msg_count_to_process = history_length
        id_offset = 0
        output_total_count = 0

        # buffer to save a bulk of messages before flushing them to a file
        buffer = deque()
        temp_files_list = []

        # process messages until either all message count requested by user are retrieved
        # or offset_id reaches msg_id=1 - the head of a channel message history
        while msg_count_to_process > 0:
            sleep(2)  # slip for a few seconds to avoid flood ban
            msg_count_to_process, id_offset = self.retrieve_message_history(peer, msg_count_to_process,
                                                                            id_offset, buffer)
            # when buffer is full, flush it into a temp file
            if len(buffer) >= 1000:
                with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as tf:
                    tf.write(codecs.BOM_UTF8.decode())
                    while len(buffer) > 0:
                        output_total_count += 1
                        print(buffer.pop(), file=tf)
                    temp_files_list.append(tf)

            # break if the very beginning of channel history is reached
            if id_offset <= 1:
                break

        # Write all chunks into resulting file
        with codecs.open(file_path, 'w', 'utf-8') as resulting_file:
            resulting_file.write(codecs.BOM_UTF8.decode())

            # flush what's left in the mem buffer into resulting file
            while len(buffer) > 0:
                output_total_count += 1
                print(buffer.pop(), file=resulting_file)

            # merge all temp files into final one and delete them
            for tf in reversed(temp_files_list):
                with codecs.open(tf.name, 'r', 'utf-8') as ctf:
                    for line in ctf.readlines():
                        print(line, file=resulting_file, end='')
                # delete temp file
                tf.close()
                os.remove(tf.name)

        return output_total_count
