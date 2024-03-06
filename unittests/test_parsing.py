"""
Test parsing routines.
"""

from pathlib import Path

from maus.edifact import EdifactFormat

from migmose.parsing import find_file_to_type


class TestParsing:
    """
    Test class for parsing functions.
    """

    def test_find_file_to_type(self):
        message_type = [EdifactFormat.ORDCHG]
        input_dir = Path("unittests/test_data/")
        file_dict = find_file_to_type(message_type, input_dir)
        assert file_dict[message_type[0]] == input_dir / Path("ORDCHG_MIG_1_1_info_20230331_v2.docx")

        # for message_type in message_types:
        #    list_of_all_files = [
        #        file for file in input_dir.iterdir() if message_type in file.name and file.suffix == ".docx"
        #    ]
        #    if len(list_of_all_files) == 1:
        #        file_dict[message_type] = list_of_all_files[0]
        #    elif len(list_of_all_files) > 1:
        #        logger.warning(f"⚠️ There are several files for {message_type}.", fg="red")
        #    else:
        #        logger.warning(f"⚠️ No file found for {message_type}.", fg="red")
        # if file_dict:
        #    return file_dict
        # logger.error("⚠️ No files found in the input directory.", fg="red")
        # raise click.Abort()
