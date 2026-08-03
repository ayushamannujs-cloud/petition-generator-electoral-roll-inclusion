"""Declaration and verification block — Section G of the intake reaches the page.

The form collects `place` and `declaration_date`; before this they were dropped
on the floor and every generated petition printed blanks for both.
"""
from __future__ import annotations

from app.generator import build_petition
from app.intake import PetitionInput
from tests.helpers import para_texts


def minimal_intake(**overrides) -> PetitionInput:
    data = dict(appellant_name="Rehana Bibi Mondal", gender="female")
    data.update(overrides)
    return PetitionInput(**data)


def _verification(doc) -> list[str]:
    return [t for t in para_texts(doc) if t.startswith(("Place:", "Date:"))]


def test_verification_prints_the_supplied_place_and_date():
    lines = _verification(
        build_petition(minimal_intake(place="Kolkata", declaration_date="17.04.2026"))
    )
    assert any("Kolkata" in line for line in lines)
    assert any("17.04.2026" in line for line in lines)


def test_verification_leaves_blanks_when_they_are_not_supplied():
    lines = _verification(build_petition(minimal_intake()))
    assert any(line.startswith("Place: ____") for line in lines)
    assert any(line.startswith("Date: ____") for line in lines)


def test_verification_keeps_the_signature_rule():
    lines = _verification(build_petition(minimal_intake(place="Kolkata")))
    assert any("Signature:" in line for line in lines)
