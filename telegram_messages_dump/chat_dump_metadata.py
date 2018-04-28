#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This Module contains classes related to Metadata Files"""

import os.path
import errno
import codecs
import json
import logging
from telegram_messages_dump.exceptions import MetadataError


class DumpMetadata:
    """ Metadata file CRUD """

    CHAT_NAME = "chat_name"
    LAST_MESSAGE_ID = "latest_message_id"
    EXPORTER = "exporter_name"

    def __init__(self, out_file_path):
        self.meta_file_path = out_file_path + '.meta'
        self._meta_dict = {}
        self.logger = logging.getLogger(__name__)

    def merge_into_settings(self, settings):
        """ Get exporter name from metadata"""
        if not self._meta_dict:
            self._loadFromFile()

        settings.chat_name = self._meta_dict[DumpMetadata.CHAT_NAME]
        settings.last_message_id = self._meta_dict[DumpMetadata.LAST_MESSAGE_ID]
        settings.exporter = self._meta_dict[DumpMetadata.EXPORTER]

    def _loadFromFile(self):
        """ Loads metadata from file """
        try:
            self.logger.debug('Load metafile %s.', self.meta_file_path)
            with codecs.open(self.meta_file_path, 'r', 'utf-8') as meta_file:
                self._meta_dict = json.load(meta_file)
                # TODO Validate Meta Dict
        except OSError as ex:
            raise MetadataError('Unable to open the metadata file "{}". {}'
                                .format(self.meta_file_path, ex.strerror)) from ex
        except ValueError as ex:
            raise MetadataError(
                'Unable to load the metadata file "{}". AttributeError: {}'
                .format(self.meta_file_path, ex)) from ex

    def delete_meta_file(self):
        """ Delete metafile if running in CONTINUE mode """
        try:
            self.logger.debug('Delete old metadata file %s.', self.meta_file_path)
            os.remove(self.meta_file_path)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise MetadataError('Failed to delete old metadata file. {}'
                                    .format(ex.strerror))

    def save_meta_file(self, new_dict):
        """ Save metafile to file"""
        try:
            self.logger.debug('Save new metadata file %s.', self.meta_file_path)
            if not self._meta_dict:
                self._meta_dict = {}

            self._meta_dict["schema"] = "http://telegram-messages-dump/schema/v/1"

            if DumpMetadata.CHAT_NAME in new_dict:
                self._meta_dict[DumpMetadata.CHAT_NAME] = new_dict[DumpMetadata.CHAT_NAME]
            if DumpMetadata.LAST_MESSAGE_ID in new_dict:
                self._meta_dict[DumpMetadata.LAST_MESSAGE_ID] =\
                     new_dict[DumpMetadata.LAST_MESSAGE_ID]
            if DumpMetadata.EXPORTER in new_dict:
                self._meta_dict[DumpMetadata.EXPORTER] = new_dict[DumpMetadata.EXPORTER]

            self.logger.info('Writing a new metadata file.')
            with open(self.meta_file_path, 'w') as mf:
                json.dump(self._meta_dict, mf, indent=4, sort_keys=False)
        except OSError as ex:
            raise MetadataError(
                'Failed to write the metadata file. {}'.format(ex.strerror))
