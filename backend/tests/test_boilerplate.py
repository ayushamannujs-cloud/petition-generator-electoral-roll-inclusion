"""Fixed wording — matched to the settled petition rather than paraphrased.

Everything here is boilerplate the appellant never chooses. Where the settled
draft carries a mechanical defect (a doubled colon, a plural verb on a singular
subject, an unfilled placeholder) it is corrected; the wording is otherwise the
exemplar's.
"""
from __future__ import annotations

from app.generator import build_petition
from app.intake import PetitionInput
from tests.helpers import all_text, para_texts


def minimal_intake(**overrides) -> PetitionInput:
    data = dict(appellant_name="Rehana Bibi Mondal", gender="female")
    data.update(overrides)
    return PetitionInput(**data)


def test_declaration_is_sworn_in_the_first_person():
    # A declaration is first-person by legal form, and the settled petition has
    # it so — distinct from the submissions, which we normalised to the third.
    text = all_text(build_petition(minimal_intake()))
    assert (
        "That I, Rehana Bibi Mondal, declare that the information provided in "
        "this memorandum is true and correct to the best of my knowledge and "
        "belief and that nothing material has been concealed or suppressed." in text
    )


def test_declaration_states_the_section_31_penalty_in_full():
    text = all_text(build_petition(minimal_intake()))
    assert (
        "punishable under Section 31 of the Representation of the People Act, "
        "1950 with imprisonment for a term which may extend to one year or with "
        "fine or with both." in text
    )


def test_preamble_names_the_online_application_and_the_impugned_order():
    text = all_text(
        build_petition(
            minimal_intake(appeal_no="APS0000000000000001", deletion_date="27.03.2026")
        )
    )
    assert "Supplementing online application being No. APS0000000000000001" in text
    assert "for the perusal of the Hon'ble Tribunal" in text
    assert "the Order dated 27.03.2026 passed by the Designated Judicial Officer" in text
    assert "exclusion from the Supplementary Electoral Roll" in text


def test_prayer_stem_matches_the_settled_wording():
    text = all_text(build_petition(minimal_intake()))
    # "your Petitioners ... prays" in the settled draft; the plural is a slip.
    assert (
        "In the circumstances as aforesaid, your Petitioner most humbly prays "
        "that this Hon'ble Appellate Tribunal may graciously be pleased to:" in text
    )


def test_first_prayer_names_the_impugned_list_and_its_date():
    relief = next(
        p.text
        for p in build_petition(minimal_intake(deletion_date="27.03.2026")).paragraphs
        if p.text.strip().startswith("(a)")
    )
    assert "impugned order/action/decision of deletion" in relief
    assert "Supplementary Electoral List dated 27.03.2026" in relief


def test_cause_title_states_the_appeal_and_the_impugned_roll():
    texts = para_texts(
        build_petition(
            minimal_intake(
                appeal_no="APS0000000000000001",
                appeal_date="04.04.2026",
                epic_no="WBX0000001",
                deletion_date="27.03.2026",
            )
        )
    )
    # Doubled colon in the settled draft ("IN THE MATTER OF: :") corrected.
    assert "IN THE MATTER OF:" in texts
    assert "IN THE MATTER OF" in texts  # the second heading carries no colon
    joined = "\n".join(texts)
    assert (
        "In the matter of Appeal no APS0000000000000001 submitted online on "
        "date 04.04.2026 challenging the deletion of voter bearing EPIC No. "
        "WBX0000001 in the roll dated 27.03.2026." in joined
    )


def test_appellant_is_numbered_one_in_the_party_block():
    texts = para_texts(
        build_petition(minimal_intake(guardian_name="Abdul Karim Mondal", address="New Tangra"))
    )
    assert any(
        t.startswith("1. Rehana Bibi Mondal, daughter of Abdul Karim Mondal") for t in texts
    )


def test_respondents_are_the_commission_the_ero_and_the_deo():
    texts = para_texts(
        build_petition(minimal_intake(constituency_name="Entally", district="Kolkata"))
    )
    joined = "\n".join(texts)
    assert "1. The Election Commission of India, Nirvachan Sadan, Ashoka Road, New Delhi-110001." in joined
    assert "2. The Electoral Registration Officer (ERO), Entally Assembly Constituency." in joined
    assert "3. The District Election Officer (DEO), Kolkata." in joined
    # The Chief Electoral Officer is not a respondent in the settled petition.
    assert "Chief Electoral Officer" not in joined


def test_respondent_tag_is_singular_as_settled():
    assert "………. Respondent" in para_texts(build_petition(minimal_intake()))


def test_forum_names_the_sir_tribunal_over_three_lines():
    texts = para_texts(build_petition(minimal_intake(tribunal_venue="Entally Jessop Building")))
    assert "BEFORE THE HON'BLE SIR APPELLATE TRIBUNAL FOR" in texts
    assert "ELECTORAL ROLLS (SIR 2026)" in texts
    assert "ENTALLY JESSOP BUILDING" in texts


def test_forum_venue_falls_back_to_a_blank():
    texts = para_texts(build_petition(minimal_intake()))
    assert "BEFORE THE HON'BLE SIR APPELLATE TRIBUNAL FOR" in texts
    assert "____" in texts
