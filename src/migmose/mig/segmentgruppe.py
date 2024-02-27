"""
contains class for structured segmentgroups in mig tables. builds table recursively.
"""

from migmose.mig.zeile import NachrichtenStrukturZeile


class SegmentGruppe(NachrichtenStrukturZeile):
    """
    class for structured segmentgroups in mig tables. builds table recursively. inherits from NachrichtenstrukturZeile
    """

    segmente: list[NachrichtenStrukturZeile]
    segmentgruppe: list["SegmentGruppe"]
