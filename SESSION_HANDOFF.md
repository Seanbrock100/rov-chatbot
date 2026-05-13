# SESSION HANDOFF — Hercules MK3 ROV Manual

**Snapshot date:** 13 May 2026
**Repo:** github.com/Seanbrock100/rov-chatbot (private)
**Live:** https://rov-chatbot-production-3d66.up.railway.app
**Local dev:** `cd rov-manual && python3 -m http.server 8765` → http://localhost:8765
**Purpose of this doc:** Drop-in orientation for a fresh AI session (Claude Create, new Claude Code session, anyone) so it doesn't have to reverse-engineer state.

> Read this first. Then `PROJECT_STATUS.md` for full vision. Then `FILE_INVENTORY.md` for code map. Then `MASTER_KNOWLEDGE.md` for the technical ground truth the chatbot is graded against.

---

## What this project IS

A digital technical reference for the Hercules MK3 ROV fleet (Seven Oceanic, Subsea 7). Three layers in one self-contained HTML file:

1. **Interactive Manual** — structured navigation to drawings and PDF manuals by functional system (Longlines / Control Room / PDU / ROV Electrical-Hydraulic-Mechanical / TMS H15 / TMS H30 / LARS / Manipulators)
2. **PDF Viewer** — tabbed in-page iframe for drawings; manuals open in new browser tab with native Ctrl+F
3. **AI Chatbot** — Claude Sonnet with vector RAG over 23,333 chunks across 392 manuals, plus drawing-family lookup, plus card-specific context injection

Sean Brock — Electronic Systems Specialist aboard Seven Oceanic — is both the builder and the primary user.

## What this project IS NOT

- Not a CMMS / maintenance tracker
- Not a sales tool for non-engineers
- Not a replacement for Subsea 7 controlled documentation (it points TO controlled documents)
- Not multi-tenant — single vessel, single ROV class, single duty engineer audience

---

## Current state — live numbers (13 May 2026)

| Item | Value | Notes |
|---|---|---|
| chunks | 23,333 | Across 392 manuals (voyage-large-2, 1536 dims) |
| drawing_families | 70 rows | Prefix/series guide with legacy warnings |
| card_index | 30 rows | Pod cards mapped to drawings + chunk IDs |
| drawings | 194 | 67 mapped to local files |
| fault_log | 1,057 | H15 + H30 Sub Engineer Log |
| handover_log | 4,060 | End-of-trip reports 2023–2026 |
| chat_log | live | Every Q&A logged with GOOD/BAD rating + free-text feedback |
| knowledge_corrections | 0 | Table ready, no entries yet |
| PDFs in manuals/ | 635 | ~1.4 GB on disk, NOT git tracked |
| index.html | 3,082 lines | Single-file architecture, intentional |

## What's working

- Full menu navigation by functional system
- Drawing tabs deduplicated on file+page
- Manuals open in new browser tab with native Ctrl+F (working `manual-viewer.html` wrapper)
- Chatbot: vector chunk search + drawing family auto-lookup + card-context injection + clickable drawing links in answers
- Chatbot prompt has hardcoded system facts to suppress prior hallucinations (CRNA, Rainbow rack, PCB-0162, RS485 CH7/CH8 etc — see MASTER_KNOWLEDGE.md)
- Q&A logging to `chat_log` with GOOD/BAD ratings and free-text feedback on BAD
- Admin panel (`admin.html`) — review/move/remove drawings with inline PDF preview, Q&A log view, CSV export
- Standalone drawing-tree HTMLs (control-room-tree, drawing-tree, lars-tree, pdu-tree) — linked from index.html for deep navigation
- file:// protocol warning banner when index.html opened directly without HTTP server

## What's broken / half-done / risk

**SECURITY — code complete, deployment pending.** The frontend password gate, admin password gate (server-side), and `hmac.compare_digest` are all committed. `/api/config` no longer leaks secrets. The deployment-side work that remains:
- Set `APP_PASSWORD` env var in Railway (the app currently bypasses the gate because the env var isn't set)
- Set `ADMIN_PASSWORD` env var in Railway (admin currently denies-by-default until this is set)
- Rotate `ANTHROPIC_KEY`, `VOYAGE_KEY`, `SUPABASE_SERVICE` — all considered compromised because `/api/config` leaked them for an unknown duration before the fix
- End-to-end browser test

See `PROJECT_STATUS.md` → Security Architecture for the full sequence.

**TREE HTML PATH MISMATCH — deploy blocker for `file://` use.** The four standalone tree HTML files (`drawing-tree.html`, `control-room-tree.html`, `lars-tree.html`, `pdu-tree.html`) hardcode `const BASE = 'http://localhost:8765/docs/'` and reference hierarchical paths (`ROV/Mechanical/Frame and Structure/...`) that exist only in the `rov-manual/docs` symlink target. On vessel `file://` deploy with a flat `manuals/` folder, every PDF link in every tree HTML 404s. Three remediation options documented in `DRAWING_INDEX.md` — design decision required (rewrite `FILES` maps to flat filenames vs. ship hierarchical folder structure vs. accept dev-only and remove from vessel deploy).

**Other open issues:**
- 174 scanned/image PDFs in manuals/ — skipped during last embed run, would need OCR (tesseract / Textract / Adobe) to become searchable
- TMA01030 was truncated at page 102 in old embed run; needs re-embed with `--force` flag. TMA01030 now has 926 chunks but full coverage not verified.
- LARS sub-sections "Sliding Weight", "Slip Ring", "Tether" have no drawings populated
- TCU wiring (ROV-0300-D-0420-90) should appear under BOTH ROV ELECTRICAL and ROV HYDRAULIC — currently only under HYDRAULIC
- Some sections in admin panel not yet reviewed (T4 reviewed; others pending)
- `/` route in `app.py` still serves `rov_agentic_chatbot.html` (file no longer exists in repo) — broken Railway root, not in scope for security fix

## Deploy plan

Vessel target: `N:\15. ROV\3. Technical Docs\` — Windows network drive on Seven Oceanic.

**Mode: static file copy** (decision locked in).
- Copy `rov-manual/` folder verbatim to the vessel drive
- Engineers open `index.html` directly in Edge (`file://`)
- 635 PDFs in `manuals/` work via iframe — no server needed for browsing
- Chatbot and live drawing search go to Railway/Supabase over the internet
- Vessel PCs are confirmed always-online; firewall may need whitelist for `*.up.railway.app` and `*.supabase.co`

**Conscious gaps shipped with deploy:** TMS / longline / cable components have minimal coverage. Thrusters / Pan&Tilt / Lights have manuals but no drawing links yet. The chatbot will hedge or give generic answers in those areas. Sean (the duty engineer) is aware of where it's thin. The `chat_log` BAD-rating + free-text feedback IS the iteration mechanism — collect real misses on vessel, fix systematically.

## Architecture in one paragraph

Static HTML/JS frontend (`rov-manual/index.html`, 3082 lines, single file by design) does menu, viewer, and chatbot UI. PDFs served from `rov-manual/manuals/` flat directory. On page load, frontend fetches `/api/config` from Railway to get Supabase URL + anon key (this endpoint is the leak). Browser reads Supabase directly for `chunks` vector search (via `match_chunks` RPC), `drawing_families` lookup, `card_index` reads, and `chat_log` writes — using anon key. All Anthropic API calls go through Flask `/anthropic/messages` proxy on Railway (`app.py`) which holds the secret Anthropic key server-side. Voyage embeddings similarly proxied. Service role key currently leaked through /api/config but also available server-side via `/supabase/<path>` proxy for writes that need it. Railway redeploys automatically on GitHub push to `main`.

## Workflow conventions Sean uses

- **Repo hygiene:** push to GitHub frequently with descriptive commit messages. Railway auto-deploys.
- **JS parse check before every push to index.html** (canonical command in README.md): `python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"`
- **Single-file `index.html` is intentional** — not "yet to be modularised". Trade-off: harder to navigate, but trivially deployable as a file:// asset on a vessel drive with zero build step.
- **No build step. No npm. No bundler.** This is a constraint, not an oversight.
- **No new external dependencies** without checking — added deps mean new things to break offline, new things vessel IT might block, new attack surface.

## What Sean asks of an AI working on this project

Direct from his system prompt:
- Be a peer, not a cheerleader. Challenge ideas. Brainstorm. Don't accept a plan that has holes — name the holes.
- Explain reasoning, not just output. Show the prompt-engineering logic when relevant.
- If a prompt is weak, propose a refined version.
- Reference prior decisions from the project rather than inventing fresh advice.
- Accept that goals shift as we proceed.

## Immediate next tasks — priority order

1. **Complete the security deployment.** Code is committed. Outstanding: set `APP_PASSWORD` + `ADMIN_PASSWORD` in Railway; rotate `ANTHROPIC_KEY` + `VOYAGE_KEY` (compromised by the pre-fix `/api/config` leak); browser test end-to-end. `SUPABASE_SERVICE` rotation **deferred as tracked tech debt** — Supabase deprecated the simple JWT secret regeneration; full migration to new `sb_publishable` / `sb_secret` keys is required (~30-45 min of focused work). See `PROJECT_STATUS.md` Security Architecture section + "Tracked tech debt — Supabase key migration" subsection for the full sequence and migration scope.
2. **Decide tree HTML strategy.** The four tree HTMLs only work in dev (localhost http server + docs symlink target). Pick one of: rewrite `FILES` to flat filenames, ship hierarchical folder to vessel alongside flat `manuals/`, or accept dev-only and link them out of `index.html` for the vessel build.
3. **Resolve `rov-manual/docs` symlink** before vessel copy.
4. **Vessel sandbox test** on a Windows machine via `file://`. Verify card click → card_index sidebar populates; drawing click → PDF tab opens; chatbot reaches Railway; check DevTools Network tab for the Anthropic POST.
5. **Actual vessel deploy** to `N:\15. ROV\3. Technical Docs\`.
6. **Re-test chatbot quality** post-embed-run. TMA01030 / TMA01071 / TMA01031 now fully searchable; old quality scores were pre-embed.
7. **Admin review pass** on sections other than T4.
8. **OCR the 174 scanned PDFs** (longer-term, not deploy-blocking).

## Things NOT to change without explicit Sean approval

- `descriptions_norm.json` — offline fallback, do not regenerate
- `manuals/` filenames — 635 PDFs linked by exact name from `DATA` in index.html
- `POD_ZONES` structure in index.html — card definitions, hand-authored
- `card_index` table contents — populated, validated
- `drawing_families` table contents — 70 rows, hand-curated with legacy warnings
- The hardcoded system facts in chatbot prompt (`MASTER_KNOWLEDGE.md` section 8) — they exist because the AI hallucinated. Don't soften them.
- Single-file architecture for index.html — see "Workflow conventions" above
- Adding a build step or framework — explicitly out of scope

## Things FAIR GAME for a fresh AI to challenge or redesign

- The chatbot UI inside the manual (could be a side panel, floating widget, dedicated route, voice — open)
- Search interface for drawings (current is menu-driven; type-to-find would be nice)
- Mobile responsiveness (vessel PCs are desktop, but Sean has been asked about tablet use on deck)
- Onboarding for engineers who haven't seen it before (currently zero — drops you on the menu)
- The fault-finding flow — could be guided/Socratic rather than free-form chat
- Image input — engineer photographs a component, chatbot identifies it (not built; would be valuable)
- The admin panel layout — functional but ugly

Go further if you've got a better idea. Sean wants challenge, not deference.
