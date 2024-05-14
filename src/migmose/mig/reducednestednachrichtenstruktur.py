"""
contains class for trees consisting of segments of mig tables
"""

import json
from pathlib import Path
from typing import Any, Optional

from loguru import logger
from maus.edifact import EdifactFormat
from pydantic import BaseModel

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur


class ReducedNestedNachrichtenstruktur(BaseModel):
    """will contain the tree structure of nachrichtenstruktur tables"""

    header_linie: Optional[NachrichtenstrukturZeile] = None
    segmente: list[Optional[NachrichtenstrukturZeile]] = []
    segmentgruppen: list[Optional["ReducedNestedNachrichtenstruktur"]] = []

    @classmethod
    def create_reduced_nested_nachrichtenstruktur(
        cls, nachrichten_struktur: NestedNachrichtenstruktur
    ) -> "ReducedNestedNachrichtenstruktur":
        """init nested Nachrichtenstruktur"""

        # Helper function to create a unique identifier for each segment
        def get_identifier(segment: Optional[NachrichtenstrukturZeile]) -> tuple[str, str]:
            if segment is None:
                return ("0", "root")
            return (segment.zaehler, segment.bezeichnung)

        # Function to process segments and remove duplicates within the same list.
        def process_segments(
            segments: list[Optional[NachrichtenstrukturZeile]],
        ) -> list[Optional[NachrichtenstrukturZeile]]:
            seen = set()
            unique_segments: list[Optional[NachrichtenstrukturZeile]] = []
            for segment in segments:
                if segment is not None:
                    identifier = get_identifier(segment)
                    if identifier not in seen:
                        seen.add(identifier)
                        unique_segments.append(segment)
            return unique_segments

        # Recursive function to traverse and clean segment groups
        def process_segmentgruppen(
            segmentgruppen_identifiers: set[tuple[str, str]],
            segment_dict: dict,
            depth: int = 0,
        ) -> list[Optional[ReducedNestedNachrichtenstruktur]]:
            """
            Recursively clean segment groups to ensure nested nachrichtenstruktur consisting only of a unique subset.
            """
            result: list[Optional[ReducedNestedNachrichtenstruktur]] = []

            for sg in sorted(segmentgruppen_identifiers):
                if sg is not None:
                    segmente, header_line, segmentgroups = segment_dict[sg]
                    if segmente is not None:
                        segmente = sorted(segmente, key=lambda x: x.zaehler)
                    _new_sg = ReducedNestedNachrichtenstruktur(header_linie=header_line, segmente=segmente)
                    _new_sg.segmentgruppen = process_segmentgruppen(segmentgroups, segment_dict, depth + 1)
                    result.append(_new_sg)
                    logger.info("Added {} with {} segments at depth {}.", sg, len(segmente), depth)
            return result

        def build_segment_dict(
            segment_groups: list[Optional[NestedNachrichtenstruktur]],
            segment_dict: (
                dict[
                    tuple[str, str],
                    tuple[
                        list[Optional[NachrichtenstrukturZeile]],
                        Optional[NachrichtenstrukturZeile],
                        set[tuple[str, str]],
                    ],
                ]
                | None
            ) = None,
        ) -> dict[
            tuple[str, str],
            tuple[list[Optional[NachrichtenstrukturZeile]], Optional[NachrichtenstrukturZeile], set[tuple[str, str]]],
        ]:
            """Build a dictionary of segments and segment groups to find unique set."""
            if segment_dict is None:
                segment_dict = {}
            for _sg in segment_groups:
                if _sg is not None:
                    name = get_identifier(_sg.header_linie)

                    # Check if the current segments are already known and complete by unknown segments
                    if name in segment_dict:
                        # make sure every possible segment is included
                        segment_dict[name] = (
                            process_segments(_sg.segmente + segment_dict[name][0]),
                            segment_dict[name][1],
                            segment_dict[name][2],
                        )
                    else:
                        segment_dict[name] = (process_segments(_sg.segmente), _sg.header_linie, set())

                    # Iterate recursively through nested segmentgroups
                    for segmentgruppe in _sg.segmentgruppen:
                        if segmentgruppe is not None:
                            sg_name = get_identifier(segmentgruppe.header_linie)
                            segment_dict[name][2].add(sg_name)
                            segment_dict = build_segment_dict([segmentgruppe], segment_dict)

            return segment_dict

        data = ReducedNestedNachrichtenstruktur()
        # Start processing the top-level segments
        if nachrichten_struktur.segmente is not None:
            data.segmente = process_segments(nachrichten_struktur.segmente)

        # Process segment groups recursively
        if nachrichten_struktur.segmentgruppen is not None:
            segment_dict = build_segment_dict(nachrichten_struktur.segmentgruppen)
            segmentgruppen_identifiers = set(
                get_identifier(sg.header_linie) for sg in nachrichten_struktur.segmentgruppen if sg is not None
            )
            data.segmentgruppen = process_segmentgruppen(segmentgruppen_identifiers, segment_dict)

        return data

    def to_json(self, message_type: EdifactFormat, output_dir: Path) -> dict[str, Any]:
        """
        writes the reduced NestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath("reduced_nested_nachrichtenstruktur.json")
        structured_json = self.model_dump()
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info("Wrote reduced nested Nachrichtenstruktur for {} to {}", message_type, file_path)
        return structured_json
