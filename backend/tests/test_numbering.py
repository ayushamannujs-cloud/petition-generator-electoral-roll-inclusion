"""Paragraph numbering — one continuous arabic run, recomputed from the evidence.

The settled petition numbers every substantive paragraph 1..N in a single run.
Which paragraphs exist depends on what the appellant actually pleads, so the
numbers cannot be written into the text — they are counted at generation time.
"""
from __future__ import annotations

from app.generator import build_petition
from app.intake import PetitionInput
from tests.helpers import numbered_facts, numbered_paragraphs


def minimal_intake(**overrides) -> PetitionInput:
    data = dict(
        appellant_name="Priya Devi Das",
        guardian_name="Ramesh Chandra Das",
        gender="female",
    )
    data.update(overrides)
    return PetitionInput(**data)


def test_facts_are_numbered_from_one_in_document_order():
    numbered = numbered_facts(build_petition(minimal_intake()))
    # Two opening facts plus the entitlement paragraph, which never varies.
    assert [n for n, _ in numbered] == [1, 2, 3]
    assert "permanent resident" in numbered[0][1]
    assert "EPIC No." in numbered[1][1]
    assert "not being otherwise disqualified" in numbered[2][1]


def test_facts_close_in_the_settled_petition_order():
    """Settled petition: documents (¶9), entitlement (¶10), then relatives (¶11)."""
    numbered = numbered_paragraphs(
        build_petition(
            minimal_intake(
                has_aadhaar=True,
                aadhaar_no="000011112222",
                relatives_on_roll=[
                    {"name": "Nasima Khatun", "relationship": "Brother"}
                ],
            )
        )
    )
    texts = [text for _, text in numbered]

    def position(needle: str) -> int:
        return next((i for i, text in enumerate(texts) if needle in text), -1)

    documents = position("relies upon and produces")
    entitlement = position("not being otherwise disqualified")
    relatives = position("close relatives")
    assert -1 not in (documents, entitlement, relatives), texts
    assert documents < entitlement < relatives


def test_evidence_shifts_the_numbers_below_it():
    """A paragraph's number is a function of what fired above it, not of its text."""

    def passport_para(**pleaded) -> list[int]:
        numbered = numbered_paragraphs(
            build_petition(
                minimal_intake(
                    has_passport=True, passport_no="X0000001", **pleaded
                )
            )
        )
        return [n for n, text in numbered if "X0000001" in text]

    assert passport_para() == [3]
    assert passport_para(notice_received=True) == [4]
    assert passport_para(notice_received=True, on_draft_roll=True) == [5]


def test_the_run_stays_dense_however_much_is_pleaded():
    numbered = numbered_paragraphs(
        build_petition(
            minimal_intake(
                on_draft_roll=True,
                notice_received=True,
                hearing_attended=True,
                under_adjudication=True,
                deleted=True,
                appeal_filed=True,
                has_passport=True,
                has_aadhaar=True,
                relatives_on_roll=[
                    {"name": "Nasima Khatun", "relationship": "Brother"}
                ],
            )
        )
    )
    numbers = [n for n, _ in numbered]
    # No gaps, no repeats, starting at 1 — whatever the appellant pleads. The
    # length is deliberately not pinned: standing grounds and submissions move it.
    assert numbers == list(range(1, len(numbers) + 1))
    assert len(numbers) > 11


def test_documents_and_relatives_paragraphs_join_the_run():
    numbered = numbered_facts(
        build_petition(
            minimal_intake(
                has_aadhaar=True,
                aadhaar_no="000011112222",
                relatives_on_roll=[
                    {"name": "Nasima Khatun", "relationship": "Brother"}
                ],
            )
        )
    )
    assert [n for n, _ in numbered] == [1, 2, 3, 4, 5]
    joined = " ".join(text for _, text in numbered)
    assert "relies upon and produces" in joined
    assert "close relatives" in joined


def test_a_pleaded_beat_joins_the_run():
    doc = build_petition(
        minimal_intake(
            notice_received=True, notice_no="EFS/123", notice_date="30.12.2025"
        )
    )
    numbered = numbered_facts(doc)
    assert [n for n, _ in numbered] == [1, 2, 3, 4]
    assert "EFS/123" in numbered[2][1]
