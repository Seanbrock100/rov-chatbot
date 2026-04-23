# Session Handoff — Hercules MK3 ROV Manual
**Date:** 23 Apr 2026 | **Last commit:** f0d5e62

## Repo
github.com/Seanbrock100/rov-chatbot
Live: https://rov-chatbot-production-3d66.up.railway.app
Local dev: http://localhost:8765 (python3 -m http.server 8765 in rov-manual/)
Supabase: ccjurdnubkmeepaztomy.supabase.co

## Current State — Everything Working

### Manual (rov-manual/index.html)
- ✅ Home screen: real HE15 photo (photos/rov_overview.jpg) — fixed div closure bug f0d5e62
- ✅ 4-layer navigation: Home → Menu → Component → Chassis → Card
- ✅ Tabbed PDF viewer: multiple drawings open simultaneously, overlay approach
- ✅ Context strip: updates on every navigation event
- ✅ Live sidebar: queries Supabase for drawings on component select
- ✅ Card panel: clicking card updates sidebar with card-specific drawings
- ✅ openDoc closes card panel before opening viewer tab
- ✅ Chat tab: context-aware, routes through Railway proxy, correction flow ready
- ✅ 134 PDFs in manuals/ — zero broken links, zero unlinked files
- ✅ 53 offline AI descriptions embedded inline
- ✅ card_index wired into openCardInfo (async Supabase fetch on card click)
- JS PARSE: CLEAN on every commit

### Supabase Database
| Table | Count | Notes |
|-------|-------|-------|
| chunks | 2,777 | 159 manuals (Cowork embed run in progress) |
| card_index | 30 | All pod cards mapped — drawings + chunk IDs |
| drawings | 194 | 67 mapped to local_file |
| fault_log | 1,057 | HE15/H30 2012-present |
| handover_log | 4,060 | 2023-present |
| knowledge_corrections | 0 | Ready, waiting first engineer correction |
| component_notes | 0 | Ready |
| manual_amendments | 0 | Ready |

### Cowork Tasks
- COWORK_TASK_RUN_EMBEDS.md — IN PROGRESS (overnight embed, check chunk count)
- COWORK_TASK_LINK_AUDIT.md — COMPLETED
- COWORK_TASK_CARD_INDEX.md — COMPLETED

## Priority Next Steps

1. **Check Cowork embed run** — query Supabase chunks table for new count
   Was 1,824 at start of session, now 2,777. Run still going? Check:
   `SELECT COUNT(*) FROM chunks` and `SELECT manual_name, COUNT(*) FROM chunks GROUP BY manual_name ORDER BY COUNT(*) DESC LIMIT 20`

2. **Browser test card_index** — reload manual, go to Electronics Pod,
   click Control Chassis, click any card (e.g. Video MUX PCB).
   Sidebar should update to show card-specific drawings from Supabase.
   Chat context banner should show the card name.

3. **Vessel deploy** — copy rov-manual/ to N:\15. ROV\3. Technical Docs\
   Test in Edge browser on vessel PC. Key test: click Drawing → opens in tab.

4. **Fix remaining small gaps:**
   - Thrusters, Pan & Tilt, TMS, Longline components have 0 drawings
   - Drawing numbers are known — just need adding to DATA object

5. **Pod SVG as viewer tab** — pod schematic should open as a tab

## Known Issues / Watch List
- TMA01030 Interface Systems Manual — truncated at page 102 (341 chunks)
  Full manual is ~200 pages. Needs --force re-embed after Cowork run completes.
- TMA01071 LARS — truncated at page 10 (62 chunks). Same issue.
- tcu.pdf — 1-chunk stub. Check if TMA01031 covers TCU content first.
- Video MUX card only got 1 chunk from card_index — will improve as more 
  TMA01030 content is embedded.
- Build stamp in header says wrong date (cosmetic — git hook issue)

## Key File Paths (Mac)
- Repo: /Users/seanbrock/Documents/GitHub/rov-chatbot/
- Manual: /Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/index.html
- PDFs: /Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/manuals/ (134 files)
- Photo: /Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/photos/rov_overview.jpg
- Google Drive: /Users/seanbrock/Library/CloudStorage/GoogleDrive-seanbrock100@gmail.com/My Drive/Work Technical Docs/
- Embed script: /Users/seanbrock/Documents/GitHub/rov-chatbot/RUN_EMBED_MANUALS.sh
- Embed log: /tmp/embed_log.txt (if Cowork run is active)

## Credentials
All fetched at runtime from Railway:
https://rov-chatbot-production-3d66.up.railway.app/api/config
Returns: anthropicKey, supabaseUrl, supabaseAnon, supabaseService, voyageKey

## JS Parse Check Command
```bash
python3 -c "
html = open('/Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/index.html').read()
script = html[html.rfind('<script>')+8:html.rfind('</script>')]
open('/tmp/vc.js','w').write('// test\n'+script)
" && node --check /tmp/vc.js && echo "PARSE OK"
```

## What NOT to touch
- descriptions_norm.json — offline fallback, do not regenerate without reason
- manuals/ folder contents — 134 PDFs, all linked, do not rename files
- POD_ZONES data in index.html — card definitions, leave as-is
- card_index table — populated, do not truncate

## ROV Photo (home screen)
Real HE15 photo now on home screen (photos/rov_overview.jpg).
Attempted AI renders in Nano Banana and Firefly — none accurate enough.
Decision: use real photo. Do not attempt further AI generation.
