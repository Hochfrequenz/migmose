"""
contains functions for file handling and parsing.
"""

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import DefaultDict, Generator, Union

import click
import docx
from docx.document import Document
from docx.oxml import CT_Tbl  # type:ignore[attr-defined]
from docx.table import Table, _Cell
from efoli import EdifactFormat, EdifactFormatVersion
from loguru import logger


def find_file_to_format(
    message_formats: list[EdifactFormat], edi_energy_repo: Path, format_version: EdifactFormatVersion
) -> dict[EdifactFormat, Path]:
    """
    finds the file with the message type in the input directory
    """
    input_dir = edi_energy_repo / Path("edi_energy_de") / Path(format_version)
    all_file_dict: DefaultDict[EdifactFormat, list[Path]] = defaultdict(list)
    file_dict: dict[EdifactFormat, Path] = {}
    for message_format in message_formats:
        for file in input_dir.iterdir():
            if "MIG" not in file.name or file.suffix != ".docx":
                continue
            if message_format is EdifactFormat.UTILMDG and "Gas" in file.name:
                all_file_dict[EdifactFormat.UTILMDG].append(file)
            elif message_format is EdifactFormat.UTILMDS and "Strom" in file.name:
                all_file_dict[EdifactFormat.UTILMDS].append(file)
            elif message_format in file.name:
                all_file_dict[message_format].append(file)
        if len(all_file_dict[message_format]) == 0:
            logger.warning(f"⚠️ No file found for {message_format}", fg="red")
            continue
        file_dict[message_format] = get_latest_file(all_file_dict[message_format])
    if file_dict:
        return file_dict
    logger.error("❌ No files found in the input directory.", fg="red")
    raise click.Abort()


_date_pattern = re.compile(r"(\d{8})\.docx$")


def _extract_date(file_path: Path) -> tuple[datetime, Path]:
    # Regex to extract the date format YYYYMMDD from the filename as a string
    match = _date_pattern.search(file_path.name)
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
    try:
        # Define the keywords to filter relevant files
        keywords = ["konsolidiertelesefassungmitfehlerkorrekturen", "außerordentlicheveröffentlichung"]
        files_containing_keywords = [
            path for path in file_list if any(keyword in path.name.lower() for keyword in keywords)
        ]
        # Find the most recent file based on keywords and date suffixes
        if any(files_containing_keywords):
            # Find the most recent file based on keywords and date suffixes
            latest_file = max(
                (path for path in files_containing_keywords),
                key=_get_sort_key,
            )
        else:  # different versions but no kosildierte Lesefassung or außerordentliche Veröffentlichung at all
            latest_file = max(
                (path for path in file_list),
                key=_get_sort_key,
            )

    except ValueError as e:
        logger.error("Error processing file list: {}", e)

    logger.info("Using the latest file: {}", latest_file)
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


_row_regex = re.compile(r"^(?P<left>\t\d+\t)(?P<nr>\d{0,5})(?P<right>\t.*)$")
"""
https://regex101.com/r/vtF07B/2
"""


def _zfill_nr(row_str: str) -> str:
    match = _row_regex.match(row_str)
    if not match:
        return row_str
    left = match.group("left")
    nr = match.group("nr")
    right = match.group("right")
    return f"{left}{nr.zfill(5)}{right}"


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
            # marks the beginning of the complete nachrichtenstruktur table
            if line.text == nachrichtenstruktur_header:
                mig_tables.extend([row.text for row in docx_object._cells[ind + 1 :]])
                break

    # filter empty rows and headers
    mig_tables = [_zfill_nr(row) for row in mig_tables if row not in ("", "\n", nachrichtenstruktur_header)]
    return mig_tables


_pattern = re.compile(
    r"MIG(?:Strom|Gas)?(?:-informatorischeLesefassung)?"
    r"(?P<version>(?:S|G)?(?P<major>\d+)\.(?P<minor>\d+)(?P<suffix>[a-z]?))"
    r"(?:_|KonsolidierteLesefassung|-AußerordentlicheVeröffentlichung)?",
    re.IGNORECASE,
)


def _extract_document_version(path: Path | str) -> tuple[str, int | None, int | None, str]:
    """
    Extracts the document version (major.minor+suffix) details from the given file path.

    Args:
        path (Path | str): The path to the file.
        Example: path/to/file/ORDCHGMIG-informatorischeLesefassung1.1a_99991231_20231001.docx
        -> version: 1.1a, major: 1, minor: 1, suffix: a

    Returns:
        tuple: A tuple containing the document version (str), major version (int or None),
                minor version (int or None), and suffix (str).
    """

    if isinstance(path, str):
        document_str = path
    else:
        document_str = str(path)
    matches = _pattern.search(document_str)
    if matches:
        document_version = matches.group("version")
        major = matches.group("major")
        minor = matches.group("minor")
        suffix = matches.group("suffix")
        if document_version == "":
            logger.warning(f"❌ No document version found in {path}.", fg="red")
        return document_version or "", int(major) or 0, int(minor) or 0, suffix or ""
    logger.error(f"❌ Unexpected document name in {path}.", fg="red")
    return "", None, None, ""


def _get_sort_key(path: Path) -> tuple[int, int, int | None, int | None, str]:
    """
    Extracts the sort key from the given path.

    Args:
        path (Path): The path object to extract the sort key from.
            Example: path/to/file/ORDCHGMIG-informatorischeLesefassung1.1a_99991231_20231001.docx
            with gueltig_von_date: 20231001 and gueltig_bis_date: 99991231, major: 1, minor: 1, suffix: a

    Returns:
        tuple: A tuple containing the "gültig von" date (int),
                "gültig bis" date (int), major version (int or None), minor version (int or None), and suffix (str).
    """
    parts = path.stem.split("_")
    gueltig_von_date = int(parts[-1])
    gueltig_bis_date = int(parts[-2])
    _, major, minor, suffix = _extract_document_version(parts[-3])
    return gueltig_von_date, gueltig_bis_date, major, minor, suffix
