import json
from pathlib import Path

from maus.edifact import EdifactFormat

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.parsing import parse_raw_nachrichtenstrukturzeile


class TestNestedNachrichtenstruktur:
    """
    A class with pytest unit tests for nested Nachrichtenstrukturen.
    """

    def test_create_nested_nachrichtenstruktur(self):
        file_path = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        raw_lines = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        assert len(nested_nachrichtenstruktur.segmente) == 5
        assert len(nested_nachrichtenstruktur.segmentgruppen[3].segmentgruppen) == 1

    def test_to_json(self, tmp_path):
        input_file = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        message_format = EdifactFormat.ORDCHG
        output_dir = tmp_path / Path("output")
        raw_lines = parse_raw_nachrichtenstrukturzeile(input_file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        nested_nachrichtenstruktur.to_json(message_format, output_dir)

        file_path = output_dir / Path(f"{message_format}_nested_nachrichtenstruktur.json")

        assert file_path.exists()

        reference_file = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2_nested_nachrichtenstruktur.json")

        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        with open(reference_file, "r", encoding="utf-8") as g:
            reference_json = json.load(g)

        assert content == reference_json
