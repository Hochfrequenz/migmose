"""
contains class for structured segmentgroups in mig tables. builds table recursively.
"""

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class SegmentGruppe(NachrichtenstrukturZeile):
    """
    class for structured segmentgroups in mig tables. builds table recursively. inherits from NachrichtenstrukturZeile
    """

    segmente: list[NachrichtenstrukturZeile]
    segmentgruppe: list["SegmentGruppe"]
