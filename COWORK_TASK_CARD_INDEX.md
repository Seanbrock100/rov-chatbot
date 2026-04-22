# COWORK TASK — Build card_index Table (Pod Card → Drawings + Manual Sections)

## YOUR MISSION
Create and populate a `card_index` table in Supabase that maps each electronics
pod card to its relevant drawings (with local filenames) and relevant manual
chunk IDs. This is the cross-reference layer that makes the chatbot and card
panel show precise, card-specific information instead of keyword guesses.

## REPO
github.com/Seanbrock100/rov-chatbot

## CREDENTIALS
```python
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
SUPABASE_URL     = cfg['supabaseUrl']
SUPABASE_SERVICE = cfg['supabaseService']
SUPABASE_ANON    = cfg['supabaseAnon']
ANTHROPIC_KEY    = cfg['anthropicKey']
```

---

## STEP 1 — CREATE THE TABLE

Run this SQL via the Supabase MCP:

```sql
CREATE TABLE IF NOT EXISTS card_index (
  id              BIGSERIAL PRIMARY KEY,
  card_key        TEXT NOT NULL UNIQUE,
  zone            TEXT NOT NULL,
  card_name       TEXT NOT NULL,
  drawing_numbers TEXT[],
  local_files     TEXT[],
  chunk_ids       BIGINT[],
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_card_index_key  ON card_index(card_key);
CREATE INDEX IF NOT EXISTS idx_card_index_zone ON card_index(zone);

COMMENT ON TABLE card_index IS
  'Maps each electronics pod card to its relevant drawings and manual chunk IDs';
COMMENT ON COLUMN card_index.card_key IS
  'Normalised key: zone/card-name e.g. control_chassis/video-mux-pcb-pcb-0124';
COMMENT ON COLUMN card_index.local_files IS
  'Flat filenames in manuals/ folder e.g. EQP952-0203-DR-PD-55017.pdf';
COMMENT ON COLUMN card_index.chunk_ids IS
  'Row IDs from the chunks table that contain relevant manual text';
```


---

## STEP 2 — UNDERSTAND THE DATA SOURCES

### Cards that need mapping (30 total, 23 unmapped)

**Control chassis (17 cards, 12 unmapped):**
- PSU 1 — SLE124
- PSU 2 — SLE112
- PSU 3 — MAX315
- PSU 4-7 — MAX124 x4
- Camera PSU x2
- Video MUX PCB — PCB-0124           ← ALREADY HAS 2 drawings
- Camera Control PCB — PCB-0161
- Relay & HK PCB 1 — PCB-0163 (Camera Power)
- Relay & HK PCB 2 — PCB-0163 (Auxiliaries)
- Thruster Control Unit PCB — PCB-0162  ← ALREADY HAS 2 drawings
- 155MHz Fibre Optic I/F — PCB-0186 (1530nm)  ← ALREADY HAS 2 drawings
- CWDM Assembly RED — ROV-0311-D-0212   ← ALREADY HAS 2 drawings
- Band Splitter — ROV-0311-D-0210
- Sixnet 9-Port Gigabit Switch — SLX-10MG-1  ← ALREADY HAS 2 drawings
- Gyro Cover Plate — EQP952-0203-DR-PD-55011  ← ALREADY HAS 2 drawings (via drawingFile)
- 24V Unregulated Supply — ROV-0311-D-0208
- System Backplane Breakout — PCB-0197

**Payload chassis (13 cards, 11 unmapped):**
- PSU 1 — SLE124
- PSU 2 — MAX315
- PSU 3-8 — MAX124 x6
- Generic Interface PCB — PCB-0115
- Payload Chassis Backplane — PCB-0169
- Relay & Housekeeping PCB — PCB-0163
- 155MHz Fibre Optic I/F — PCB-0186 (1370nm)  ← ALREADY HAS 2 drawings
- CWDM Assembly BLUE — ROV-0311-D-0212  ← ALREADY HAS 2 drawings
- Sixnet 10-Port Gigabit Switch
- RS232 Module — PCB-0032
- SFP Ethernet Module x2 (MRV)
- Optical Transceivers x4
- Fan Tray

### Available drawings (key ones for pod cards)
All filenames are flat in manuals/ folder:
- EQP952-0203-DR-PD-55000.pdf  — Pod Assembly GA (top level)
- EQP952-0203-DR-PD-55001.pdf  — Control Chassis Assembly GA
- EQP952-0203-DR-PD-55002.pdf  — Payload Chassis Assembly GA
- EQP952-0203-DR-PD-55003.pdf  — Control Penetrator Ring GA
- EQP952-0203-DR-PD-55004.pdf  — Payload Penetrator Ring GA
- EQP952-0203-DR-PD-55006.pdf  — Control Chassis Earth Strip Plate
- EQP952-0203-DR-PD-55007.pdf  — Payload Chassis Earth Strip Plate
- EQP952-0203-DR-PD-55011.pdf  — Gyro Cover Plate
- EQP952-0203-DR-PD-55016.pdf  — Payload Chassis Wiring Diagram
- EQP952-0203-DR-PD-55017.pdf  — Control Chassis Wiring Diagram
- EQP952-0203-DR-PD-55018.pdf  — Control Chassis Wiring (sheet 2)
- EQP952-0203-DR-PD-55019.pdf  — Payload Chassis Wiring (sheet 2)
- ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf
- ROV-0311-D-0206-00 Pod control earth strip plate 1 of 1.pdf
- ROV-0311-D-0208-00 Pod valve pack unregulated supply.pdf
- ROV-0311-D-0212-00.pdf       — CWDM Assembly
- ROV-0300-D-0420-00 TCU Assembly.pdf
- ROV-0300-D-0420-90 TCU Wiring Diagram.pdf

### Available manual chunks (key ones already found)
From Supabase chunks table, relevant chunk IDs:
- 338-346: ROV Master Knowledge v2.pdf (system overview)
- 2720-2760: TMA01030 Interface Systems Manual (PCB-specific sections)
- TMA01031 has 569 chunks covering control system detail


---

## STEP 3 — POPULATE card_index USING AI-ASSISTED MAPPING

For each card, you need to:
1. Search Supabase chunks for relevant text using the Supabase REST API
2. Use Claude to identify which chunk IDs are actually relevant
3. Map drawing filenames based on what the card touches (wiring, assembly, etc.)
4. Insert the row into card_index

### Python script to generate the mappings

```python
import requests, json, time

cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
SB_URL  = cfg['supabaseUrl']
SB_SVC  = cfg['supabaseService']
SB_ANON = cfg['supabaseAnon']
ANT_KEY = cfg['anthropicKey']

SB_HEADERS = {'apikey': SB_SVC, 'Authorization': f'Bearer {SB_SVC}', 'Content-Type': 'application/json'}
ANT_HEADERS = {'x-api-key': ANT_KEY, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'}

def search_chunks(query, limit=8):
    """Search chunks using match_chunks RPC (vector search)"""
    r = requests.post(f'{SB_URL}/rest/v1/rpc/match_chunks',
        headers=SB_HEADERS,
        json={'query_text': query, 'match_count': limit}, timeout=30)
    return r.json() if r.ok else []

def ask_claude(prompt):
    r = requests.post('https://api.anthropic.com/v1/messages',
        headers=ANT_HEADERS,
        json={'model': 'claude-sonnet-4-20250514', 'max_tokens': 800,
              'messages': [{'role': 'user', 'content': prompt}]},
        timeout=30)
    return r.json()['content'][0]['text']

def insert_card_index(row):
    r = requests.post(f'{SB_URL}/rest/v1/card_index',
        headers={**SB_HEADERS, 'Prefer': 'return=minimal'},
        json=row, timeout=15)
    return r.ok

# CARDS TO MAP
CARDS = [
    # (zone, card_name, search_query, known_drawings)
    ('control_chassis', 'PSU 1 — SLE124',
     'SLE124 power supply 24V control chassis',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'PSU 2 — SLE112',
     'SLE112 secondary power supply control chassis',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'PSU 3 — MAX315',
     'MAX315 sensor instrument power supply',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'PSU 4-7 — MAX124 x4',
     'MAX124 auxiliary power supply units',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'Camera PSU x2',
     'camera power supply 24V backplane camera heads',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'Video MUX PCB — PCB-0124',
     'video multiplexer PCB-0124 camera coax Y/C signal',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf',
      'EQP952-0203-DR-PD-55018.pdf', 'ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf']),

    ('control_chassis', 'Camera Control PCB — PCB-0161',
     'camera control PCB-0161 iris focus zoom backplane',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'Relay & HK PCB 1 — PCB-0163 (Camera Power)',
     'relay housekeeping PCB-0163 camera power switching backplane CON 31-37',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'Relay & HK PCB 2 — PCB-0163 (Auxiliaries)',
     'relay housekeeping PCB-0163 auxiliary power switching backplane CON 45-51',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', 'Thruster Control Unit PCB — PCB-0162',
     'thruster control unit PCB-0162 servo valve backplane CON 66-72',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf',
      'ROV-0300-D-0420-90 TCU Wiring Diagram.pdf', 'ROV-0300-D-0420-00 TCU Assembly.pdf']),

    ('control_chassis', '155MHz Fibre Optic I/F — PCB-0186 (1530nm)',
     '155MHz fibre optic interface PCB-0186 1530nm serial channel',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf',
      'ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf', 'ROV-0311-D-0212-00.pdf']),

    ('control_chassis', 'CWDM Assembly RED — ROV-0311-D-0212',
     'CWDM assembly RED band 1470 1490 1510 1530nm wavelength fibre',
     ['ROV-0311-D-0212-00.pdf', 'ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf',
      'EQP952-0203-DR-PD-55003.pdf']),

    ('control_chassis', 'Band Splitter — ROV-0311-D-0210',
     'band splitter COM RED BLUE wavelength fibre optic pod',
     ['ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf',
      'EQP952-0203-DR-PD-55001.pdf']),

    ('control_chassis', 'Sixnet 9-Port Gigabit Switch — SLX-10MG-1',
     'Sixnet SLX-10MG-1 ethernet network switch bottomside',
     ['ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf',
      'EQP952-0203-DR-PD-55001.pdf']),

    ('control_chassis', 'Gyro Cover Plate — EQP952-0203-DR-PD-55011',
     'gyro cover plate Octans Nano RS232 CH2 CON60 backplane',
     ['EQP952-0203-DR-PD-55011.pdf', 'EQP952-0203-DR-PD-55001.pdf',
      'EQP952-0203-DR-PD-55017.pdf']),

    ('control_chassis', '24V Unregulated Supply — ROV-0311-D-0208',
     'unregulated 24V supply valve pack VP1 VP2 RS485',
     ['ROV-0311-D-0208-00 Pod valve pack unregulated supply.pdf',
      'EQP952-0203-DR-PD-55001.pdf']),

    ('control_chassis', 'System Backplane Breakout — PCB-0197',
     'system backplane breakout PCB-0197 main distribution board',
     ['EQP952-0203-DR-PD-55001.pdf', 'EQP952-0203-DR-PD-55017.pdf']),

    # Payload chassis
    ('payload_chassis', 'PSU 1 — SLE124',
     'SLE124 main 24V power supply payload chassis',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', 'PSU 2 — MAX315',
     'MAX315 secondary power supply payload chassis',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', 'PSU 3-8 — MAX124 x6',
     'MAX124 six power supply modules payload chassis',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', 'Generic Interface PCB — PCB-0115',
     'generic interface PCB-0115 payload sensor connections backplane CON 5',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', 'Payload Chassis Backplane — PCB-0169',
     'payload chassis backplane PCB-0169 card stack',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', 'Relay & Housekeeping PCB — PCB-0163',
     'relay housekeeping PCB-0163 payload chassis switching monitoring',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', '155MHz Fibre Optic I/F — PCB-0186 (1370nm)',
     '155MHz fibre optic interface PCB-0186 1370nm payload BLUE CWDM',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf',
      'ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf']),

    ('payload_chassis', 'CWDM Assembly BLUE — ROV-0311-D-0212',
     'CWDM assembly BLUE band 1270 1290 1310 1370nm payload survey',
     ['ROV-0311-D-0212-00.pdf', 'ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf',
      'EQP952-0203-DR-PD-55004.pdf']),

    ('payload_chassis', 'Sixnet 10-Port Gigabit Switch',
     'Sixnet 10 port gigabit switch payload ethernet E1 E2 E4 survey',
     ['ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf',
      'EQP952-0203-DR-PD-55002.pdf']),

    ('payload_chassis', 'RS232 Module — PCB-0032',
     'RS232 module PCB-0032 serial communications payload instruments',
     ['EQP952-0203-DR-PD-55002.pdf', 'EQP952-0203-DR-PD-55016.pdf']),

    ('payload_chassis', 'SFP Ethernet Module x2 (MRV)',
     'SFP ethernet module MRV media converter 1290nm 1370nm fibre',
     ['ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf',
      'EQP952-0203-DR-PD-55002.pdf']),

    ('payload_chassis', 'Optical Transceivers x4',
     'optical transceiver 1310nm 1330nm 1390nm 1410nm BLUE CWDM',
     ['ROV-0311-D-0212-00.pdf', 'ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf']),

    ('payload_chassis', 'Fan Tray',
     'fan tray chassis cooling 24V payload',
     ['EQP952-0203-DR-PD-55002.pdf']),
]

results = []
for zone, name, query, drawings in CARDS:
    card_key = zone + '/' + name.lower().replace(' ', '-').replace('—', '-').replace('–', '-').replace('(', '').replace(')', '').replace('.', '').replace('×', 'x')

    # Search for relevant chunks
    chunks = search_chunks(query + ' Hercules MK3 electronics pod', limit=10)
    chunk_ids = [c['id'] for c in chunks[:6]]

    # Ask Claude to verify which chunks are actually relevant
    if chunks:
        chunk_previews = '\n'.join([f"ID {c['id']} [{c.get('manual_name','')} {c.get('page_label','')}]: {c.get('text','')[:150]}" for c in chunks[:6]])
        verification = ask_claude(
            f"For the Hercules MK3 ROV card '{name}' ({zone}), which of these chunk IDs contain directly relevant technical content? Reply with ONLY the relevant IDs as a comma-separated list, or NONE.\n\n{chunk_previews}"
        )
        # Parse IDs from response
        import re
        found_ids = [int(x) for x in re.findall(r'\b(\d+)\b', verification) if int(x) in chunk_ids]
        chunk_ids = found_ids if found_ids else chunk_ids[:3]

    row = {
        'card_key': card_key,
        'zone': zone,
        'card_name': name,
        'drawing_numbers': [],  # populate from drawings list
        'local_files': drawings,
        'chunk_ids': chunk_ids,
        'notes': f'Mapped {len(drawings)} drawings, {len(chunk_ids)} chunks'
    }

    ok = insert_card_index(row)
    status = 'OK' if ok else 'FAIL'
    print(f"{status}: {name} | {len(drawings)} drawings | {len(chunk_ids)} chunks")
    results.append({'card': name, 'status': status, 'drawings': len(drawings), 'chunks': len(chunk_ids)})
    time.sleep(0.5)

print(f"\nDone: {sum(1 for r in results if r['status']=='OK')}/{len(results)} successful")
```


---

## STEP 4 — WIRE card_index INTO index.html

After the table is populated, update `openCardInfo()` in
`rov-manual/index.html` to query card_index from Supabase on card click.

Find the `openCardInfo` function and add a Supabase fetch at the top:

```javascript
async function openCardInfo(zone, cardIdx) {
  const z = POD_ZONES[zone];
  const c = z.cards[cardIdx];
  // ... existing setup code ...

  // NEW: Fetch from card_index if CONFIG is loaded
  if (CONFIG.supabaseUrl && CONFIG.supabaseAnon) {
    const cardKey = normKey(zone, c.name);
    try {
      const r = await fetch(
        CONFIG.supabaseUrl + '/rest/v1/card_index?card_key=eq.' + encodeURIComponent(cardKey) + '&limit=1',
        { headers: { 'apikey': CONFIG.supabaseAnon, 'Authorization': 'Bearer ' + CONFIG.supabaseAnon } }
      );
      if (r.ok) {
        const rows = await r.json();
        if (rows.length > 0) {
          const idx = rows[0];
          // Update sidebar drawings from card_index
          if (idx.local_files && idx.local_files.length) {
            renderCardDrawingsInSidebar(idx.local_files, c.name);
          }
          // Update related drawings panel in card-info-panel
          if (idx.local_files && idx.local_files.length) {
            renderCardDrawingsInPanel(idx.local_files);
          }
          // Fetch relevant manual chunks
          if (idx.chunk_ids && idx.chunk_ids.length) {
            fetchCardChunks(idx.chunk_ids);
          }
        }
      }
    } catch(e) { console.warn('card_index fetch failed:', e); }
  }

  // ... rest of existing code ...
}
```

This is a code change — make it carefully. Run JS parse check after editing.

---

## STEP 5 — VERIFICATION

```sql
-- Check card_index was populated correctly
SELECT zone, card_name, array_length(local_files, 1) as drawing_count,
       array_length(chunk_ids, 1) as chunk_count
FROM card_index
ORDER BY zone, card_name;
```

Expected: 30 rows, all with local_files populated, most with chunk_ids.

---

## STEP 6 — COMMIT

```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
# Only commit index.html if you made the openCardInfo change
git add rov-manual/index.html
git commit -m "Wire card_index into openCardInfo — live drawing and chunk lookup per card"
git push origin main
```

The Supabase table changes don't need committing (they're in the DB already).

---

## DO NOT
- Do not modify POD_ZONES data in index.html (leave existing card definitions)
- Do not delete existing drawings[] arrays on cards (they are overrides)
- Do not run JS parse check after every edit — catch errors early
- Do not skip the Claude verification step for chunk IDs — accuracy matters
- Run JS parse check: `python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js`

---

## REPORT BACK
When done, share:
1. SQL query result from STEP 5 (full table contents)
2. Any cards that got 0 chunk_ids (couldn't find relevant manual sections)
3. Confirmation JS parse is clean if you edited index.html
