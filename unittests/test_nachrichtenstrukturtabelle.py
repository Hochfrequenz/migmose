import csv
from pathlib import Path

from maus.edifact import EdifactFormat

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.parsing import parse_raw_nachrichtenstrukturzeile


class TestNachrichtenstrukturTabelle:
    """
    A class with pytest unit tests for NachrichtenstrukturTabellen.
    """

    def test_init_nachrichtenstrukturtabelle(self):
        raw_lines = [
            "\t0580\t527\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation",
            "\t0590\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation",
        ]
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.init_raw_table(raw_lines)
        assert len(nachrichtenstrukturtabelle.lines) == len(raw_lines)
        assert nachrichtenstrukturtabelle.lines[0].zaehler == "0580"

    def test_parse(self):
        file_path = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        raw_lines = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.init_raw_table(raw_lines)
        assert len(nachrichtenstrukturtabelle.lines) == 18

    def test_output_as_csv(self, tmp_path):
        input_file = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        message_format = EdifactFormat.ORDCHG
        output_dir = tmp_path / Path("output")
        raw_lines = parse_raw_nachrichtenstrukturzeile(input_file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.init_raw_table(raw_lines)
        nachrichtenstrukturtabelle.output_as_csv(message_format, output_dir)

        file_path = output_dir / Path(f"{message_format}_nachrichtenstruktur.csv")

        assert file_path.exists()

        reference_file = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2_nested_nachrichtenstruktur.csv")

        with open(file_path, "r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            with open(reference_file, "r", encoding="utf-8") as reference_csv:
                reference_reader = csv.DictReader(reference_csv)
                assert reader.fieldnames == reference_reader.fieldnames
                for row, reference_row in zip(reader, reference_reader):
                    assert row == reference_row
