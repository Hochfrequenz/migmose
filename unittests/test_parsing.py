"""
Test parsing routines.
"""

import json
import logging
from pathlib import Path

from maus.edifact import EdifactFormat
from pytest_loguru.plugin import caplog  # type: ignore[import] # pylint: disable=unused-import

from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile, preliminary_output_as_json


class TestParsing:
    """
    Test class for parsing functions.
    """

    def test_find_file_to_format(self):
        """
        Test find_file_to_format function. Tests whether the MIG to edifact format ORDCHG is found in the test folder.
        """
        message_format = [EdifactFormat.ORDCHG]
        input_dir = Path("unittests/test_data/")
        file_dict = find_file_to_format(message_format, input_dir)
        assert file_dict[EdifactFormat.ORDCHG] == input_dir / Path("ORDCHG_MIG_1_1_info_20230331_v2.docx")

    def test_find_only_one_file(self, caplog):
        """
        Tests to find multiple formats when one is not present.
        """
        message_formats = [EdifactFormat.ORDCHG, EdifactFormat.ORDRSP]
        input_dir = Path("unittests/test_data/")
        with caplog.at_level(logging.WARNING):
            file_dict = find_file_to_format(message_formats, input_dir)
            assert f"No file found for {EdifactFormat.ORDRSP}." in caplog.text
            assert file_dict[EdifactFormat.ORDCHG] == input_dir / Path("ORDCHG_MIG_1_1_info_20230331_v2.docx")

    def test_parse_raw_nachrichtenstrukturzeile(self):
        """
        Test to parse the raw nachrichtenstrukturzeile from a docx file.
        """
        input_file = Path("unittests/test_data/ORDCHG_MIG_1_1_info_20230331_v2.docx")
        mig_table = parse_raw_nachrichtenstrukturzeile(input_file)
        assert len(mig_table) == 18
        assert "Nachrichten-Kopfsegment" in mig_table[0]
        assert "Nachrichten-Endesegment" in mig_table[-1]

    def test_preliminary_output_as_json(self, tmp_path):
        """Tests the preliminary output as json function.
        Asserts that the outputfile exists and has the correct content."""
        table = ["line1", "line2", "line3"]
        message_format = EdifactFormat.ORDCHG
        output_dir = tmp_path / Path("output")

        preliminary_output_as_json(table, message_format, output_dir)

        file_path = output_dir / f"{message_format}_preliminary_output.json"
        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as json_file:
            content = json.load(json_file)
            assert content == {"line1": None, "line2": None, "line3": None}
