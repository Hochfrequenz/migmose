"""
Extend the existing edifact format enum from maus.edifact with the formats UTILMDS, UTILMDG
for Strom, Gas respectively.
"""

from enum import Enum


# pylint: disable=too-few-public-methods
class ExtendedEdifactFormat(str, Enum):
    """
    existing EDIFACT formats from maus.edifact extended with UTILMDS and UTILMDG.
    """

    APERAK = "APERAK"
    COMDIS = "COMDIS"  #: communication dispute
    CONTRL = "CONTRL"  #: control messages
    IFTSTA = "IFTSTA"  #: Multimodaler Statusbericht
    INSRPT = "INSRPT"  #: Prüfbericht
    INVOIC = "INVOIC"  #: invoice
    MSCONS = "MSCONS"  #: meter readings
    ORDCHG = "ORDCHG"  #: changing an order
    ORDERS = "ORDERS"  #: orders
    ORDRSP = "ORDRSP"  #: orders response
    PRICAT = "PRICAT"  #: price catalogue
    QUOTES = "QUOTES"  #: quotes
    REMADV = "REMADV"  #: zahlungsavis
    REQOTE = "REQOTE"  #: request quote
    PARTIN = "PARTIN"  #: market partner data
    UTILMD = "UTILMD"  #: utilities master data
    UTILMDS = "UTILMDS"  #: utilities master data, Strom
    UTILMDG = "UTILMDG"  #: utilities master data, Gas
    UTILTS = "UTILTS"  #: formula

    def __str__(self):
        return self.value
