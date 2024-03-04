"""
contains class for structured segmentgroups in mig tables. Builds table recursively.
"""

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
