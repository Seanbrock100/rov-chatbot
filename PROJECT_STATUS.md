# Hercules MK3 ROV Interactive Manual & Chatbot — Project Vision & Progress
**Last Updated:** 28 April 2026
**Author:** Sean Brock / Subsea 7 Seven Oceanic

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
| `rov-manual/index.html` | Main manual — all DATA, menu, chatbot, viewer | 304KB |
| `rov-manual/admin.html` | Admin panel — review/move/remove drawings | 22KB |
| `rov-manual/manual-viewer.html` | PDF viewer wrapper (opens manuals in new tab) | 6KB |
| `rov-manual/manuals/` | 593 PDFs (not git tracked) | ~1.3GB |
| `embed_new_files.py` | Batch embed script for Cowork | 246 lines |

### JS Parse Check Command
```bash
python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"
```

---

## Database State (28 April 2026)

| Table | Count | Notes |
|-------|-------|-------|
| `chunks` | 3,612 | Across 175 embedded manuals |
| `drawing_families` | 70 rows | Full Hercules MK3 prefix/series guide |
| `card_index` | 30 rows | ROV pod card signal path data |
| `drawings` | 194 | 67 mapped to local files |
| `fault_log` | 1,057 | |
| `handover_log` | 4,060 | |

### Supabase RPCs
| Function | Purpose |
|----------|---------|
| `match_chunks(query_text, match_count)` | Vector semantic search across all chunks |
| `lookup_drawing_family(p_query)` | Drawing number family lookup by prefix/series |
| `search_fuzzy(p_manual, p_query, p_limit, p_threshold)` | pg_trgm fuzzy search within a manual |
| `search_part_number(p_manual, p_query, p_limit)` | Exact part number keyword search |

### Embedding Gap
- **PDFs in manuals/:** 593
- **Embedded in DB:** 175 (3,612 chunks)
- **Not yet embedded:** ~391 files (all new migration files)
- **Embed script ready:** `embed_new_files.py` — hand to Cowork to run overnight
- **Model required:** `voyage-large-2` (1536 dimensions — DO NOT use voyage-3 or voyage-3-lite)

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
| "Sonar relay card in pod" | — | 2/10 | No chunks in DB yet — will improve after embed run |

**Fundamental limitation:** 391 files not yet embedded. Chatbot answers from general ROV knowledge + system prompt for unanswered questions. After embed run, quality will increase significantly for component-specific queries.

---

## Outstanding Tasks — Priority Order

### 1. IMMEDIATE — Embed run (hand to Cowork)
```
Run: python3 /Users/seanbrock/Documents/GitHub/rov-chatbot/embed_new_files.py
Log: /tmp/embed_new_files.log
Time: Several hours (391 files, some 100MB+)
```
This is the single biggest quality improvement available. Until it runs, the chatbot cannot answer detailed questions about LARS, TMS H30, Atlas manipulator, HPU compensators, term can wiring, or control room equipment.

### 2. SHORT TERM — Admin panel review
Work through each section in `admin.html`:
- Check for misplaced drawings (e.g., any remaining project tooling in wrong section)
- Flag duplicates (some files copied with different names)
- Save and apply data_patch.js for each session

### 3. SHORT TERM — TCU wiring only in ROV Electrical
Sean's confirmed structure has TCU wiring drawing (ROV-0300-D-0420-90) appearing under BOTH:
- ROV ELECTRICAL (wiring drawing only)
- ROV HYDRAULIC (full TCU section — assembly + wiring + servo valve + schematic)
This cross-reference hasn't been implemented yet — full TCU is only under Hydraulic currently.

### 4. MEDIUM TERM — Chatbot specific knowledge
Add to system prompt once confirmed:
- Which relay card the sonar powers through (currently unknown without embed)
- Camera 1-5 connector assignments in EQP952-0203-DR-PD-55017
- Specific penetrator assignments from pod drawings

### 5. MEDIUM TERM — LARS/TMS sub-section data
LARS has 10 sub-sections in the menu but several are empty (sliding weight, slip ring, tether).
These need drawings/manuals populated once the local docs review identifies what's available.

### 6. LONGER TERM — Vessel deploy test
- Copy `rov-manual/` folder to Windows machine
- Test in Edge via `file://` protocol
- Verify PDF viewer, chatbot (needs internet), and admin panel all function
- Note: Chatbot requires internet to reach Railway + Supabase

---

## Session History Summary

### Session 1 (early April 2026)
- Built initial ROV manual structure
- Created Supabase schema (chunks, drawings, card_index, fault_log, handover_log)
- Embedded first batch of manuals (175 files, 3,612 chunks)
- Built chatbot with signal path priority

### Session 2 (23 April 2026)
- Fixed PDF tab deduplication (same file + different page = separate tab)
- Tab labels now show drawing title not filename
- Built `manual-viewer.html` — manuals open in new browser tab with Ctrl+F
- T4 section: mapped all 34 drawings to exact page numbers (drawing + parts list)
- Added `drawing_families` table (70 rows) with full prefix guide and warnings
- Wired drawing family lookup into chatbot (fires on drawing number detection)
- Restructured menu by functional discipline

### Session 3 (25 April 2026)
- Major restructure: confirmed technician mental model for menu organisation
- Implemented Longlines / Control Room / PDU / ROV Electrical/Hydraulic/Mechanical / TMS H15 / TMS H30 / LARS (10 sub-sections) / Manipulators
- Catalogued 1,590 ROV-relevant PDFs from local `work documents/3. Technical Docs`
- Applied drawing family knowledge to categorise 548/568 files
- Copied 379 new PDFs to manuals/ — full migration complete
- Populated 24 DATA sections in index.html from migration plan
- Built `admin.html` with integrated PDF preview, MOVE/REMOVE/RESTORE, DRG NUMBERS reference
- Added `embed_new_files.py` for Cowork batch embed job
- Database check: confirmed 391 files need embedding

### Session 4 (28 April 2026)
- Chatbot quality testing — honest assessment showed 4/10 overall
- Fixed: drawing family context moved to TOP of system prompt (was being ignored)
- Fixed: hardcoded system-specific facts (CRNA, Rainbow rack, PCB-0162, RS485 ch7+8)
- Fixed: ROV-0300-D-0440-00 explicitly described as hydraulic schematic (not pod drawing)
- Fixed: hallucinated "TCU video card" and "Camera Control Card" removed
- Re-tested: quality improved to 8-9/10 for signal path and drawing ID questions
- Tested experienced technician questions:
  - T4 o-ring part numbers: correctly found from DB (7/10)
  - Sonar relay card: correctly admitted not in DB (2/10 — needs embed run)
- Confirmed: embed run is the single most impactful next step

---

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

## Vessel Deployment Notes

The system is designed to work in two modes:

**Online mode** (internet access):
- Full chatbot via Railway proxy → Anthropic API
- Drawing family lookup via Supabase
- Chunk search (vector) via Supabase

**Offline mode** (vessel intranet only):
- Manual navigation and PDF viewer: fully functional
- Chatbot: NOT available (needs internet)
- Admin panel: fully functional

**Deploy steps:**
1. Copy entire `rov-manual/` folder to vessel network drive
2. Open `index.html` directly in browser (file:// protocol)
3. PDF viewer detects file:// and uses iframe fallback automatically
4. Drawings open at correct pages, manuals open in new tabs with Ctrl+F
