#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

class ExporterContext:
    """ Exporter context """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self):
        # Is processing the first record
        self.is_first_record = False
        # Is processing the last record
        self.is_last_record = True
        # Is working in continue/incremental mode
        self.is_continue_mode = False
