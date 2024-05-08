import json
from pathlib import Path

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur
from migmose.parsing import parse_raw_nachrichtenstrukturzeile


class TestReducedNestedNachrichtenstruktur:
    """test class for create_reduced_nested_nachrichtenstruktur"""

    input_data = NestedNachrichtenstruktur(
        header_linie=None,
        segmente=[
            NachrichtenstrukturZeile(
                zaehler="101",
                bezeichnung="SG1",
                bdew_status="D",
                nr=None,
                ebene=0,
                inhalt="None",
                standard_status="M",
                standard_maximale_wiederholungen=1,
                bdew_maximale_wiederholungen=1,
            ),
            NachrichtenstrukturZeile(
                zaehler="101",
                bezeichnung="SG1",
                bdew_status="R",
                nr=None,
                ebene=0,
                inhalt="None",
                standard_status="M",
                standard_maximale_wiederholungen=1,
                bdew_maximale_wiederholungen=1,
            ),
            NachrichtenstrukturZeile(
                zaehler="102",
                bezeichnung="SG2",
                bdew_status="S",
                nr=None,
                ebene=0,
                inhalt="None",
                standard_status="M",
                standard_maximale_wiederholungen=1,
                bdew_maximale_wiederholungen=1,
            ),
        ],
        segmentgruppen=[
            NestedNachrichtenstruktur(
                header_linie=NachrichtenstrukturZeile(
                    zaehler="201",
                    bezeichnung="SG5",
                    bdew_status="D",
                    nr=None,
                    ebene=0,
                    inhalt="None",
                    standard_status="M",
                    standard_maximale_wiederholungen=1,
                    bdew_maximale_wiederholungen=1,
                ),
                segmente=[
                    NachrichtenstrukturZeile(
                        zaehler="103",
                        bezeichnung="SG3",
                        bdew_status="S",
                        nr=None,
                        ebene=1,
                        inhalt="None",
                        standard_status="M",
                        standard_maximale_wiederholungen=1,
                        bdew_maximale_wiederholungen=1,
                    ),
                ],
                segmentgruppen=[],
            ),
            NestedNachrichtenstruktur(
                header_linie=NachrichtenstrukturZeile(
                    zaehler="201",
                    bezeichnung="SG5",
                    bdew_status="D",
                    nr=None,
                    ebene=0,
                    inhalt="None",
                    standard_status="M",
                    standard_maximale_wiederholungen=1,
                    bdew_maximale_wiederholungen=1,
                ),
                segmente=[
                    NachrichtenstrukturZeile(
                        zaehler="103",
                        bezeichnung="SG3",
                        bdew_status="S",
                        nr=None,
                        ebene=1,
                        inhalt="None",
                        standard_status="M",
                        standard_maximale_wiederholungen=1,
                        bdew_maximale_wiederholungen=1,
                    ),
                    NachrichtenstrukturZeile(
                        zaehler="107",
                        bezeichnung="SG7",
                        bdew_status="S",
                        nr=None,
                        ebene=1,
                        inhalt="None",
                        standard_status="M",
                        standard_maximale_wiederholungen=1,
                        bdew_maximale_wiederholungen=1,
                    ),
                ],
                segmentgruppen=[],
            ),
        ],
    )

    def test_create_reduced_nested_nachrichtenstruktur(self, tmp_path):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        file_path = Path(
            "unittests/test_data/IFTSTAMIG-informatorischeLesefassung2.0emitFehlerkorrekturenStand11.03.2024_99991231_20240311.docx"
        )
        raw_lines = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        reduced_nested_nachrichtenstruktur = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(
            nested_nachrichtenstruktur
        )
        reduced_nested_nachrichtenstruktur.to_json("IFTSTA", tmp_path)
        with open(tmp_path / "IFTSTA_reduced_nested_nachrichtenstruktur.json", "r", encoding="utf-8") as file1:
            actual_reduced_nested_json = json.load(file1)
            with open(
                Path("unittests/test_data/IFTSTA_reduced_nested_nachrichtenstruktur.json"), "r", encoding="utf-8"
            ) as file2:
                expected_reduced_nested_json = json.load(file2)
                assert actual_reduced_nested_json == expected_reduced_nested_json
