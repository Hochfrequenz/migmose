import json

import pytest
from maus.edifact import EdifactFormatVersion

from migmose.edifactformat import ExtendedEdifactFormat
from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur
from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile
from unittests import expected_output_dir, path_to_test_edi_energy_mirror_repo


class TestReducedNestedNachrichtenstruktur:
    """test class for create_reduced_nested_nachrichtenstruktur"""

    @pytest.mark.parametrize(
        "message_format",
        [
            pytest.param(ExtendedEdifactFormat.ORDCHG, id="ORDCHG"),
            pytest.param(ExtendedEdifactFormat.UTILMDS, id="UTILMDS"),
            pytest.param(ExtendedEdifactFormat.IFTSTA, id="IFTSTA"),
        ],
    )
    def test_create_reduced_nested_nachrichtenstruktur(self, message_format: ExtendedEdifactFormat, tmp_path):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        file_path_dict = find_file_to_format(
            [message_format], path_to_test_edi_energy_mirror_repo, EdifactFormatVersion.FV2310
        )
        file_path = file_path_dict[message_format]
        raw_lines = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        reduced_nested_nachrichtenstruktur = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(
            nested_nachrichtenstruktur
        )
        reduced_nested_nachrichtenstruktur.to_json(message_format, tmp_path)
        with open(tmp_path / "reduced_nested_nachrichtenstruktur.json", "r", encoding="utf-8") as file1:
            actual_reduced_nested_json = json.load(file1)
            with open(
                expected_output_dir
                / EdifactFormatVersion.FV2310
                / message_format
                / "reduced_nested_nachrichtenstruktur.json",
                "r",
                encoding="utf-8",
            ) as file2:
                expected_reduced_nested_json = json.load(file2)
                assert actual_reduced_nested_json == expected_reduced_nested_json
