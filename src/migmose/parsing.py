"""
contains functions for file handling and parsing.
"""

import json
from pathlib import Path
from typing import Generator, Union

import click
import docx  # type: ignore[import]
from docx.document import Document  # type: ignore[import]
from docx.oxml import CT_Tbl  # type: ignore[import]
from docx.table import Table, _Cell  # type: ignore[import]
from docx.text.paragraph import Paragraph  # type: ignore[import]
from loguru import logger
from maus.edifact import EdifactFormat


def find_file_to_format(message_formats: list[EdifactFormat], input_dir: Path) -> dict[EdifactFormat, Path]:
    """
    finds the file with the message type in the input directory
    """
    file_dict = {}
    for message_format in message_formats:
        list_of_all_files = [
            file for file in input_dir.iterdir() if message_format in file.name and file.suffix == ".docx"
        ]
        if len(list_of_all_files) == 1:
            file_dict[message_format] = list_of_all_files[0]
        elif len(list_of_all_files) > 1:
            logger.warning(f"⚠️ There are several files for {message_format}.", fg="red")
        else:
            logger.warning(f"⚠️ No file found for {message_format}.", fg="red")
    if file_dict:
        return file_dict
    logger.error("❌ No files found in the input directory.", fg="red")
    raise click.Abort()


def preliminary_output_as_json(table: list[str], message_format: EdifactFormat, output_dir: Path) -> None:
    """
    Writes the preliminary output as json.
    Serves only as a preliminary helper function until more precise class methods are implemented.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir.joinpath(f"{message_format}_preliminary_output.json")
    structured_json = {line: None for line in table}
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(structured_json, json_file, indent=4)
    logger.info(f"Created and wrote to {file_path}")


def get_paragraphs_up_to_diagram(parent: Union[Document, _Cell]) -> Generator[Union[Paragraph, Table], None, None]:
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
    doc = docx.Document(input_path)
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
    mig_tables = [row for row in mig_tables if row not in ("\n", nachrichtenstruktur_header)]
    return mig_tables
