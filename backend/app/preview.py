"""Render the petition as HTML for live preview.

Reuses `build_petition` and walks the produced document in document order, so the
preview is exactly the content of the downloadable .docx — never a second copy
of the wording.
"""
from __future__ import annotations

from html import escape

from docx.document import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.generator import build_petition
from app.intake import PetitionInput

_ALIGN_CLASS = {
    WD_ALIGN_PARAGRAPH.CENTER: "center",
    WD_ALIGN_PARAGRAPH.RIGHT: "right",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
    WD_ALIGN_PARAGRAPH.LEFT: "left",
}


def _iter_blocks(doc: Document):
    """Yield Paragraph and Table objects in document order."""
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def _paragraph_html(p: Paragraph) -> str:
    text = escape(p.text)
    if not text.strip():
        return ""
    cls = _ALIGN_CLASS.get(p.alignment, "left")
    bold = any(r.bold for r in p.runs)
    inner = f"<strong>{text}</strong>" if bold else text
    return f'<p class="{cls}">{inner}</p>'


def _table_html(t: Table) -> str:
    rows = []
    for ri, row in enumerate(t.rows):
        tag = "th" if ri == 0 else "td"
        cells = "".join(f"<{tag}>{escape(c.text)}</{tag}>" for c in row.cells)
        rows.append(f"<tr>{cells}</tr>")
    return '<table class="doc-table">' + "".join(rows) + "</table>"


def render_html(intake: PetitionInput) -> str:
    doc = build_petition(intake)
    parts: list[str] = []
    for block in _iter_blocks(doc):
        if isinstance(block, Paragraph):
            parts.append(_paragraph_html(block))
        else:
            parts.append(_table_html(block))
    return '<div class="petition">' + "".join(p for p in parts if p) + "</div>"
