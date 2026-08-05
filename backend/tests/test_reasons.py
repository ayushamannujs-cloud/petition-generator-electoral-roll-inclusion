"""Deletion reasons — why the roll and the appellant's documents disagree.

A multi-select, like the documents held: name mismatch (appellant or father),
address change (marriage or plain transfer), or free-text other. Each reason
composes into the facts and, where it carries legal weight, fires a ground.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.generator import build_petition
from app.intake import PetitionInput
from tests.helpers import all_text, numbered_facts, numbered_paragraphs


def minimal_intake(**overrides) -> PetitionInput:
    data = dict(
        appellant_name="Rehana Bibi Mondal",
        guardian_name="Abdul Karim Mondal",
        gender="female",
    )
    data.update(overrides)
    return PetitionInput(**data)


def married_intake(**overrides) -> PetitionInput:
    data = dict(
        address="Ward 42, Kolkata",
        address_changed=True,
        address_change_reason="marriage",
        previous_address="Bankura",
        spouse_name="Sirajul Islam",
        marriage_date="1st January 2010",
        previous_constituency="Example (SC) - 100",
        registered_since="2016",
    )
    data.update(overrides)
    return minimal_intake(**data)


def test_appellant_name_mismatch_is_recorded_in_the_identity_paragraph():
    identity = numbered_paragraphs(
        build_petition(
            minimal_intake(
                mismatch_appellant_name=True, name_on_roll="Rehana Bibi Mandal"
            )
        )
    )[1][1]
    assert "Rehana Bibi Mandal" in identity  # as printed on the roll
    assert "Rehana Bibi Mondal" in identity  # as the documents have it


def test_father_name_mismatch_is_recorded_in_the_identity_paragraph():
    identity = numbered_paragraphs(
        build_petition(
            minimal_intake(
                mismatch_father_name=True, father_name_on_roll="Abdul Karim Mandal"
            )
        )
    )[1][1]
    assert "Abdul Karim Mandal" in identity
    assert "Abdul Karim Mondal" in identity


def test_clerical_variation_ground_fires_on_an_appellant_name_mismatch():
    text = all_text(
        build_petition(
            minimal_intake(
                mismatch_appellant_name=True, name_on_roll="Rehana Bibi Mandal"
            )
        )
    )
    assert "clerical variation" in text
    assert "no disqualification under the Representation of the People Act, 1950" in text


def test_clerical_variation_ground_fires_on_a_father_name_mismatch():
    text = all_text(
        build_petition(
            minimal_intake(mismatch_father_name=True, father_name_on_roll="Abdul Karim Mandal")
        )
    )
    assert "clerical variation" in text


def test_clerical_variation_ground_is_absent_without_a_mismatch():
    assert "clerical variation" not in all_text(build_petition(minimal_intake()))


def test_plain_transfer_pleads_the_move_without_the_marriage():
    first = numbered_paragraphs(
        build_petition(married_intake(address_change_reason="transfer"))
    )[0][1]
    assert "shifted her residence permanently from Bankura" in first
    assert "Example (SC) - 100" in first
    assert "marrying" not in first


def test_residence_paragraph_stands_alone_when_no_move_is_pleaded():
    first = numbered_paragraphs(
        build_petition(minimal_intake(address="Ward 42, Kolkata"))
    )[0][1]
    assert "permanent resident of Ward 42, Kolkata" in first
    assert "shifted" not in first


def test_a_pleaded_move_must_say_which_kind():
    # Marriage and transfer plead differently; there is no safe default.
    with pytest.raises(ValidationError, match="address_change_reason"):
        minimal_intake(address_changed=True)


def test_other_reason_takes_its_own_numbered_paragraph():
    # Free text cannot be safely welded into someone else's sentence, so unlike
    # the listed reasons this one stands as a paragraph of its own.
    numbered = numbered_facts(
        build_petition(
            minimal_intake(
                other_reason="the Appellant's date of birth was mis-recorded "
                "during the 2002 revision"
            )
        )
    )
    assert [n for n, _ in numbered] == [1, 2, 3, 4]
    assert "mis-recorded during the 2002 revision" in numbered[2][1]


def test_other_reason_is_absent_when_not_pleaded():
    numbered = numbered_facts(build_petition(minimal_intake()))
    assert [n for n, _ in numbered] == [1, 2, 3]


def test_marriage_clause_joins_the_residence_paragraph():
    # Settled petition ¶1: residence and the move that explains it are one
    # paragraph, not two — so the clause must compose, not take its own number.
    first = numbered_paragraphs(build_petition(married_intake()))[0][1]
    assert first.startswith("1. ")
    assert "Ward 42, Kolkata" in first
    assert "shifted her residence permanently from Bankura" in first
    assert "Sirajul Islam" in first
    assert "1st January 2010" in first
    assert "Example (SC) - 100" in first
    assert "2016" in first
