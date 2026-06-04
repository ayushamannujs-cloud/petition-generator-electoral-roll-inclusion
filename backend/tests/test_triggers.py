"""Triggered law (4b) — only when its dependent particular (3b) holds."""
from __future__ import annotations

from app.intake import PetitionInput
from app.generator import build_petition
from tests.helpers import all_text


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


def test_passport_unlocks_passports_act():
    off = all_text(build_petition(base(has_passport=False)))
    assert "Passports Act" not in off

    on = all_text(build_petition(base(has_passport=True, passport_no="Z1234567")))
    assert "Passports Act, 1967" in on
    assert "Z1234567" in on


def test_2002_mapping_with_aadhaar_unlocks_motab_shaikh_and_adr():
    text = all_text(
        build_petition(base(mapped_2002_sir=True, has_aadhaar=True, aadhaar_no="1111 2222 3333"))
    )
    assert "Motab Shaikh" in text
    assert "ADR" in text
    # authorities-rules.md §4b rule 2: the citation states its own trigger.
    assert "2002" in text and "Aadhaar" in text


def test_2002_mapping_without_aadhaar_does_not_unlock():
    text = all_text(build_petition(base(mapped_2002_sir=True, has_aadhaar=False)))
    assert "Motab Shaikh" not in text


def test_aadhaar_without_2002_mapping_does_not_unlock():
    text = all_text(build_petition(base(mapped_2002_sir=False, has_aadhaar=True)))
    assert "Motab Shaikh" not in text
