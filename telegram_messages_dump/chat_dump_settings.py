#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This Module contains classes related to CLI interactions"""
import argparse


class CustomFormatter(argparse.HelpFormatter):
    """ Custom formatter for setting argparse formatter_class.
        It only outputs raw 'usage' text and omits other sections
        (e.g. positional, optional params and epilog).
    """

    def __init__(self, prog=''):
        argparse.HelpFormatter.__init__(self, prog, max_help_position=100, width=150)

    def add_usage(self, usage, actions, groups, prefix=None):
        if usage is not argparse.SUPPRESS:
            args = usage, actions, groups, ''
            self._add_item(self._format_usage, args)

    def _format_usage(self, usage, actions, groups, prefix):
        # if usage is specified, use that
        if usage is not None:
            usage = usage % dict(prog=self._prog)

        return "\n\r%s\n\r" % usage


class CustomArgumentParser(argparse.ArgumentParser):
    """ Custom ArgumentParser.
        Outputs raw 'usage' text and omits other sections.
    """

    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        return formatter.format_help()



class ChatDumpSettings:
    """ Parses CLI arguments. """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self, usage):

        # From telegram-cli
        self.api_id = 2899
        self.api_hash = '36722c72256a24c1225de00eb6a1ca74'

        # Parse parameters
        parser = CustomArgumentParser(formatter_class=CustomFormatter, usage=usage)

        parser.add_argument('-c', '--chat', required=True, type=str)
        parser.add_argument('-p', '--phone', required=True, type=str)
        parser.add_argument('-l', '--limit', default=100, type=int)
        parser.add_argument('-o', '--out', default='', type=str)
        parser.add_argument('-cl', '--clean', action='store_true')
        parser.add_argument('-e', '--exp', default='text', type=str)

        args = parser.parse_args()

        # Validate chat name
        if not args.chat.startswith('@'):
            parser.error('Chat name must start with "@"')
        else:
            args.chat = args.chat[1:]

        # Validate phone number
        try:
            if int(args.phone) <= 0:
                raise ValueError
        except ValueError:
            parser.error('Phone number is invalid.')

        # Validate phone number
        if args.limit < 0:
            parser.error('Phone number is invalid.')

        # Validate output file
        out_file = 'telegram_{}.log'.format(args.chat)

        if args.out:
            out_file = args.out

        try:
            with open(out_file, mode='w+'):
                pass
        except OSError as ex:
            parser.error('Output file path "{}" is invalid. {}'.format(out_file, ex.strerror))


        # Validate exporter name
        exp_file = args.exp.strip()
        if not exp_file:
            parser.error('Exporter name is invalid.')

        self.chat_name = args.chat
        self.phone_num = args.phone
        self.out_file = out_file
        self.limit = args.limit
        self.is_clean = args.clean
        self.exporter = exp_file
