import os

import docx
from django.conf import settings
from docx.api import Document
from docx.document import Document as _Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell, _Row
from docx.text.paragraph import Paragraph

PROPOSAL_DOC_TEMPLATE = os.path.join(
    settings.BASE_DIR,
    'rational',
    'doc_templates',
    'proposal_template.docx'
)


def iter_block_items(parent):
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    elif isinstance(parent, _Row):
        parent_elm = parent._tr
    else:
        raise ValueError("something's not right")
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def replace_text(valve_dict, block):
    for k, v in valve_dict.items():
        for run in block.runs:
            if k in run.text:
                new_text = run.text.replace(k, v)
                run.text = new_text


def create_doc(params_dict):
    doc = docx.Document(PROPOSAL_DOC_TEMPLATE)
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            replace_text(params_dict, block)
        elif isinstance(block, Table):
            for row in block.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_text(params_dict, paragraph)
    return doc
