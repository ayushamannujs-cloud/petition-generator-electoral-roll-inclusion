"""GROUNDS and SUBMISSIONS — counsel's markup asked for these to be separated.

    "Write grounds as a separately - 3/4 grounds briefly. Why your prayers
     should be allowed - violation of PNJ - violation of art 14- right to vote-
     non communication of order - non application of mind - incorrectly excluded
     even though there were sufficient documents to establish... etc."
    "... First state facts then go into submissions."

So: facts, then a short headed GROUNDS section, then SUBMISSIONS — all sharing
the one arabic run.
"""
from __future__ import annotations

from app.generator import build_petition
from app.intake import PetitionInput
from tests.helpers import all_text, numbered_paragraphs, para_texts


def minimal_intake(**overrides) -> PetitionInput:
    data = dict(
        appellant_name="Rehana Bibi Mondal",
        guardian_name="Abdul Karim Mondal",
        gender="female",
    )
    data.update(overrides)
    return PetitionInput(**data)


def test_grounds_are_a_headed_section():
    assert "GROUNDS" in para_texts(build_petition(minimal_intake()))


def test_grounds_state_the_four_counsel_asked_for():
    text = all_text(build_petition(minimal_intake()))
    assert "principles of natural justice" in text
    assert "Articles 14 and 21" in text
    assert "non-application of mind" in text
    assert "sufficient documents" in text


def test_submissions_are_a_headed_section_after_the_grounds():
    texts = para_texts(build_petition(minimal_intake()))
    assert "SUBMISSIONS" in texts
    assert texts.index("GROUNDS") < texts.index("SUBMISSIONS")


def test_submissions_carry_the_standing_argument():
    text = all_text(build_petition(minimal_intake()))
    assert "bona fide Indian citizen" in text


def test_continuous_residence_is_dated_when_the_year_is_pleaded():
    absent = all_text(build_petition(minimal_intake(district="Kolkata")))
    assert "continuous resident of Kolkata," in absent

    present = all_text(
        build_petition(minimal_intake(district="Kolkata", continuous_resident_since="2007"))
    )
    assert "continuous resident of Kolkata since 2007" in present


def test_draft_roll_submission_fires_only_when_the_draft_roll_is_pleaded():
    absent = all_text(build_petition(minimal_intake()))
    assert "duly included in the draft roll" not in absent
    present = all_text(
        build_petition(minimal_intake(on_draft_roll=True, draft_roll_date="19.11.2025"))
    )
    assert "duly included in the draft roll" in present


def test_hearing_submission_fires_only_when_the_hearing_is_pleaded():
    absent = all_text(build_petition(minimal_intake()))
    assert "to their satisfaction" not in absent
    present = all_text(
        build_petition(
            minimal_intake(hearing_attended=True, hearing_officer="the AERO, Entally")
        )
    )
    assert "to their satisfaction" in present


def test_grounds_continue_the_same_arabic_run_as_the_facts():
    numbered = numbered_paragraphs(build_petition(minimal_intake()))
    numbers = [n for n, _ in numbered]
    assert numbers == list(range(1, len(numbers) + 1))
    # The PNJ ground is numbered, and numbered after the last fact.
    entitlement = next(i for i, (_, t) in enumerate(numbered) if "disqualified" in t)
    pnj = next(i for i, (_, t) in enumerate(numbered) if "natural justice" in t)
    assert entitlement < pnj
