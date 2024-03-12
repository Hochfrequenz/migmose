"""
contains class for lines in mig tables
"""

from typing import Any

from pydantic import BaseModel


class NachrichtenstrukturZeile(BaseModel):
    """
    class for lines in mig tables, e.g. (ORDCHG):
    {
        "zaehler": "0010",
        "nr": "1",
        "bezeichnung": "UNH",
        "standard_status": "M",
        "bdew_status": "M",
        "standard_maximale_wiederholungen": 1,
        "bdew_maximale_wiederholungen": 1,
        "ebene": 0,
        "inhalt": "Nachrichten-Kopfsegment"
        }
    """

    zaehler: str
    nr: str | None = None
    bezeichnung: str
    standard_status: str
    bdew_status: str
    standard_maximale_wiederholungen: int
    bdew_maximale_wiederholungen: int
    ebene: int
    inhalt: str

    @classmethod
    def init_raw_lines(cls, raw_line: str) -> "NachrichtenstrukturZeile":
        """
        reads one raw line and returns a NachrichtenstrukturZeile object
        """
        fields = raw_line.split("\t")[1:]
        field_names = [
            "zaehler",
            "nr",
            "bezeichnung",
            "standard_status",
            "bdew_status",
            "standard_maximale_wiederholungen",
            "bdew_maximale_wiederholungen",
            "ebene",
            "inhalt",
        ]
        is_line_segmentgroup = len(fields) == len(field_names) - 1
        is_line_incomplete = len(fields) != len(field_names) and not is_line_segmentgroup

        if is_line_segmentgroup:
            field_names = field_names[:1] + field_names[2:]
        if is_line_incomplete:
            raise ValueError(f"Expected 8 or 9 fields, got {len(fields)}, line: {raw_line}")
        field_dict: dict[str, Any] = dict(zip(field_names, fields))
        return cls(**field_dict)
