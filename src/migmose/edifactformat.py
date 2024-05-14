"""
Extend the existing edifact format enum from maus.edifact with the formats UTILMDS, UTILMDG
for Strom, Gas respectively.
"""

from maus.edifact import EdifactFormat


class ExtendedEdifactFormat(EdifactFormat):
    UTILMDS = "UTILMDS"  #: utilities master data, Strom
    UTILMDG = "UTILMDG"  #: utilities master data, Gas
