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
        def get_identifier(segment: NachrichtenstrukturZeile) -> tuple[str, str]:
            return (segment.zaehler, segment.bezeichnung)

        # Helper function to create a unique identifier for each segment group using header data
        def get_segmentgruppe_identifier(segment_group: NestedNachrichtenstruktur) -> tuple[str, str]:
            header = segment_group.header_linie
            return (header.zaehler, header.bezeichnung)

        def count_segments(segment_group: NestedNachrichtenstruktur) -> int:
            # Start with counting segments directly under the current segment group
            total_segments = len(segment_group.segmente)
            # Recursively count segments in nested segment groups
            for nested_sg in segment_group.segmentgruppen:
                total_segments += count_segments(nested_sg)

            return total_segments

        # Function to process segments and remove duplicates within the same list.
        def process_segments(segments: list[Optional[NachrichtenstrukturZeile]]):
            seen = set()
            unique_segments = []
            for segment in segments:
                identifier = get_identifier(segment)
                if identifier not in seen:
                    seen.add(identifier)
                    unique_segments.append(segment)
            return unique_segments

        # Recursive function to traverse and clean segment groups
        def process_segmentgruppen(
            segmentgruppen: NestedNachrichtenstruktur, segment_count_dict: dict, seen: dict = None, depth: int = 0
        ):
            """Recursively clean segment groups to avoid duplicates, keep largest,
            with debugging for circular references."""
            if seen is None:
                seen = {}
            result = []

            for sg in segmentgruppen:
                identifier = get_segmentgruppe_identifier(sg)
                max_count, max_sg = segment_count_dict[identifier]

                if identifier not in seen:
                    seen[identifier] = max_sg
                    print(f"Added {identifier} with {max_count} segments at depth {depth}.")

                sg.segmente = process_segments(max_sg.segmente)
                sg.segmentgruppen = process_segmentgruppen(max_sg.segmentgruppen, segment_count_dict, seen, depth + 1)

            # Compile the unique list from the seen dictionary after recursive processing to avoid circular reference
            if depth == 0:  # Only compile on the initial call, not recursive ones
                result = [seen[key] for key in seen]
            return result

        def build_segment_count_dict(segment_groups: NestedNachrichtenstruktur):
            segment_count_dict = {}
            for sg in segment_groups:
                name = get_segmentgruppe_identifier(sg)
                count = count_segments(sg)

                # Check if the current segment group's count is greater than the stored count
                if name in segment_count_dict:
                    existing_count, _ = segment_count_dict[name]
                    if count > existing_count:
                        segment_count_dict[name] = (count, sg)
                else:
                    segment_count_dict[name] = (count, sg)

                # Process nested segment groups recursively and update the dictionary
                nested_counts = build_segment_count_dict(sg.segmentgruppen)
                for nested_name, (nested_count, nested_sg) in nested_counts.items():
                    if nested_name in segment_count_dict:
                        existing_count, _ = segment_count_dict[nested_name]
                        if nested_count > existing_count:
                            segment_count_dict[nested_name] = (nested_count, nested_sg)
                    else:
                        segment_count_dict[nested_name] = (nested_count, nested_sg)

            return segment_count_dict

        data = ReducedNestedNachrichtenstruktur()
        # Start processing the top-level segments
        if nachrichten_struktur.segmente is not None:
            data.segmente = process_segments(nachrichten_struktur.segmente)

        # Process segment groups recursively
        if nachrichten_struktur.segmentgruppen is not None:
            segment_count_dict = build_segment_count_dict(nachrichten_struktur.segmentgruppen)
            data.segmentgruppen = process_segmentgruppen(nachrichten_struktur.segmentgruppen, segment_count_dict)

        return data

    def to_json(self, message_type: EdifactFormat, output_dir: Path) -> dict[str, Any]:
        """
        writes the NestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath(f"{message_type}_reduced_nested_nachrichtenstruktur.json")
        structured_json = self.model_dump()
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info(f"Wrote nested Nachrichtenstruktur for {message_type} to {file_path}")
        return structured_json
