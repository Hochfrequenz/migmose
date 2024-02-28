"""
contains class mig tables
"""

from pydantic import BaseModel

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class NachrichtenstrukturTabelle(BaseModel):
    """
    class for mig tables
    """

    lines: list[NachrichtenstrukturZeile]
