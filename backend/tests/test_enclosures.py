"""Document inventory -> ID table + enclosures (cascade-enclosure edge)."""
from __future__ import annotations

from app.intake import PetitionInput
from app.generator import build_petition
from tests.helpers import all_text, index_of


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


def test_no_documents_means_no_doc_table_and_bare_enclosures():
    doc = build_petition(base())
    assert len(doc.tables) == 0
    text = all_text(doc)
    assert "ENCLOSURES:" in text


def test_held_documents_listed_in_enclosures():
    doc = build_petition(
        base(has_aadhaar=True, aadhaar_no="1111 2222 3333", has_passport=True, passport_no="Z1234567")
    )
    text = all_text(doc)
    # cascade-enclosure: each held document becomes a numbered enclosure.
    encl_start = index_of(doc, "ENCLOSURES:")
    enclosures = "\n".join(p.text for p in doc.paragraphs[encl_start:])
    assert "Aadhaar" in enclosures
    assert "Passport" in enclosures
    assert "Z1234567" in enclosures


def test_documents_relied_upon_table_present_when_docs_held():
    doc = build_petition(base(has_pan=True, has_aadhaar=True, aadhaar_no="1111 2222 3333"))
    assert len(doc.tables) == 1
    headers = [c.text for c in doc.tables[0].rows[0].cells]
    assert "Document" in headers
    body = all_text(doc)
    assert "PAN" in body and "Aadhaar" in body


def test_other_documents_flow_through():
    doc = build_petition(base(other_documents=["Ration card", "Birth certificate"]))
    text = all_text(doc)
    assert "Ration card" in text
    assert "Birth certificate" in text


def test_documents_section_craves_leave_for_further_documents():
    # Settled ¶9 closes with this, unnumbered and back at the margin.
    text = all_text(build_petition(PetitionInput(
        appellant_name="Rehana Bibi Mondal", gender="female", has_aadhaar=True)))
    assert (
        "Leave is hereby craved to submit and rely on additional supporting "
        "documents at the time of hearing if necessary." in text
    )


def test_leave_is_not_craved_when_no_documents_are_relied_upon():
    text = all_text(build_petition(PetitionInput(
        appellant_name="Rehana Bibi Mondal", gender="female")))
    assert "Leave is hereby craved" not in text
