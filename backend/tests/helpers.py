"""Shared test helpers for reading back generated petitions."""
from __future__ import annotations

import re

from docx.document import Document

_NUMBERED = re.compile(r"^(\d+)\.\s")


def _run(doc: Document, stop_at: tuple[str, ...]) -> list[tuple[int, str]]:
    """Walk the arabic run, from the SHEWETH opener until one of `stop_at`.

    Starting at SHEWETH matters: the respondent list above it carries its own
    1./2./3. and would otherwise be read as part of the run.
    """
    out: list[tuple[int, str]] = []
    started = False
    for p in doc.paragraphs:
        text = p.text.strip()
        if text.startswith("MOST RESPECTFULLY SHEWETH"):
            started = True
            continue
        if not started:
            continue
        if any(text.startswith(marker) for marker in stop_at):
            break
        match = _NUMBERED.match(text)
        if match:
            out.append((int(match.group(1)), text))
    return out


def numbered_paragraphs(doc: Document) -> list[tuple[int, str]]:
    """(number, text) for every numbered paragraph — facts, grounds, submissions."""
    return _run(doc, ("ENCLOSURES:",))


def numbered_facts(doc: Document) -> list[tuple[int, str]]:
    """Just the facts portion. Assert on this when a test is about the facts, so
    that adding standing grounds or submissions cannot break it."""
    return _run(doc, ("GROUNDS", "ENCLOSURES:"))


def all_text(doc: Document) -> str:
    """Flatten every paragraph (body + tables) into one newline-joined string."""
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.extend(p.text for p in cell.paragraphs)
    return "\n".join(parts)


def para_texts(doc: Document) -> list[str]:
    """Ordered list of non-empty body paragraph texts."""
    return [p.text for p in doc.paragraphs if p.text.strip()]


def index_of(doc: Document, needle: str) -> int:
    """Index of the first body paragraph containing needle, else -1."""
    for i, p in enumerate(doc.paragraphs):
        if needle in p.text:
            return i
    return -1
