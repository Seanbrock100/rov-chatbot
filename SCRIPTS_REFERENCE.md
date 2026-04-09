# ROV Chatbot — Scripts & Pipeline Reference

*Permanent reference document. Keep this updated when new scripts are created.*

---

## Repository Location

```
/Users/seanbrock/Documents/GitHub/rov-chatbot/
```

**Git push (SSH configured — no password needed):**
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
git add . && git commit -m "message" && git push origin main
```
Railway auto-deploys ~60 seconds after push.

---

## Deployed Application

| Item | Value |
|---|---|
| Live URL | https://rov-chatbot-production-3d66.up.railway.app |
| Health check | https://rov-chatbot-production-3d66.up.railway.app/health |
| GitHub | github.com/Seanbrock100/rov-chatbot |
| Hosting | Railway (Flask + Gunicorn) |
| Database | Supabase — ccjurdnubkmeepaztomy.supabase.co |
| Embeddings | Voyage AI — voyage-large-2 (1536 dimensions) |
| Chatbot AI | Anthropic — claude-sonnet-4-20250514 |

---

## Supabase Tables

| Table | Contents | Search Method |
|---|---|---|
| `chunks` | Embedded manual text chunks | Vector similarity (match_chunks RPC) |
| `drawings` | Indexed drawings + cable drawings | Vector similarity (match_drawings RPC) |
| `fault_log` | H15 + H30 Sub Engineer Log entries 2012–present | ilike text search on `description` |
| `handover_log` | End of trip reports 2023–2026 | ilike text search on `content` |

---

## Script 1 — `embed_manual.py`

**Location:** `/Users/seanbrock/Documents/GitHub/rov-chatbot/embed_manual.py`
**In repo:** Yes

**Purpose:** Embeds a PDF technical manual into the Supabase `chunks` table.
Two-pass pipeline:
- Pass 1: pdfplumber extracts text from readable pages
- Pass 2: Claude vision (claude-opus-4) extracts content from diagram/image-heavy pages
- Each page chunk embedded via Voyage AI, stored with page number metadata

**Usage:**
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
export VOYAGE_KEY="pa-..." ANTHROPIC_KEY="sk-ant-..." SUPABASE_SERVICE="eyJ..."

python3 embed_manual.py --pdf "/full/path/to/manual.pdf" --name "Display Name"
```

**Requirements:** `pip install pdfplumber requests` + `brew install poppler`

**Writes to `chunks`:** `manual_name, chunk_index, start_page, end_page, page_label, text, embedding(1536)`

**Manuals already embedded (12):**
011-8239, Atlas7r Manual, Model914-X-Series, Aleron VP, H15-GA TMA01028, Hercules MK3 Lighting JB,
Hercules Mk3, NIC-OPS-010 Seven Oceanic Databook, ROV Master Knowledge v2,
Seven Oceanic ROV Handbook, TMA01030 Interface systems, TMA01031 Control system

**Still to embed:** Bowman heat exchanger, SMD Valve packs, IXBlue Octans Nano Gyro,
LARS TMA01071, Winch H15/H30 manuals, Control Room Sixnet manuals, tcu.pdf, Cardev filter

---

## Script 2 — `index_drawings.py`

**Location:** `/Users/seanbrock/index_drawings.py`
**In repo:** No — runs locally on Mac only (accesses Google Drive mirror)

**Purpose:** Indexes PDF drawings into Supabase `drawings` table. Rasterises each PDF page
via pdftoppm, sends to Claude vision for metadata extraction, embeds via Voyage AI.

**Usage:**
```bash
export ANTHROPIC_KEY="sk-ant-..." VOYAGE_KEY="pa-..." SUPABASE_SERVICE="eyJ..."
python3 /Users/seanbrock/index_drawings.py --folder "Subfolder/Name"
# Folder is relative to: .../My Drive/Work Technical Docs/
```

**Writes to `drawings`:** `drawing_number, title, system, description, drive_url, folder_name, embedding(1536)`

**Drive URL format:** `https://drive.google.com/drive/search?q=FILENAME.pdf`

**Already indexed (~172 drawings):**
- Herc Drawings/Herc15-30-MK III Drawings (~77 — ROV-0311, HCV-0015, PDU series)
- Cables/ folder (73 cable drawings — CAB-xxxx, ROV cables, camera, gyro, laser etc.)
- Pod Changes/ (10 mod sketches — EQP952-0203-DR-PD-54xxx, ROV-0311-D-0203/0204, with supersedes flags)
- POD Drawing post update 2025/ (12 — EQP952-0203-DR-PD-55xxx, current versions)

**Still to index:** Control Room/Console wiring, Lars/Latch Beam, Winch/H15, Winch/H30

**Key behaviour:** Skips already-indexed files. Pod Changes tagged with supersedes context.
Uses pdftoppm to rasterise before Claude vision.

---

## Script 3 — `ingest_fault_log.py`

**Location:** `/tmp/ingest_fault_log.py`
**In repo:** No — one-time ingestion, keep at /tmp for re-runs

**Purpose:** Reads Herc 15 and H30 Sub Engineer Log XLS workbooks, extracts all section sheets,
inserts into Supabase `fault_log` table.

**Source files:**
```
.../Sub Eng Logs/HERC 15/Herc 15 Sub Eng Log.xls
.../Sub Eng Logs/HERC 30/Herc 30 Sub Eng Log.xls
```

**Usage:** `python3 /tmp/ingest_fault_log.py`
(Fetches Supabase config automatically from deployed Railway app)

**Requirements:** `pip install xlrd --break-system-packages`

**Skips:** Structure-Buoyancy, PID, Fibers Routing, Running Hours, Re-Term Log, SAP IDs

**Writes to `fault_log`:** `vehicle (H15/H30), log_date, section, description, engineer, gomars_ref, source_file`

**Current row count:** 1,031 entries

**Known quirk:** Some sheets use col 8 for description (wide-format). Script detects dynamically.

---

## Script 4 — `ingest_handover.py`

**Location:** `/tmp/ingest_handover.py`
**In repo:** No — one-time ingestion

**Purpose:** Reads end-of-trip Word documents (2023–2026), extracts sections, auto-categorises
each block via Claude Haiku (fault/maintenance/outstanding/watchout/general), inserts into
Supabase `handover_log` table.

**Source files:** `.../end of trip reports/End of Trip Reports/2023–2026/`

**Usage:**
```bash
nohup python3 /tmp/ingest_handover.py > /tmp/handover_log.txt 2>&1 &
```

**Requirements:** `pip install python-docx --break-system-packages`

**Handles two formats:**
- Old (2022–2023): free-form paragraphs under headings
- New (2024–present): table-based, Item/Details columns, engineer names in final table

**Writes to `handover_log`:** `trip_start, trip_end, outgoing_engineer, incoming_engineer, vessel, section, content, category, source_file`

**Current row count:** ~1,015 entries

**Important:** Claude Haiku wraps JSON in markdown fences.
Strip with: `re.sub(r'^\`\`\`(?:json)?\s*', '', text.strip())`

---

## Script 5 — `recategorise_v2.py`

**Location:** `/tmp/recategorise_v2.py`
**In repo:** No — maintenance/utility script

**Purpose:** Re-runs categorisation on all `handover_log` entries. Use when initial ingestion
failed to categorise correctly.

**Usage:**
```bash
nohup python3 /tmp/recategorise_v2.py > /tmp/recat_log.txt 2>&1 &
```

**Check category status:**
```python
import requests
r = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
h = {'apikey': r['supabaseAnon'], 'Authorization': f'Bearer {r["supabaseAnon"]}', 'Prefer': 'count=exact'}
for cat in ['fault','maintenance','outstanding','watchout','general']:
    res = requests.get(f'{r["supabaseUrl"]}/rest/v1/handover_log', headers=h,
        params={'category': f'eq.{cat}', 'select': 'id'})
    print(f'{cat}: {res.headers.get("Content-Range","?").split("/")[-1]}')
```

---

## Chatbot Tools — Routing Rules

| Tool | Table | Trigger |
|---|---|---|
| `search_manuals` | `chunks` (vector) | Fault-finding, specs, procedures, technical details |
| `search_drawings` | `drawings` (vector) | "Show me drawing", drawing numbers, "cable for X" |
| `search_fault_log` | `fault_log` (ilike) | "Has this happened before", historical faults, recurring issues |
| `search_handover_log` | `handover_log` (ilike) | Outstanding jobs, recent trips, handover history |

`search_fault_log` accepts optional `vehicle` filter: `H15` or `H30`
`search_handover_log` accepts optional `category` filter: fault/maintenance/outstanding/watchout

---

## Loading API Keys (all scripts)

All ingestion scripts auto-load from the deployed Railway app:
```python
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
# cfg keys: anthropicKey, voyageKey, supabaseUrl, supabaseAnon, supabaseService
```

For embed_manual.py / index_drawings.py (need env vars):
```bash
eval $(python3 -c "
import requests, json
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
print(f'export VOYAGE_KEY={cfg[\"voyageKey\"]}')
print(f'export ANTHROPIC_KEY={cfg[\"anthropicKey\"]}')
print(f'export SUPABASE_SERVICE={cfg[\"supabaseService\"]}')
")
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| Railway not redeploying | Push didn't trigger | `git commit --allow-empty -m "trigger" && git push origin main` |
| `Expecting value` JSON error | Haiku wraps JSON in fences | Strip backticks before json.loads() |
| Zero rows from section sheet | Description in col 8 not col 1 | Dynamic col detection in ingest_fault_log v2 |
| Background script no log | Python stdout buffering | Run with `python3 -u script.py` |
| Module not found | Missing pip packages | `pip3 install PACKAGE --break-system-packages` |

---

## Standard Workflows

### Add a new manual:
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
# Set keys (see above)
python3 embed_manual.py --pdf "/full/path/FILE.pdf" --name "Display Name"
```

### Add new drawing folder:
```bash
# Set keys
python3 /Users/seanbrock/index_drawings.py --folder "Folder/Relative/To/Work Technical Docs"
```

### Add new handover reports (annual):
```bash
# Update the year range in ingest_handover.py then re-run
nohup python3 /tmp/ingest_handover.py > /tmp/handover_log.txt 2>&1 &
```

---

*Last updated: April 2026*
