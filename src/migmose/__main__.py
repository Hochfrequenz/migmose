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


if __name__ == "__main__":
    # doc = docx.Document(Path("C:\\GitRepos\\migmose\\unittests\\test_data\\ORDCHG_MIG_1_1_info_20230331_v2.docx"))
    doc = docx.Document(Path("C:\\GitRepos\\migmose\\unittests\\test_data\\UTILMD_MIG_Strom_S1.1_info_20230331.docx"))
    test = get_paragraphs_up_to_diagram(doc)
    mig_tables = []
    for i in test:
        if isinstance(i, Table):
            for ind, testtest in enumerate(i._cells):
                if testtest.text == "Status\tMaxWdh\n\tZähler\tNr\tBez\tSta\tBDEW\tSta\tBDEW\tEbene\tInhalt":
                    print(i._cells[ind + 2].text)
                    mig_tables.extend([row.text for row in i._cells[ind + 2 :]])
                break
    for item in mig_tables:
        if item != "\n":
            print(item)
