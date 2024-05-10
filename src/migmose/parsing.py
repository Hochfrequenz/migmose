"""
contains functions for file handling and parsing.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Generator, Union

import click
import docx
from docx.document import Document
from docx.oxml import CT_Tbl
from docx.table import Table, _Cell
from loguru import logger
from maus.edifact import EdifactFormat


def find_file_to_format(
    message_formats: list[EdifactFormat], edi_energy_repo: Path, format_version
) -> dict[EdifactFormat, Path]:
    """
    finds the file with the message type in the input directory
    """
    input_dir = edi_energy_repo / Path("edi_energy_de") / Path(format_version)
    file_dict: dict[EdifactFormat, Path] = {}
    for message_format in message_formats:
        list_of_all_files: list[Path] = [
            file
            for file in input_dir.iterdir()
            if message_format in file.name and "MIG" in file.name and file.suffix == ".docx"
        ]

        if len(list_of_all_files) == 1:
            file_dict[message_format] = list_of_all_files[0]
        elif len(list_of_all_files) > 1:
            file_dict[message_format] = get_latest_file(list_of_all_files)
        else:
            logger.warning(f"⚠️ No file found for {message_format}.", fg="red")
    if file_dict:
        return file_dict
    logger.error("❌ No files found in the input directory.", fg="red")
    raise click.Abort()


def get_latest_file(file_list: list[Path]) -> Path:
    """
    This function takes a list of docx files Path
    and returns the Path of the latest MIG docx file based on the timestamp in its name.
    The timestamp is assumed to be formatted as YYYYMMDD and located just before the ".docx" extension.

    Parameters:
        file_list (list of Path): A list containing file paths with timestamps.

    Returns:
        Path: The path of the latest file. Returns None if no valid date is found.
    """

    def extract_date(file_path: Path) -> tuple[datetime, Path]:
        # Regex to extract the date format YYYYMMDD from the filename as a string
        match = re.search(r"(\d{8})\.docx$", file_path.name)
        if match:
            # Return the date as a datetime object for comparison and the path for use
            return datetime.strptime(match.group(1), "%Y%m%d"), file_path
        logger.warning(
            f"⚠️ No timestamp in filename found in {file_path}."
            + "in case of multiple docx files in this path, it must be a "
            + "timestamp with format 'yyyyMMdd.docx' in filename.",
            fg="red",
        )
        raise click.Abort()

    # Initialize variables to keep track of the latest file and date
    latest_file: Path
    latest_date: datetime | None = None

    for file_path in file_list:
        date, path = extract_date(file_path)
        if latest_date is None or date > latest_date:
            latest_file = path
            latest_date = date

    # Return the path of the file with the latest date
    return latest_file


def get_paragraphs_up_to_diagram(parent: Union[Document, _Cell]) -> Generator[Table, None, None]:
    """Goes through paragraphs and tables"""
    # pylint: disable=protected-access
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("Passed parent argument must be of type Document or _Cell")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_Tbl):
            yield Table(child, parent)


def parse_raw_nachrichtenstrukturzeile(input_path: Path) -> list[str]:
    """
    parses raw nachrichtenstrukturzeile from a table. returns list of raw lines
    """
    # pylint: disable=protected-access
    doc = docx.Document(str(input_path.absolute()))
    docx_objects = get_paragraphs_up_to_diagram(doc)
    mig_tables = []
    nachrichtenstruktur_header = "Status\tMaxWdh\n\tZähler\tNr\tBez\tSta\tBDEW\tSta\tBDEW\tEbene\tInhalt"
    for docx_object in docx_objects:
        for ind, line in enumerate(docx_object._cells):
            # marks the beginning of the complete nachrichtentruktur table
            if line.text == nachrichtenstruktur_header:
                mig_tables.extend([row.text for row in docx_object._cells[ind + 1 :]])
            break
    # filter empty rows and headers
    mig_tables = [row for row in mig_tables if row not in ("", "\n", nachrichtenstruktur_header)]
    return mig_tables
