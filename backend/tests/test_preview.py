"""Live preview — render the exact petition as HTML (same content as the .docx)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.intake import PetitionInput
from app.preview import render_html
from app.main import app

client = TestClient(app)


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


def test_render_html_contains_text_and_ceremonial_anchor():
    html = render_html(base(epic_no="ABC1234567"))
    assert "Priya Devi Das" in html
    assert "MOST RESPECTFULLY SHEWETH:" in html
    assert "ABC1234567" in html


def test_render_html_marks_centered_headings():
    html = render_html(base())
    # the forum line is a centered heading; preview must preserve the role.
    assert "center" in html
    assert "<table" not in html  # no tables when nothing is held


def test_render_html_renders_tables():
    html = render_html(
        base(relatives_on_roll=[{"name": "Ramesh Chandra Das", "relationship": "Father", "epic_no": "X9"}])
    )
    assert "<table" in html
    assert "Ramesh Chandra Das" in html
    assert "Relationship" in html


def test_preview_endpoint_returns_html():
    resp = client.post(
        "/api/petition/preview",
        json={"appellant_name": "Priya Devi Das", "gender": "female"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "MOST RESPECTFULLY SHEWETH:" in resp.text


def test_preview_escapes_html_in_user_input():
    html = render_html(
        PetitionInput(appellant_name="<script>alert(1)</script>", gender="female")
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
