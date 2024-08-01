"""
Test parsing routines.
"""

import logging
from pathlib import Path

import pytest
from efoli import EdifactFormat, EdifactFormatVersion
from pytest_loguru.plugin import caplog  # type: ignore[import-untyped] # pylint: disable=unused-import

from migmose.parsing import _extract_document_version, find_file_to_format, parse_raw_nachrichtenstrukturzeile
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
            assert "⚠️ No file found for ORDRSP" in caplog.text
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

    # pylint: disable=line-too-long
    @pytest.mark.parametrize(
        "file_path",
        [
            pytest.param(
                Path("edi_energy_de/FV2310/REQOTEMIG-informatorischeLesefassung1.3_20250403_20231001.docx"),
                id="REQOTE",
            ),
            pytest.param(
                Path(
                    "edi_energy_de/FV2310/UTILMDMIGStrom-informatorischeLesefassungS1.1-AußerordentlicheVeröffentlichung_20231022_20231001.docx"
                ),
                id="UTILMDS",
            ),
            pytest.param(
                Path(
                    "edi_energy_de/FV2310/UTILMDMIGGas-informatorischeLesefassungG1.0aKonsolidierteLesefassungmitFehlerkorrekturenStand12.12.2023_99991231_20231212.docx"
                ),
                id="UTILMDG",
            ),
            pytest.param(
                Path(
                    "edi_energy_de/FV2310/IFTSTAMIG-informatorischeLesefassung-AußerordentlicheVeröffentlichung_20231022_20231001.docx"
                ),
                id="IFTSTA",
            ),
            pytest.param(
                Path("edi_energy_de/FV2310/REMADVMIG-informatorischeLesefassung2.9b_20240402_20231001.docx"),
                id="REMADV",
            ),
        ],
    )
    def test_extract_document_version(self, file_path: Path, snapshot):
        assert _extract_document_version(file_path) == snapshot
