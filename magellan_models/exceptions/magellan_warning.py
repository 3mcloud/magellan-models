""" Module for Warnings Logic"""


class MagellanWarning(UserWarning):
    """Generic Warning Class"""


class MagellanParserWarning(MagellanWarning):
    """Warning for Parser complications"""


class MagellanRuntimeWarning(MagellanWarning):
    """Warning for Runtime complications"""
