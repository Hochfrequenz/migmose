from pathlib import Path

from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
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
