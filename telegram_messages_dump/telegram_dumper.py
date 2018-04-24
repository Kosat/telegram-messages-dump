#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is a main Module that contains code
    that fetches messages from Telegram and do processing.
"""

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
from telegram_messages_dump.utils import sprint


class TelegramDumper(TelegramClient):
    """ Authenticates and opens new session. Retrieves message history for a chat. """

    def __init__(self, session_user_id, settings, exporter):

        sprint('Initializing session...')
        super().__init__(session_user_id,
                         settings.api_id,
                         settings.api_hash,
                         connection_mode=ConnectionMode.TCP_FULL,
                         proxy=None,
                         update_workers=1)

        self.settings = settings
        self.exporter = exporter
        self.exporter_context = ExporterContext()
        self.msg_count_to_process = 0
        self.id_offset = 0
        self.init_connect()

    def init_connect(self):
        """ Connect to the Telegram server and Authenticate. """
        sprint('Connecting to Telegram servers...')
        if not self.connect():
            sprint('Initial connection failed. Retrying...')
            if not self.connect():
                sprint('Could not connect to Telegram servers.')
                return

        # Then, ensure we're authorized and have access
        if not self.is_user_authorized():
            sprint('First run. Sending code request...')
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

    def resolve_name(self, name):
        # Search in dialogs first, this way we will find private groups and
        # channels.
        dialogs = self.get_dialogs()
        for dialog in dialogs:
            if dialog.name == name:
                return dialog.entity
            if dialog.entity.username == name:
                return dialog.entity
            if name.startswith('@') and dialog.entity.username == name[1:]:
                return dialog.entity

        # Fallback to ResolveUsernameRequest, this way we will find public
        # not-joined groups and channels but only using username (search by
        # name is not reliable so we don't do it).
        if name.startswith('@'):
            name = name[1:]
        peer = self(ResolveUsernameRequest(name))
        if peer.chats is not None and peer.chats:
            return peer.chats[0]
        if peer.users is not None and peer.users:
            return peer.users[0]
        raise ValueError('Error: failed to resolve chat name into chat_id')

    def run(self):
        """ Dumps all desired chat messages into a file """
        chat = self.resolve_name(self.settings.chat_name)
        sprint('Chat name {} resolved into channel id={}'.format(self.settings.chat_name, chat.id))

        # Dump history to file
        count = self.dump_messages_in_file(chat)

        if self.settings.is_clean:
            try:
                # TODO self.log_out()
                sprint('Session data cleared.')
            # pylint: disable=broad-except
            except Exception:
                sprint('Error: failed to log-out.')

        sprint('{} messages were successfully written in resulting file. Done!'.format(count))

    def retrieve_message_history(self, peer, buffer):
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

        # First retrieve the messages and some information
        # make 5 attempts
        for _ in range(0, 5):
            try:
                messages = self.get_message_history(
                    peer, limit=100, offset_id=self.id_offset)

                if messages.total > 0 and messages:
                    sprint('Processing messages with ids {}-{} ...'
                           .format(messages[0].id, messages[-1].id))
            except FloodWaitError as ex:
                sprint('FloodWaitError detected. Sleep for {} sec before reconnecting! \n'
                       .format(ex.seconds))
                sleep(ex.seconds)
                self.init_connect()
                continue
            break


        # Iterate over all (in reverse order so the latest appear
        # the last in the console) and print them with format provided by exporter.
        for msg in messages:
            self.exporter_context.is_first_record = True if self.msg_count_to_process == 1 else False
            msg_dump_str = self.exporter.format(msg, self.exporter_context)

            buffer.append(msg_dump_str)

            self.msg_count_to_process -= 1
            self.id_offset = msg.id
            self.exporter_context.is_last_record = False
            if self.msg_count_to_process == 0:
                break

        return

    def dump_messages_in_file(self, peer):
        """ Retrieves messages in small chunks (Default: 100) and saves them in in-memory 'buffer'.
            When buffer reaches '1000' messages they are saved into intermediate temp file.
            In the end messages from all the temp files are being moved into resulting file in
            ascending order along with the remaining ones in 'buffer'.
            After all, temp files are deleted.

             :param peer: Chat/Channel object that contains the message history of interest

             :return  Number of files that were saved into resulting file
        """
        history_length = self.settings.limit if self.settings.limit > 0 else sys.maxsize
        file_path = self.settings.out_file

        sprint('Dumping {} messages into "{}" file ...'
               .format('all' if history_length == sys.maxsize else history_length, file_path))

        self.msg_count_to_process = history_length
        self.id_offset = 0
        output_total_count = 0

        # buffer to save a bulk of messages before flushing them to a file
        buffer = deque()
        temp_files_list = []

        # process messages until either all message count requested by user are retrieved
        # or offset_id reaches msg_id=1 - the head of a channel message history
        while self.msg_count_to_process > 0:
            sleep(2)  # slip for a few seconds to avoid flood ban
            self.retrieve_message_history(peer, buffer)
            # when buffer is full, flush it into a temp file
            if len(buffer) >= 1000:
                with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as tf:
                    tf.write(codecs.BOM_UTF8.decode())
                    while buffer:
                        output_total_count += 1
                        print(buffer.pop(), file=tf)
                    temp_files_list.append(tf)

            # break if the very beginning of channel history is reached
            if self.id_offset <= 1:
                break

        # Write all chunks into resulting file
        with codecs.open(file_path, 'w', 'utf-8') as resulting_file:
            resulting_file.write(codecs.BOM_UTF8.decode())

            self.exporter.begin_final_file(resulting_file)

            # flush what's left in the mem buffer into resulting file
            while buffer:
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

            self.exporter.end_final_file(resulting_file)

        return output_total_count


class ExporterContext:
    """ Exporter context """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self):
        # Is processing the first record
        self.is_first_record = False
        # Is processing the last record
        self.is_last_record = True
