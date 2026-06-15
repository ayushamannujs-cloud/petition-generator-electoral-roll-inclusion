# Petition Generator

A web app that generates electoral roll deletion appeal petitions for West Bengal's SIR-2026 (Special Intensive Revision) process — as formatted, filing-ready `.docx` documents.

Built by [@ayushamannujs-cloud](https://github.com/ayushamannujs-cloud), a law student at NUJS Kolkata, while working with a legal aid organisation on SIR-2026 voter appeals.

---

## The problem

In 2026, West Bengal's SIR-2026 exercise deleted large numbers of names from electoral rolls. Each affected voter had **15 days** to file a formal appeal before an Appellate Tribunal. The online appeal has several constrains, like word limit and no place to attach relevant documents. Thus the only option was an offline petition which required a proper legal petition — caption block, numbered facts, legal grounds citing specific statutes and precedents, prayers, enclosures list, signed declaration. Drafting one manually takes 45–90 minutes. Legal aid volunteers were doing this at scale.

## What this does

Fill an intake form — appellant's name, EPIC number, documents they have (Aadhaar, passport, PAN), whether they received a notice, whether they appeared for hearing, family linkage. The system generates a complete, formatted `.docx` petition tailored to that person's exact fact pattern.

The legal grounds are **conditional** — they fire based on what the appellant actually has:

| If the appellant has... | The system automatically includes... |
|---|---|
| Aadhaar + 2002 roll mapping | *Motab Shaikh v ECI* + *ADR v ECI* |
| Passport | Passports Act, 1967 + police verification argument |
| No notice received | Natural Justice ground |
| Appeared but still deleted | Non-Application of Mind ground |
| Name spelling mismatch | Clerical Variation ground |
| Relatives on roll | Citizenship corroboration block |

A **live preview** renders the petition in real-time as you type — exact Bookman Old Style 12pt, A4, asymmetric margins — so the lawyer can review before downloading. Prayers are auto-lettered and conditional. The compensation prayer only appears when hardship is pleaded. The appeal date is validated against the 15-day window.

## Honest limitations

- Hardcoded to SIR-2026 West Bengal electoral appeals. Not a general petition tool.
- Output needs human review before filing — treat it as a strong first draft.
- Not field-tested at scale. Used partially during SIR-2026 with manual editing by volunteers.
- No authentication, no persistence, no production deployment.

## Stack

```
backend/    FastAPI + python-docx
  app/intake.py      PetitionInput model — the intake questionnaire
  app/generator.py   build_petition() — assembles the .docx
  app/preview.py     render_html() — live preview
  app/main.py        POST /api/petition  →  .docx download
                     POST /api/petition/preview  →  HTML preview

frontend/   Vite + React + TypeScript
  src/App.tsx        Intake form
  src/api.ts         API calls
```

## Run

Requires Python 3 and Node.js. Run the backend and frontend in two separate terminals.

**Before starting — clear port 8000** (skip if you know it's free):
```bash
kill -9 $(lsof -ti :8000) 2>/dev/null; true
```

**Backend** (port 8000):
```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # recommended
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
npm run dev
```

Open the dev URL Vite prints (usually `http://localhost:5173`), fill the intake form, click **Generate petition (.docx)**. The frontend talks to the backend at `http://localhost:8000` by default; to point it elsewhere, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE`.

> **If port 8000 is occupied by another app** (e.g. you have a different project running there), the frontend will silently hit the wrong backend and all fetches will fail. The port-clear command above prevents this. Alternatively, start the backend on a different port and set `VITE_API_BASE` accordingly.

## Troubleshooting

- **`npm error … Could not read package.json` / `ENOENT`** — you're in the wrong folder. `npm install` and `npm run dev` must be run inside `frontend/`, not the repo root.
- **`pip install -r requirements.txt` can't find the file** — run it from inside `backend/`.
- **The form lets you type but nothing happens on Generate / preview is blank** — the backend isn't reachable. Confirm it's running (`curl http://localhost:8000/api/health` should return `{"status":"ok"}`) and that the ports match.
- **`ERROR: [Errno 48] Address already in use`** — another process holds port 8000. Run `kill -9 $(lsof -ti :8000)` (macOS/Linux) then restart the backend.

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest -q
```

44 behavioural tests asserting on the generated document's actual content — section order, Bookman 12pt / A4 / asymmetric margins, ceremonial anchors, gender-driven pronouns, triggered law presence and absence, validation errors. Not implementation details.

## Context

This is part of a larger set of experiments at the intersection of legal aid and software. The conditional grounds idea — that legal reasoning has a structure that can be encoded — is explored more generally in [Project Sunshine](https://github.com/ayushamannujs-cloud), a platform for building and sharing legal reasoning as reusable structures.

## Feedback and collaboration

Early-stage work. If you're working on access to justice technology, electoral rights, or legal aid automation — feedback, criticism, and collaboration welcome. Open an issue or reach out.
