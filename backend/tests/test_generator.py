"""Behavioural tests for the petition .docx generator (core slice)."""
from __future__ import annotations

from app.intake import PetitionInput
from app.generator import build_petition
from tests.helpers import all_text, index_of


def minimal_intake(**overrides) -> PetitionInput:
    """A core-slice intake with sensible defaults; override per test."""
    data = dict(
        appellant_name="Priya Devi Das",
        guardian_name="Ramesh Chandra Das",
        gender="female",
    )
    data.update(overrides)
    return PetitionInput(**data)


def _party_line(doc, name="Priya Devi Das") -> str:
    # The settled petition numbers the appellant "1." in the party block.
    return next(p.text for p in doc.paragraphs if p.text.strip().startswith(f"1. {name}"))


def test_party_block_names_both_father_and_husband():
    # Settled form: "<name>, daughter of <father>, wife of <husband>, residing
    # at ..." — the roll's guardian and the married name both.
    line = _party_line(
        build_petition(
            minimal_intake(guardian_name="Abdul Karim Mondal", spouse_name="Sirajul Islam")
        )
    )
    assert "daughter of Abdul Karim Mondal" in line
    assert "wife of Sirajul Islam" in line


def test_party_block_omits_the_spouse_when_none_is_pleaded():
    line = _party_line(build_petition(minimal_intake(guardian_name="Ramesh Chandra Das")))
    assert "daughter of Ramesh Chandra Das" in line
    assert "wife of" not in line


def test_party_block_spouse_relation_follows_gender():
    line = _party_line(
        build_petition(minimal_intake(gender="male", spouse_name="Anita Das"))
    )
    assert "husband of Anita Das" in line


def test_contact_details_stay_out_of_the_filed_document():
    # Deliberate: the settled petition has no contact line anywhere. The field
    # exists so a volunteer can reach the appellant, not to be filed.
    text = all_text(build_petition(minimal_intake(contact="98300 12345")))
    assert "98300 12345" not in text


def test_cause_title_contains_appellant_name():
    doc = build_petition(minimal_intake(appellant_name="Priya Devi Das"))
    assert "Priya Devi Das" in all_text(doc)


def test_fixed_section_sequence_in_order():
    doc = build_petition(minimal_intake())
    # Scaffold rule 5: mandatory section order.
    markers = [
        "BEFORE THE HON'BLE",        # forum
        "IN THE MATTER OF",          # cause title
        "VERSUS",                    # respondents divider
        "MOST RESPECTFULLY SHEWETH", # preamble opener
        "That the Appellant",        # facts
        "GROUNDS",                   # counsel's separated grounds section
        "SUBMISSIONS",               # then the elaboration
        "bona fide and for the ends of justice",  # closing tag — settled ¶23
        "most humbly prays",         # prayer stem, after the closing tag
        "D E C L A R A T I O N",     # declaration heading, letter-spaced as settled
        "Place:",                    # verification block
    ]
    positions = [index_of(doc, m) for m in markers]
    assert all(p != -1 for p in positions), dict(zip(markers, positions))
    assert positions == sorted(positions), positions


def test_ceremonial_anchors_verbatim():
    text = all_text(build_petition(minimal_intake()))
    # boilerplate-rules.md §5: the four fixed anchors, verbatim.
    assert "MOST RESPECTFULLY SHEWETH:" in text
    assert (
        "most humbly prays that this Hon'ble Appellate Tribunal may graciously "
        "be pleased to:"
    ) in text
    assert "This application is made bona fide and for the ends of justice." in text
    assert "true and correct" in text  # declaration clause


def test_residuary_prayer_is_always_last_relief():
    text = all_text(build_petition(minimal_intake()))
    residuary = (
        "Pass such further or other order(s) as Your Honour may deem fit and "
        "proper in the interest of justice."
    )
    assert residuary in text
    # boilerplate-rules.md §6: residuary clause is the final relief.
    assert text.rstrip().index(residuary) > text.index("Set aside")


def test_epic_echoes_in_cause_title_and_facts():
    text = all_text(build_petition(minimal_intake(epic_no="ABC1234567")))
    # particulars-rules: EPIC is an echo (appears at multiple sites).
    assert text.count("ABC1234567") >= 2


def test_address_and_constituency_fill_their_slots():
    doc = build_petition(
        minimal_intake(
            address="45 Netaji Subhas Road, Kolkata 700001",
            constituency_name="Entally",
            constituency_no="163",
        )
    )
    text = all_text(doc)
    assert "45 Netaji Subhas Road, Kolkata 700001" in text
    assert "Entally" in text
    assert "163" in text


def test_gender_drives_pronouns_female():
    text = all_text(build_petition(minimal_intake(gender="female")))
    assert "daughter of" in text
    assert " he " not in f" {text} " and " his " not in f" {text} "


def test_gender_drives_pronouns_male():
    text = all_text(build_petition(minimal_intake(gender="male")))
    assert "son of" in text
    assert " she " not in f" {text} " and " her " not in f" {text} "


def test_standing_law_always_present():
    # authorities-rules.md §4a: invariant authorities appear regardless of facts.
    text = all_text(build_petition(minimal_intake()))
    assert "Article 326" in text
    assert "Articles 14" in text and "21" in text
    assert "Representation of the People Act, 1951" in text
    assert "Representation of the People Act, 1950" in text  # s.31 declaration
    assert "natural justice" in text
    assert "non-application of mind" in text


def test_facts_open_with_That_and_grounds_with_It_is_submitted():
    doc = build_petition(minimal_intake())
    facts_i = index_of(doc, "That the Appellant")
    grounds_i = index_of(doc, "It is submitted that")
    assert facts_i != -1 and grounds_i != -1
    assert facts_i < grounds_i  # facts narrate before grounds argue
