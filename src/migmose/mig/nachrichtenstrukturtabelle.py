"""
contains class mig tables
"""

import csv
from pathlib import Path

from loguru import logger
from maus.edifact import EdifactFormat
from pydantic import BaseModel

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class NachrichtenstrukturTabelle(BaseModel):
    """
    class for mig tables
    """

    lines: list[NachrichtenstrukturZeile]

    @classmethod
    def init_raw_table(cls, raw_lines: list[str]) -> "NachrichtenstrukturTabelle":
        """
        reads table as list of raw lines and returns a NachrichtenstrukturTabelle
        consisting of NachrichtenstrukturZeilen
        """
        collected_lines: list[NachrichtenstrukturZeile] = []
        for raw_line in raw_lines:
            collected_lines.append(NachrichtenstrukturZeile.init_raw_lines(raw_line))
        return cls(lines=collected_lines)

    def output_as_csv(self, message_type: EdifactFormat, output_dir: Path) -> None:
        """
        writes the NestedNachrichtenstruktur as json
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir.joinpath(f"{message_type}_nachrichtenstruktur.csv")
        fieldnames = list(NachrichtenstrukturZeile.model_json_schema()["properties"].keys())
        with open(file_path, "w", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for nachrichtenstruktur_zeile in self.lines:
                writer.writerow(nachrichtenstruktur_zeile.model_dump())
        logger.info(f"Wrote Nachrichtenstruktur for {message_type} to {file_path}")
