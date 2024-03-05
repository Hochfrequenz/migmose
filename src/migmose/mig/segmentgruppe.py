"""
contains class for structured segmentgroups in mig tables. Builds table recursively.
"""

from typing import Optional, Tuple

from pydantic import BaseModel

from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class SegmentGruppe(BaseModel):
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

    header_linie: Optional[NachrichtenstrukturZeile] = None
    segmente: list[Optional[NachrichtenstrukturZeile]] = []
    segmentgruppen: list[Optional["SegmentGruppe"]] = []

    @classmethod
    def structure_table(
        cls, table: NachrichtenstrukturTabelle, segmentgruppe: Optional[NachrichtenstrukturZeile] = None, index: int = 0
    ) -> Tuple["SegmentGruppe", int]:
        """init structured table"""
        collected_segments: list[Optional[NachrichtenstrukturZeile]] = []
        collected_segmentgroups: list[Optional["SegmentGruppe"]] = []
        i = index
        while i < len(table.lines):
            line = table.lines[i]
            is_line_segmentgruppe = line.nr is None
            if is_line_segmentgruppe:
                added_segmentgroup, i = cls.structure_table(table, line, i + 1)
                collected_segmentgroups.append(added_segmentgroup)
            else:
                collected_segments.append(line)
                i += 1
            if i < len(table.lines) - 1:
                next_line_segmentgruppe = table.lines[i].nr is None

                if segmentgruppe is not None and (
                    (next_line_segmentgruppe and table.lines[i].ebene <= segmentgruppe.ebene)  # type: ignore [operator]
                    or (line.ebene > table.lines[i].ebene)  # type: ignore [operator]
                ):
                    return (
                        cls(
                            header_linie=segmentgruppe,
                            segmente=collected_segments,
                            segmentgruppen=collected_segmentgroups,
                        ),
                        i,
                    )
        return cls(header_linie=segmentgruppe, segmente=collected_segments, segmentgruppen=collected_segmentgroups), i
