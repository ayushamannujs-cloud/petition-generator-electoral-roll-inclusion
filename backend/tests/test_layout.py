"""Placement — measured off the settled petition's line geometry.

All offsets are from the left text margin (1.5"). From the PDF:

    cause title / parties / prayer   right-hand column at +2.75"
    facts        number at +0",  wraps to +0.25"   (hanging indent)
    submissions  number at +0",  text at +0.5",  wraps to +0.25"
    prayers      letter at column +0",  wraps to column +0.25"
"""
from __future__ import annotations

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

from app.generator import build_petition
from app.intake import PetitionInput
from app.preview import render_html

RIGHT_COLUMN = Inches(2.75)
HANGING = Inches(0.25)


def minimal_intake(**overrides) -> PetitionInput:
    data = dict(appellant_name="Rehana Bibi Mondal", gender="female")
    data.update(overrides)
    return PetitionInput(**data)


def _find(doc, needle):
    return next(p for p in doc.paragraphs if needle in p.text)


def test_cause_title_block_sits_in_the_right_hand_column():
    doc = build_petition(minimal_intake())
    assert _find(doc, "IN THE MATTER OF").paragraph_format.left_indent == RIGHT_COLUMN


def test_versus_is_centred_within_the_column_not_the_page():
    versus = _find(build_petition(minimal_intake()), "VERSUS")
    assert versus.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert versus.paragraph_format.left_indent == RIGHT_COLUMN


def test_fact_paragraphs_hang_from_the_margin():
    fact = _find(build_petition(minimal_intake()), "permanent resident")
    fmt = fact.paragraph_format
    assert fmt.left_indent == HANGING
    assert fmt.first_line_indent == -HANGING


def test_submissions_set_their_text_deeper_than_the_facts():
    submission = _find(build_petition(minimal_intake()), "bona fide Indian citizen")
    assert "\t" in submission.text
    positions = [t.position for t in submission.paragraph_format.tab_stops]
    assert Inches(0.5) in positions


def test_prayer_block_sits_in_the_right_hand_column():
    doc = build_petition(minimal_intake())
    assert _find(doc, "most humbly prays").paragraph_format.left_indent == RIGHT_COLUMN
    relief = next(p for p in doc.paragraphs if p.text.strip().startswith("(a)"))
    assert relief.paragraph_format.left_indent == RIGHT_COLUMN + HANGING
    assert relief.paragraph_format.first_line_indent == -HANGING


def test_declaration_heading_is_letter_spaced():
    assert "D E C L A R A T I O N" in [
        p.text.strip() for p in build_petition(minimal_intake()).paragraphs
    ]


def test_preview_carries_indentation_from_the_document():
    # The preview must inherit geometry rather than guess at it, or it will tell
    # the volunteer the petition looks fine when the .docx does not.
    html = render_html(minimal_intake())
    # Proportional to the 5.77" text column, not absolute: the preview pane is
    # narrower than A4, so 2.75" of indent would swallow it. 2.75/5.77 = 47.68%.
    assert "margin-left:47.68%" in html  # right-hand column
    assert "margin-left:4.33%;text-indent:-4.33%" in html  # hanging numbers
