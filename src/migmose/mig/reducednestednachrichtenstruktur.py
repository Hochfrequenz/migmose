"""
contains class for trees consisting of segments of mig tables
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Optional, TypeAlias

from efoli import EdifactFormat
from jinja2 import Template
from loguru import logger
from pydantic import BaseModel, Field

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur

_SegmentDict: TypeAlias = (
    dict[
        tuple[str, str],
        tuple[
            list[Optional[NachrichtenstrukturZeile]],
            Optional[NachrichtenstrukturZeile],
            set[tuple[str, str]],
        ],
    ]
    | None
)


# Helper function to create a unique identifier for each segment
def _get_identifier(segment: Optional[NachrichtenstrukturZeile]) -> tuple[str, str]:
    if segment is None:
        return "0", "root"
    return segment.zaehler, segment.bezeichnung


# Function to process segments and remove duplicates within the same list.
def _process_segments(
    segments: list[Optional[NachrichtenstrukturZeile]],
) -> list[Optional[NachrichtenstrukturZeile]]:
    seen = set()
    unique_segments: list[Optional[NachrichtenstrukturZeile]] = []
    for segment in segments:
        if segment is not None:
            identifier = _get_identifier(segment)
            if identifier not in seen:
                seen.add(identifier)
                unique_segments.append(segment)
    return unique_segments


# Recursive function to traverse and clean segment groups
def _process_segmentgruppen(
    segmentgruppen_identifiers: set[tuple[str, str]],
    segment_dict: _SegmentDict,
    depth: int = 0,
) -> list[Optional["ReducedNestedNachrichtenstruktur"]]:
    """
    Recursively clean segment groups to ensure nested nachrichtenstruktur consisting only of a unique subset.
    """
    result: list[Optional[ReducedNestedNachrichtenstruktur]] = []

    for sg in sorted(segmentgruppen_identifiers):
        if sg is not None:
            # not sure about those type hints... they please mypy but I'm not the dev of this code
            segmente: list[Optional[NachrichtenstrukturZeile]]
            header_line: Optional[NachrichtenstrukturZeile]
            segmentgroups: set[tuple[str, str]]
            segmente, header_line, segmentgroups = segment_dict[sg]  # type:ignore[index]
            if segmente is not None:
                segmente = sorted(segmente, key=lambda x: x.zaehler)
            _new_sg = ReducedNestedNachrichtenstruktur(header_linie=header_line, segmente=segmente)
            _new_sg.segmentgruppen = _process_segmentgruppen(segmentgroups, segment_dict, depth + 1)
            result.append(_new_sg)
            logger.info("Added {} with {} segments at depth {}.", sg, len(segmente), depth)
    return result


def _build_segment_dict(
    segment_groups: list[Optional[NestedNachrichtenstruktur]],
    segment_dict: _SegmentDict = None,
) -> dict[
    tuple[str, str],
    tuple[list[Optional[NachrichtenstrukturZeile]], Optional[NachrichtenstrukturZeile], set[tuple[str, str]]],
]:
    """Build a dictionary of segments and segment groups to find unique set."""
    if segment_dict is None:
        segment_dict = {}
    for _sg in segment_groups:
        if _sg is not None:
            name = _get_identifier(_sg.header_linie)

            # Check if the current segments are already known and complete by unknown segments
            if name in segment_dict:
                # make sure every possible segment is included
                segment_dict[name] = (
                    _process_segments(_sg.segmente + segment_dict[name][0]),
                    segment_dict[name][1],
                    segment_dict[name][2],
                )
            else:
                segment_dict[name] = (_process_segments(_sg.segmente), _sg.header_linie, set())

            # Iterate recursively through nested segmentgroups
            for segmentgruppe in _sg.segmentgruppen:
                if segmentgruppe is not None:
                    sg_name = _get_identifier(segmentgruppe.header_linie)
                    segment_dict[name][2].add(sg_name)
                    segment_dict = _build_segment_dict([segmentgruppe], segment_dict)

    return segment_dict


def _dict_to_tree_str(tree: DefaultDict[str, list[NachrichtenstrukturZeile]]) -> str:
    template_str = """{%- for key, segment_list in tree.items() -%}
    {{-key-}}:{%- for segment in segment_list -%}
    {{segment.bezeichnung}}[{{segment.standard_status}};{{segment.bdew_status}}]
    {%- if not loop.last -%},{%- endif -%}
    {%- endfor -%}{{"\n"}}
    {%- endfor -%}
    """
    template = Template(template_str)
    return template.render(tree=tree)


def _build_tree_dict(
    reduced_nestednachrichtenstruktur: "ReducedNestedNachrichtenstruktur",
    tree_dict: Optional[DefaultDict[str, list[NachrichtenstrukturZeile]]] = None,
) -> DefaultDict[str, list[NachrichtenstrukturZeile]]:
    """
    Build a dictionary to compose the .tree files in the MAUS library.
    """
    if tree_dict is None:
        tree_dict = defaultdict(list)
    if (
        reduced_nestednachrichtenstruktur.header_linie is None
        and reduced_nestednachrichtenstruktur.segmente[0] is not None
    ):
        tree_dict["/"] = [
            NachrichtenstrukturZeile(
                zaehler="0",
                nr="00000",
                bezeichnung="UNB",
                standard_status="M",
                bdew_status="M",
                standard_maximale_wiederholungen=0,
                bdew_maximale_wiederholungen=0,
                ebene=0,
                inhalt="0",
            ),
            reduced_nestednachrichtenstruktur.segmente[0],
            NachrichtenstrukturZeile(
                zaehler="0",
                nr="00000",
                bezeichnung="UNZ",
                standard_status="M",
                bdew_status="M",
                standard_maximale_wiederholungen=0,
                bdew_maximale_wiederholungen=0,
                ebene=0,
                inhalt="0",
            ),
        ]
        tree_dict["UNH"].extend(
            [
                segment
                for segment in reduced_nestednachrichtenstruktur.segmente
                if segment and segment.bezeichnung not in ["UNH", "UNT"]
            ]
        )
        tree_dict["UNH"].extend(
            [sg.header_linie for sg in reduced_nestednachrichtenstruktur.segmentgruppen if sg and sg.header_linie]
        )
        tree_dict["UNH"].extend(
            [
                segment
                for segment in reduced_nestednachrichtenstruktur.segmente
                if segment and segment.bezeichnung in ["UNT"]
            ]
        )
    elif reduced_nestednachrichtenstruktur.header_linie is not None:
        if reduced_nestednachrichtenstruktur.segmente not in [[], [None]]:
            tree_dict[reduced_nestednachrichtenstruktur.header_linie.bezeichnung].extend(
                [segment for segment in reduced_nestednachrichtenstruktur.segmente if segment]
            )
        if reduced_nestednachrichtenstruktur.segmentgruppen:
            tree_dict[reduced_nestednachrichtenstruktur.header_linie.bezeichnung].extend(
                [sg.header_linie for sg in reduced_nestednachrichtenstruktur.segmentgruppen if sg and sg.header_linie]
            )
    else:
        raise ValueError("No header line or segment found.")
    for segmentgruppe in reduced_nestednachrichtenstruktur.segmentgruppen:
        if segmentgruppe is not None:
            tree_dict = _build_tree_dict(segmentgruppe, tree_dict)
    return tree_dict


class ReducedNestedNachrichtenstruktur(BaseModel):
    """will contain the tree structure of nachrichtenstruktur tables"""

    header_linie: Optional[NachrichtenstrukturZeile] = None
    segmente: list[Optional[NachrichtenstrukturZeile]] = Field(default_factory=list)
    segmentgruppen: list[Optional["ReducedNestedNachrichtenstruktur"]] = Field(default_factory=list)

    @classmethod
    def create_reduced_nested_nachrichtenstruktur(
        cls, nachrichten_struktur: NestedNachrichtenstruktur
    ) -> "ReducedNestedNachrichtenstruktur":
        """init nested Nachrichtenstruktur"""

        data = ReducedNestedNachrichtenstruktur()
        # Start processing the top-level segments
        if nachrichten_struktur.segmente is not None:
            data.segmente = _process_segments(nachrichten_struktur.segmente)

        # Process segment groups recursively
        if nachrichten_struktur.segmentgruppen is not None:
            segment_dict = _build_segment_dict(nachrichten_struktur.segmentgruppen)
            segmentgruppen_identifiers = set(
                _get_identifier(sg.header_linie) for sg in nachrichten_struktur.segmentgruppen if sg is not None
            )
            data.segmentgruppen = _process_segmentgruppen(segmentgruppen_identifiers, segment_dict)

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

    def output_tree(self, message_type: EdifactFormat, output_dir: Path, document_version: str) -> None:
        """Writes reduced NestedNachrichtenstruktur in the .tree grammar of MAUS."""
        # generate tree dict
        tree_dict = _build_tree_dict(self)
        # convert tree dict to string
        tree_str = _dict_to_tree_str(tree_dict)
        # write tree file
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{message_type}{document_version}.tree"
        with open(file_path, "w", encoding="utf-8") as tree_file:
            tree_file.write(tree_str)
        logger.info("Wrote reduced .tree file for {} to {}", message_type, file_path)
