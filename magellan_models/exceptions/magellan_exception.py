""" Module for Exceptions logic"""


class MagellanException(Exception):
    """Generic Exception Class"""


class MagellanRuntimeException(MagellanException):
    """Exception class for Runtime errors"""


class MagellanParserException(MagellanException):
    """Exception class for Parser errors"""
