"""
contains class for trees consisting of segments of mig tables
"""

import json
from pathlib import Path
from typing import Any, Optional, Tuple, TypeAlias

from loguru import logger
from maus.edifact import EdifactFormat
from pydantic import BaseModel, Field

from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur


# define helper functions
def _iterate_through_nested_nachrichtenstruktur(
    nested_nachrichtenstruktur: NestedNachrichtenstruktur,
) -> "SegmentGroupHierarchy":
    segment_group: Optional[str] = None
    opening_segment: Optional[str] = None
    if nested_nachrichtenstruktur.header_linie is not None:
        segment_group = nested_nachrichtenstruktur.header_linie.bezeichnung
    if nested_nachrichtenstruktur.segmente is not None:
        opening_segment = nested_nachrichtenstruktur.segmente[0].bezeichnung
    sub_hierarchy: list[Optional["SegmentGroupHierarchy"]] = []
    while segment_group in nested_nachrichtenstruktur.segmentgruppen:
        sub_hierarchy.append(_iterate_through_nested_nachrichtenstruktur(segment_group))
    return SegmentGroupHierarchy(
        segment_group=segment_group, opening_segment=opening_segment, sub_hierarchy=sub_hierarchy
    )


class SegmentGroupHierarchy(BaseModel):
    """Contains the model for a segment group hierachy used by the MAUS library."""

    opening_segment: Optional[str] = None
    segment_group: Optional[str] = None
    sub_hierarchy: list[Optional["SegmentGroupHierarchy"]] = Field(default_factory=list)

    @classmethod
    def create_segmentgroup_hierarchy(
        self, nested_nachrichtenstruktur: NestedNachrichtenstruktur
    ) -> "SegmentGroupHierarchy":
        """init Segmentrgroup Hierarchy"""
        segment_group: Optional[str] = None
        opening_segment: Optional[str] = None
        if nested_nachrichtenstruktur.header_linie is not None:
            segment_group = nested_nachrichtenstruktur.header_linie.bezeichnung
        if nested_nachrichtenstruktur.segmente is not None:
            opening_segment = nested_nachrichtenstruktur.segmente[0].bezeichnung
        sub_hierarchy: list[Optional["SegmentGroupHierarchy"]] = []
        for sub_segmentgroup in nested_nachrichtenstruktur.segmentgruppen:
            sub_hierarchy.append(self.create_segmentgroup_hierarchy(sub_segmentgroup))

        return SegmentGroupHierarchy(
            segment_group=segment_group, opening_segment=opening_segment, sub_hierarchy=sub_hierarchy
        )

    def to_json(self, message_type: EdifactFormat, output_dir: Path) -> dict[str, Any]:
        """
        writes the reduced NestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath("sgh.json")
        structured_json = self.model_dump()
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info("Wrote reduced nested Nachrichtenstruktur for {} to {}", message_type, file_path)
        return structured_json
