#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is a main Module that contains code
    that fetches messages from Telegram and do processing.
"""

import os
import os.path
import sys
import codecs
import tempfile
import logging
from collections import deque
from getpass import getpass
from time import sleep
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError, UsernameNotOccupiedError, UsernameInvalidError
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telegram_messages_dump.utils import sprint
from telegram_messages_dump.utils import JOIN_CHAT_PREFIX_URL
from telegram_messages_dump.exceptions import DumpingError
from telegram_messages_dump.exceptions import MetadataError
from telegram_messages_dump.exporter_context import ExporterContext


class TelegramDumper(TelegramClient):
    """ Authenticates and opens new session. Retrieves message history for a chat. """

    def __init__(self, session_user_id, settings, metadata, exporter):

        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing session...')
        super().__init__(session_user_id,
                         settings.api_id,
                         settings.api_hash,
                         proxy=None,
                         update_workers=1)

        # Settings as specified by user or defaults or from metadata
        self.settings = settings

        # Metadata that was possibly loaded from .meta file and will be saved there
        self.metadata = metadata

        # Exporter object that converts msg -> string
        self.exporter = exporter

        # The context that will be passed to the exporter
        self.exporter_context = ExporterContext()
        self.exporter_context.is_continue_mode = self.settings.is_incremental_mode

        # How many massages user wants to be dumped
        # explicit --limit, or default of 100 or unlimited (int.Max)
        self.msg_count_to_process = 0

        # Messages page offset for fetching
        self.id_offset = 0

        # A list of paths to the temp files
        self.temp_files_list = deque()

        # Actual lattets message id that was prossessed since the dumper started running
        self.cur_latest_message_id = self.settings.last_message_id

        # The number of messages written into a resulting file de-facto
        self.output_total_count = 0

    def run(self):
        """ Dumps all desired chat messages into a file """

        ret_code = 0
        try:
            self._init_connect()
            try:
                chatObj = self._getChannel()
            except ValueError as ex:
                ret_code = 1
                self.logger.error('%s', ex,
                                  exc_info=self.logger.level > logging.INFO)
                return
            # Fetch history in chunks and save it into a resulting file
            self._do_dump(chatObj)
        except (DumpingError, MetadataError) as ex:
            self.logger.error('%s', ex, exc_info=self.logger.level > logging.INFO)
            ret_code = 1
        except KeyboardInterrupt:
            sprint("Received a user's request to interrupt, stopping…")
            ret_code = 1
        except Exception as ex:  # pylint: disable=broad-except
            self.logger.error('Uncaught exception occured. %s', ex,
                              exc_info=self.logger.level > logging.INFO)
            ret_code = 1
        finally:
            self.logger.debug('Make sure there are no temp files left undeleted.')
            # Clear temp files if any
            while self.temp_files_list:
                try:
                    os.remove(self.temp_files_list.pop().name)
                except Exception:  # pylint: disable=broad-except
                    pass

        if self.settings.is_clean:
            try:
                # TODO
                # self.log_out()
                self.logger.info('Session data cleared.')
            except Exception:  # pylint: disable=broad-except
                sprint('Failed to logout and clean session data.')

        sprint('{} messages were successfully written in the resulting file. Done!'
               .format(self.output_total_count))
        return ret_code

    def _init_connect(self):
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

    def _getChannel(self):
        """ Returns telethon.tl.types.Channel object resolved from chat_name
            at Telegram server
        """
        name = self.settings.chat_name

        # For private channуls try to resolve channel peer object from its invitation link
        # Note: it will only work if the login user has already joined the private channel.
        # Otherwise, get_entity will throw ValueError
        if name.startswith(JOIN_CHAT_PREFIX_URL):
            self.logger.debug('Trying to resolve as invite url.')
            try:
                peer = self.get_entity(name)
                if peer:
                    sprint('Invitation link "{}" resolved into channel id={}'.format(
                        name, peer.id))
                    return peer
            except ValueError as ex:
                self.logger.debug('Failed to resolve "%s" as an invitation link. %s',
                                  self.settings.chat_name,
                                  ex,
                                  exc_info=self.logger.level > logging.INFO)

        if name.startswith('@'):
            name = name[1:]
            self.logger.debug('Trying ResolveUsernameRequest().')
            try:
                peer = self(ResolveUsernameRequest(name))
                if peer.chats is not None and peer.chats:
                    sprint('Chat name "{}" resolved into channel id={}'.format(
                        name, peer.chats[0].id))
                    return peer.chats[0]
                if peer.users is not None and peer.users:
                    sprint('User name "{}" resolved into channel id={}'.format(
                        name, peer.users[0].id))
                    return peer.users[0]
            except (UsernameNotOccupiedError, UsernameInvalidError) as ex:
                self.logger.debug('Failed to resolve "%s" as @-chat-name. %s',
                                  self.settings.chat_name,
                                  ex,
                                  exc_info=self.logger.level > logging.INFO)

        # Search in dialogs first, this way we will find private groups and
        # channels.
        self.logger.debug('Fetch loggedin user`s dialogs')
        dialogs_count = self.get_dialogs(0).total
        self.logger.info('%s user`s dialogs found', dialogs_count)
        dialogs = self.get_dialogs(limit=None)
        self.logger.debug('%s dialogs fetched.', len(dialogs))
        for dialog in dialogs:
            if dialog.name == name:
                sprint('Dialog title "{}" resolved into channel id={}'.format(
                    name, dialog.entity.id))
                return dialog.entity
            if hasattr(dialog.entity, 'username') and dialog.entity.username == name:
                sprint('Dialog username "{}" resolved into channel id={}'.format(
                    name, dialog.entity.id))
                return dialog.entity
            if name.startswith('@') and dialog.entity.username == name[1:]:
                sprint('Dialog username "{}" resolved into channel id={}'.format(
                    name, dialog.entity.id))
                return dialog.entity
        self.logger.debug('Specified chat name was not found among dialogs.')

        raise ValueError('Failed to resolve dialogue/chat name "{}".'.format(name))

    def _fetch_messages_from_server(self, peer, buffer):
        """ Retrieves a number (100) of messages from Telegram's DC and adds them to 'buffer'.
            :param peer:        Chat/Channel object
            :param buffer:      buffer where to place retrieved messages

            :return
                latest_message_id The latest/biggest Message ID that sucessfully went into buffer.
        """
        messages = []

        # First retrieve the messages and some information
        # make 5 attempts
        for _ in range(0, 5):
            try:
                # NOTE: Telethon will make 5 attempts to reconnect
                # before failing
                messages = self.get_messages(
                    peer, limit=100, offset_id=self.id_offset)

                if messages.total > 0 and messages:
                    sprint('Processing messages with ids {}-{} ...'
                           .format(messages[0].id, messages[-1].id))
            except FloodWaitError as ex:
                sprint('FloodWaitError detected. Sleep for {} sec before reconnecting! \n'
                       .format(ex.seconds))
                sleep(ex.seconds)
                self._init_connect()
                continue
            break

        latest_message_id = -1 \
            if not messages or self.settings.last_message_id >= messages[0].id \
            else messages[0].id

        # Iterate over all (in reverse order so the latest appear
        # the last in the console) and print them with format provided by exporter.
        for msg in messages:
            self.exporter_context.is_first_record = True \
                if self.msg_count_to_process == 1 \
                else False

            if self.settings.last_message_id >= msg.id:
                self.msg_count_to_process = 0
                break

            msg_dump_str = self.exporter.format(msg, self.exporter_context)

            buffer.append(msg_dump_str)

            self.msg_count_to_process -= 1
            self.id_offset = msg.id
            self.exporter_context.is_last_record = False
            if self.msg_count_to_process == 0:
                break

        return latest_message_id

    def _do_dump(self, peer):
        """ Retrieves messages in small chunks (Default: 100) and saves them in in-memory 'buffer'.
            When buffer reaches '1000' messages they are saved into intermediate temp file.
            In the end messages from all the temp files are being moved into resulting file in
            ascending order along with the remaining ones in 'buffer'.
            After all, temp files are deleted.

             :param peer: Chat/Channel object that contains the message history of interest

             :return  Number of files that were saved into resulting file
        """
        self.msg_count_to_process = self.settings.limit \
            if self.settings.limit != -1\
            and not self.settings.is_incremental_mode\
            else sys.maxsize

        self._check_preconditions()

        # Current buffer of messages, that will be batched into a temp file
        # or otherwise written directly into the resulting file if there are too few of them
        # to form a batch of size 1000.
        buffer = deque()

        # Delete old metafile in Continue mode
        if not self.settings.is_incremental_mode:
            self.metadata.delete_meta_file()

        temp_files_list_meta = deque()  # a list of meta info about batches

        # process messages until either all message count requested by user are retrieved
        # or offset_id reaches msg_id=1 - the head of a channel message history
        try:
            while self.msg_count_to_process > 0:
                # slip for a few seconds to avoid flood ban
                sleep(2)

                latest_message_id_fetched = self._fetch_messages_from_server(
                    peer, buffer)

                # This is for the case when buffer with fewer than 1000 records
                # Relies on the fact that `_fetch_messages_from_server` returns messages
                # in reverse order
                if self.cur_latest_message_id < latest_message_id_fetched:
                    self.cur_latest_message_id = latest_message_id_fetched
                # when buffer is full, flush it into a temp file
                # Assume that once a message got into temp file it will be counted as successful
                # 'output_total_count'. This has to be improved.
                if len(buffer) >= 1000:
                    self._flush_buffer_in_temp_file(buffer)
                    temp_files_list_meta.append(latest_message_id_fetched)
                # break if the very beginning of channel history is reached
                if self.id_offset <= 1:
                    break
        except RuntimeError as ex:
            sprint('Fetching messages from server failed. ' + str(ex))
            sprint('Warn: The resulting file will contain partial/incomplete data.')

        # Write all chunks into resulting file
        sprint('Merging results into an output file.')
        try:
            self._write_final_file(buffer, temp_files_list_meta)
        except OSError as ex:
            raise DumpingError("Dumping to a final file failed.") from ex

        # Metadata that will be written into a metafile
        meta_dict = {
            "latest_message_id": self.cur_latest_message_id,
            "exporter_name": self.settings.exporter,
            "chat_name": self.settings.chat_name
        }
        self.metadata.save_meta_file(meta_dict)

    def _flush_buffer_in_temp_file(self, buffer):
        """ Flush buffer into a new temp file """
        with tempfile \
                .NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as tf:
            self.output_total_count += self._flush_buffer_into_filestream(buffer, tf)
            self.temp_files_list.append(tf)

    def _flush_buffer_into_filestream(self, buffer, file_stream):
        """ Flush buffer into a file stream """
        count = 0
        while buffer:
            count += 1
            cur_message = buffer.pop()
            print(cur_message, file=file_stream)
        return count

    def _write_final_file(self, buffer, temp_files_list_meta):
        result_file_mode = 'a' if self.settings.last_message_id > -1 else 'w'
        with codecs.open(self.settings.out_file, result_file_mode, 'utf-8') as resulting_file:
            if self.settings.is_addbom:
                resulting_file.write(codecs.BOM_UTF8.decode())

            self.exporter.begin_final_file(
                resulting_file, self.exporter_context)

            # flush what's left in the mem buffer into resulting file
            self.output_total_count += self._flush_buffer_into_filestream(
                buffer, resulting_file)

            self._merge_temp_files_into_final(
                resulting_file, temp_files_list_meta)

    def _merge_temp_files_into_final(self, resulting_file, temp_files_list_meta):
        """ merge all temp files into final one and delete them """
        while self.temp_files_list:
            tf = self.temp_files_list.pop()
            with codecs.open(tf.name, 'r', 'utf-8') as ctf:
                for line in ctf.readlines():
                    print(line, file=resulting_file, end='')
            # delete temp file
            self.logger.debug("Delete temp file %s", tf.name)
            tf.close()
            os.remove(tf.name)
            # update the latest_message_id metadata
            batch_latest_message_id = temp_files_list_meta.pop()
            if batch_latest_message_id > self.cur_latest_message_id:
                self.cur_latest_message_id = batch_latest_message_id

    def _check_preconditions(self):
        """ Check preconditions before processing data """
        out_file_path = self.settings.out_file
        if self.settings.is_incremental_mode:
            # In incrimental mode
            sprint('Switching to incremental mode.')
            self.logger.debug('Checking if output file exists.')
            if not os.path.exists(out_file_path):
                raise DumpingError(
                    'Error: Output file does not exist. Path="' + out_file_path + '"')
            sprint('Dumping messages newer than {} using "{}" dumper.'
                   .format(self.settings.last_message_id, self.settings.exporter))
        else:
            # In NONE-incrimental mode
            if os.path.exists(out_file_path):
                sprint('Warning: The output file already exists.')
                if not self._is_user_confirmed('Are you sure you want to overwrite it? [y/n]'):
                    raise DumpingError("Terminating on user's request...")
            # Check if output file can be created/overwritten
            try:
                with open(out_file_path, mode='w+'):
                    pass
            except OSError as ex:
                raise DumpingError('Output file path "{}" is invalid. {}'.format(
                    out_file_path, ex.strerror))
            sprint('Dumping {} messages into "{}" file ...'
                   .format('all' if self.msg_count_to_process == sys.maxsize
                           else self.msg_count_to_process, out_file_path))

    def _is_user_confirmed(self, msg):
        """ Get confirmation from user """
        if self.settings.is_quiet_mode:
            return True
        continueResponse = input(msg).lower().strip()
        return continueResponse == 'y'\
            or continueResponse == 'yes'
