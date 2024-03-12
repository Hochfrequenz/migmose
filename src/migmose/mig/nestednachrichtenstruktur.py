"""
contains class for structured segmentgroups in mig tables. Builds table recursively.
"""

import json
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger
from maus.edifact import EdifactFormat
from pydantic import BaseModel

from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class NestedNachrichtenstruktur(BaseModel):
    """
    class for structured segmentgroups in mig tables. Builds table recursively. Inherits from NachrichtenstrukturZeile
    e.g.(ORDCHG):
    {
    "segmente": [
        {
        "zaehler": "0160",
        "nr": "7",
        "bezeichnung": "NAD",
        "standard_status": "M",
        "bdew_status": "M",
        "standard_maximale_wiederholungen": 1,
        "bdew_maximale_wiederholungen": 1,
        "ebene": 1,
        "inhalt": "MP-ID Absender"
        }
        ],
    "segmentgruppen": [
    {
        "segmente": [
        {
            "zaehler": "0260",
            "nr": "8",
            "bezeichnung": "CTA",
            "standard_status": "M",
            "bdew_status": "M",
            "standard_maximale_wiederholungen": 1,
            "bdew_maximale_wiederholungen": 1,
            "ebene": 2,
            "inhalt": "Ansprechpartner"
            },
            {
            "zaehler": "0270",
            "nr": "9",
            "bezeichnung": "COM",
            "standard_status": "C",
            "bdew_status": "R",
            "standard_maximale_wiederholungen": 5,
            "bdew_maximale_wiederholungen": 5,
            "ebene": 3,
            "inhalt": "Kommunikationsverbindung"
            }
            ],
        "segmentgruppen": []
        }
        ]
    }
    """

    header_linie: Optional[NachrichtenstrukturZeile] = None
    segmente: list[Optional[NachrichtenstrukturZeile]] = []
    segmentgruppen: list[Optional["NestedNachrichtenstruktur"]] = []

    @classmethod
    def structure_table(
        cls, table: NachrichtenstrukturTabelle, segmentgruppe: Optional[NachrichtenstrukturZeile] = None, index: int = 0
    ) -> Tuple["NestedNachrichtenstruktur", int]:
        """init structured table"""
        collected_segments: list[Optional[NachrichtenstrukturZeile]] = []
        collected_segmentgroups: list[Optional["NestedNachrichtenstruktur"]] = []
        i = index
        while i < len(table.lines):
            line = table.lines[i]
            is_line_segmentgruppe = line.nr is None
            if is_line_segmentgruppe:
                added_segmentgroup, i = cls.structure_table(table, line, i + 1)
                collected_segmentgroups.append(added_segmentgroup)
            else:
                collected_segments.append(line)
                i += 1
            if i < len(table.lines):
                next_line_segmentgruppe = table.lines[i].nr is None

                if segmentgruppe is not None and (
                    (next_line_segmentgruppe and table.lines[i].ebene <= segmentgruppe.ebene)  # type: ignore [operator]
                    or (line.ebene > table.lines[i].ebene)  # type: ignore [operator]
                ):
                    return (
                        cls(
                            header_linie=segmentgruppe,
                            segmente=collected_segments,
                            segmentgruppen=collected_segmentgroups,
                        ),
                        i,
                    )
        return cls(header_linie=segmentgruppe, segmente=collected_segments, segmentgruppen=collected_segmentgroups), i

    @classmethod
    def output_as_json(
        cls, instance: "NestedNachrichtenstruktur", message_type: EdifactFormat, output_dir: Path
    ) -> None:
        """
        writes the NestedNachrichtenstruktur as json
        """

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath(f"{message_type}_Nested_nachrichtenstruktur.json")
        structured_json = instance.model_dump()
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info(f"Wrote nested Nachrichtenstruktur for {message_type} to {file_path}")
