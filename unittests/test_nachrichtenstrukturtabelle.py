import csv
from pathlib import Path

from maus.edifact import EdifactFormat, EdifactFormatVersion

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.parsing import parse_raw_nachrichtenstrukturzeile
from unittests import expected_output_dir, path_to_test_FV2310


class TestNachrichtenstrukturTabelle:
    """
    A class with pytest unit tests for NachrichtenstrukturTabellen.
    """

    def test_init_nachrichtenstrukturtabelle(self):
        raw_lines = [
            "\t0580\t527\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation",
            "\t0590\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation",
        ]
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        assert len(nachrichtenstrukturtabelle.lines) == len(raw_lines)
        assert nachrichtenstrukturtabelle.lines[0].zaehler == "0580"

    def test_parse(self):
        input_file = path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
        (raw_lines, _) = parse_raw_nachrichtenstrukturzeile(input_file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        expected_csv_file = (
            expected_output_dir / EdifactFormatVersion.FV2310 / EdifactFormat.ORDCHG / "nachrichtenstruktur.csv"
        )
        with open(expected_csv_file, encoding="utf-8") as csvfile:
            number_of_lines_in_csv = sum(1 for _ in csvfile) - 1  # excl. header
            assert len(nachrichtenstrukturtabelle.lines) == number_of_lines_in_csv
            csvfile.seek(0)

            reader = csv.DictReader(csvfile)

            for actual_line, expected_line in zip(nachrichtenstrukturtabelle.lines, reader):
                for key, value in expected_line.items():
                    actual_value = getattr(actual_line, key)
                    if value == "":
                        assert actual_value is None
                    else:
                        assert str(actual_value) == value

    def test_to_csv(self, tmp_path):
        input_file = path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
        message_format = EdifactFormat.ORDCHG
        output_dir = tmp_path
        (raw_lines, _) = parse_raw_nachrichtenstrukturzeile(input_file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nachrichtenstrukturtabelle.to_csv(message_format, output_dir)

        file_path = output_dir / Path("nachrichtenstruktur.csv")

        assert file_path.exists()

        reference_file = (
            expected_output_dir / EdifactFormatVersion.FV2310 / EdifactFormat.ORDCHG / "nachrichtenstruktur.csv"
        )

        with open(file_path, "r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            with open(reference_file, "r", encoding="utf-8") as reference_csv:
                reference_reader = csv.DictReader(reference_csv)
                assert reader.fieldnames == reference_reader.fieldnames
                for row, reference_row in zip(reader, reference_reader):
                    assert row == reference_row
