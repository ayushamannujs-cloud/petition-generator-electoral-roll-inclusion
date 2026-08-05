"""Relatives switch, hardship cascade, and conditional reliefs."""
from __future__ import annotations

from app.intake import PetitionInput
from app.generator import build_petition
from tests.helpers import all_text


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


def test_relatives_block_closes_with_the_corroboration_argument():
    # Settled ¶11 follows the (a)-(e) list with prose drawing the inference.
    text = all_text(
        build_petition(base(relatives_on_roll=[{"name": "Nasima Khatun", "relationship": "Brother"}]))
    )
    assert "The presence of the above relatives" in text
    assert "resided in India and West Bengal continuously" in text
    assert "unjustified and untenable in law" in text


def test_no_corroboration_argument_without_relatives():
    assert "The presence of the above relatives" not in all_text(build_petition(base()))


def test_restoration_prayer_names_where_on_the_roll():
    # Settled prayer (b) identifies the constituency, part and serial number —
    # a direction to "restore the name" is unenforceable without them.
    doc = build_petition(
        base(constituency_no="163", constituency_name="Entally", part_or_serial_no="161/146")
    )
    relief = next(p.text for p in doc.paragraphs if p.text.strip().startswith("(b)"))
    assert "163" in relief
    assert "Entally" in relief
    assert "161/146" in relief


def test_restoration_prayer_falls_back_to_blanks():
    relief = next(
        p.text for p in build_petition(base()).paragraphs if p.text.strip().startswith("(b)")
    )
    assert "____" in relief


def test_relatives_table_and_argument_appear():
    doc = build_petition(
        base(relatives_on_roll=[
            {"name": "Ramesh Chandra Das", "relationship": "Father", "epic_no": "XYZ9999999"},
        ])
    )
    text = all_text(doc)
    assert "Ramesh Chandra Das" in text
    assert "XYZ9999999" in text
    assert any(t.text == "Relationship" for tbl in doc.tables for r in tbl.rows for t in r.cells)
    assert "citizenship" in text.lower()


def test_no_relatives_means_no_table():
    doc = build_petition(base())
    assert len(doc.tables) == 0


def test_hardship_injects_pnj_and_unlocks_compensation():
    text = all_text(
        build_petition(base(hardship="elderly and unwell", relief_compensation=True))
    )
    assert "elderly and unwell" in text
    assert "compensation" in text.lower()
    assert "mental agony" in text.lower()


def test_default_reliefs_present_and_lettered():
    text = all_text(build_petition(base()))
    assert "Set aside" in text
    assert "restore" in text.lower()
    assert "interim" in text.lower()
    # compensation off by default
    assert "compensation" not in text.lower()


def test_residuary_relief_is_always_lettered_last():
    text = all_text(build_petition(base(relief_compensation=True, hardship="ill")))
    residuary = "Pass such further or other order(s)"
    comp = "compensation"
    assert text.lower().index(comp) < text.index(residuary)
