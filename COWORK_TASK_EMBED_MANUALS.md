# COWORK TASK — Embed Remaining Manuals into Supabase (Persistent, Resume-able)

## YOUR MISSION
Embed all missing ROV technical manuals into the Supabase `chunks` table.
The embed script crashes partway through. Your job is to run it, detect failures,
fix them, and keep going until ALL manuals are embedded. Do NOT stop on first error.

## REPO
github.com/Seanbrock100/rov-chatbot

## WHAT'S ALREADY EMBEDDED (DO NOT RE-EMBED)

Already in Supabase chunks table (confirmed):
- 011-8239.pdf (T4 manual) — 50 chunks
- 8228_Atlas7r Manual.pdf (Atlas manual) — 36 chunks  
- 914-0601-00-Model914-X-Series_UserManual.pdf (Pan&Tilt) — 50 chunks
- Aleron VP Manual.pdf — 16 chunks
- H15- GA Top Level & Schematics Manual - TMA01028.pdf — 29 chunks
- Hercules MK3 Lighting JB with Oceantools Lamps - User Manual OR-TE-03338.pdf — 14 chunks
- Hercules Mk3.pdf — 3 chunks
- NIC-OPS-010 - Seven Oceanic Databook.pdf — 100 chunks
- ROV Master Knowledge v2.pdf — 10 chunks
- Seven Oceanic ROV HAndbook.pdf — 5 chunks
- TMA01030 - Interface systems manual.pdf — 50 chunks
- TMA01031 - Control system manual.pdf — 50 chunks

## MANUALS THAT NEED EMBEDDING
The following PDFs are in Google Drive and need to be found, downloaded, and embedded.
Check Google Drive first using the drive_search tool.
Priority order (embed in this sequence):

### HIGH PRIORITY (critical for card cross-reference)
1. TMA01071 - LARS Technical Manual (full)
2. TMA01029 - H30 GA Top Level & Schematics Manual
3. ROV-0300-D-0440-00 Hydraulic Diagram (all sheets)
4. TCU Manual / ROV-0300-D-0420-90 documentation

### MEDIUM PRIORITY
5. Any PDU manuals not yet embedded
6. TMS (Tether Management System) manual if available
7. HPU service manual if available

## HOW TO RUN THE EMBED SCRIPT

### Prerequisites
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
# Get API credentials
python3 -c "import requests; cfg=requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json(); print('SUPABASE_URL:', cfg['supabaseUrl'][:40]); print('Key present:', bool(cfg.get('voyageKey')))"
```

### The embed script (embed_manual.py) usage
```bash
python3 embed_manual.py "path/to/manual.pdf" "Manual Display Name"
```

### CRITICAL — The script crashes on large PDFs. Here is a RESILIENT wrapper:
Write a new script called `embed_resilient.py` that:
1. Calls embed_manual.py page-by-page or in batches of 10 pages
2. On any error: logs the error, waits 5 seconds, retries up to 3 times
3. On persistent failure: skips that page/batch, logs it, continues with next
4. At the end: reports total chunks embedded and any skipped pages
5. Checks Supabase FIRST to see if manual is already partially embedded
6. Only embeds pages that aren't already in the chunks table

### Checking what's already embedded for a specific manual:
```python
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
supabase_url = cfg['supabaseUrl']
supabase_key = cfg['supabaseKey']

headers = {'apikey': supabase_key, 'Authorization': f'Bearer {supabase_key}'}
r = requests.get(f"{supabase_url}/rest/v1/chunks?manual_name=eq.TMA01071-LARS.pdf&select=page_label", headers=headers)
print(f"Already embedded pages: {len(r.json())}")
```

## VERIFICATION FOR EACH MANUAL
After embedding each manual, confirm:
```sql
SELECT manual_name, COUNT(*) as chunks 
FROM chunks 
WHERE manual_name = 'MANUAL_NAME_HERE'
GROUP BY manual_name;
```
Expected: at least 20+ chunks for a substantial manual.

## WHAT TO REPORT BACK
For each manual attempted:
- Manual name
- Number of chunks now in Supabase
- Any pages/sections that failed and why
- Whether it was already partially embedded

## DO NOT
- Do not delete existing chunks
- Do not re-embed manuals already in the table (check first)
- Do not stop if one manual fails — move to the next
- Do not embed the same pages twice
