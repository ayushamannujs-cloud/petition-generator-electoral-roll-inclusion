# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A generator for West Bengal SIR-2026 electoral-roll deletion appeal petitions. An intake questionnaire (~50 fields) is poured into a formatted, filing-ready `.docx`. Legal content is **conditional**: which facts, grounds, prayers and enclosures appear depends on the appellant's answers. See `README.md` for the domain framing and the trigger table.

## Commands

Python deps are declared in `backend/requirements.txt` (runtime) and `backend/requirements-dev.txt` (adds pytest and httpx, which Starlette's TestClient needs). They install into a repo-root virtualenv at `.venv` — that path is what `run.sh` expects, not `backend/venv`.

```bash
# Tests — must run from backend/ (pytest.ini sets testpaths=tests; imports are `app.*` / `tests.*`)
cd backend && ../.venv/bin/python -m pytest -q
../.venv/bin/python -m pytest tests/test_triggers.py -q            # one file
../.venv/bin/python -m pytest -q -k "compensation"                 # one test

# Run the app: builds the frontend if needed, serves UI+API, prints the LAN address.
./run.sh                        # --build to force a frontend rebuild; PORT=n to override

# Or the backend alone. --host 0.0.0.0 is what makes it reachable from other devices.
cd backend && ../.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 2026

# Frontend
cd frontend && npm run build    # tsc -b && vite build — required before the backend can serve the UI
npm run dev                     # vite dev server; proxies /api to :2026, binds 0.0.0.0
npm run lint                    # eslint
```

The frontend has no test runner.

**The app is single-origin.** `main.py` mounts `frontend/dist` at `/`, so one port serves both the UI and the API, and `api.ts` calls relative paths (`/api/petition`). This is what lets a volunteer on the LAN open `http://<your-ip>:2026` with nothing configured on their end. Consequences worth knowing:

- The UI is only served **after `npm run build`**. Without `dist/`, the mount is skipped and the API still works alone.
- The mount is registered last in `main.py` so `/api/*` routes match first. `test_api_routes_are_not_shadowed_by_the_frontend_mount` guards that ordering.
- `frontend/.env` deliberately leaves `VITE_API_BASE` **empty**. Setting an absolute URL there bakes that host into the bundle and breaks every device except the one that built it.
- In `npm run dev`, vite proxies `/api` to `localhost:2026` (`vite.config.ts`), so dev and production take the same relative code path.

## Architecture

**`build_petition(intake) -> docx.Document` in `backend/app/generator.py` is the single source of truth for petition content.** Everything else is a view over it:

- `main.py` streams `build_petition()` output as a `.docx` download (`POST /api/petition`).
- `preview.py` calls `build_petition()` and walks the resulting document body in document order (`_iter_blocks` over `w:p` / `w:tbl`), converting paragraphs and tables to HTML (`POST /api/petition/preview`).

The preview must **never** re-state petition wording. If you need new text in the preview, add it to the generator. `test_preview.py` guards this by asserting preview output contains generator strings.

`generator.py` is intentionally a deep module: one public function, private `_section(doc, intake, counter)` helpers called in a fixed order inside `build_petition`. That call order *is* the mandatory section sequence (forum → cause title → respondents → preamble → facts → documents → entitlement → relatives → **GROUNDS** → **SUBMISSIONS** → closing tag → prayer → declaration → verification → enclosures) and is asserted by `test_fixed_section_sequence_in_order` plus `test_facts_close_in_the_settled_petition_order`. Note the closing tag precedes the prayer: the settled petition numbers *"This application is made bona fide…"* as its last paragraph, ¶23, and the prayer follows unnumbered. Reordering the calls changes the legal document's structure.

### Paragraph numbering

Substantive paragraphs carry a single continuous arabic run. `_Counter` is created once per `build_petition` and threaded through the section helpers; `_numbered()` takes the next number **as the paragraph is emitted**, so a paragraph that doesn't fire leaves no gap and everything below it shifts up. Numbers are written as literal text (`"3. That the Appellant…"`), not Word list properties — that matches how the settled petition sets them at the margin, and keeps them visible to both the tests and the HTML preview.

Consequences: never hardcode a paragraph number, in text or in a cross-reference; derive it from the counter. Adding an unconditional paragraph shifts every number below it, so tests asserting exact counts will legitimately need updating. `numbered_paragraphs()` in `tests/helpers.py` reads the run back — it starts after `MOST RESPECTFULLY SHEWETH` because the respondent list above carries its own `1./2./3.`, and stops at the separately-numbered enclosures.

### Conditional legal content

Two categories, both driven by boolean flags on `PetitionInput`:

- **Standing law** — `_grounds` holds counsel's four, always present and invariant across appellants: natural justice → Article 14/21 and the Article 326 right to vote plus non-communication of the order → non-application of mind → incorrectly excluded despite sufficient documents. These describe what the *authority* did wrong, so nothing appellant-specific belongs here; that goes in the facts or in `_submissions`.
- **Triggered law** — fires only on specific intake combinations, e.g. `has_passport` adds the Passports Act 1967 paragraph inside `_facts`; `mapped_2002_sir and has_aadhaar` adds the *Motab Shaikh* / *ADR* precedent ground; a name mismatch fires the clerical variation ground. Narrative beats in `_beats` follow the same no-flag-no-paragraph rule, in strict chronology.

### Deletion reasons compose as clauses, not paragraphs

The reasons a roll disagrees with an appellant's documents — `mismatch_appellant_name`, `mismatch_father_name`, `address_changed` (`marriage` or `transfer`), and free-text `other_reason` — are a multi-select, like the documents held. They resolve in **two tiers**, which is the part that is easy to get wrong:

- Reasons describing *who the appellant is* compose as **clauses into an existing paragraph**. The move that explains an address lands as the second sentence of ¶1 (`_address_change_clause` → `_residence`); name variations land in ¶2 (`_name_variation_clauses` → `_identity`). They take no number of their own, because the settled petition keeps residence and the move that produced it in a single paragraph.
- Reasons describing *what happened*, and free text that cannot be safely welded into someone else's sentence, take **their own numbered paragraph** (`_other_reason`, and everything in `_beats`).

So a paragraph builder that needs conditional content assembles a `list[str]` of clauses and joins them before emitting once. Appending a `_numbered()` call instead is what produces the "1. That the Appellant is a permanent resident… 2. That the Appellant shifted her residence…" split that the exemplar does not have.

`contact` is intentionally never rendered — the settled petition has no contact line, so the field exists only so a volunteer can reach the appellant. `test_contact_details_stay_out_of_the_filed_document` locks that in; it is not a dead field to be wired up.

`address_changed` requires `address_change_reason` — marriage and transfer plead differently and there is no safe default. Every other sub-field falls back to `____` in the generator, matching how the rest of the intake behaves, so the live preview keeps rendering while a volunteer is still typing.

**Cascade constraints** are enforced in two places and must stay consistent: `PetitionInput._check_constraints` (Pydantic `model_validator`) rejects `relief_compensation` without `hardship` and an `appeal_date` outside the 15-day `APPEAL_WINDOW_DAYS` window; `_prayer` independently re-checks `relief_compensation and hardship` before emitting the relief. Prayers are auto-lettered `(a)`, `(b)`, … in emission order, with the residuary clause always last.

### Placement

Measured off the settled petition's line geometry, as offsets from the 1.5″ text margin:

| block | left indent | first line | notes |
|---|---|---|---|
| cause title, parties, VERSUS, respondents | 2.75″ | — | a right-hand column, not full width |
| prayer stem | 2.75″ | — | same column |
| prayers (a)–(e) | 3.0″ | −0.25″ | hanging, within the column |
| facts / grounds | 0.25″ | −0.25″ | number at the margin, text wraps in |
| submissions | 0.25″ | −0.25″ + tab stop at 0.5″ | `_numbered(..., deep=True)` |

`VERSUS` and `AND` are centred *within the column*, which falls out of setting `left_indent` on a centred paragraph — the exemplar puts them at x≈414pt, the column's midpoint, not the page's. Party tags stay right-aligned to the margin and need no indent. `_p()` takes `left_indent` / `first_line_indent` / `tab_stop`, so placement is per-call rather than per-role; `_forum` is centred full-width while `AND` is centred in the column, and both use `role="heading"`.

**The preview converts these to percentages of the text column** (`_text_width_inches`, read off `doc.sections[0]`), because the preview pane is roughly half a viewport wide and a literal 2.75″ indent would swallow it. 2.75″ of a 5.77″ column is 47.68%. Note that subtracting two python-docx `Length` values yields a bare EMU int with no `.inches`, so convert before arithmetic.

### Typography is behaviour, not styling

Page geometry and fonts are legal filing requirements, asserted in `test_typography.py`: A4 (210×297 mm), asymmetric margins (left/top 1.5″, right/bottom 1″), Bookman Old Style 12pt, 1.5 line spacing on body paragraphs. All text goes through `_p(doc, text, role)` where `role` (`heading`/`body`/`party`/`left`) sets alignment and boldness — don't call `doc.add_paragraph()` directly.

### Type duplication

`PetitionInput` exists twice — `backend/app/intake.py` (Pydantic) and `frontend/src/api.ts` (TypeScript interface). There is no codegen. Adding an intake field means editing both, plus a form control in `App.tsx`. Field names must match exactly; the backend returns 422 on invalid intake and `previewPetition` deliberately swallows 422 (incomplete form → empty preview).

## Testing conventions

107 tests, all behavioural — they build a document and assert on its rendered content, never on implementation details. `tests/helpers.py` provides `all_text`, `para_texts`, `index_of`, and the two run readers.

**Use `numbered_facts()` when a test is about the facts, and `numbered_paragraphs()` only when it is about the whole run.** Grounds and submissions share the arabic run, so a test that pins the full run's length breaks every time standing content is added — which is exactly what happened when the GROUNDS section landed. Density (`numbers == list(range(1, len(numbers) + 1))`) is the durable invariant; exact lengths are not.

When adding conditional legal content, assert **both presence and absence**: the ground appears when its trigger is set, and is absent when it isn't (see `test_triggers.py`). Ceremonial anchors ("MOST RESPECTFULLY SHEWETH:", the prayer stem, the bona fide closing tag) are asserted verbatim — a wording change there is a deliberate legal decision, not a typo fix.

## Note on code comments

Source comments cite design documents (`scaffold-rules.md`, `boilerplate-rules.md`, `authorities-rules.md`, `intake-form.md`) that are **not in this repository**. Treat those citations as historical provenance; the tests are the enforceable specification.
