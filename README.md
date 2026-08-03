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

Requires Python 3 and Node.js.

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
./run.sh
```

`run.sh` builds the frontend on first run, starts the backend, and prints the
addresses to share. The backend serves both the UI and the API from **one
port**, so a single URL works from any device on your network:

```
This Mac          http://localhost:2026
Same wifi         http://your-macbook.local:2026
Same wifi (IP)    http://192.168.x.x:2026
```

Anyone on the same wifi can open those — nothing leaves the network, and
nothing is stored. Keep the window open; Ctrl-C stops it. Pass `--build` after
editing anything in `frontend/src`; backend edits reload on their own.

For frontend work with hot reload, run `npm run dev` inside `frontend/`
alongside the backend; vite proxies `/api` through to port 2026.

## Troubleshooting

- **`npm error … Could not read package.json` / `ENOENT`** — you're in the wrong folder. `npm install` and `npm run dev` must be run inside `frontend/`, not the repo root.
- **`pip install` can't find the requirements file** — the paths above are relative to the repo root. From inside `backend/`, use `requirements-dev.txt`.
- **Opening the URL gives `{"detail":"Not Found"}`** — the frontend hasn't been built yet. Run `./run.sh --build`.
- **Generate does nothing, or the preview stays blank** — check the backend is up: `curl http://localhost:2026/api/health` should return `{"status":"ok"}`.
- **`ERROR: [Errno 48] Address already in use`** — something already holds the port. `run.sh` detects this and says so; to clear it, `kill $(lsof -ti :2026)`.
- **Another device can't reach it** — it must be on the same wifi, and the server must be started with `--host 0.0.0.0` (`run.sh` does this). Your IP changes when you join a different network; `run.sh` prints the current one each time.

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
