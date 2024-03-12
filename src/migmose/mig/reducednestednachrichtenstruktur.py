"""
contains class for trees consisting of segments of mig tables
"""

from typing import Optional

from pydantic import BaseModel

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class ReducedNestedNachrichtenstruktur(BaseModel):
    """will contain the tree structure of nachrichtenstruktur tables"""

    header_linie: Optional[NachrichtenstrukturZeile] = None
    segmente: list[NachrichtenstrukturZeile]
    segmentgruppe: list["ReducedNestedNachrichtenstruktur"]
