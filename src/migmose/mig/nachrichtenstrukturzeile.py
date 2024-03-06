"""
contains class for lines in mig tables
"""

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
