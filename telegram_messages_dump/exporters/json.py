#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import json as jsonStd
from datetime import date, datetime
from .common import common

class json(object):
    """ json exporter plugin.
        By convention it has to be called exactly the same as its file name.
        (Apart from .py extention)
    """
    # pylint: disable=no-self-use

    def __init__(self):
        """ constructor """
        pass

    def format(self, msg, exporter_context):
        """ Formatter method. Takes raw msg and converts it to a *one-line* string.
            :param msg: Raw message object :class:`telethon.tl.types.Message` and derivatives.
                        https://core.telegram.org/type/Message

            :returns: *one-line* string containing one message data.
        """
        # pylint: disable=line-too-long
        name, _, content, re_id, is_sent_by_bot, is_contains_media, media_content = common.extract_message_data(msg)

        msgDictionary = {
            'message_id': msg.id,
            'from_id': msg.from_id,
            'reply_id': re_id,
            'author': name,
            'sent_by_bot': is_sent_by_bot,
            'date': msg.date,
            'content': content,
            'contains_media': is_contains_media,
            'media_content': media_content
        }
        msg_dump_str = jsonStd.dumps(
            msgDictionary, default=self._json_serial, ensure_ascii=False)
        if exporter_context.is_last_record:
            return msg_dump_str
        else:
            return msg_dump_str + ","

    def begin_final_file(self, resulting_file):
        """ Hook executes at the beginning of writing a resulting file. (After BOM is written)"""
        print("[", file=resulting_file)

    def end_final_file(self, resulting_file):
        """ Hook executes at the end of writing a resulting file. Right before closing it."""
        print("]", file=resulting_file)

    def _json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code
           https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))
