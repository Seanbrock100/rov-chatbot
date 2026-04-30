# Session Report — Hercules MK3 ROV Chatbot
**Date:** 22 April 2026  
**Repo:** github.com/Seanbrock100/rov-chatbot

---

## Task A — RUN_EMBED_MANUALS.sh (completed)

Fixed the batch embed script that runs overnight to push manual PDFs into Supabase as vector chunks. Corrections made:

- **Munk Crane path**: `Munk Crane ROV Hanger` → `Munk Crane Rov Hanger` (actual Drive folder name)
- **ROV Lights**: switched from glob to `find` for recursive subfolder scanning
- **AleronVpSoftware**: removed — folder has no PDFs (software repo only)
- **IXBlue**: added skip logic for EQP-numbered drawing files (belong in `index_drawings.py`, not `embed_manual.py`)
- **Lars**: added skip for TMA01071 (already embedded — 62 chunks); OCE-0400 wiring diagrams embedded fresh
- **tcu.pdf**: commented out — already has a 1-chunk stub; flagged for manual review before re-embedding
- **Resilience**: removed implicit `set -e`; every section now uses `|| echo "⚠ Failed, continuing..."` so a single PDF failure doesn't abort the whole 75-PDF run

Script is ready for: `nohup bash RUN_EMBED_MANUALS.sh > /tmp/embed_log.txt 2>&1 &`

---

## Task B — Link Audit: rov-manual/index.html (completed)

Full audit of every drawing and manual link in the interactive manual. Target was zero broken links and zero unlinked PDFs.

**Before → After:**

| Metric | Before | After |
|--------|--------|-------|
| Total PDFs in manuals/ | 123 | 134 |
| Referenced in index.html | 78 | 134 |
| Broken links | 15 | **0** ✅ |
| Unlinked PDFs in manuals/ | 60 | **0** ✅ |

**What was fixed:**
- 5 filename mismatches (hyphen vs space, truncated names)
- 7 wrong subdirectory paths (`manuals/drawings/…` → flat `manuals/` structure)
- 11 PDFs located on Google Drive and copied into `manuals/`
- ~60 new DATA entries added across `electronics_pod`, `tcu`, `hpu`, `frame`, `lars`, `control_room`, `pdu`

Full details in `LINK_AUDIT_REPORT.md`. Committed in the same push.

---

## Task C — card_index Table: Populate + Wire into openCardInfo (completed)

### Step 3 — Populate card_index

Ran a Python script to map all 30 electronics pod cards to their relevant drawings and Supabase chunk IDs. Two bugs in the task-provided script were corrected before running:

1. **Wrong RPC parameter**: task script used `query_text` but `match_chunks` requires `query_embedding` (a 1536-dim Voyage AI vector). Fixed by calling Voyage AI first, then passing the vector.
2. **Wrong key normalisation**: task script replaced spaces with hyphens, producing keys like `control_chassis/psu-1---sle124`. JS `normKey()` keeps spaces, producing `control_chassis/psu 1 - sle124`. Fixed `py_norm_key()` to mirror the JS exactly (replaces `×→x`, `–→-`, `—→-`, collapses `--`, `&→and`, removes `()`, lowercases — no space replacement).
3. **Card name Unicode**: used exact names from POD_ZONES (`PSU 4–7 — MAX124 ×4` with en-dash, em-dash, ×) rather than the ASCII approximations in the task brief.

**Result — 30/30 rows inserted, all with drawings and chunks:**

| Zone | Cards | Drawing range | Chunk range |
|------|-------|--------------|-------------|
| control_chassis | 17 | 2–4 per card | 1–6 per card |
| payload_chassis | 13 | 1–3 per card | 1–10 per card |

Zero zero-chunk cards. Zero failed inserts.

### Step 4 — Wire into openCardInfo

Converted `openCardInfo` from a synchronous function to `async` and added a Supabase card_index fetch. Two helper functions extracted:

- **`renderCardDrawingsInSidebar(drawingsOrFiles, cardName)`** — renders the left sidebar drawing list; accepts either `{num,title,file}` objects (from POD_ZONES) or flat filename strings (from card_index)
- **`renderCardDrawingsInPanel(drawingsOrFiles)`** — renders the right column of the card-info-panel overlay; same dual-format support

**Behaviour on card click:**
1. POD_ZONES hardcoded drawings render immediately (zero latency, no network)
2. Async Supabase fetch fires in the background using `normKey(zone, c.name)` as the lookup key
3. When card_index row arrives, both the sidebar and the panel are updated with the full `local_files` list from the DB — giving each card its complete mapped drawing set

**JS parse check:** PARSE OK  
**Commit:** `1fd365d` — `Wire card_index into openCardInfo — live drawing and chunk lookup per card`

---

## Summary of Commits

| Hash | Message |
|------|---------|
| (earlier) | Fix and update RUN_EMBED_MANUALS.sh |
| (earlier) | Link audit: fix broken paths, add missing drawing/manual links |
| `1fd365d` | Wire card_index into openCardInfo — live drawing and chunk lookup per card |

---

## Remaining / Next Steps

- **Overnight embed run**: `nohup bash RUN_EMBED_MANUALS.sh > /tmp/embed_log.txt 2>&1 &` — 75 PDFs across 13 manual groups still to be embedded into Supabase
- **tcu.pdf**: 1-chunk stub in Supabase — verify whether TMA01031 already covers TCU content; if not, `--force` re-embed
- **IXBlue EQP drawing files**: add to `RUN_INDEX_DRAWINGS.sh` rather than embed_manual
- **card_index chunk quality**: a few cards got only 1 chunk (PSU 4–7, Band Splitter, Relay & HK PCBs) — may improve once overnight embed run adds more manual content to the chunks table
