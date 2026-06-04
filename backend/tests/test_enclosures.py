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
