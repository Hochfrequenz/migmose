from pathlib import Path

from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.parsing import parse_raw_nachrichtenstrukturzeile


class TestNestedNachrichtenstruktur:
    """
    A class with pytest unit tests.
    """

    def test_build_segmentgruppen(self):
        file_path = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        raw_lines = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.init_raw_table(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.structure_table(nachrichtenstrukturtabelle)
        assert len(nested_nachrichtenstruktur.segmente) == 5
        assert len(nested_nachrichtenstruktur.segmentgruppen[3].segmentgruppen) == 1
