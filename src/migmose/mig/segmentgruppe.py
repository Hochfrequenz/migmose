"""
contains class for structured segmentgroups in mig tables. Builds table recursively.
"""

from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class SegmentGruppe(NachrichtenstrukturZeile):
    """
    class for structured segmentgroups in mig tables. Builds table recursively. Inherits from NachrichtenstrukturZeile
    e.g.(ORDCHG):
    {
    "segmente": [
        {
        "zaehler": "0160",
        "nr": "7",
        "bezeichnung": "NAD",
        "standard_status": "M",
        "bdew_status": "M",
        "standard_maximale_wiederholungen": 1,
        "bdew_maximale_wiederholungen": 1,
        "ebene": 1,
        "inhalt": "MP-ID Absender"
        }
        ],
    "segmentgruppen": [
    {
        "segmente": [
        {
            "zaehler": "0260",
            "nr": "8",
            "bezeichnung": "CTA",
            "standard_status": "M",
            "bdew_status": "M",
            "standard_maximale_wiederholungen": 1,
            "bdew_maximale_wiederholungen": 1,
            "ebene": 2,
            "inhalt": "Ansprechpartner"
            },
            {
            "zaehler": "0270",
            "nr": "9",
            "bezeichnung": "COM",
            "standard_status": "C",
            "bdew_status": "R",
            "standard_maximale_wiederholungen": 5,
            "bdew_maximale_wiederholungen": 5,
            "ebene": 3,
            "inhalt": "Kommunikationsverbindung"
            }
            ],
        "segmentgruppen": []
        }
        ]
    }
    """

    segmente: list[NachrichtenstrukturZeile]
    segmentgruppen: list["SegmentGruppe"]

    @classmethod
    def structure_table(cls, table: NachrichtenstrukturTabelle, index: int = 0) -> "SegmentGruppe":
        collected_segments: list[NachrichtenstrukturZeile] = []
        collected_segmentgroups: list["SegmentGruppe"] = []
        for i, line in enumerate(table.lines[index:]):
            is_line_segmentgruppe = line.nr is None
            if not is_line_segmentgruppe:
                collected_segments.append(line)
            elif is_line_segmentgruppe and line.ebene == table.lines[i - 1].ebene + 1:
                collected_segmentgroups.append(cls.structure_table(table, i + 1))
            else:
                return cls(segmente=collected_segments, segmentgruppen=collected_segmentgroups)
        return cls(segmente=collected_segments, segmentgruppen=collected_segmentgroups)
