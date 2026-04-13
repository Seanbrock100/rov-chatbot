# COWORK TASK — Fix & Complete Manual Embedding into Supabase

## YOUR MISSION
The ROV manual embedding pipeline is broken in two ways:
1. A 50-chunk truncation bug means large manuals are only partially embedded
2. Key manuals are missing from Supabase entirely

Fix the script, clean up bad data, and embed all missing manuals completely.
Do NOT stop on first error. Work through all manuals in priority order.
Report chunk counts after each manual is embedded.

---

## CREDENTIALS (fetch from live app config)
```python
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
VOYAGE_KEY       = cfg['voyageKey']
ANTHROPIC_KEY    = cfg['anthropicKey']
SUPABASE_URL     = cfg['supabaseUrl']       # https://ccjurdnubkmeepaztomy.supabase.co
SUPABASE_SERVICE = cfg['supabaseService']   # service role key (has write access)
```

---

## THE BUG — 50 CHUNK TRUNCATION

Every manual in Supabase stops at exactly 50 chunks (chunk_index 0-49).
This is because embed_manual.py stores chunks in one batch of 50 and exits.

**Current database state (all truncated):**

| Manual | Current chunks | Last page | Problem |
|--------|---------------|-----------|---------|
| TMA01030 - Interface systems manual.pdf | 50 | Pages 134-136 | TRUNCATED - manual is 200+ pages |
| TMA01031 - Control system manual.pdf | 50 | Pages 98-100 | TRUNCATED - manual is 150+ pages |
| 011-8239.pdf (T4 manual) | 50 | Pages 9-11 | TRUNCATED |
| 914-0601-00-Model914-X-Series_UserManual.pdf | 50 | Pages 9-10 | TRUNCATED |
| NIC-OPS-010 - Seven Oceanic Databook.pdf | 100 | Pages 8-10 | DUPLICATED (embedded twice) |
| H15- GA Top Level & Schematics Manual - TMA01028.pdf | 29 | Pages 93-106 | Likely OK (small manual) |
| Aleron VP Manual.pdf | 16 | Pages 9-10 | Likely OK |
| Hercules MK3 Lighting JB manual | 14 | Pages 8-10 | Likely OK |
| ROV Master Knowledge v2.pdf | 10 | Pages 7-8 | Very sparse - 10 chunks only |
| Seven Oceanic ROV Handbook | 5 | Pages 8-10 | Very sparse |
| Hercules Mk3.pdf | 3 | Pages 1-2 | Almost empty |
| 8228_Atlas7r Manual.pdf | 36 | Pages 9-11 | Likely OK |

**Also completely MISSING from Supabase (not embedded at all):**
- TMA01071 - LARS Technical Manual (priority - needed for LARS cards)
- TMA01029 - H30 GA Top Level & Schematics Manual
- ROV-0300-D-0440-00 Hydraulic Diagram documentation
- Any PDU service manuals

---

## STEP 1 — FIX embed_manual.py

The file is at: `/Users/seanbrock/Documents/GitHub/rov-chatbot/embed_manual.py`

Read it first. The bug is in the `embed_and_store` function.
The SUPABASE_BATCH constant (= 50) controls insert batch size, but the loop
that calls insert_chunks appears to exit after first batch.

**Find and fix the loop so it processes ALL chunks, not just the first 50.**

After fixing, verify with this test:
```python
# Create 120 fake chunks and check all 120 get stored
# (dry run - don't actually insert, just trace the loop)
chunks = [{'id': i, 'text': f'chunk {i}'} for i in range(120)]
batches_needed = (len(chunks) + 50 - 1) // 50
print(f"120 chunks needs {batches_needed} batches")  # Should print 3
```

---

## STEP 2 — CLEAN UP NIC-OPS DUPLICATE

Delete all NIC-OPS chunks then re-embed:
```python
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
url, key = cfg['supabaseUrl'], cfg['supabaseService']
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Delete duplicates
r = requests.delete(f'{url}/rest/v1/chunks',
    headers=headers,
    params={'manual_name': 'eq.NIC-OPS-010 - Seven Oceanic Databook.pdf'})
print('Deleted NIC-OPS:', r.status_code)
```

---

## STEP 3 — GET THE MISSING PDFs FROM GOOGLE DRIVE

TMA01030 and TMA01031 exist in Google Drive but the local files are 
just .gdoc shortcut files (177 bytes), NOT actual PDFs.

Use Google Drive search to find and download them:
```
Search Google Drive for: TMA01030 Interface systems manual
Search Google Drive for: TMA01031 Control system manual  
Search Google Drive for: TMA01071 LARS Technical Manual
```

Download each as PDF and save to:
`/Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/manuals/`

Using these exact filenames:
- `TMA01030 - Interface systems manual.pdf`
- `TMA01031 - Control system manual.pdf`
- `TMA01071 - LARS Technical Manual.pdf`

---

## STEP 4 — RE-EMBED TRUNCATED MANUALS

After fixing the bug, re-embed these in priority order.
Use --force flag to delete existing chunks and start fresh.

Check which PDFs exist locally first:
```bash
ls /Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/manuals/*.pdf | head -30
```

**Priority order:**

### 1. TMA01030 (most critical - pod card cross-reference)
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
python3 embed_manual.py \
  --pdf "rov-manual/manuals/TMA01030 - Interface systems manual.pdf" \
  --name "TMA01030 - Interface systems manual.pdf" \
  --force \
  --voyage-key $VOYAGE_KEY \
  --anthropic-key $ANTHROPIC_KEY \
  --supabase-url $SUPABASE_URL \
  --supabase-key $SUPABASE_SERVICE
```

### 2. TMA01031 (control system - pod cards)
```bash
python3 embed_manual.py \
  --pdf "rov-manual/manuals/TMA01031 - Control system manual.pdf" \
  --name "TMA01031 - Control system manual.pdf" \
  --force \
  [same keys]
```

### 3. TMA01071 (LARS - needed for LARS card system)
```bash
python3 embed_manual.py \
  --pdf "rov-manual/manuals/TMA01071 - LARS Technical Manual.pdf" \
  --name "TMA01071 - LARS Technical Manual.pdf" \
  [same keys - no --force as it's new]
```

### 4. 011-8239.pdf (T4 manual - currently truncated)
```bash
python3 embed_manual.py \
  --pdf "rov-manual/manuals/011-8239.pdf" \
  --name "011-8239.pdf" \
  --force \
  [same keys]
```

### 5. 914-0601-00-Model914-X-Series_UserManual.pdf (pan/tilt)
```bash
python3 embed_manual.py \
  --pdf "rov-manual/manuals/914-0601-00-Model914-X-Series_UserManual.pdf" \
  --name "914-0601-00-Model914-X-Series_UserManual.pdf" \
  --force \
  [same keys]
```

### 6. NIC-OPS-010 (re-embed after cleanup in Step 2)
```bash
python3 embed_manual.py \
  --pdf "rov-manual/manuals/NIC-OPS-010 - Seven Oceanic Databook.pdf" \
  --name "NIC-OPS-010 - Seven Oceanic Databook.pdf" \
  [same keys - no --force, already deleted in Step 2]
```

---

## RESILIENCE RULES — CRITICAL

The script may crash on large PDFs. Follow these rules:

1. **On any crash** — check how many chunks were stored before the crash:
```python
r = requests.get(f'{url}/rest/v1/chunks',
    headers=headers,
    params={'manual_name': 'eq.MANUAL_NAME', 'select': 'chunk_index'})
stored_so_far = len(r.json())
print(f'Stored before crash: {stored_so_far}')
```

2. **Do NOT re-run with --force** if partial data exists — you'll lose what was stored.
   Instead fix the bug and resume from where it stopped.

3. **If vision (Claude) API times out** on diagram pages — continue without vision,
   the text-only chunks are still valuable.

4. **Always verify after each manual:**
```sql
SELECT manual_name, COUNT(*) as chunks, MAX(chunk_index) as last_index
FROM chunks
GROUP BY manual_name
ORDER BY manual_name;
```

---

## VERIFICATION — WHAT SUCCESS LOOKS LIKE

After completing all steps, the chunks table should show:

| Manual | Expected min chunks |
|--------|-------------------|
| TMA01030 - Interface systems manual.pdf | 80+ |
| TMA01031 - Control system manual.pdf | 60+ |
| TMA01071 - LARS Technical Manual.pdf | 50+ |
| 011-8239.pdf | 60+ |
| 914-0601-00-Model914-X-Series_UserManual.pdf | 60+ |
| NIC-OPS-010 - Seven Oceanic Databook.pdf | 60+ (no duplicates) |

Run final verification SQL:
```sql
SELECT manual_name, COUNT(*) as chunks,
       MAX(chunk_index) as last_index,
       COUNT(*) / COUNT(DISTINCT chunk_index) as duplicate_ratio
FROM chunks
GROUP BY manual_name
ORDER BY manual_name;
```

`duplicate_ratio` must be 1 for all rows (no duplicates).

---

## COMMIT WHEN DONE
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
git add embed_manual.py
git commit -m "Fix embed_manual.py: resolve 50-chunk truncation bug"
git push origin main
```

Also report back:
- Final chunk counts per manual
- Any manuals that could not be found on Google Drive
- Any manuals that failed to embed and why
- The exact bug you found and how you fixed it
