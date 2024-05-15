"""
Test parsing routines.
"""

import logging

import pytest
from maus.edifact import EdifactFormat, EdifactFormatVersion
from pytest_loguru.plugin import caplog  # type: ignore[import] # pylint: disable=unused-import

from migmose.edifactformat import ExtendedEdifactFormat
from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile, sanitize_message_format
from unittests import expected_output_dir, path_to_test_edi_energy_mirror_repo, path_to_test_FV2310


class TestParsing:
    """
    Test class for parsing functions.
    """

    def test_find_file_to_format(self):
        """
        Test find_file_to_format function. Tests whether the MIG to edifact format ORDCHG is found in the test folder.
        """
        message_format = [EdifactFormat.ORDCHG]
        file_dict = find_file_to_format(
            message_format, path_to_test_edi_energy_mirror_repo, EdifactFormatVersion.FV2310
        )
        assert (
            file_dict[EdifactFormat.ORDCHG]
            == path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
        )

    def test_find_only_one_file(self, caplog):
        """
        Tests to find multiple formats when one is not present.
        """
        message_formats = [EdifactFormat.ORDCHG, EdifactFormat.ORDRSP]
        with caplog.at_level(logging.WARNING):
            file_dict = find_file_to_format(
                message_formats, path_to_test_edi_energy_mirror_repo, EdifactFormatVersion.FV2310
            )
            assert f"No file found for {EdifactFormat.ORDRSP}." in caplog.text
            assert (
                file_dict[EdifactFormat.ORDCHG]
                == path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
            )

    def test_find_only_one_file_multiple_docx(self):
        """
        Tests to find multiple docx files with the same message_format.
        """
        message_formats = [EdifactFormat.IFTSTA]
        file_dict = find_file_to_format(
            message_formats, path_to_test_edi_energy_mirror_repo, EdifactFormatVersion.FV2310
        )
        assert (
            file_dict[EdifactFormat.IFTSTA]
            == path_to_test_FV2310
            / "IFTSTAMIG-informatorischeLesefassung2.0emitFehlerkorrekturenStand11.03.2024_99991231_20240311.docx"
        )

    def test_parse_raw_nachrichtenstrukturzeile(self):
        """
        Test to parse the raw nachrichtenstrukturzeile from a docx file.
        """
        input_file = path_to_test_FV2310 / "ORDCHGMIG-informatorischeLesefassung1.1_99991231_20231001.docx"
        mig_table = parse_raw_nachrichtenstrukturzeile(input_file)
        expected_csv_file = (
            expected_output_dir / EdifactFormatVersion.FV2310 / EdifactFormat.ORDCHG / "nachrichtenstruktur.csv"
        )
        with open(expected_csv_file, encoding="utf-8") as csvfile:
            number_of_lines_in_csv = sum(1 for _ in csvfile) - 1  # excl. header
            assert len(mig_table) == number_of_lines_in_csv
            csvfile.seek(0)
            next(csvfile)
            for actual_line, expected_line in zip(mig_table, csvfile):
                assert actual_line.replace("\t", "") == expected_line.strip().replace(",", "")

    @pytest.mark.parametrize(
        "message_format, format_version, expected_output",
        [
            pytest.param(
                [
                    ExtendedEdifactFormat.UTILMD,
                    ExtendedEdifactFormat.UTILMDS,
                ],
                EdifactFormatVersion.FV2310,
                [ExtendedEdifactFormat.UTILMDG, ExtendedEdifactFormat.UTILMDS],
                id="FV2310",
            ),
            pytest.param(
                [ExtendedEdifactFormat.UTILMD, ExtendedEdifactFormat.UTILMDG, ExtendedEdifactFormat.UTILMDS],
                EdifactFormatVersion.FV2304,
                [ExtendedEdifactFormat.UTILMD],
                id="FV2304",
            ),
            pytest.param(
                [ExtendedEdifactFormat.IFTSTA],
                EdifactFormatVersion.FV2310,
                [ExtendedEdifactFormat.IFTSTA],
                id="FV2310 no UTILMD",
            ),
            pytest.param(
                [ExtendedEdifactFormat.IFTSTA],
                EdifactFormatVersion.FV2304,
                [ExtendedEdifactFormat.IFTSTA],
                id="FV2304 no UTILMD",
            ),
        ],
    )
    def test_sanitize_message_format(
        self,
        message_format: list[ExtendedEdifactFormat],
        format_version: EdifactFormatVersion,
        expected_output: list[ExtendedEdifactFormat],
    ):
        message_format = sanitize_message_format(message_format, format_version)
        assert message_format == expected_output
