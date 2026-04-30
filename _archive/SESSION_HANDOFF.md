# Session Handoff — Hercules MK3 ROV Manual
**Date:** 23 Apr 2026 | **Last commit:** 9488422

## Repo
github.com/Seanbrock100/rov-chatbot  
Live: https://rov-chatbot-production-3d66.up.railway.app  
Local dev: http://localhost:8765 (python3 -m http.server 8765 in rov-manual/)  
Supabase: ccjurdnubkmeepaztomy.supabase.co

## Credentials
All from: https://rov-chatbot-production-3d66.up.railway.app/api/config  
Returns: anthropicKey, supabaseUrl, supabaseAnon, supabaseService, voyageKey

## Current State — Database
| Table | Count |
|-------|-------|
| chunks | ~2,783 across 162 manuals |
| card_index | 30 rows (all pod cards mapped) |
| drawings | 194 (67 mapped to local_file) |
| fault_log | 1,057 | handover_log | 4,060 |
| knowledge_corrections | 0 (ready) |

## What Was Built Today

### PDF Viewer (in index.html viewer tabs)
- Multi-page viewer with ◀/▶ navigation and keyboard arrow keys
- Page counter shows current/total (e.g. Page 281 / 461)
- TOC panel for manuals >20 pages (queries Supabase chunks for section names)
- Drawings open at precise page numbers (all T4 joints mapped to exact pages)
- Deduplication on file+page so same manual opens at different pages as separate tabs
- Tab labels show drawing title not filename

### T4 Manipulator — Complete page map (011-8239.pdf)
All 34 entries mapped with drawing + parts list pages:
- Azimuth: p281/283, Clevis Pin: p285/286, Elbow: p287/289
- Compensator: p291/295, Pitch/Yaw: p301/303 (interchangeable joint)
- In-Arm PCB: p312/313, Forearm: p329/331, Master Arm: p332/335
- Upper Arm/Shoulder: p342/345, Solenoid Valve: p347/348
- Wrist Camera: p349/351, Lock Valve: p359/360, Wrist: p363/365
- T4 General/Torque: p368/372, Nose Block: p404/405, Jaw Intermeshing: p417

### Manual Viewer (manual-viewer.html)
Standalone page opened in new browser tab: manual-viewer.html?manual=FILENAME.pdf

**Features:**
- Search sidebar (left, 300px) with AUTO/EXACT/AI mode buttons
- pdf.js canvas rendering — shows result page ±1 (3 pages max, no full PDF load)
- PREV/NEXT buttons to step through pages from a result
- ↗ FULL PDF button in topbar
- Ctrl+F hint link at bottom of sidebar
- AUTO mode detects: part numbers (101-xxxx), torque (75 Nm), codes (ROV-0311) → EXACT; topics → AI

**Search algorithm:**
1. AI vector search (match_chunks RPC) — biased to this manual
2. Keyword search per term in parallel (Promise.all) — always runs
3. Scoring: primary term (first word) gates inclusion, secondary terms boost score
4. OCR concat bonus: +30 if chunk contains words concatenated (e.g. "clevisshearpin")
5. Skip TOC/index pages (page < 15)
6. Keyword results surface first, AI-only results appended after

**Key insight:** T4 manual OCR concatenated part descriptions (CLEVISSHEARPIN not CLEVIS SHEAR PIN).  
The concat bonus specifically addresses this — searching "clevis shear pin" now surfaces  
chunk at pages 218/230/254 (which contain KIT,CLEVISSHEARPIN) above assembly procedure chunks.

### Chatbot System Prompt
- Signal path priority: always trace source → connector → PCB → backplane → uplink
- "Point to drawing, don't invent" principle explicitly in prompt
- "Wrong answer worse than no answer"
- Detects path questions (regex) → widens search context beyond current card
- Card description from DESCRIPTIONS injected directly when on a card
- No HD video — system uses analogue Y/C

### Data Corrections Made
- Thrusters: fixed drawings (was showing TCU drawings), description corrected (Curvetech/TCU/servo valves)
- Aleron VP Manual moved from atlas_manip to valve_packs
- Video MUX description: full signal path 1→5 with 1610nm wavelength, Rainbow rack, CRNA Interface Card
- All 5 previously empty components now have drawings (rov_lights, pan_tilt, tms, longline, cables)

## Files
- rov-manual/index.html — main manual (~1,968 lines, JS PARSE OK)
- rov-manual/manual-viewer.html — standalone manual reader with search (374 lines)
- rov-manual/manual-search.html — legacy search popup (superseded by manual-viewer.html)
- rov-manual/manuals/ — 134 PDFs (flat, not git tracked)
- rov-manual/photos/rov_overview.jpg — real HE15 photo (451KB, 1200×1200)

## JS Parse Check
```bash
python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"
```

## Priority Next Steps
1. **Test manual-viewer search** — reload http://localhost:8765, go to T4, open manual, search "clevis shear pin" → should show page 218 first
2. **Vessel deploy** — copy rov-manual/ to N:\15. ROV\3. Technical Docs\ and test in Edge
3. **TMA01030 re-embed** — Interface Systems Manual truncated at page 102, needs --force
4. **card_index chunk quality** — some cards have 1 chunk only, improves after more embedding

## Known Issues
- match_chunks RPC returns 404 from browser (anon key may not have RPC access) — keyword fallback handles this
- manual-viewer TOC uses chunks table page_label — quality depends on embed coverage
- Video MUX 1530nm vs 1610nm: confirmed 1610nm from chunk 39 of EQP952-0203-DR-PD-55017
