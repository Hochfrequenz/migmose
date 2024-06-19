"""Contains class SegmentLayout"""

from typing import Optional

from pydantic import BaseModel


class SegmentLayoutLine(BaseModel):
    """
    Class to capture the layout of a segment.
    """

    bezeichnung: str
    name: str
    standard_status: str
    bdew_status: str
    standard_format: str
    bdew_format: str
    anwendung: str


class SegmentLayout(BaseModel):
    """
    Class to capture the layout of a segment.
    """

    struktur: list["SegmentLayoutLine"]
    bemerkung: Optional[str] = None
    beispiel: Optional[str] = None
