"""
contains CLI logic for migmose.
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


# add CLI logic
@click.command()
@click.option(
    "-i",
    "--input_dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory containing the .docx files",
    help="Set path to directory which contains the .docx files for the migs",
)
@click.option(
    "-mt",
    "--message_type",
    type=click.Choice(["UTILMD", "ORDCHG"], case_sensitive=False),
    prompt="Please specify which message type to be parsed.",
    help="Defines the set of message types to be parsed.",
    multiple=True,
)
@click.option(
    "-o",
    "--output_dir",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory which should contain the output files.",
    help="Set path to directory which contains the output files. If the directory does not exist, it will be created.",
)
def main(input_dir: Path, output_dir, message_type: list[str]) -> None:
    """
    Main function. Uses CLI input.
    """
    dict_files = find_file_to_type(message_type, input_dir)
    for m_type, file in dict_files.items():
        mig_table = parse_raw_nachrichtenstrukturzeile(file)
        for item in mig_table:
            print(item)
        preliminary_output_as_json(mig_table, m_type, output_dir)


def find_file_to_type(message_types: list[str], input_dir: Path) -> dict[str, Path]:
    """
    finds the file with the message type in the input directory
    """
    file_dict = {}
    for message_type in message_types:
        list_of_all_files = [
            file for file in input_dir.iterdir() if message_type in file.name and file.suffix == ".docx"
        ]
        if len(list_of_all_files) == 1:
            file_dict[message_type] = list_of_all_files[0]
        elif len(list_of_all_files) > 1:
            logger.warning(f"⚠️ There are several files for {message_type}.", fg="red")
        else:
            logger.warning(f"⚠️ No file found for {message_type}.", fg="red")
    if file_dict:
        return file_dict
    logger.error("⚠️ No files found in the input directory.", fg="red")
    raise click.Abort()


def preliminary_output_as_json(table: list[str], message_type: str, output_dir: Path) -> None:
    """
    writes the preliminary output as json
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir.joinpath(f"{message_type}_preliminary_output.json")
    structured_json = {line: None for line in table}
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(structured_json, json_file, indent=4, encoding="utf-8")
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
    parses raw nachrichtenstrukturzeile from a table . returns list of raw lines
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


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
