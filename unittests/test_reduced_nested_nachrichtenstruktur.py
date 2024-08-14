import json

import pytest
from efoli import EdifactFormat, EdifactFormatVersion
from maus.reader.tree_to_sgh import check_file_can_be_parsed_as_tree

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import (
    ReducedNestedNachrichtenstruktur,
    _build_tree_dict,
    _dict_to_tree_str,
)
from migmose.parsing import _extract_document_version, find_file_to_format, parse_raw_nachrichtenstrukturzeile
from unittests import expected_output_dir, path_to_test_edi_energy_mirror_repo


class TestReducedNestedNachrichtenstruktur:
    """test class for create_reduced_nested_nachrichtenstruktur"""

    @pytest.mark.parametrize(
        "message_format",
        [
            pytest.param(EdifactFormat.ORDCHG, id="ORDCHG"),
            pytest.param(EdifactFormat.UTILMDS, id="UTILMDS"),
            pytest.param(EdifactFormat.IFTSTA, id="IFTSTA"),
        ],
    )
    def test_create_reduced_nested_nachrichtenstruktur(self, message_format: EdifactFormat, tmp_path, snapshot):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        file_path_dict = find_file_to_format(
            [message_format], path_to_test_edi_energy_mirror_repo, EdifactFormatVersion.FV2310
        )
        file_path = file_path_dict[message_format]
        (raw_lines, _) = parse_raw_nachrichtenstrukturzeile(file_path)
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
            assert actual_reduced_nested_json == snapshot

    @pytest.mark.parametrize(
        "message_format",
        [
            pytest.param(EdifactFormat.ORDCHG, id="ORDCHG"),
            pytest.param(EdifactFormat.UTILMDS, id="UTILMDS"),
            pytest.param(EdifactFormat.IFTSTA, id="IFTSTA"),
        ],
    )
    def test_build_tree_dict_and_generate_str(self, message_format: EdifactFormat, snapshot):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        # read the reduced_nested_nachrichtenstruktur.json
        reduced_nested_nachrichtenstruktur_path = (
            expected_output_dir
            / EdifactFormatVersion.FV2310
            / message_format
            / "reduced_nested_nachrichtenstruktur.json"
        )
        with open(reduced_nested_nachrichtenstruktur_path, "r", encoding="utf-8") as file1:
            reduced_nested_json = json.load(file1)
            reduced_nested_nachrichtenstruktur = ReducedNestedNachrichtenstruktur(**reduced_nested_json)
            tree_dict = _build_tree_dict(reduced_nested_nachrichtenstruktur)
            assert tree_dict == snapshot
            tree_str = _dict_to_tree_str(tree_dict)
            assert tree_str == snapshot

    @pytest.mark.parametrize(
        "message_format",
        [
            pytest.param(EdifactFormat.ORDCHG, id="ORDCHG"),
            pytest.param(EdifactFormat.UTILMDS, id="UTILMDS"),
            pytest.param(EdifactFormat.IFTSTA, id="IFTSTA"),
        ],
    )
    def test_output_tree(self, message_format: EdifactFormat, tmp_path, snapshot):
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
        document_version = _extract_document_version(file_path)
        reduced_nested_nachrichtenstruktur.output_tree(message_format, tmp_path, document_version)
        with open(tmp_path / f"{message_format}{document_version}.tree", "r", encoding="utf-8") as actual_file:
            assert actual_file.read() == snapshot
        try:
            check_file_can_be_parsed_as_tree(tmp_path / f"{message_format}{document_version}.tree")
        except ValueError as e:
            assert False, f"maus exception: {e}"
