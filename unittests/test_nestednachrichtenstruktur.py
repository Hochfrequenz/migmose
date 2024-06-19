import json
from pathlib import Path

from maus.edifact import EdifactFormat, EdifactFormatVersion

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.parsing import parse_raw_nachrichtenstrukturzeile
from unittests import expected_output_dir, path_to_test_FV2310


class TestNestedNachrichtenstruktur:
    """
    A class with pytest unit tests for nested Nachrichtenstrukturen.
    """

    def test_create_nested_nachrichtenstruktur(self):
        file_path = path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
        raw_lines, _ = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        assert len(nested_nachrichtenstruktur.segmente) == 5
        # pylint: disable=unsubscriptable-object
        assert len(nested_nachrichtenstruktur.segmentgruppen[3].segmentgruppen) == 1

    def test_to_json(self, tmp_path):
        input_file = path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
        message_format = EdifactFormat.ORDCHG
        output_dir = tmp_path
        raw_lines, _ = parse_raw_nachrichtenstrukturzeile(input_file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        nested_nachrichtenstruktur.to_json(message_format, output_dir)

        file_path = output_dir / Path("nested_nachrichtenstruktur.json")

        assert file_path.exists()

        reference_file = (
            expected_output_dir / EdifactFormatVersion.FV2310 / EdifactFormat.ORDCHG / "nested_nachrichtenstruktur.json"
        )

        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        with open(reference_file, "r", encoding="utf-8") as g:
            reference_json = json.load(g)

        assert content == reference_json
