# Card System Brief — Hercules MK3 ROV Manual

**For:** Claude Designer session, or any AI / engineer working on this project
**Snapshot date:** 13 May 2026
**Companion to:** `PROJECT_STATUS.md`, `DRAWING_INDEX.md`, `SECURITY_BRIEF.md`, `FILE_INVENTORY.md`

> The card system is the central navigation pattern in this manual. Read this before touching `POD_ZONES`, `DESCRIPTIONS`, `openCardInfo()`, the chassis SVGs, or the card sidebar.

---

## What it is

Each pod in the ROV (Electronics Pod, PDU, T4 manipulator, LARS chassis etc.) is rendered as a **chassis-view diagram** that mirrors the real physical layout. Inside each chassis, every clickable tile is a **card** representing a real piece of hardware in its real position: a PCB in its slot, a backplane connector, a fuse rack, a junction box. Click a card → sidebar fills with that card's drawings, description, and links into the PDF library.

### Concrete example

Open the Control Chassis view (`EQP952-0203-DR-PD-55001`) → see the chassis diagram with cards laid out as they sit physically: `PSU 1 — SLE124`, `PSU 2 — SLE112`, `PSU 3 — MAX315`, `Video MUX PCB — PCB-0124`, `Camera Control PCB — PCB-0161`, `155MHz Fibre Optic I/F — PCB-0186 (1530nm)` and so on. Click `Video MUX PCB — PCB-0124` → sidebar shows: the short card detail, the long-form fault-diagnosis text (signal path, power rails, fault tree), plus clickable links to the wiring diagram (`EQP952-0203-DR-PD-55017`) and assembly drawing (`EQP952-0203-DR-PD-55001`). Click a drawing link → PDF tab opens at the correct page.

### Why cards, not a menu

An engineer diagnosing a fault at 2am has opened the physical pod. They see a board in a slot. They want to find that exact board in the manual the same way their eyes find it on the chassis — by position and label, not by drilling through a tree of bullets. The chassis-view-plus-click pattern is a near-direct mapping of how the engineer reasons. Anything that breaks that mapping (e.g. presenting cards in a list sorted alphabetically rather than by physical position) loses the design intent.

---

## Data architecture — three sources, not two

Cards pull from three independent data sources. Each has a different role and a different failure mode.

| Source | Lives in | What it provides | Loads when |
|---|---|---|---|
| `POD_ZONES` | `index.html` line ~1545 | Card name, position, short `detail` text, optional inline `drawings: [{num,title,file}]` array, optional `drawingFile` shortcut, plus zone-level `title`/`drawing`/`file`/`body` | Synchronous, on page load |
| `DESCRIPTIONS` | `index.html` line ~743 | Long-form fault-diagnosis text per card, keyed by `${zone}/${normalised_card_name}` (lowercase, unicode dashes preserved). Hand-authored from TMA01030 source. | Synchronous, on page load |
| Supabase `card_index` | `card_index` table, 30 rows | Authoritative drawing list per card (`local_files[]`) + chunk_ids back into the manual corpus | Async after card click, overlays the `POD_ZONES` drawing list when richer |

Three sources, two layers in priority order:
1. **Static + instant:** `POD_ZONES` + `DESCRIPTIONS` render the sidebar synchronously from in-page data. No network wait.
2. **Live overlay:** `card_index` fetched async; if the row has non-empty `local_files`, it overrides the drawing list. Description never changes — it stays from `DESCRIPTIONS`.

This is the same offline-first / network-second pattern as the rest of the manual.

---

## Card click flow — `openCardInfo(zone, cardIdx)` at `index.html` line ~1736

1. **Instant render** from `POD_ZONES[zone].cards[cardIdx]` — title and short detail
2. **Description lookup** from `DESCRIPTIONS[${zone}/${normKey(cardName)}]` — long-form text. Falls back to `detail` if no `DESCRIPTIONS` entry exists.
3. **Drawing list** initially populated from `POD_ZONES` card's `drawings: []` array (or single `drawingFile` shortcut)
4. **Async fetch:** `card_index?card_key=eq.<normalised_key>` from Supabase using anon key
5. If a row returned and `local_files` is non-empty → re-render the drawing list from `local_files`
6. Description and short detail stay as-is. Only the drawing list overlays.

`normKey()` (`index.html` line ~745) normalises the key consistently across the JS and the Python embed scripts. **It must match `py_norm_key()` byte-for-byte** — unicode dashes preserved, multi-space collapsed, surrounding whitespace trimmed. Diverging implementations cause the `card_index` lookup to silently miss.

---

## Visual treatment today

Each pod has a hand-drawn chassis SVG embedded in `index.html`. Cards are simple labelled rectangles, hand-positioned per chassis to match the real physical layout. Hover state is minimal. The visual hierarchy comes from labels and positioning, not styling.

Sidebar is a fixed right-side panel showing:
- Card name (title)
- Long-form description (from `DESCRIPTIONS`) or short detail (from `POD_ZONES`) if no long-form exists
- A list of `(drawing_number, title, filename)` rows that each open the PDF viewer tab at the correct page

No animations. No transitions. Form follows function — this is a tool, not a presentation.

---

## What's load-bearing — preserve these in any redesign

If a proposed change touches any of these, stop and confirm with Sean before implementing:

1. **`POD_ZONES` data shape.** The structure `{title, drawing, file, body, cards: [{name, detail, drawings, drawingFile}]}` is consumed by the click handler. Changing field names breaks the sidebar silently.
2. **`DESCRIPTIONS` key format: `${zone}/${normalised_card_name}`** in lowercase with unicode dashes preserved. The match is exact-string — any normalisation drift breaks every card description.
3. **`normKey()` JS function must match `py_norm_key()` server-side.** This is enforced by convention, not by tests. Don't "simplify" one without the other.
4. **Cards represent real physical hardware in real positions.** Don't decouple the SVG layout from physical reality to make it "look cleaner". The position-to-position mapping is the entire point of the system.
5. **The chassis SVGs are documentation, not decoration.** They're hand-drawn to match actual hardware. They're authored once and don't auto-generate. Treat them as source-of-truth artefacts.
6. **Instant render before network.** The sidebar must populate from `POD_ZONES` + `DESCRIPTIONS` before any Supabase round-trip completes. A vessel engineer with patchy internet at 2am still gets a usable sidebar.
7. **Drawing links open PDFs at the correct page** via the viewer tab. The `drawings[].file` field path and the manuals/ folder structure are tightly coupled — renaming a PDF silently breaks every reference in `POD_ZONES`.
8. **Card key normalisation is stable.** Don't change `normKey()` after `card_index` rows are populated — you'll orphan every existing row.

---

## Fair game — redesign welcomed

These are pure UX/UI surfaces with no data-coupling implications:

- **Card visual treatment** — colour, typography, hover/focus/active states, micro-animations, depth/shadow, hit area sizing. Touch-target sizing for tablet use on deck would be valuable.
- **Affordance for "this is clickable".** Currently weak — first-time users may not realise cards are interactive until they hover. A subtle border or cursor change on hover, or a one-time tutorial on first visit.
- **Sidebar layout and content density.** Currently plain — title, prose paragraph, list of drawings. Lots of room for typographic hierarchy, collapsible sections, "show more" patterns, drawing thumbnails.
- **Search within a chassis** — type-to-find a card by name without scrolling.
- **Cross-pod card search** — find every card called "PCB-0163" across all chassis (currently appears in multiple zones).
- **"Show related"** — `card_index.chunk_ids` is populated but not surfaced. A button to inline-display the manual excerpt corresponding to those chunks would be valuable.
- **Mobile/tablet responsive chassis SVG** — current layout assumes desktop screen real estate.
- **Onboarding** — first-time users drop on the menu with no introduction to how cards work.
- **Empty/loading/error states** — currently terse. Could be much friendlier without compromising the underlying logic.
- **Click-through animation** — the sidebar currently pops in. Could be a slide, a focus shift, anything that feels less abrupt.

---

## Known limitations (honest framing — don't paper over)

1. **Not every card has a `card_index` row.** Only 30 rows in the table today. Most cards fall back to `POD_ZONES` which is fine, but means the live-overlay enrichment is uneven across the manual.
2. **Race condition under fast clicking.** If a user clicks card A, then quickly clicks card B before A's `card_index` fetch returns, A's response can overwrite B's sidebar. Not catastrophic — the sidebar is wrong for 200ms then self-corrects on next click. Worth fixing if you're already in the area.
3. **`DESCRIPTIONS` and `snippets.json` are two parallel description sources** with overlapping purposes — `DESCRIPTIONS` (in `index.html`) is what cards actually use; `snippets.json` (separate file, ~15.7 KB) appears to be a parallel store with similar content for ~20 major components. Their relationship is not currently documented. Investigate before changing either.
4. **The chassis SVGs are spread across `index.html`** rather than externalised. Editing one means hunting through the HTML. Externalisation to standalone `.svg` files referenced via `<object>` or `<img>` is a defensible refactor but would change file-load timing.
5. **No "this card has been viewed" / "favourite this card" affordance.** A duty engineer hunting through many cards has no breadcrumb.
6. **Cards on the chassis SVGs are not keyboard-navigable.** Mouse-only today.

---

## Smoke test before committing any card-system change

If you touch `POD_ZONES`, `DESCRIPTIONS`, `openCardInfo()`, the chassis SVGs, or anything in the card sidebar render path:

1. **Click 3 cards in 3 different chassis** — sidebar should populate instantly with title + detail/description + drawing list each time. No console errors.
2. **Click a drawing link in the sidebar** — PDF viewer tab should open at the correct page.
3. **Click a card that you know has a `card_index` row** (e.g. one of the well-trafficked Control Chassis cards) — sidebar should briefly show `POD_ZONES` drawings, then update to `card_index.local_files` drawings within ~500ms.
4. **JS parse check** (project canonical):
   ```bash
   python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"
   ```
5. **Test on `file://` protocol** — open `index.html` directly in a browser via double-click (not via the dev http server). Card click should still work for cards that don't depend on `card_index`. This is the vessel-deploy scenario.

If all five pass, the card system contract is intact.

---

## Where the card system lives in code

| Location | Purpose |
|---|---|
| `index.html` ~line 743 | `DESCRIPTIONS` constant — hand-authored long-form fault-diagnosis text |
| `index.html` ~line 745 | `normKey()` function — card-key normaliser |
| `index.html` ~line 1545 | `POD_ZONES` constant — static card data per chassis |
| `index.html` ~line 1639 | Zone view renderer — builds the chassis SVG and card overlays |
| `index.html` ~line 1664 | Card click handler — wires SVG onclick to `openCardInfo()` |
| `index.html` ~line 1736 | `openCardInfo(zone, cardIdx)` — async function, the heart of the system |
| `index.html` ~line 1760 | Supabase `card_index` fetch |
| Chassis SVGs in `index.html` | Hand-drawn per pod, positioned to match physical layout |
| Supabase `card_index` table | Live overlay data, 30 rows |
| Supabase `match_chunks` RPC | Not directly used by cards, but `card_index.chunk_ids` references chunks discoverable via this RPC |

Line numbers shift as edits happen. Grep for `POD_ZONES`, `DESCRIPTIONS`, `openCardInfo`, `card_index` to find current locations.

---

## Cross-references

- For the wider drawing-index architecture (`card_index`, `drawing_families`, the standalone tree HTMLs as three independent layers) see `DRAWING_INDEX.md`. The card system is Layer 1 of that picture.
- For the security model behind any Supabase call see `SECURITY_BRIEF.md`. The direct browser → Supabase `card_index` lookup uses the public-by-design anon key and is deliberately not gated.
- For the full project vision and outstanding work see `PROJECT_STATUS.md`.
- For every file in the project see `FILE_INVENTORY.md`.

---

## One-paragraph TL;DR

Cards are the navigation primitive of this manual: each represents a real PCB / connector / module in a real chassis position, rendered as a clickable tile on a hand-drawn chassis SVG. Click a card → sidebar shows the card's name, long-form fault-diagnosis description, and clickable links to its drawings. Data comes from three sources: `POD_ZONES` (in-page static, has card definitions and short details), `DESCRIPTIONS` (in-page static, has long-form fault text keyed by `zone/normalised_name`), and Supabase `card_index` (live overlay that enriches the drawing list async). The instant-render-from-static / async-overlay-from-network pattern is load-bearing for offline use on vessel. The chassis SVGs are documentation that happens to be interactive — their position-to-physical-position mapping is the design intent and must be preserved through any redesign.
