"""
contains class for trees consisting of segments of mig tables
"""

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class BaumSegmentGruppe(NachrichtenstrukturZeile):
    """will contain the tree structure of nachrichtenstruktur tables"""

    segmente: list[NachrichtenstrukturZeile]
    segmentgruppe: list["BaumSegmentGruppe"]
