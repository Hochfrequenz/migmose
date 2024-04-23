import unittest

from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur


class TestReducedNestedNachrichtenstruktur(unittest.IsolatedAsyncioTestCase):
    """test class for create_reduced_nested_nachrichtenstruktur"""

    def setUp(self) -> None:
        self.input_data = {
            "header_linie": None,
            "segmente": [
                {"zaehler": "101", "bezeichnung": "Segment1", "bdew_status": "D"},
                {"zaehler": "101", "bezeichnung": "Segment1", "bdew_status": "R"},
                {"zaehler": "102", "bezeichnung": "Segment2"},
            ],
            "segmentgruppen": [
                {
                    "header_linie": {"zaehler": "201", "bezeichnung": "SegmentGroup1"},
                    "segmente": [{"zaehler": "103", "bezeichnung": "Segment3"}],
                }
            ],
        }

    def test_create_reduced_nested_nachrichtenstruktur(self):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        expected_output = {
            "header_linie": None,
            "segmente": [
                {"zaehler": "101", "bezeichnung": "Segment1", "bdew_status": "D"},
                {"zaehler": "102", "bezeichnung": "Segment2"},
            ],
            "segmentgruppen": [
                {
                    "header_linie": {"zaehler": "201", "bezeichnung": "SegmentGroup1"},
                    "segmente": [{"zaehler": "103", "bezeichnung": "Segment3"}],
                    "segmentgruppen": [],
                }
            ],
        }

        output = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(
            json_nachrichten_struktur=self.input_data
        )

        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
