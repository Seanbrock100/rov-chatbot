# Hercules MK3 ROV Interactive Manual & Chatbot — Project Vision & Progress
**Last Updated:** 13 May 2026
**Author:** Sean Brock / Subsea 7 Seven Oceanic
**Companions:** `SESSION_HANDOFF.md` (drop-in orientation), `FILE_INVENTORY.md` (every file mapped), `MASTER_KNOWLEDGE.md` (technical ground truth)

---

## Vision Statement

Build a digital technical reference system for the Hercules MK3 ROV fleet that a subsea engineer can use on shift — offshore, on a vessel network drive, or online — to find drawings, trace signal paths, and get accurate answers to technical questions without hunting through paper files or emailing the office.

The system has three layers:
1. **Interactive Manual** — structured navigation to drawings and manuals by functional system
2. **Manual Viewer** — open any PDF in a new browser tab with Ctrl+F for exact search
3. **AI Chatbot** — conversational technical assistant grounded in the actual ROV documentation

---

## System Architecture

### Repositories & Infrastructure
| Component | Location |
|-----------|----------|
| **Code repo** | github.com/Seanbrock100/rov-chatbot |
| **Live (online)** | https://rov-chatbot-production-3d66.up.railway.app |
| **Local dev** | http://localhost:8765 (python3 -m http.server 8765 in rov-manual/) |
| **Database** | Supabase — ccjurdnubkmeepaztomy.supabase.co |
| **Config endpoint** | https://rov-chatbot-production-3d66.up.railway.app/api/config |

### Key Files
| File | Purpose | Size |
|------|---------|------|
| `rov-manual/index.html` | Main manual — all DATA, menu, chatbot, viewer | 312 KB / 3,082 lines |
| `rov-manual/admin.html` | Admin panel — review/move/remove drawings + Q&A log + CSV export | 27 KB / 500 lines |
| `rov-manual/manual-viewer.html` | PDF viewer wrapper (opens manuals in new tab) | 1.4 KB / 34 lines |
| `rov-manual/control-room-tree.html` | Standalone Control Room drawing index | 23 KB / 574 lines |
| `rov-manual/drawing-tree.html` | Full drawing family tree (70 prefix series) | 36 KB / 721 lines |
| `rov-manual/lars-tree.html` | Standalone LARS drawing index (10 sub-systems) | 31 KB / 658 lines |
| `rov-manual/pdu-tree.html` | Standalone PDU drawing index | 22 KB / 566 lines |
| `rov-manual/snippets.json` | Component long-form descriptions | 16 KB |
| `rov-manual/docs` | Symlink to reorganised folder — **breaks on vessel copy** | — |
| `rov-manual/manuals/` | **635 PDFs** (not git tracked) | ~1.4 GB |
| `app.py` | Railway Flask proxy + password gate infrastructure | 156 lines |
| `embed_new_files.py` | Batch embed script for Cowork | 275 lines |
| `reorganise_tech_docs.py` | Reorganise + auto-rename Technical Docs folder | 482 lines |

### JS Parse Check Command
```bash
python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"
```

---

## Database State (13 May 2026)

| Table | Count | Notes |
|-------|-------|-------|
| `chunks` | **23,333** | Across **392** embedded manuals |
| `drawing_families` | 70 rows | Full Hercules MK3 prefix/series guide |
| `card_index` | 30 rows | ROV pod card signal path data |
| `drawings` | 194 | 67 mapped to local files |
| `fault_log` | 1,057 | H15 + H30 Sub Engineer Log |
| `handover_log` | 4,060 | End-of-trip reports 2023–2026 |
| `chat_log` | live (growing) | Q&A logging with GOOD/BAD ratings + free-text feedback |
| `knowledge_corrections` | 0 | Table ready; no review workflow yet — **add `status` column before enabling for vessel users** |

### Embed run results (Cowork, 30 April 2026)
| Stat | Count |
|------|-------|
| Files embedded | **161** |
| Files skipped (scanned/image PDFs — no text) | 174 |
| Files with errors | 0 |
| Chunks before run | 7,850 across 210 manuals |
| Chunks after run | **23,333 across 392 manuals** |
| Net gain | **+15,483 chunks, +182 manuals** |

### Top embedded manuals by chunk count
| Manual | Chunks | Relevance |
|--------|--------|-----------|
| TMA01071 Complete.pdf | 3,560 | Full LARS technical manual |
| Control System Manual TMA01031 Hyperlinked.pdf | 1,552 | TCU/software — critical |
| Alstrom T3 spares price list.pdf | 1,103 | T4 spares reference |
| 8239.pdf | 1,084 | T4 Schilling manual |
| Interface system Manual TMA01030.pdf | 926 | Electronics pod — critical |
| 8212 TITAN 4 PN 199-0295.pdf | 724 | T4 manipulator |
| Control System Manual TMA01031.pdf | 569 | TCU control system |
| T3-T4 slave electronics upgrade.pdf | 523 | Electronics upgrade |
| TMA01030 Interface systems manual.pdf | 341 | Pod interface |
| OR-TE-01228 LARS IAS Design Package.pdf | 294 | LARS design |

### 174 skipped files (scanned/image PDFs)
These have no extractable text — OCR would be required to make them searchable. Not a blocker for current use. Drawings are navigated directly via the manual viewer.

### Supabase RPCs
| Function | Purpose |
|----------|---------|
| `match_chunks(query_text, match_count)` | Vector semantic search across all chunks |
| `lookup_drawing_family(p_query)` | Drawing number family lookup by prefix/series |
| `search_fuzzy(p_manual, p_query, p_limit, p_threshold)` | pg_trgm fuzzy search within a manual |
| `search_part_number(p_manual, p_query, p_limit)` | Exact part number keyword search |

### Embedding status (post 30 April 2026 run)
- **PDFs in manuals/:** 593
- **Embedded with text:** 392 manuals ✅
- **Skipped (scanned/image):** 174 — no extractable text, OCR needed for search
- **Model used:** `voyage-large-2` (1536 dimensions)
- **Next embed run:** Only needed if new PDFs added to manuals/

---

## Manual Structure — Confirmed Menu Organisation

Based on technician mental model discussion (April 2026):

```
LONGLINES              (top level — own section)
CONTROL ROOM           (standalone — PCs, joysticks, RS232, monitors, PCBs)
PDU                    (standalone — power supply to whole system)

ROV — ELECTRICAL
  ├── Electronics Pod  (EQP952-0203-DR-PD-55xxx series — post-MOTC current)
  ├── Term Can         (always electrical — penetrators, wiring, umbilical term)
  └── Lights           (wiring, JB drawings, Oceantools manuals)

ROV — HYDRAULIC
  ├── HPU — Pump & Tank  (ROV-0249 series, TMA00974)
  ├── Valve Packs        (VP1/VP2 Curvetech + Aleron manip circuit)
  ├── TCU — Thruster Control  (ROV-0300-D-0420 assembly+wiring, PCB-0162)
  ├── Pan & Tilt         (hydraulically driven from VP1 Curvetech)
  └── Thrusters          (Curvetech HTE300/380 — hydraulically driven)

ROV — MECHANICAL
  └── Frame & Structure  (ROV-0300-D-01xx, SSA-0277, buoyancy, tool tray)

TMS — H15              (own section — FORUM MK2B)
TMS — H30              (own section — different system entirely)

LARS — Launch & Recovery
  ├── LCC Winch
  ├── Latch Beam
  ├── Latch Beam Winch
  ├── Cursor
  ├── Sliding Weight
  ├── LARS HPU
  ├── Moonpool Doors
  ├── Service Winch
  ├── Service Winch Slip Ring
  └── Tether

MANIPULATORS
  ├── T4 — Schilling (011-8239.pdf — 70 drawings + manuals)
  └── Atlas — Schilling (IVP controller, 36 items)

REFERENCE
  ├── Cables Index
  └── All Drawings
```

**Key decisions recorded:**
- TCU sits under ROV HYDRAULIC (controls hydraulic servo valves via RS485)
- Term Can is ALWAYS electrical — even o-rings are found under electrical section
- Pan & Tilt is ROV HYDRAULIC (driven from VP1, cameras just bolt on)
- Thrusters are ROV HYDRAULIC (hydraulically driven, not electric)
- TMS H15 and H30 are SEPARATE sections (completely different systems)
- LARS has 10 sub-sections (it's a large topic on its own)

---

## Drawing Number Family Tree (Key Facts)

The `drawing_families` Supabase table has 70 rows covering the full numbering system.
The `lookup_drawing_family(p_query)` RPC is called automatically when a drawing number is detected in a chatbot message.

| Prefix | What it means | Current? |
|--------|--------------|---------|
| `ROV-0226-420` | **LEGACY TCU junction box** — superseded by ROV-0300-D-0420 | ❌ DO NOT USE |
| `ROV-0300-D-0400` | **Jupiter valve pack** — PROJECT TOOLING only, not permanent ROV | ⚠️ Tooling |
| `ROV-0300-D-0420` | TCU assembly and wiring — CURRENT | ✅ |
| `ROV-0300-D-0440` | Hydraulic schematic (3 sheets + parts list) — full ROV circuit | ✅ |
| `ROV-0305-D-0450` | Curvetech VP1/VP2 GA — thruster control valve packs | ✅ |
| `ROV-0311-D-02xx` | **Pre-MOTC pod drawings** — superseded by EQP952 | ❌ Old |
| `EQP952-0203-DR-PD-55xxx` | **Current post-MOTC electronics pod drawings** | ✅ Current |
| `OCE-0400-DR-0xxx` | LARS drawings (Oceanic) | ✅ |
| `TMAxxxxx` | Technical manuals | ✅ |
| `011-8239` | Schilling/TechnipFMC T4 manual — 101-xxxx joint drawings inside | ✅ |

---

## T4 Manipulator — Full Page Map (011-8239.pdf)

All 34 entries with exact page numbers for drawing + parts list:

| Drawing | Title | Pages |
|---------|-------|-------|
| 101-4042 | Azimuth Actuator — Drawing | p.281 |
| 101-4042 | Azimuth Actuator — Parts List | p.283 |
| 101-4051 | Clevis Shear Pin Kit | p.285 |
| 101-4077 | Elbow Rotary Actuator — Drawing | p.287 |
| 101-4077 | Elbow Rotary Actuator — Parts List | p.289 |
| 101-4163 | Compensator 2-Litre — Drawing | p.291 |
| 101-4163 | Compensator 2-Litre — Parts List | p.295 |
| 101-4182 | **Pitch/Yaw Assembly — Drawing (interchangeable joint)** | p.301 |
| 101-4182 | Pitch/Yaw Assembly — Parts List | p.303 |
| 101-4859 | In-Arm SCE/PCB Controller — Drawing | p.312 |
| 101-4859 | In-Arm SCE/PCB Controller — Parts List | p.313 |
| 101-5723 | Forearm Assembly — Drawing | p.329 |
| 101-5723 | Forearm Assembly — Parts List | p.331 |
| 101-5781 | Master Arm Controller — Drawing | p.332 |
| 101-5781 | Master Arm Controller — Parts List | p.335 |
| 101-5977 | Upper Arm/Shoulder HAWE — Drawing | p.342 |
| 101-5977 | Upper Arm/Shoulder HAWE — Parts List | p.345 |
| 101-5979 | Solenoid Valve HAWE — Drawing | p.347 |
| 101-5979 | Solenoid Valve HAWE — Parts List | p.348 |
| 101-6039 | Wrist Camera T4 NTSC — Drawing | p.349 |
| 101-6039 | Wrist Camera T4 NTSC — Parts List | p.351 |
| 101-6190 | Lock Valve Assembly 3000PSI — Drawing | p.359 |
| 101-6190 | Lock Valve Assembly 3000PSI — Parts List | p.360 |
| 101-6789 | Wrist Actuator — Drawing | p.363 |
| 101-6789 | Wrist Actuator — Parts List | p.365 |
| 101-6790 | T4 Slave Arm General (with torque values) — Drawing | p.368 |
| 101-6790 | T4 Slave Arm General — Parts List | p.372 |
| 101-7282 | Nose Block Piston Kit | p.404 |
| 101-7867 | Jaw Kit — 3 Finger Intermeshing (fitted) | p.417 |
| 025-0102 | T4 Hydraulic Schematic & Map (HAWE) | p.272 |
| 035-0027 | Master Arm Electrical Schematic | p.275 |

**Note:** Pitch and Yaw joints are INTERCHANGEABLE — a pitch joint can be used as a yaw joint and vice versa.

---

## PDF Library — Migration Status

### Local docs location
`/Users/seanbrock/work documents/3. Technical Docs`

### manuals/ directory
- **593 PDFs** total (as of 28 April 2026)
- **~1.3GB** total size
- **Not git tracked** (too large — must be copied manually to vessel)

### Migration completed (April 2026)
- Catalogued 1,590 ROV-relevant PDFs from local docs
- Categorised 548/568 against drawing family knowledge
- Copied 379 new PDFs to manuals/ in one batch run
- 8 files correctly excluded (project tooling, work orders, legacy)
- 391 files now in manuals/ but NOT YET embedded in Supabase

### Excluded files (do not add to manual)
- `ROV-0226-420-xx` — legacy TCU junction box drawings (superseded)
- `ROV-0300-D-0400` — Jupiter valve pack (project tooling, not permanent ROV)
- Work order sign-off sheets (F710, F711)
- Software license PDFs
- `T2Specs.pdf` — T2 manipulator, different system, not fitted

---

## PDF Viewer & Manual Navigation

### How it works
- **Drawings** open in the viewer tab system within the manual (iframe, page-specific)
- **Manuals** open in a new browser tab via `window.open()` with native Ctrl+F
- `manual-viewer.html?manual=FILENAME.pdf` — simple wrapper that opens PDF in new tab
- PDF tab deduplication: same file + different page = separate tab

### Tab system
- Each drawing click opens a new tab at the exact page (e.g., `#page=281`)
- Tab labels show drawing title not filename
- Tabs deduplicated on `file + page` combination
- Max tabs configurable, oldest closed when limit reached

### File protocol support
- Works from `file://` (vessel network drive) and `http://` (local server / Railway)
- Vessel deploy: copy entire `rov-manual/` folder to `N:\15. ROV\3. Technical Docs\`

---

## Admin Panel (`admin.html`)

**Access:** Click the tiny ⚙ gear icon in the top-right of the manual header (subtle — engineers won't hit it accidentally)

**Features:**
- Three-pane layout: Section list | Drawing/manual list | PDF preview
- Click any item → PDF loads instantly in the right pane
- **→ MOVE** button — reassign drawing/manual to different section
- **✕ REMOVE** button — flag as removed (reversible with RESTORE)
- **REMOVED** filter tab — see everything flagged for removal
- **💾 SAVE CHANGES** — downloads `data_patch.js` to apply to index.html
- **📚 DRG NUMBERS** button — opens drawing number reference panel

**Workflow for review:**
1. Open admin panel → click section → scan list
2. Click any item to preview in the right pane
3. Use MOVE or REMOVE as needed
4. SAVE CHANGES → apply patch to index.html

**Current review status:** T4 section reviewed and corrected. Other sections pending admin review.

---

## AI Chatbot

### Architecture
- Model: `claude-sonnet-4-20250514`
- Max tokens: 1000
- System prompt built dynamically per message
- Searches Supabase for relevant chunks and drawings before answering
- Drawing number detection: regex fires on `ROV-xxxx`, `EQP-xxxx`, `101-xxxx` etc.

### System prompt key elements (in priority order)
1. **Drawing family facts** — injected FIRST if drawing number detected in message
2. **System-specific component names** — prevents hallucination of wrong names
3. **Signal path priority** — trace complete path with connectors, cards, protocols
4. **CRITICAL RULE** — never invent part numbers, point to drawing instead
5. **Card description** — injected when engineer is on a specific component card
6. **Relevant chunks** — top 4 chunks from vector search
7. **Relevant drawings** — top 4 drawings from DB

### Known-correct system facts (hardcoded to prevent hallucination)
- Video is analogue Y/C — NOT HD
- Camera signal goes through **video multiplexer** then **fibre uplink** — NOT through TCU
- TCU controls thrusters via **RS485 channels 7 and 8** to Curvetech VP1/VP2
- **PCB-0162** is the TCU thruster control board
- Pod uses **CRNA Interface Card** and **Rainbow rack** at surface
- There is NO "Camera Control Card" or "TCU video card" on this system
- **ROV-0300-D-0440-00 is the HYDRAULIC SCHEMATIC** (3 sheets) — NOT a pod drawing

### Chatbot quality assessment (April 2026)

| Test question | Before fix | After fix | Notes |
|--------------|-----------|----------|-------|
| "No video from camera 1" | 4/10 | 8/10 | Now correctly names multiplexer, CRNA, Rainbow rack |
| "What is ROV-0300-D-0440-00?" | 1/10 | 9/10 | Now correctly says hydraulic schematic |
| "TCU or VP1 fault on port thruster?" | 6/10 | 9/10 | Now correctly says RS485 ch7, PCB-0162 |
| "T4 pitch/yaw o-ring kit" | — | 7/10 | Found actual part numbers from DB, honest about kit number gap |
| "Sonar relay card in pod" | — | 2/10 | Pre-embed run — TMA01030 now has 926 chunks, expect improvement |

**Post embed-run state:** 23,333 chunks across 392 manuals. Full LARS (3,560 chunks), pod interface manual (926 chunks), T4 manual (1,084 chunks), control system (1,552 chunks) all now searchable. Re-test recommended.

### Q&A logging & feedback loop (added May 2026)

Every chatbot response is logged to Supabase `chat_log` with the question, response, retrieved chunks, system prompt, and timestamp. The UI shows GOOD / BAD rating buttons under each answer. BAD opens an inline text input for free-text feedback that updates the same `chat_log` row.

This is the iteration mechanism for the chatbot's known gaps — vessel engineers flag specific misses, Sean reviews the queue via the admin panel's Q&A log view (with CSV export), and feeds confirmed corrections back into the system prompt, MASTER_KNOWLEDGE.md, or targeted re-embedding.

The `knowledge_corrections` table exists for a future engineer-submitted correction flow. **It has no review workflow yet.** Before this is exposed to vessel users, add a `status` column (`pending` / `approved` / `rejected`) so corrections are reviewed rather than auto-incorporated.

---

## Security Architecture (code complete 13 May 2026 — awaiting Railway env var configuration + key rotation)

### State

The frontend password gate, server-side admin auth, and `hmac.compare_digest` constant-time password comparison are all coded and committed. `/api/config` no longer returns any secret keys. The next step is Railway-side: set `APP_PASSWORD` and `ADMIN_PASSWORD` env vars, then rotate the previously-leaked keys.

### Architecture

Two independent password layers, both validated server-side:

| Gate | Env var | Frontend behaviour | Default when env var unset |
|---|---|---|---|
| App-wide | `APP_PASSWORD` | Prompt on page load if `passwordRequired` true; sessionStorage; re-prompt on browser restart; silent reject on wrong password (clear field + brief red flash); 401 from any Railway proxy clears sessionStorage and re-prompts | **Bypass** — app works without password (dev mode) |
| Admin only | `ADMIN_PASSWORD` | Prompt on admin overlay entry; never persisted (re-prompt every admin entry); on 401 shows "Invalid credentials" and clears field | **Deny by default** — admin locked out (destructive ops must never silently grant access) |

The browser never holds Anthropic, Voyage, or Supabase service role keys. All paid-API calls (`/anthropic/messages`, `/voyage/embeddings`) and all service-role-needing Supabase writes (`/supabase/<path>`) route through Flask proxies with the `X-App-Password` header. Direct browser → Supabase reads (`chat_log` writes, `card_index` lookups, `match_chunks` RPC, `lookup_drawing_family` RPC) keep using the public anon key — no Flask round-trip needed.

### Remaining work (Sean's side, in order)

1. Set `APP_PASSWORD` env var in Railway (16+ chars, store in password manager)
2. Set `ADMIN_PASSWORD` env var in Railway (different password, also 16+ chars)
3. Rotate `ANTHROPIC_KEY` (Anthropic console → create new → update Railway env var → test → delete old)
4. Rotate `VOYAGE_KEY` (same pattern)
5. ~~Rotate `SUPABASE_SERVICE`~~ — **DEFERRED 13 May 2026.** Supabase has deprecated the simple legacy regenerate-JWT-secret rotation. The current path requires migrating to new `sb_publishable` / `sb_secret` keys (~30-45 min of code changes in `app.py` and `index.html`, plus client + server testing). Deferred deliberately to avoid big code changes while Claude Designer exploration is running in parallel. **Tracked tech debt** — schedule a focused 1-hour session this week to migrate properly. See "Open work — Supabase key migration" below.
6. End-to-end test in browser

`SUPABASE_ANON` does NOT need rotation — public-by-design.

### Tracked tech debt — Supabase key migration

**Risk accepted today:** the leaked `service_role` JWT remains valid until manual migration to the new keys system. Anyone who captured it from `/api/config` pre-fix can still abuse it (read/write/delete any Supabase row, bypass RLS). The `/api/config` leak is plugged so no NEW exposure happens; this is residual risk from the pre-fix window.

**Migration scope when ready:**
- Server: `app.py` `/supabase/<path>` proxy needs `Authorization: Bearer` header dropped — new sb_secret keys reject it, only `apikey` header is accepted
- Client: every direct browser→Supabase call in `index.html` needs the same change (card_index lookup, chat_log writes, match_chunks RPC, lookup_drawing_family RPC — ~5-6 locations)
- Create new `sb_publishable` and `sb_secret` keys in Supabase Settings → API Keys
- Update Railway env vars (`SUPABASE_ANON` → new publishable value; `SUPABASE_SERVICE` → new secret value)
- Test all Supabase paths end-to-end
- Disable legacy `anon` + `service_role` keys in Supabase dashboard
- Then future Supabase rotations are trivial (same model as Anthropic / Voyage)

---

## Outstanding Tasks — Priority Order (13 May 2026)

### 1. CRITICAL — Complete the security deploy
Code is committed. Outstanding: set `APP_PASSWORD` and `ADMIN_PASSWORD` env vars in Railway, rotate `ANTHROPIC_KEY` + `VOYAGE_KEY` (compromised by the pre-fix `/api/config` leak), end-to-end test. `SUPABASE_SERVICE` rotation deferred as tracked tech debt — see Security Architecture section above. Full sequence in that section.

### 2. CRITICAL — Tree HTML `BASE` path mismatch
`drawing-tree.html`, `control-room-tree.html`, `lars-tree.html`, `pdu-tree.html` hardcode `BASE = 'http://localhost:8765/docs/'` and reference hierarchical paths (`ROV/Mechanical/...`) that only exist in the `rov-manual/docs` symlink target. On vessel `file://` deploy with a flat `manuals/` folder, every PDF link in every tree HTML 404s. Three remediation options documented in `DRAWING_INDEX.md` — design decision needed (rewrite FILES maps to flat filenames vs. ship hierarchical copy vs. accept dev-only).

### 3. CRITICAL — Resolve `rov-manual/docs` symlink before vessel copy
Symlink points to `/Users/seanbrock/work documents/3. Technical Docs - Hercules MK3` — will break or duplicate on copy to vessel drive. Either delete the symlink, replace with a real folder/README, or document the resolution step in the deploy procedure.

### 4. SHORT TERM — Vessel deploy test (sandboxed)
Copy `rov-manual/` to a Windows test machine (not the vessel drive yet). Open in Edge via `file://`. Test: card click → `card_index` sidebar populates; drawing click → PDF tab at correct page; chatbot reaches Railway and answers. Check DevTools Network tab for the Anthropic POST.

### 5. SHORT TERM — Actual vessel deploy to `N:\15. ROV\3. Technical Docs\`
Only after #1, #2, #3, #4 pass. Confirm firewall whitelist for `*.up.railway.app` and `*.supabase.co` if needed.

### 6. SHORT TERM — Re-test chatbot quality
T4 o-rings, sonar relay, LARS questions, HPU schematic questions. Previous scores were pre-embed-run; TMA01030/01031/01071 are now fully searchable.

### 7. SHORT TERM — Admin panel review pass
All sections other than T4. Flag misplaced drawings and duplicates. Save and apply `data_patch.js`.

### 8. SHORT TERM — TCU wiring cross-reference
`ROV-0300-D-0420-90` should appear under both ROV ELECTRICAL (wiring only) and ROV HYDRAULIC (full TCU section, already there).

### 9. MEDIUM TERM — `knowledge_corrections` review workflow
Add `status` column (`pending`/`approved`/`rejected`). Build the admin queue UI before exposing the correction submission to vessel users.

### 10. MEDIUM TERM — Empty LARS/TMS sub-sections
Sliding weight, slip ring, tether — identify available drawings.

### 11. MEDIUM TERM — OCR the 174 scanned PDFs
Tesseract, AWS Textract, or Adobe. Priority candidates: wiring diagrams and parts lists in scanned format.

---

## Session History Summary

### Session 1 (early April 2026)
- Built initial ROV manual structure in index.html
- Created Supabase schema (chunks, drawings, card_index, fault_log, handover_log)
- Embedded first batch of manuals (175 files, 3,612 chunks)
- Built chatbot with signal path priority and vector search

### Session 2 (23 April 2026)
- Fixed PDF tab deduplication (same file + different page = separate tab)
- Tab labels now show drawing title not filename
- Built `manual-viewer.html` — manuals open in new browser tab with native Ctrl+F
- T4 section: mapped all 34 drawings to exact page numbers in 011-8239.pdf
- Added `drawing_families` table (70 rows) with full prefix/series guide and warnings
- Wired drawing family lookup into chatbot (auto-fires on drawing number detection)
- Initial menu restructure by functional discipline

### Session 3 (25 April 2026)
- Major restructure: confirmed technician mental model for menu organisation
- Implemented: Longlines / Control Room / PDU / ROV Electrical/Hydraulic/Mechanical / TMS H15 / TMS H30 / LARS (10 sub-sections) / Manipulators
- Catalogued 1,590 ROV-relevant PDFs from local `work documents/3. Technical Docs`
- Applied drawing family knowledge to categorise 548/568 files
- Copied 379 new PDFs to manuals/ — full migration complete
- Populated 24 DATA sections in index.html from migration plan
- Built `admin.html` with integrated PDF preview, MOVE/REMOVE/RESTORE, DRG NUMBERS reference
- Added `embed_new_files.py` for Cowork batch embed job

### Session 4 (28 April 2026)
- Chatbot quality testing — honest assessment: 4/10 overall before fixes
- Fixed: drawing family context moved to TOP of system prompt (was being ignored when buried)
- Fixed: hardcoded system-specific component names (CRNA, Rainbow rack, PCB-0162, RS485 CH7/CH8)
- Fixed: ROV-0300-D-0440-00 explicitly described as hydraulic schematic (not pod drawing)
- Fixed: hallucinated "TCU video card" and "Camera Control Card" removed from responses
- Re-tested: quality improved to 8-9/10 for signal path and drawing ID questions
- T4 o-ring part numbers test: 7/10 (found actual numbers from DB)
- Sonar relay card test: 2/10 (no chunks in DB yet at that point)
- PROJECT_STATUS.md created with full vision/progress documentation

### Session 5 (29-30 April 2026)
- System prompt expanded with full specific component names: PCB-0124 Video MUX, PCB-0162 TCU board, PCB-0186 FO Interface, CRNA Interface Card, Rainbow rack, RS485 CH7→VP1/CH8→VP2, gyro CON60/RS232 CH2, sonar RS232 CH3, CWDM wavelengths
- Viewer tab bug fixed: tabs now clear when navigating back to main menu
- Root cause identified: `viewer-ph` placeholder being set `display:flex` in `sel()` after every section change, sitting underneath tab overlays and causing blank viewer
- Fix: `viewer-ph` always `display:none` in `sel()` — `renderTabContent` exclusively owns placeholder visibility
- **Embed run completed via Cowork (30 April 2026):**
  - 161 new files embedded successfully, 174 scanned PDFs skipped, 0 errors
  - Database grew: 3,612 → **23,333 chunks**, 175 → **392 manuals**
  - Net gain: +15,483 chunks, +182 manuals
  - TMA01071 LARS manual: 3,560 chunks — full LARS library now searchable
  - TMA01031 Control System Manual: 1,552 chunks — TCU/software fully searchable
  - TMA01030 Interface Systems Manual: 926 chunks — pod interface fully searchable
- PROJECT_STATUS.md updated to reflect post-embed state

### Session 6 (May 2026 — present)
- **Q&A logging built** — every chatbot response written to Supabase `chat_log` with question, response, retrieved chunks, system prompt. GOOD / BAD rating buttons added to every answer. BAD opens inline text input for free-text feedback; BAD events update the same `chat_log` row. Admin panel gains Q&A log view with CSV export. This is the iteration mechanism for chatbot gaps.
- **Card descriptions rewritten** — replaced bloated generic descriptions with factual content from TMA01030: connector IDs, power rails, fault diagnosis paths. Card sidebar now meaningfully useful.
- **Drawing-tree HTMLs added** — `control-room-tree.html`, `drawing-tree.html`, `lars-tree.html`, `pdu-tree.html`. Standalone deep navigation for each major subsystem, linked from main menu.
- **Reorganise script** — `reorganise_tech_docs.py` (482 lines) added with companion task doc. Builds parallel `Technical Docs - Hercules MK3/` folder structure mirroring the manual's functional taxonomy. Auto-renames drawing-number-only PDFs by extracting the title block via pdfminer. Test-first by default, `--full` flag for production run. **Source folder never touched.** Reorganised folder is symlinked into `rov-manual/docs` for in-app browsing.
- **Security infrastructure scaffolded in `app.py`** — `APP_PASSWORD` env var, `@require_password` decorator, `/api/auth` endpoint, `/supabase/<path>` proxy with anon/service key selection. Not yet enabled: `APP_PASSWORD` not set in Railway, `/api/config` still leaks secret keys, frontend prompt UI not built.
- **Vessel deploy plan locked in** — static file copy to `N:\15. ROV\3. Technical Docs\`, not a Flask local instance, not a shortcut. Engineers open `index.html` via `file://`. Manual + viewer fully offline; chatbot + live drawing search require internet to Railway + Supabase.
- **Documentation reset** — `SESSION_HANDOFF.md`, `FILE_INVENTORY.md` added at repo root. `PROJECT_STATUS.md` refreshed.

## Known Issues & Limitations

| Issue | Status | Fix |
|-------|--------|-----|
| 391 files not embedded | ⏳ Pending | Run embed_new_files.py via Cowork |
| match_chunks RPC returns 404 from file:// | Working around | Keyword fallback handles it |
| Chatbot can't answer without embedded data | By design | Embed run will fix most gaps |
| LARS sliding weight, slip ring, tether sections empty | To do | Need drawing identification |
| TCU wiring not cross-linked to ROV Electrical | To do | Add ROV-0300-D-0420-90 to electrical section |
| TMA01030 truncated at page 102 in old embed | To do | Re-embed with --force flag |
| Manual search (removed) | Resolved | Use browser native Ctrl+F |
| Admin panel saves patch file not auto-applies | By design | Manual step for safety |

---

## Vessel Deployment Plan (locked in May 2026)

**Mode: static file copy.** Not a local Flask instance. Not a shortcut to Railway. Hybrid online/offline by design.

**Target path:** `N:\15. ROV\3. Technical Docs\` on the Seven Oceanic Windows network drive.

**What gets copied:**
```
rov-manual/             ← entire folder, verbatim
  index.html
  admin.html
  *-tree.html
  manual-viewer.html
  manuals/  (635 PDFs)
  photos/
  snippets.json
  missing-drawings.md
  (docs symlink — must be resolved before copy)
```

**How engineers use it:**
1. Open `index.html` directly in Edge (`file://`)
2. Navigate the menu to the system / component of interest
3. Click a drawing → opens in viewer tab at the correct page (works offline, PDFs are local)
4. Click a manual → opens in new browser tab with native Ctrl+F (works offline)
5. Ask the chatbot a question → requires internet (Railway proxy → Anthropic)
6. Rate the answer GOOD / BAD; BAD prompts for free-text feedback → logged to `chat_log` for review

**What works offline (no internet):**
- Full menu navigation
- All 635 PDFs in `manuals/`
- Admin panel (move/remove/restore actions, save data_patch.js locally)
- Drawing-tree subsystem indexes

**What requires internet (Railway + Supabase):**
- Chatbot (Anthropic API via Railway proxy)
- Live drawing search via Supabase `match_chunks` / `drawing_families`
- `card_index` sidebar population on card click
- Q&A logging to `chat_log` and rating submissions

**Conscious gaps shipped with the deploy:**
- TMS / longline / cable components: minimal coverage
- Thrusters / Pan & Tilt / Lights: manuals present, drawing links absent
- TMA01030 Interface Systems Manual: previously truncated at p.102 — needs re-embed with `--force`
- TMA01071 LARS Manual: previously truncated at p.10 — re-embedded now via Session 5 run, but verify coverage of latter sections
- The chatbot will be generic or honest about gaps in those areas. Sean (the duty engineer) knows where it's thin. The `chat_log` BAD-rating + free-text feedback IS the iteration mechanism.

**Firewall requirement (Subsea 7 vessel IT):**
HTTPS outbound to `*.up.railway.app` and `*.supabase.co` from vessel PCs. Anthropic and Voyage do NOT need separate whitelisting — they are proxied through Railway.

**Deploy-blocking prerequisites:**
1. Security fix complete (see "Security Architecture" section)
2. `rov-manual/docs` symlink resolved
3. Sandbox test pass on a Windows VM or test PC before touching the actual vessel drive
