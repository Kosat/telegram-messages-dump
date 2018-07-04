#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Various utility functions/classes """

def sprint(string, *args, **kwargs):
    """Safe Print (handle UnicodeEncodeErrors on some terminals)"""
    try:
        print(string, *args, **kwargs)
    except UnicodeEncodeError:
        string = string.encode('utf-8', errors='ignore') \
            .decode('ascii', errors='ignore')
        print(string, *args, **kwargs)


JOIN_CHAT_PREFIX_URL = 'https://t.me/joinchat/'
