"""FastAPI app exposing the petition generator."""
from __future__ import annotations

import io
import re
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.generator import build_petition
from app.intake import PetitionInput
from app.preview import render_html

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# The built frontend, served from this same app so the whole thing is one origin
# on one port — which is what lets a volunteer on the LAN just open the URL.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

app = FastAPI(title="SIR-2026 Petition Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


def _filename(intake: PetitionInput) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", intake.appellant_name).strip("_") or "petition"
    return f"{slug}_SIR2026_appeal.docx"


@app.post("/api/petition")
def generate_petition(intake: PetitionInput) -> StreamingResponse:
    doc = build_petition(intake)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type=DOCX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{_filename(intake)}"'},
    )


@app.post("/api/petition/preview", response_class=HTMLResponse)
def preview_petition(intake: PetitionInput) -> HTMLResponse:
    return HTMLResponse(content=render_html(intake))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Mounted last so the /api routes above always win. Absent before the first
# `npm run build`, in which case the API still serves fine on its own.
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
