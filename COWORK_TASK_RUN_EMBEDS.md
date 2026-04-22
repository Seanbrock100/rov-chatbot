# COWORK TASK — Run RUN_EMBED_MANUALS.sh (Overnight Embed Run)

## YOUR MISSION
Run the overnight manual embedding script to push ~75 PDFs from Google Drive
into Supabase as vector chunks. The script is already fixed and resilient.
Monitor it, report chunk counts when done.

## REPO
github.com/Seanbrock100/rov-chatbot

---

## WHAT THIS DOES
Embeds 13 groups of technical manuals into the Supabase `chunks` table
so the chatbot can search them. Each PDF is chunked, vision-processed for
diagrams, and embedded via Voyage AI into a 1024-dim vector.

Estimated runtime: 2–4 hours depending on PDF sizes and API latency.

---

## STEP 1 — VERIFY GOOGLE DRIVE IS SYNCED

Check the Drive folder exists and has files:
```bash
ls "/Users/seanbrock/Library/CloudStorage/GoogleDrive-seanbrock100@gmail.com/My Drive/Work Technical Docs/" | head -20
```

If the Drive folder is missing or empty, stop and report back.
Do NOT proceed if Drive is not mounted.

---

## STEP 2 — CHECK WHAT'S ALREADY EMBEDDED

Before running, check the current state so you can compare after:
```python
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
url, key = cfg['supabaseUrl'], cfg['supabaseService']
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

r = requests.get(f'{url}/rest/v1/chunks?select=manual_name&limit=2000', headers=headers)
from collections import Counter
counts = Counter(row['manual_name'] for row in r.json())
print(f"Currently {len(counts)} manuals, {sum(counts.values())} total chunks")
for name, count in sorted(counts.items()):
    print(f"  {count:4d}  {name}")
```

Save this output — you'll compare it at the end.

---

## STEP 3 — RUN THE SCRIPT

The script is at:
`/Users/seanbrock/Documents/GitHub/rov-chatbot/RUN_EMBED_MANUALS.sh`

Run it in the background so it survives session timeouts:
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
nohup bash RUN_EMBED_MANUALS.sh > /tmp/embed_log.txt 2>&1 &
echo "PID: $!"
```

Note the PID. The script will run for 2-4 hours.

---

## STEP 4 — MONITOR PROGRESS

Check the log periodically:
```bash
# See last 30 lines of log
tail -30 /tmp/embed_log.txt

# Count how many sections have started
grep "^===" /tmp/embed_log.txt

# Check for failures
grep "⚠" /tmp/embed_log.txt

# Check if still running (replace PID)
ps aux | grep embed
```

Check every 30 minutes. Report if more than 3 consecutive failures appear.

---

## STEP 5 — VERIFY WHEN COMPLETE

The script prints "=== All embed_manual runs complete ===" when done.

Then run the verification query from Step 2 again and compare.
Also run this summary:
```sql
SELECT 
  manual_name,
  COUNT(*) as chunks,
  MAX(chunk_index) as last_index
FROM chunks
WHERE created_at > NOW() - INTERVAL '8 hours'
GROUP BY manual_name
ORDER BY COUNT(*) DESC;
```

---

## STEP 6 — HANDLE THE TCU STUB

After the main run completes, check if TMA01031 already covers TCU content:
```bash
# Search chunks for TCU content from TMA01031
python3 -c "
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
url, key = cfg['supabaseUrl'], cfg['supabaseService']
r = requests.post(f'{url}/rest/v1/rpc/match_chunks',
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'},
    json={'query_text':'TCU thruster control unit servo valve PCB-0162','match_count':5})
for c in r.json():
    print(c['manual_name'], c['page_label'], ':', c['text'][:100])
"
```

If TMA01031 returns good TCU content → tcu.pdf stub is fine, leave it.
If TMA01031 returns nothing relevant → re-embed tcu.pdf:
```bash
DRIVE="/Users/seanbrock/Library/CloudStorage/GoogleDrive-seanbrock100@gmail.com/My Drive/Work Technical Docs"
python3 embed_manual.py --pdf "$DRIVE/tcu/tcu.pdf" --name "TCU Manual" --force
```

---

## WHAT TO REPORT BACK

1. Final chunk counts per manual (from Step 5 query)
2. Any sections that failed completely (grep "⚠" output)
3. Total new chunks added (compare Step 2 before/after)
4. TCU stub decision — leave it or re-embedded?
5. Any Drive folders that were missing

---

## DO NOT
- Do not re-embed manuals already in the chunks table (the script handles this)
- Do not run with --force unless specifically instructed
- Do not commit any files (embed script writes to Supabase only, no file changes)
- Do not stop the process if individual PDFs fail — the script continues automatically
