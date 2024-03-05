from pathlib import Path

from migmose.__main__ import parse_raw_nachrichtenstrukturzeile
from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
from migmose.mig.segmentgruppe import SegmentGruppe


class TestSegmentgruppe:
    """
    A class with pytest unit tests.
    """

    def test_build_segmentgruppen(self):
        file_path = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        raw_lines = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.init_raw_table(raw_lines)
        segmentgruppe, _ = SegmentGruppe.structure_table(nachrichtenstrukturtabelle)
        assert len(segmentgruppe.segmente) == 5
        assert len(segmentgruppe.segmentgruppen[3].segmentgruppen) == 1
