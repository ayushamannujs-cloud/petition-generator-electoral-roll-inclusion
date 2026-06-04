"""API tests — the petition endpoint streams a downloadable .docx."""
from __future__ import annotations

import io

import docx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_post_petition_returns_docx_with_appellant_name():
    resp = client.post(
        "/api/petition",
        json={"appellant_name": "Priya Devi Das", "gender": "female"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == DOCX_MIME
    assert "attachment" in resp.headers.get("content-disposition", "")

    doc = docx.Document(io.BytesIO(resp.content))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Priya Devi Das" in text
    assert "MOST RESPECTFULLY SHEWETH:" in text


def test_post_petition_rejects_missing_name():
    resp = client.post("/api/petition", json={"gender": "female"})
    assert resp.status_code == 422


def test_content_disposition_is_exposed_to_cross_origin_browser():
    # The browser can only read the download filename if CORS exposes the header.
    resp = client.post(
        "/api/petition",
        json={"appellant_name": "Priya Devi Das", "gender": "female"},
        headers={"Origin": "http://localhost:5180"},
    )
    exposed = resp.headers.get("access-control-expose-headers", "")
    assert "Content-Disposition" in exposed
