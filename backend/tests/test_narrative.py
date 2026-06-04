"""Narrative arc — the 6 conditional beats (narrative-arc-rules.md)."""
from __future__ import annotations

from app.intake import PetitionInput
from app.generator import build_petition
from tests.helpers import all_text, index_of


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


def test_beats_absent_by_default():
    text = all_text(build_petition(base()))
    assert "Draft Electoral Roll" not in text
    assert "Supplementary" not in text


def test_draft_roll_beat_appears_when_on():
    text = all_text(build_petition(base(on_draft_roll=True, draft_roll_date="19.11.2025")))
    assert "Draft Electoral Roll" in text
    assert "19.11.2025" in text


def test_deletion_beat_carries_impugned_date():
    text = all_text(build_petition(base(deleted=True, deletion_date="27.03.2026")))
    assert "27.03.2026" in text
    assert "deleted" in text.lower()


def test_beats_run_in_chronological_order():
    doc = build_petition(
        base(
            on_draft_roll=True, draft_roll_date="19.11.2025",
            notice_received=True, notice_no="N/12", notice_date="30.12.2025",
            hearing_attended=True, hearing_officer="AERO", hearing_date="15.01.2026",
            under_adjudication=True,
            deleted=True, deletion_date="27.03.2026",
            appeal_filed=True, appeal_no="A/99", appeal_date="04.04.2026",
        )
    )
    order = [
        index_of(doc, "Draft Electoral Roll"),
        index_of(doc, "notice"),
        index_of(doc, "hearing"),
        index_of(doc, "Under Adjudication"),
        index_of(doc, "Supplementary"),
        index_of(doc, "appeal bearing No. A/99"),
    ]
    assert all(i != -1 for i in order), order
    assert order == sorted(order), order
