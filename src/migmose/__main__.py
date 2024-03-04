"""
contains CLI logic for migmose.
"""

from pathlib import Path
from typing import Generator, Union

import docx
from docx.document import Document
from docx.oxml import CT_P, CT_Tbl
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph


def get_paragraphs_up_to_diagram(parent: Union[Document, _Cell]) -> Generator[Union[Paragraph, Table], None, None]:
    """Goes through paragraphs and tables until a diagram is found"""
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("Passed parent argument must be of type Document or _Cell")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def parse_raw_nachrichtenstrukturzeile(input: Path) -> list[str]:
    """
    parses raw nachrichtenstrukturzeile from a table . returns list of raw lines
    """
    doc = docx.Document(input)
    docx_objects = get_paragraphs_up_to_diagram(doc)
    mig_tables = []
    nachrichtenstruktur_header = "Status\tMaxWdh\n\tZähler\tNr\tBez\tSta\tBDEW\tSta\tBDEW\tEbene\tInhalt"
    for object in docx_objects:
        if isinstance(object, Table):
            for ind, line in enumerate(object._cells):
                # marks the beginning of the complete nachrichtentruktur table
                if line.text == nachrichtenstruktur_header:
                    mig_tables.extend([row.text for row in object._cells[ind + 1 :]])
                break
    # filter empty rows and headers
    mig_tables = [row for row in mig_tables if row != "\n" and row != nachrichtenstruktur_header]
    return mig_tables


if __name__ == "__main__":
    testpath = Path("C:\\GitRepos\\migmose\\unittests\\test_data\\ORDCHG_MIG_1_1_info_20230331_v2.docx")
    # testpath = Path("C:\\GitRepos\\migmose\\unittests\\test_data\\UTILMD_MIG_Strom_S1.1_info_20230331.docx")
    mig_table = parse_raw_nachrichtenstrukturzeile(testpath)
    for item in mig_table:
        print(item)
