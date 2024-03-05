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
    bezeichnung: str | None = None
    standard_status: str | None = None
    bdew_status: str | None = None
    standard_maximale_wiederholungen: int | None = None
    bdew_maximale_wiederholungen: int | None = None
    ebene: int | None = None
    inhalt: str | None = None

    @classmethod
    def init_raw_lines(cls, raw_line: str) -> "NachrichtenstrukturZeile":
        """
        reads one raw line and returns a NachrichtenstrukturZeile object"""
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
        if len(fields) == len(field_names) - 1:
            field_names = field_names[:1] + field_names[2:]
        elif len(fields) != len(field_names):
            raise ValueError(f"Expected 8 or 9 fields, got {len(fields)}, line: {raw_line}")
        field_dict: dict[str, Any] = dict(zip(field_names, fields))
        return cls(**field_dict)
