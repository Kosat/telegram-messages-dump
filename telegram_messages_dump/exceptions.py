""" Custom Exceptions used throughout telegram_message_dump tool. """

class DumpingError(Exception):
    """ Dumping exception"""
    pass


class MetadataError(Exception):
    """ Metadata processing exception"""
    pass
