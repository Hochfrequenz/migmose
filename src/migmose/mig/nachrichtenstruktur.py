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

    @classmethod
    def init_raw_table(cls, raw_lines: list[str]) -> "NachrichtenstrukturTabelle":
        """
        reads table as list of raw lines and returns a NachrichtenstrukturTabelle
        consisting of NachrichtenstrukturZeilen
        """
        collected_lines: list[NachrichtenstrukturZeile] = []
        for raw_line in raw_lines:
            collected_lines.append(NachrichtenstrukturZeile.init_raw_lines(raw_line))
        return cls(lines=collected_lines)
