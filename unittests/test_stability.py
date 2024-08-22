"""
tests that running migmose over multiple files does not change the results
"""

import csv
import random
import uuid
from pathlib import Path
from typing import TypeAlias
from uuid import UUID

from efoli import EdifactFormat

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur
from migmose.parsing import parse_raw_nachrichtenstrukturzeile
from unittests import path_to_test_FV2310

_CsvFileContent: TypeAlias = list[list[str]]


def _read_csv_file(file_path: Path) -> _CsvFileContent:
    with open(file_path, encoding="utf-8", mode="r", newline="") as file:
        reader = csv.reader(file)
        return list(reader)


def test_stability(tmp_path) -> None:
    input_files: list[tuple[UUID, Path, EdifactFormat]] = [
        (
            uuid.uuid4(),
            path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx",
            EdifactFormat.ORDCHG,
        ),
        (
            uuid.uuid4(),
            path_to_test_FV2310
            / "IFTSTAMIG-informatorischeLesefassung2.0e-AußerordentlicheVeröffentlichung_99991231_20231001.docx",
            EdifactFormat.IFTSTA,
        ),
        (
            uuid.uuid4(),
            path_to_test_FV2310
            # pylint:disable=line-too-long
            / "UTILMDMIGStrom-informatorischeLesefassungS1.1KonsolidierteLesefassungmitFehlerkorrekturenStand12.12.2023_20240402_20231212.docx",
            EdifactFormat.UTILMDS,
        ),
    ]
    results: dict[UUID, list[_CsvFileContent]] = {}
    for i in range(10):
        for file_id, input_file, message_format in random.sample(input_files, len(input_files)):
            output_dir = tmp_path / f"output-{message_format}-{i}"
            raw_lines = parse_raw_nachrichtenstrukturzeile(input_file)
            nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
            nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
                nachrichtenstrukturtabelle
            )
            _ = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(nested_nachrichtenstruktur)
            # just repeating these steps with the nachrichtenstruktur, because they're also done in __main__.py
            nachrichtenstrukturtabelle.to_csv(message_format, output_dir)
            results[file_id] = results.get(file_id, []) + [_read_csv_file(output_dir / "nachrichtenstruktur.csv")]
    for file_id, csv_files in results.items():
        assert all(csv_file == csv_files[0] for csv_file in csv_files)
