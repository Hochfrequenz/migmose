"""
contains class for trees consisting of segments of mig tables
"""

import json
from pathlib import Path
from types import NoneType
from typing import Any, Optional, Tuple

from loguru import logger
from maus.edifact import EdifactFormat
from pydantic import BaseModel

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class ReducedNestedNachrichtenstruktur(BaseModel):
    """will contain the tree structure of nachrichtenstruktur tables"""

    header_linie: Optional[NachrichtenstrukturZeile] = None
    segmente: list[Optional[NachrichtenstrukturZeile]] = []
    segmentgruppen: list[Optional["ReducedNestedNachrichtenstruktur"]] = []

    @classmethod
    def create_reduced_nested_nachrichtenstruktur(cls, json_nachrichten_struktur: dict[str, Any]) -> dict[str, Any]:
        """init nested Nachrichtenstruktur"""

        def remove_duplicates(cls, data) -> dict[str, Any]:
            # Helper function to create a unique identifier for each segment
            def get_identifier(segment) -> tuple[str, str]:
                return (segment.get("zaehler"), segment.get("bezeichnung"))

            # Helper function to create a unique identifier for each segment group using header data
            def get_segmentgruppe_identifier(segment_group) -> tuple[str, str]:
                header = segment_group.get("header_linie", {})
                return (header.get("zaehler"), header.get("bezeichnung"))

            def count_segments(segment_group) -> int:
                # Start with counting segments directly under the current segment group
                total_segments = len(segment_group.get("segmente", []))
                # Recursively count segments in nested segment groups
                for nested_sg in segment_group.get("segmentgruppen", []):
                    total_segments += count_segments(nested_sg)

                return total_segments

            # Function to process segments and remove duplicates within the same list
            def process_segments(segments):
                seen = set()
                unique_segments = []
                for segment in segments:
                    identifier = get_identifier(segment)
                    if identifier not in seen:
                        seen.add(identifier)
                        unique_segments.append(segment)
                return unique_segments

            # Recursive function to traverse and clean segment groups
            def clean_segmentgruppen(segmentgruppen):
                seen = {}
                unique_segmentgruppen = []
                for sg in segmentgruppen:
                    identifier = get_segmentgruppe_identifier(sg)
                    current_count = count_segments(sg)

                    if identifier in seen:
                        # Compare segment counts and keep the one with more segments
                        existing_sg, existing_count = seen[identifier]
                        if current_count > existing_count:
                            # Replace the existing segment group with this one because it has more segments
                            unique_segmentgruppen.remove(existing_sg)
                            unique_segmentgruppen.append(sg)
                            seen[identifier] = (sg, current_count)
                    else:
                        # If not seen, add it directly
                        seen[identifier] = (sg, current_count)
                        unique_segmentgruppen.append(sg)

                    # Process segments within this group
                    sg["segmente"] = process_segments(sg.get("segmente", []))
                    # Recursively clean nested segment groups
                    sg["segmentgruppen"] = clean_segmentgruppen(sg.get("segmentgruppen", []))

                return unique_segmentgruppen

            # Start processing the top-level segments
            if "segmente" in data:
                data["segmente"] = process_segments(data["segmente"])

            # Process segment groups recursively
            if "segmentgruppen" in data:
                data["segmentgruppen"] = clean_segmentgruppen(data["segmentgruppen"])

            return data

        return remove_duplicates(cls, json_nachrichten_struktur)

    @classmethod
    def save_to_json_file(
        cls, message_type: EdifactFormat, output_dir: Path, structured_json: dict[str, Any]
    ) -> dict[str, Any]:
        """
        writes the ReducedNestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath(f"{message_type}_reduced_nested_nachrichtenstruktur.json")
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info(f"Wrote nested Nachrichtenstruktur for {message_type} to {file_path}")
        return structured_json
