"""
contains class for trees consisting of segments of mig tables
"""

import json
from pathlib import Path
from typing import Optional

from efoli import EdifactFormat
from loguru import logger
from pydantic import BaseModel, Field

from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur


class SegmentGroupHierarchy(BaseModel):
    """
    This module contains the same model for a segment group hierarchy as used by the MAUS library,
    which can be found here:
    (https://github.com/Hochfrequenz/mig_ahb_utility_stack/blob/eae2d84d600f42257cf364190da486aa011a5882/src/maus/models/message_implementation_guide.py#L17). # pylint: disable=line-too-long
    However, instead of using the attrs class, we are creating a Pydantic class.
    """

    opening_segment: Optional[str] = None
    segment_group: Optional[str] = None
    sub_hierarchy: list[Optional["SegmentGroupHierarchy"]] = Field(default_factory=list)

    @classmethod
    def create_segmentgroup_hierarchy(
        cls, reduced_nested_nachrichtenstruktur: ReducedNestedNachrichtenstruktur
    ) -> "SegmentGroupHierarchy":
        """init Segmentrgroup Hierarchy"""
        segment_group: Optional[str] = None
        opening_segment: Optional[str] = None
        if reduced_nested_nachrichtenstruktur.header_linie is not None:
            segment_group = reduced_nested_nachrichtenstruktur.header_linie.bezeichnung
        if (
            any(reduced_nested_nachrichtenstruktur.segmente)
            and reduced_nested_nachrichtenstruktur.segmente[0] is not None
        ):
            opening_segment = reduced_nested_nachrichtenstruktur.segmente[0].bezeichnung
        sub_hierarchy: list[Optional["SegmentGroupHierarchy"]] = []
        for sub_segmentgroup in reduced_nested_nachrichtenstruktur.segmentgruppen:
            if sub_segmentgroup is not None:
                sub_hierarchy.append(cls.create_segmentgroup_hierarchy(sub_segmentgroup))

        return SegmentGroupHierarchy(
            segment_group=segment_group, opening_segment=opening_segment, sub_hierarchy=sub_hierarchy
        )

    def to_json(self, message_type: EdifactFormat, output_dir: Path) -> None:
        """
        writes the reduced NestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath(f"{message_type}.sgh.json")
        structured_json = self.model_dump(mode="json")
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info("Wrote segmentgroup hierarchy {}.(sgh.json) for {} to {}", message_type, message_type, file_path)
