"""Typography & page geometry — scaffold-rules.md §1-4."""
from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from app.intake import PetitionInput
from app.generator import build_petition


def _intake() -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female")


def _find(doc, needle):
    return next(p for p in doc.paragraphs if needle in p.text)


def test_page_is_a4_with_asymmetric_margins():
    sec = build_petition(_intake()).sections[0]
    # A4 portrait.
    assert round(sec.page_width.mm) == 210
    assert round(sec.page_height.mm) == 297
    # Left & top get the extra half-inch (1.5"); right & bottom 1".
    assert sec.left_margin == Inches(1.5)
    assert sec.top_margin == Inches(1.5)
    assert sec.right_margin == Inches(1)
    assert sec.bottom_margin == Inches(1)


def test_body_font_is_bookman_12pt():
    fact = _find(build_petition(_intake()), "That the Appellant")
    run = fact.runs[0]
    assert run.font.name == "Bookman Old Style"
    assert run.font.size == Pt(12)


def test_headings_centered_body_justified():
    doc = build_petition(_intake())
    forum = _find(doc, "BEFORE THE HON'BLE")
    fact = _find(doc, "That the Appellant")
    assert forum.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert fact.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY


def test_party_tags_right_aligned():
    doc = build_petition(_intake())
    appellant_tag = _find(doc, "………. Appellant")
    assert appellant_tag.alignment == WD_ALIGN_PARAGRAPH.RIGHT


def test_body_line_spacing_is_one_and_half():
    fact = _find(build_petition(_intake()), "That the Appellant")
    assert fact.paragraph_format.line_spacing == 1.5
