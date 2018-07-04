#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This Module contains classes related to CLI interactions"""

import argparse
from telegram_messages_dump.utils import JOIN_CHAT_PREFIX_URL


class ChatDumpSettings:
    """ Parses CLI arguments. """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self, usage):

        # From telegram-cli
        self.api_id = 2899
        self.api_hash = '36722c72256a24c1225de00eb6a1ca74'

        # Parse parameters
        parser = CustomArgumentParser(
            formatter_class=CustomFormatter, usage=usage)

        parser.add_argument('-c', '--chat', default='', required=False, type=str)
        parser.add_argument('-p', '--phone', required=True, type=str)
        parser.add_argument('-o', '--out', default='', type=str)
        parser.add_argument('-e', '--exp', default='', type=str)
        parser.add_argument('--continue', dest='increment',
                            default='*', type=str, nargs='?')
        parser.add_argument('-l', '--limit', default=-1, type=int)
        parser.add_argument('-cl', '--clean', action='store_true')
        parser.add_argument('-v', '--verbose', action='store_true')
        parser.add_argument('--addbom', action='store_true')
        parser.add_argument('-q', '--quiet', action='store_true')

        args = parser.parse_args()

        # Trim extra spaces in string param values
        if args.chat:
            args.chat = args.chat.strip()
        if args.exp:
            args.exp = args.exp.strip()
        if args.out:
            args.out = args.out.strip()
        if args.phone:
            args.phone = args.phone.strip()

        # Detect Normal/Incremental mode
        self._process_incremental_mode_option(args, parser)

        # Check if user specified the right options depending on the mode
        self._check_options_consistency(args, parser)

        # Validate chat name
        if self.last_message_id != -1 and not args.chat != "":
            parser.error("Chat name can't be empty")

        # Validate phone number
        try:
            if int(args.phone) <= 0:
                raise ValueError
        except ValueError:
            parser.error('Phone number is invalid.')

        # Validate limit / set default
        if not self.is_incremental_mode and args.limit < 0:
            args.limit = 100

        # Validate exporter name / set default
        exp_file = 'text' if not args.exp else args.exp
        if not exp_file:
            parser.error('Exporter name is invalid.')

        # Default output file if not specified by user
        OUTPUT_FILE_TEMPLATE = 'telegram_{}.log'
        if args.out != '':
            out_file = args.out
        elif args.chat.startswith(JOIN_CHAT_PREFIX_URL):
            out_file = OUTPUT_FILE_TEMPLATE.format(args.chat.rsplit('/', 1)[-1])
        else:
            out_file = OUTPUT_FILE_TEMPLATE.format(args.chat)

        self.chat_name = args.chat
        self.phone_num = args.phone
        self.out_file = out_file
        self.exporter = exp_file
        self.limit = args.limit
        self.is_clean = args.clean
        self.is_verbose = args.verbose
        self.is_addbom = args.addbom
        self.is_quiet_mode = args.quiet

    def _process_incremental_mode_option(self, args, parser):
        """ Arguments parsing related to --continue setting """
        self.last_message_id = -1
        self.is_incremental_mode = False

        if not args.increment == '*':
            # if user specified --continue with/without a parameter
            self.is_incremental_mode = True
            if args.increment:
                # else-if user specified --continue with one param that is expected to be uint
                # Try parse it as int assuming it is the last message_id
                try:
                    self.last_message_id = int(args.increment)
                except ValueError:
                    parser.error(
                        'Unable to parse MSG_ID in --continue=<MSG_ID>')
        return

    def _check_options_consistency(self, args, parser):
        if self.is_incremental_mode:
            if args.out == "":
                parser.error('To increment an existing dump file. '
                             'You have to specify it using --out or -o setting.')
            if self.last_message_id != -1:
                # In case of --continue=<MSG_ID>
                if args.chat == "":
                    parser.error('chat name must be specified explicitely '
                                 'when using --continue=<MSG_ID>')
                if args.exp == "":
                    parser.error('exporter must be specified explicitely '
                                 'when using --continue=<MSG_ID>')
                if args.limit != -1:
                    parser.error('limit setting is not allowed '
                                 'when using --continue=<MSG_ID>')
            else:
                # In case of --continue
                if args.chat != "":
                    parser.error('chat name must NOT be specified explicitely '
                                 'when using --continue')
                if args.exp != "":
                    parser.error('exporter must NOT be specified explicitely '
                                 'when using --continue')
                if args.limit != -1:
                    parser.error('limit setting is not allowed '
                                 'when using --continue')
        else:
            # In case of Normal mode
            if args.chat == "":
                parser.error('the following arguments are required: -c/--chat ')
        return


class CustomFormatter(argparse.HelpFormatter):
    """ Custom formatter for setting argparse formatter_class.
        It only outputs raw 'usage' text and omits other sections
        (e.g. positional, optional params and epilog).
    """

    def __init__(self, prog=''):
        argparse.HelpFormatter.__init__(
            self, prog, max_help_position=100, width=150)

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
