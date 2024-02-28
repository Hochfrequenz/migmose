"""
contains class for lines in mig tables
"""

from pydantic import BaseModel


class NachrichtenstrukturZeile(BaseModel):
    """
    class for lines in mig tables
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
