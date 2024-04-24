import unittest

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur


class TestReducedNestedNachrichtenstruktur(unittest.IsolatedAsyncioTestCase):
    """test class for create_reduced_nested_nachrichtenstruktur"""

    def setUp(self) -> None:
        self.input_data = ReducedNestedNachrichtenstruktur(
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
                ReducedNestedNachrichtenstruktur(
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
                )
            ],
        )

    def test_create_reduced_nested_nachrichtenstruktur(self):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        expected_output = ReducedNestedNachrichtenstruktur(
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
                ReducedNestedNachrichtenstruktur(
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
                )
            ],
        )

        output = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(self.input_data)

        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
