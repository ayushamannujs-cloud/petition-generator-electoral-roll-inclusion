"""Relatives switch, hardship cascade, and conditional reliefs."""
from __future__ import annotations

from app.intake import PetitionInput
from app.generator import build_petition
from tests.helpers import all_text


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


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
