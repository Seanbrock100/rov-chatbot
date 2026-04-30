# ROV Chatbot & Interactive Manual — Master Project Summary
**Prepared: 09 Apr 2026 | Author: Sean Brock | Platform: Claude + Desktop Commander**

---

## 1. PROJECT OVERVIEW

Two connected tools built for the Hercules MK3 ROV fleet (HE15/HE30) aboard Seven Oceanic:

### Tool A — ROV Agentic Chatbot
A web-based AI chatbot that answers technical questions by searching indexed ROV manuals, drawings, fault logs, and handover reports. Live at:
`https://rov-chatbot-production-3d66.up.railway.app`

### Tool B — Interactive Technical Manual
An offline-capable HTML manual with clickable schematics, drawing access, and pre-generated AI component descriptions. Located at:
`rov-manual/index.html` (copy to vessel network drive with `manuals/` folder)

---

## 2. TECH STACK

| Component | Technology |
|-----------|-----------|
| Frontend (chatbot) | `rov_agentic_chatbot.html` — single-file HTML/JS |
| Frontend (manual) | `rov-manual/index.html` — single-file HTML/JS |
| Backend | Flask (`app.py`) on Railway |
| Vector DB | Supabase (ccjurdnubkmeepaztomy.supabase.co) |
| Embeddings | Voyage AI `voyage-large-2` |
| LLM | Anthropic `claude-sonnet-4-20250514` |
| PDF rendering | pdf.js 3.11.174 (CDN) |
| Repo | github.com/Seanbrock100/rov-chatbot |
| Deploy | Railway (auto-deploy on git push, ~60s) |
| Build stamp | Pre-push git hook auto-updates timestamp |

---

## 3. FILE INDEX

### Repository Root
```
rov-chatbot/
├── app.py                        Flask backend — API endpoints, tool routing
├── rov_agentic_chatbot.html      Chatbot UI — agentic tool-use loop
├── index.html                    Redirect page (points to chatbot)
├── Procfile                      Railway start command
├── requirements.txt              Python dependencies
├── ROV Master Knowledge v2.docx  Master knowledge base (needs re-embed after corrections)
├── embed_manual.py               Script: embed PDF manuals into Supabase chunks table
├── index.html                    (root redirect)
├── SCRIPTS_REFERENCE.md          Full script usage guide + Drive audit backlog
├── RUN_EMBED_MANUALS.sh          Batch script: embed 13 manual groups overnight
├── RUN_INDEX_DRAWINGS.sh         Batch script: index 6 drawing folders (batch 1)
├── RUN_INDEX_DRAWINGS_BATCH2.sh  Batch script: index 11 drawing folders (batch 2)
└── PROJECT_SUMMARY.md            This file
```

### Interactive Manual (`rov-manual/`)
```
rov-manual/
├── index.html                    The interactive manual (single deployable file)
├── descriptions.json             Raw AI descriptions — 53 entries (source)
├── descriptions_norm.json        Normalised AI descriptions — offline lookup key/value store
├── snippets.json                 System overview snippets (legacy, now inline in index.html)
├── photos/                       ROV and component photos (populate on vessel)
│   └── rov_overview.jpg          (PENDING — take photo of ROV on vessel)
└── manuals/                      ALL PDFs flat in one folder — 112 files
    ├── EQP952-0203-DR-PD-55000.pdf   Electronics Pod Assembly GA
    ├── EQP952-0203-DR-PD-55001.pdf   Control Chassis Assembly GA
    ├── EQP952-0203-DR-PD-55002.pdf   Payload Chassis Assembly GA
    ├── EQP952-0203-DR-PD-55003.pdf   Control Penetrator Ring GA
    ├── EQP952-0203-DR-PD-55004.pdf   Payload Penetrator Ring GA
    ├── EQP952-0203-DR-PD-55016.pdf   Payload Chassis Wiring Diagram
    ├── EQP952-0203-DR-PD-55017.pdf   Control Chassis Wiring Diagram
    ├── ROV-0311-D-0212-00.pdf         CWDM Assembly
    ├── ROV-0300-D-0420-90 TCU Wiring Diagram.pdf
    ├── H15- GA Top Level & Schematics Manual - TMA01028.pdf
    ├── H30 - GA Top Level & Schematics Manual - TMA01029.pdf
    └── ... 101 more PDFs (all flat, no subfolders)
```

---

## 4. SUPABASE DATABASE

**Project:** ccjurdnubkmeepaztomy.supabase.co

| Table | Contents | Count | Search Method |
|-------|----------|-------|---------------|
| `chunks` | Manual text chunks with embeddings | ~413 chunks, 12 manuals | Vector similarity (`match_chunks` RPC) |
| `drawings` | Drawing metadata with embeddings | ~194 drawings | Vector similarity (`match_drawings` RPC) |
| `fault_log` | H15+H30 sub-engineer fault logs 2012–present | 1,031 entries | ILIKE text search |
| `handover_log` | End-of-trip handover reports 2023–2026 | ~1,015 entries | ILIKE text search |

**Chatbot tools:**
- `search_manuals` → chunks table
- `search_drawings` → drawings table
- `search_fault_log` → fault_log table
- `search_handover_log` → handover_log table

---

## 5. CHATBOT AGENTIC TOOL-USE FLOW

```
User question
  → Claude selects relevant tools
  → Tool calls (1–4 tools per query)
  → Results synthesised into answer
  → Citations shown with drawing numbers
```

Supported query types: fault finding, drawing lookup, spec queries, handover history, outstanding jobs, component descriptions.

---

## 6. INTERACTIVE MANUAL — NAVIGATION LAYERS

```
Layer 1: ROV photo → click → system menu (all components)
Layer 2: Component page
  ├── For Electronics Pod: Pod schematic SVG (both chassis)
  │     ├── Click chassis → Layer 3 (chassis detail)
  │     └── Click penetrator ring oval → opens ring GA PDF
  └── For all others: Drawing list + manual list in sidebar

Layer 3: Chassis detail view (Electronics Pod only)
  ├── LEFT: Penetrator ring GA PDF rendered via pdf.js (click → open full PDF)
  ├── CENTRE: Card list SVG — each card clickable
  └── SIDEBAR: Card list with "▶ VIEW DETAILS" for each card

Layer 4: Card info panel (click any card)
  ├── LEFT: AI-generated component description (loaded from descriptions_norm.json — OFFLINE)
  └── RIGHT: Related drawings list (click → open PDF in new tab)
```

---

## 7. SEAN'S INPUTS & CORRECTIONS (TECHNICAL GROUND TRUTH)

These corrections came directly from Sean reviewing actual drawings on the vessel. They override any earlier AI-generated assumptions.

### Electronics Pod — Confirmed from 55016/55017

**Camera system:**
- All 8 cameras are **coaxial** — SIGNAL(Y) + SIGNAL(C) on 8-pin Mini Burton 5929-0207-PE04
- **24V power comes from Camera PSU via backplane** — NOT through the penetrator ring
- Focus Hi/Lo signals also via the 8-pin connector
- Video MUX PCB handles the coax routing

**Thruster signal routing:**
- Thrusters get their servo valve signals from the **TCU PCB card in the control chassis** via the penetrator ring (CON28/CON29, 12-pin Burton 5507-2412-PE04)
- The thruster cable carries the servo signal — not a separate dedicated penetrator

**Serial channel table (confirmed from 55017):**
- CH1 RS232 — T4 Manipulator
- CH2 RS232 — Gyro (Octans Nano)
- CH3 RS232 — Tritech Sonar
- CH4 TTL — Responder
- CH5 RS232 — Digiquartz Depth (**primary ROV depth sensor**)
- CH6 RS232 — Altimeter/DVL
- CH7 RS485 — Valve Pack 1
- CH8 RS485 — Valve Pack 2
- CH9 RS232 — Lights JB (+ 110Vac L/N ×2 + coax ×2)
- CH10 RS232 — Tooling (V1–V8 servo + 24V inst + HPU press + TCU WI)

**DIGIQ (station table label):** = Digiquartz depth sensor (not "digital cameras")

**Compensators:** Analogue 0–10V sensors in the compensators themselves (not digital), 4-off

**Payload ring (55004):**
- Atlas manipulator on **CH10** (RS232 + 24V HP 10A)
- Remaining channels project-reserved for sonars, DVL, ROV nav, PHINS
- "Sensors & Control 24V" ports = available for future tooling (not currently wired)

### Electronics Pod GA Drawing Layout (from 55001/55002)

**55001 Control Chassis — left to right:**
- LEFT: Penetrator ring (oval flange, CB plate strip, two PSU blocks visible in end view)
- PSU column: SLE124, SLE112, MAX315, MAX124×4
- PCB rows: 155MHz Fibre I/F, Relay&HK ×2, TCU Control, Camera Control
- Centre-right: Sensors & Ctrl 24V ×2, Camera PSU ×2, Video MUX
- CWDM RED assembly + Band Splitter + Sixnet 9-port
- RIGHT (Section F-F): Gyro cover plate, 4× D-sub 25-way, 3× fans

**55002 Payload Chassis — left to right:**
- LEFT: Penetrator ring (same oval flange style)
- PSU bank: 24V/1a, 24V/1b, PSU2 MAX315, PSU3–6 MAX124×4, 24V/1c, 24V/1d
- Cards: Payload Backplane + Relay&HK, 155MHz Fibre I/F (1370nm), Generic Interface PCB
- RIGHT: 10-slot fibre module cage (MOD 1–10, two columns — Part Section C-C), Sixnet 10-port, fans

### File/Folder Structure (Sean's confirmed approach)
- **All PDFs flat in `manuals/` folder** — no subfolders
- `descriptions_norm.json` alongside `index.html` for offline descriptions
- No live API calls in the manual — fully offline on vessel network drive
- pdf.js loads from CDN (needs internet) OR can be bundled locally if needed

---

## 8. KNOWN ISSUES / BUGS FIXED THIS SESSION

| Issue | Fix | Commit |
|-------|-----|--------|
| JS parse error — page unclickable | Rewrote `buildChassisSVG` without nested template literals | `e0b71b9` |
| Pen ring SVG was oval with holes | Replaced with circular face-on annulus matching actual drawing | `830ed81` |
| Pen ring still schematic not real GA | Replace SVG with pdf.js canvas rendering actual GA PDF | `61f4419` |
| All drawing paths used `manuals/drawings/...` subdirectory that doesn't exist | 106 path fixes to flat `manuals/` structure | `94d9730` |
| Card click triggered live API call | Replaced with offline `descriptions_norm.json` reader | `94d9730` |
| `openMenu` function deleted by edit | Restored | `909b70e` |
| CWDM wavelength error (1490→1550nm) in master knowledge doc | Noted — **ROV Master Knowledge v2.docx needs re-embedding** | Pending |

---

## 9. PENDING TASKS

### High Priority
- [ ] **Re-embed ROV Master Knowledge v2.docx** after correcting CWDM 1490nm→1550nm error
- [ ] **Run RUN_EMBED_MANUALS.sh** overnight to embed remaining 13 manual groups
- [ ] **Run RUN_INDEX_DRAWINGS.sh + RUN_INDEX_DRAWINGS_BATCH2.sh** to index 17 drawing folders
- [ ] **Copy `rov-manual/` to vessel network drive** (index.html + descriptions_norm.json + manuals/ folder)
- [ ] **Take ROV overview photo** → save as `rov-manual/photos/rov_overview.jpg`

### Medium Priority
- [ ] **Add fault_log semantic search** — add voyage-large-2 embeddings to fault_log description column
- [ ] **Layer 2 review for non-pod components** — TCU, HPU, Valve Packs, LARS, TMS pages need drawings populated
- [ ] **Add component photos** for Layer 2 pages (take on vessel)
- [ ] **Verify handover_log categorisation** — re-run recategorise_v2.py if 'general' count still high

### Future
- [ ] **Jarvis assistant** — Home Assistant MCP backbone personal assistant (separate project)
- [ ] **Bundle pdf.js locally** — for fully offline operation without CDN dependency
- [ ] **Expand descriptions.json** — add descriptions for TCU, HPU, LARS, TMS components as Layer 2 develops

---

## 10. DEPLOY / UPDATE WORKFLOW

```bash
# Make changes to any file
git add -A
git commit -m "description"
git push origin main
# Railway auto-deploys in ~60 seconds
# Build stamp auto-updates via pre-push hook
```

**Manual update on vessel:**
1. `git pull` on Mac
2. Copy `rov-manual/index.html`, `rov-manual/descriptions_norm.json`, `rov-manual/descriptions.json`
3. Copy `rov-manual/manuals/` (all 112 PDFs flat)
4. Paste to `\\server\ROV-Manual\`
5. Open in Edge

---

## 11. TASKS SUITABLE FOR COWORK OFFLOAD

The following tasks are well-defined, self-contained, and can be delegated to Cowork as a sub-agent with clear verification criteria:

### COWORK TASK 1 — Layer 2 Drawings Population
**Task:** Populate the `DATA` object in `rov-manual/index.html` with correct drawing entries for all non-pod components: TCU, HPU, Valve Packs, Thrusters, ROV Lights, ROV Term Can, Frame, T4 Manip, Atlas Manip, Pan & Tilt, TMS (all variants), LARS (all variants), Control Console, Control Room, PDU, Longline, Cables.
**Input:** The flat file list from `rov-manual/manuals/` (112 PDFs already known)
**Output:** Updated `DATA` object with all drawing entries mapped to actual filenames
**Verify:** Each drawing entry's `file:` path must exist in `rov-manual/manuals/`

### COWORK TASK 2 — Descriptions Generation for All Components
**Task:** Generate `descriptions.json` entries for all non-pod components listed in SNIPPETS (TCU, HPU, Valve Packs, Thrusters, etc.) using the same format as existing entries.
**Input:** `descriptions.json` format, SNIPPETS text as context, component names
**Output:** Additional entries in `descriptions_norm.json`
**Verify:** All keys match the format `zone/normalised-name`, prose quality

### COWORK TASK 3 — Fault Log Embedding Script
**Task:** Write a Python script that reads `fault_log` entries from Supabase, generates voyage-large-2 embeddings for the `description` field, and updates the table with a new `embedding` column.
**Input:** `embed_manual.py` as reference, Supabase credentials from `/api/config`
**Output:** A working `embed_fault_log.py` script
**Verify:** Run on 10 test records, confirm embeddings stored, confirm match_chunks-style RPC query works

### COWORK TASK 4 — Manual Embed Backlog
**Task:** Run `RUN_EMBED_MANUALS.sh` against the PDFs in Google Drive (once synced to Mac) and confirm all 13 manual groups are embedded.
**Input:** `SCRIPTS_REFERENCE.md` for script usage, list of pending manuals
**Output:** Confirmed chunk counts in Supabase for each manual group
**Verify:** Query Supabase chunks table, confirm counts per manual source

---

## 12. CORRECTIONS SUMMARY FOR NEW CHAT CONTEXT

When starting a new chat, paste this block to restore context:

```
PROJECT: Hercules MK3 ROV chatbot + interactive manual
VESSEL: Seven Oceanic (Subsea 7) — HE15/HE30
REPO: github.com/Seanbrock100/rov-chatbot
LIVE URL: https://rov-chatbot-production-3d66.up.railway.app
SUPABASE: ccjurdnubkmeepaztomy.supabase.co
DEPLOY: git push → Railway auto-deploy ~60s

CONFIRMED TECHNICAL FACTS (from actual drawings):
- Cameras 1-8: 8-pin Mini Burton 5929-0207-PE04, coax video Y/C + 24V via backplane (NOT through ring)
- TCU servo valve signals exit control ring via CON28/CON29 (12-pin Burton 5507-2412-PE04)
- CH1=T4, CH2=Gyro, CH3=Sonar, CH4=Responder TTL, CH5=Digiquartz Depth, CH6=Alt/DVL, CH7=VP1 RS485, CH8=VP2 RS485, CH9=Lights, CH10=Tooling
- Atlas manipulator on payload ring CH10 (RS232 + 24V HP 10A)
- Remaining payload ring channels = project-reserved
- All PDFs flat in manuals/ folder (no subfolders)
- descriptions_norm.json = offline AI descriptions (53 entries, all pod cards + ring connections)
- No live API calls in the manual — fully offline

CURRENT BUILD: 09 Apr 2026 18:05 UTC (commit 94d9730)
```
