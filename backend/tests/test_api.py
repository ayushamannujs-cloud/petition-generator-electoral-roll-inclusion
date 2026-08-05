"""API tests — the petition endpoint streams a downloadable .docx."""
from __future__ import annotations

import io

import docx
import pytest
from fastapi.testclient import TestClient

from app.main import FRONTEND_DIST, app

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


def test_api_routes_are_not_shadowed_by_the_frontend_mount():
    # The frontend is mounted at "/", so the API routes must still match first.
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.post(
        "/api/petition/preview",
        json={"appellant_name": "Priya Devi Das", "gender": "female"},
    ).status_code == 200


@pytest.mark.skipif(not FRONTEND_DIST.is_dir(), reason="frontend not built")
def test_root_serves_the_built_frontend():
    # One origin, one port — this is what lets another device on the LAN just
    # open the URL instead of needing an API host configured on its own side.
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert '<div id="root">' in resp.text


def test_content_disposition_is_exposed_to_cross_origin_browser():
    # The browser can only read the download filename if CORS exposes the header.
    resp = client.post(
        "/api/petition",
        json={"appellant_name": "Priya Devi Das", "gender": "female"},
        headers={"Origin": "http://localhost:5180"},
    )
    exposed = resp.headers.get("access-control-expose-headers", "")
    assert "Content-Disposition" in exposed
