# Hercules MK3 ROV Interactive Manual & Chatbot

Interactive technical reference system for the Hercules MK3 ROV fleet — Seven Oceanic, Subsea 7.

## Live system
**Online:** https://rov-chatbot-production-3d66.up.railway.app  
**Local:** `cd rov-manual && python3 -m http.server 8765` → http://localhost:8765

## What it is

Three-layer system:
1. **Interactive Manual** — structured navigation to drawings and manuals by functional system (Longlines / Control Room / PDU / ROV Electrical/Hydraulic/Mechanical / TMS H15 / TMS H30 / LARS / Manipulators)
2. **PDF Viewer** — click any drawing to open at the correct page; manuals open in new tab with native Ctrl+F
3. **AI Chatbot** — conversational technical assistant grounded in 23,333 chunks from 392 embedded manuals

## Repository structure

```
rov-manual/         Main manual (serve this folder via http)
  index.html        Manual, viewer, chatbot — everything in one file
  admin.html        Admin panel — review/move/remove drawings with PDF preview
  manual-viewer.html  Simple PDF wrapper for new-tab viewing
  manuals/          593 PDFs (~1.3GB) — not git tracked
  photos/           ROV photo assets

app.py              Railway proxy server (Anthropic + Supabase API keys)
Procfile            Railway deployment config
requirements.txt    Python dependencies

embed_new_files.py  Batch embed script — run via Cowork when adding new PDFs
PROJECT_STATUS.md   Full project progress, architecture, session history
MASTER_KNOWLEDGE.md Ground truth technical reference — PCBs, signals, hydraulics
_archive/           Old files kept for reference
```

## Database (Supabase)
- **23,333 chunks** across 392 manuals (voyage-large-2, 1536 dims)
- `drawing_families` — 70-row drawing number prefix guide
- `match_chunks(query_text, match_count)` — vector search RPC
- `lookup_drawing_family(p_query)` — drawing number lookup RPC

## Adding new PDFs
1. Copy PDFs to `rov-manual/manuals/`
2. Run `python3 embed_new_files.py` (hand to Cowork — takes hours)
3. Update DATA sections in `rov-manual/index.html` via admin panel

## Vessel deployment
Copy `rov-manual/` to `N:\15. ROV\3. Technical Docs\` and open `index.html` in Edge.  
Note: PDF viewer requires a local server (`python3 -m http.server 8765`) or the Railway URL.  
Chatbot requires internet. Manual navigation and PDF viewer work fully offline.

## JS parse check
```bash
python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"
```
