# FILE INVENTORY — Hercules MK3 ROV Manual

**Snapshot date:** 13 May 2026 (post security session)
**Repo root:** `/Users/seanbrock/Documents/GitHub/rov-chatbot/`

> Every file/folder in the project, what it does, and where it sits in the architecture.
> Companion to `SESSION_HANDOFF.md` (orientation), `PROJECT_STATUS.md` (vision/progress), `SECURITY_BRIEF.md` (security model), and `DRAWING_INDEX.md` (drawing-index feature).

---

## Repo root

### Documentation

| File | Purpose |
|---|---|
| `README.md` | One-page project overview + live URLs + JS parse check command. Public-facing entry point. |
| `PROJECT_STATUS.md` | Vision statement + architecture + full session history + outstanding tasks. The "deep" reference. |
| `SESSION_HANDOFF.md` | Drop-in orientation for a fresh AI session. Read first. |
| `FILE_INVENTORY.md` | This file. Every file mapped. |
| `MASTER_KNOWLEDGE.md` | Ground truth technical reference (PCBs, signals, hydraulics, drawing numbers). The chatbot prompt is graded against this. v2.0, source manuals TMA01030/01031/00974/01028/01029. |
| `DRAWING_INDEX.md` | Three-layer drawing-index feature reference: `card_index` flow, `drawing_families` chatbot integration, and the standalone tree HTMLs. Includes the dev-only limitation of tree HTMLs in full detail. |
| `SECURITY_BRIEF.md` | Self-contained briefing on the security architecture (two-gate model, accepted residual risk, hard constraints, fair-game redesign areas). Read this before any change touching `app.py`, auth flows, or env vars. |
| `CARD_SYSTEM_BRIEF.md` | Self-contained briefing on the card navigation system (three data sources — `POD_ZONES`, `DESCRIPTIONS`, `card_index`; click flow; load-bearing constraints; fair-game redesign areas). Read this before any change touching the chassis SVGs, card sidebar, or card click handler. |
| `COWORK_TASK_REORGANISE_TECH_DOCS.md` | Run instructions for `reorganise_tech_docs.py` — the script that built the parallel reorganised folder structure. |

### Server (Railway-deployed)

| File | Purpose |
|---|---|
| `app.py` | Flask proxy server. 181 lines. Routes: `/` (serves index), `/<file>` (static), `/api/config` (public values only — no secrets), `/api/auth` (app password check, `hmac.compare_digest`), `/api/admin-auth` (admin password check, deny-by-default), `/voyage/embeddings` (gated), `/anthropic/messages` (gated), `/supabase/<path>` (gated, anon/service key selection), `/health`. Decorator `@require_password` enforces `X-App-Password` header. |
| `Procfile` | Railway start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| `requirements.txt` | flask 3.0.3, flask-cors 4.0.1, requests 2.31.0, gunicorn 21.2.0 |
| `.gitignore` | Excludes `rov-manual/manuals/`, `.DS_Store`, CAD/binary formats, `__pycache__`, logs |

### Ingestion / utility scripts (Python)

| File | Purpose |
|---|---|
| `embed_new_files.py` | 275 lines. Batch script run via Cowork. Walks `rov-manual/manuals/`, extracts text from PDFs (pdfplumber pass 1, Claude vision pass 2 for image-heavy pages), chunks to ~500 words with overlap, embeds via Voyage AI `voyage-large-2` (1536 dims), writes to Supabase `chunks` table. Skips files already in DB. Last run 30 April 2026: 161 new files, +15,483 chunks. |
| `reorganise_tech_docs.py` | 482 lines. One-shot reorganisation script. Takes the source `~/work documents/3. Technical Docs/` tree, builds parallel `Technical Docs - Hercules MK3/` tree organised by functional system, copies (never moves) files into it, renames drawing-number-only filenames using pdfminer to extract the title block. Test mode by default; `--full` runs all folders. |
| `reorganise_mk3.py` | 886 lines. Earlier/larger version of the reorganise script — full automated rebuild. Likely superseded by `reorganise_tech_docs.py` but retained for reference. **Verify with Sean before deleting.** |

### `_archive/`

Old reference material — not loaded by anything.

| File | Was |
|---|---|
| `_archive/PROJECT_SUMMARY.md` | Pre-PROJECT_STATUS.md project summary |
| `_archive/ROV Master Knowledge v2.docx` | Word doc precursor to `MASTER_KNOWLEDGE.md` |
| `_archive/SESSION_HANDOFF.md` | Earlier session handoff doc (predecessor to current root-level one) |
| `_archive/SESSION_REPORT_22APR2026.md` | One-off session report |
| `_archive/embed_manual.py` | Earlier version of the embed script, single-PDF rather than batch |

---

## `rov-manual/` — the frontend

This is the folder that gets copied to `N:\15. ROV\3. Technical Docs\` on vessel deploy.

### HTML (the application)

| File | Lines | Purpose |
|---|---|---|
| `index.html` | 3,082 | **The application.** Single file containing all menu DATA, viewer tabs, chatbot UI, Supabase client code, Anthropic client (via Railway proxy), card descriptions, drawing family integration. 312 KB. Self-contained by design — no build step, no bundler, no npm. |
| `admin.html` | 500 | Admin panel. Three-pane: section list \| drawing list \| PDF preview. Move/remove/restore drawings. Q&A log view with CSV export. Drawing number reference. Saves `data_patch.js` for manual application to index.html. Access: tiny ⚙ icon in main header. |
| `manual-viewer.html` | 34 | Minimal PDF wrapper — opens any manual in a new browser tab with native Ctrl+F for text search. URL pattern: `manual-viewer.html?manual=FILENAME.pdf`. |
| `control-room-tree.html` | 574 | Standalone drawing index for the Control Room subsystem. Linked from main menu. |
| `drawing-tree.html` | 721 | Full drawing family tree — all 70 prefix series with browseable structure. |
| `lars-tree.html` | 658 | Standalone LARS drawing index — 10 sub-systems (LCC, latch beam, cursor etc.). |
| `pdu-tree.html` | 566 | Standalone PDU drawing index. |

### Data

| File | Purpose |
|---|---|
| `snippets.json` | 15.7 KB. Hand-authored long-form descriptions for ~20 major components (electronics pod, TCU, manipulators etc.). Used inline by `index.html` for card-info side panels and as a context source. |
| `missing-drawings.md` | 6.7 KB. Tracking list of drawings known to be needed but not yet sourced/embedded. Working notes. |

### Symlink — important for deploy

| Path | Points to |
|---|---|
| `rov-manual/docs` → `/Users/seanbrock/work documents/3. Technical Docs - Hercules MK3` | The reorganised reference folder. **NOT git tracked.** **Will NOT survive copy to vessel drive** — either breaks or duplicates 1.4 GB depending on copy method. Recommend resolving before vessel deploy (either remove the symlink, or replace with a real folder/README). |

### Assets

| Path | Contents |
|---|---|
| `rov-manual/manuals/` | **635 PDFs, ~1.4 GB.** Not git tracked (in `.gitignore`). Master PDF library. Filenames are referenced by exact name in `DATA` blocks within `index.html`. Renaming any file silently breaks links. |
| `rov-manual/photos/` | ROV photo assets (`rov_overview.jpg` etc.). Tracked. |
| `rov-manual/.DS_Store` | macOS metadata. Should be in `.gitignore`. |

---

## Supabase — `ccjurdnubkmeepaztomy.supabase.co`

### Tables

| Table | Rows | Purpose | Access pattern |
|---|---|---|---|
| `chunks` | 23,333 | Embedded PDF text chunks. Columns: `manual_name`, `chunk_index`, `page_label`, `text`, `embedding(1536)`. | Read via `match_chunks` RPC (anon). Write via service role (Cowork embed script). |
| `drawing_families` | 70 | Drawing number prefix/series guide with legacy warnings. | Read via `lookup_drawing_family` RPC (anon, auto-fired by chatbot when drawing number detected). |
| `drawings` | 194 | Indexed drawings: drawing number, title, system, description, drive URL, embedding. 67 mapped to local files in `manuals/`. | Read directly with anon (search) and via `match_chunks` analogue. |
| `card_index` | 30 | Pod card → drawings + chunk IDs mapping. Powers the card-click sidebar. | Read direct from browser using anon key. |
| `fault_log` | 1,057 | H15 + H30 Sub Engineer Log entries 2012–present. | Text search via `ilike` on `description`. |
| `handover_log` | 4,060 | End-of-trip Word doc content, 2023–2026. Category column populated by Claude Haiku. | Text search via `ilike` on `content`. |
| `chat_log` | live (growing) | Every chatbot Q&A logged with system prompt, response, retrieved chunks, rating (GOOD/BAD), free-text feedback. | Write direct from browser using anon key (`POST /rest/v1/chat_log`). Admin panel reads + CSV-exports. |
| `knowledge_corrections` | 0 | Schema ready, empty. Intended for engineer-submitted corrections to chatbot answers. **No review workflow yet** — adding a `status` column (`pending`/`approved`/`rejected`) is recommended before this goes live with vessel users. |

### RPCs

| Function | Purpose |
|---|---|
| `match_chunks(query_embedding, match_count)` | Vector similarity search across `chunks`. Returns top N by cosine similarity. |
| `lookup_drawing_family(p_query)` | Drawing number family lookup by prefix. Auto-fires when chatbot detects a drawing number regex match. |
| `search_fuzzy(p_manual, p_query, p_limit, p_threshold)` | pg_trgm fuzzy text search within a specific manual. |
| `search_part_number(p_manual, p_query, p_limit)` | Exact part-number keyword search within a specific manual. |

---

## Runtime infrastructure

| Service | Purpose | Cost / tier |
|---|---|---|
| Railway | Hosts Flask `app.py` via gunicorn. Auto-deploys on push to `main`. Holds env vars `ANTHROPIC_KEY`, `VOYAGE_KEY`, `SUPABASE_URL`, `SUPABASE_ANON`, `SUPABASE_SERVICE`, `APP_PASSWORD` (latter pending set). | Hobby/free tier — fine for single-vessel use |
| Supabase | Postgres + pgvector + auth + REST API. Tables above. | Free tier |
| Anthropic API | Claude Sonnet 4 (`claude-sonnet-4-20250514`) — chatbot model | Per-token, paid |
| Voyage AI | `voyage-large-2` embeddings (1536 dims) — used by embed script only | Per-token, paid |
| GitHub | Source control. Private repo. SSH push configured on Sean's Mac. | Free private |

---

## Environment variables (Railway)

| Var | Sensitivity | Used by |
|---|---|---|
| `ANTHROPIC_KEY` | SECRET | `/anthropic/messages` proxy in `app.py` |
| `VOYAGE_KEY` | SECRET | `/voyage/embeddings` proxy in `app.py` |
| `SUPABASE_URL` | public | Returned by `/api/config`, used by browser for direct reads |
| `SUPABASE_ANON` | public-by-design | Returned by `/api/config`, used by browser for direct reads |
| `SUPABASE_SERVICE` | SECRET (legacy JWT — rotation deferred as tracked tech debt, see SECURITY_BRIEF.md) | Used server-side by `/supabase/<path>` for writes |
| `APP_PASSWORD` | SECRET | Validated by `@require_password` decorator and `/api/auth` |
| `ADMIN_PASSWORD` | SECRET | Validated by `/api/admin-auth`. Deny-by-default when unset. |

---

## File flow on vessel deploy

```
Sean's Mac                              Vessel drive
─────────────                           ─────────────────────────────
rov-manual/                  COPY  ──►  N:\15. ROV\3. Technical Docs\
  index.html                              index.html
  admin.html                              admin.html
  *-tree.html                             *-tree.html
  manual-viewer.html                      manual-viewer.html
  manuals/ (635 PDFs)                     manuals/
  photos/                                 photos/
  snippets.json                           snippets.json
  docs (symlink) ✗ BREAKS               (symlink dangles or duplicates)
```

Engineer opens `index.html` in Edge via `file://`. Chatbot and live drawing search call out to Railway + Supabase over the internet. Manual navigation and PDF viewing work fully offline.

---

## Cross-references — when to read what

| If you're trying to... | Read |
|---|---|
| Get oriented in 5 minutes | `SESSION_HANDOFF.md` |
| Understand the vision and decisions made | `PROJECT_STATUS.md` |
| Find a specific file | This document (`FILE_INVENTORY.md`) |
| Check what the chatbot is graded against | `MASTER_KNOWLEDGE.md` |
| Run the reorganise script | `COWORK_TASK_REORGANISE_TECH_DOCS.md` |
| Run a JS parse check before pushing | `README.md` (canonical command) |
| Add new PDFs to the searchable corpus | `embed_new_files.py` (run via Cowork) |
| Understand the drawing-index layers | `DRAWING_INDEX.md` |
| Change auth, `app.py`, or env vars safely | `SECURITY_BRIEF.md` (read FIRST) |
| Redesign the card navigation system | `CARD_SYSTEM_BRIEF.md` (read FIRST) |
