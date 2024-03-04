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
    nr: str
    bezeichnung: str
    standard_status: str
    bdew_status: str
    standard_maximale_wiederholungen: int
    bdew_maximale_wiederholungen: int
    ebene: int
    inhalt: str
