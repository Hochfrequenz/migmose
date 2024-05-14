"""
contains class for structured segmentgroups in mig tables. Builds table recursively.
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
    def create_nested_nachrichtenstruktur(
        cls, table: NachrichtenstrukturTabelle, header_line: Optional[NachrichtenstrukturZeile] = None, index: int = 0
    ) -> Tuple["NestedNachrichtenstruktur", int]:
        """init nested Nachrichtenstruktur"""
        collected_segments: list[Optional[NachrichtenstrukturZeile]] = []
        collected_segmentgroups: list[Optional["NestedNachrichtenstruktur"]] = []
        i = index
        while i < len(table.lines):
            line = table.lines[i]
            is_line_segmentgruppe = line.nr is None
            if is_line_segmentgruppe:
                added_segmentgroup, i = cls.create_nested_nachrichtenstruktur(table, line, i + 1)
                collected_segmentgroups.append(added_segmentgroup)
            else:
                collected_segments.append(line)
                i += 1
            if i < len(table.lines) and not isinstance(header_line, NoneType):
                is_next_line_segmentgruppe = table.lines[i].nr is None
                is_current_ebene_greater_than_next_ebene = line.ebene > table.lines[i].ebene
                is_current_header_ebene_greater_eq_than_next_ebene = header_line.ebene >= table.lines[i].ebene

                if (
                    is_next_line_segmentgruppe and is_current_header_ebene_greater_eq_than_next_ebene
                ) or is_current_ebene_greater_than_next_ebene:
                    return (
                        cls(
                            header_linie=header_line,
                            segmente=collected_segments,
                            segmentgruppen=collected_segmentgroups,
                        ),
                        i,
                    )
        return cls(header_linie=header_line, segmente=collected_segments, segmentgruppen=collected_segmentgroups), i

    def to_json(self, message_type: EdifactFormat, output_dir: Path) -> dict[str, Any]:
        """
        writes the NestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath("nested_nachrichtenstruktur.json")
        structured_json = self.model_dump()
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(structured_json, json_file, indent=4)
        logger.info(f"Wrote nested Nachrichtenstruktur for {message_type} to {file_path}")
        return structured_json
