# DRAWING INDEX — Implementation Summary

**Snapshot date:** 13 May 2026
**Companion to:** `PROJECT_STATUS.md`, `FILE_INVENTORY.md`, `MASTER_KNOWLEDGE.md`

> The "Drawing Index" is the umbrella term for three independent layers that connect the manual's UI to the drawing corpus. Each layer answers a different question.
>
> Layer 1 — *"Show me every drawing that belongs to this card."*
> Layer 2 — *"What does this drawing number actually mean?"*
> Layer 3 — *"Let me browse the drawing tree by assembly hierarchy."*

---

## Layer 1 — `card_index` (Supabase) → card sidebar

### Purpose
When an engineer clicks a card on a pod chassis view (e.g. PCB-0094 Video MUX), the sidebar refreshes with **the full list of drawings associated with that specific card**, not just the hardcoded ones in `POD_ZONES`. This gives a card-centric view of the drawing corpus.

### Data model — Supabase `card_index` table

30 rows. Each row maps one pod card to its drawing set.

| Column | Type | Notes |
|---|---|---|
| `card_key` | text (PK) | Normalised `zone/cardname` key — e.g. `electronics_pod/pcb-0094 video mux` |
| `local_files` | text[] | Filenames in `manuals/` — e.g. `['ROV-0311-D-0650-00.pdf', 'PCB-0094_video_mux.pdf']` |
| `chunk_ids` | int[] | (Populated) IDs into `chunks` table for retrieval by the chatbot |

### Key generation — `normKey()` in `index.html` (line 745)
JavaScript function that normalises a zone + card name into a stable lowercase key. Must match the `py_norm_key()` function in the embed scripts byte-for-byte — unicode dashes preserved, multi-space collapsed, surrounding whitespace trimmed.

### Flow — `openCardInfo(zone, cardIdx)` at `index.html` line 1736

1. Engineer clicks a card on a chassis SVG → calls `openCardInfo(zone, cardIdx)`
2. **Instant render** — sidebar populated from the hardcoded `POD_ZONES[zone].cards[cardIdx].drawings` array. No network wait.
3. **Async overlay** — fetch `card_index?card_key=eq.<normalised>` from Supabase using anon key
4. If row returned and `local_files` is non-empty → re-render sidebar from `local_files`, overriding the hardcoded list
5. Card description (long text) loaded from local `DESCRIPTIONS` cache (offline-capable)

### Why two data sources?
- `POD_ZONES` (in `index.html`) is hand-authored, ships in the static HTML, works offline. Guarantees instant response even when Railway/Supabase are unreachable.
- `card_index` (in Supabase) is editable without redeploy. Maintained centrally, surfaces newly catalogued drawings without touching the HTML.

The pattern is "static fallback + live overlay". Sidebar is correct enough offline; gets richer online.

### Network behaviour
- Uses anon key, direct from browser to Supabase REST API (no Flask proxy)
- 200ms typical latency on Mac, ~600ms on vessel
- Silent failure on network error — sidebar keeps the `POD_ZONES` fallback
- No password gate (anon key reads only)

---

## Layer 2 — `drawing_families` (Supabase) → chatbot fact injection

### Purpose
When the chatbot is asked a question that mentions a drawing number, the system **injects authoritative facts about that drawing series into the system prompt before the model answers**. This stops the chatbot from inventing drawing meanings or contradicting known legacy/superseded relationships.

### Data model — Supabase `drawing_families` table

70 rows. Each row defines a drawing-number prefix or series.

| Column | Notes |
|---|---|
| `series` | Series identifier — e.g. `ROV-0311-D-0650`, `EQP952-0203-DR-PD-55003` |
| `description` | What the series IS — e.g. `Rainbow Rack` |
| `section` | Which functional system it belongs to |
| `is_current` | Boolean — false means superseded |
| `superseded_by` | Newer series that replaces this one |
| `warning` | Free text — e.g. "Often confused with the CRNA, but different card" |

Hand-curated by Sean. Source of truth for "what is this drawing number actually?"

### Auto-fire detection — `index.html` line 2472

```js
const drgNumMatches = msg.match(/(?:ROV|EQP|HCV|OCE|PDU|SSA|TMA|CAB)-[\w-]+|\d{3}-\d{4}/gi) || [];
```

Regex covers:
- Prefixed numbers — `ROV-0311-D-0200-00`, `EQP952-0203-DR-PD-55003`, `TMA01030-...`
- Bare four-digit-after-three-digit pattern (catches loose references like `952-0203`)

When the regex matches, the first 3 drawing numbers are looked up in parallel via the `lookup_drawing_family` Postgres RPC.

### RPC — `lookup_drawing_family(p_query text)`
Returns matching rows from `drawing_families` based on prefix/series match. Implementation lives in Supabase (Postgres function), not in the frontend.

### Injection format — `index.html` line 2486

```
⚠️ DRAWING NUMBER FACTS — YOU MUST USE THESE, DO NOT CONTRADICT THEM:
<series> IS: <description> | section: <section> | STATUS: SUPERSEDED by <new> | WARNING: <warning>
```

This block prepends the rest of the system prompt. The capitalisation and explicit "do not contradict" framing exists because earlier versions of the chatbot would override the injected facts with confident-but-wrong guesses about what a drawing series was. The aggressive framing measurably suppressed that behaviour in QA.

### Effect on answers
Without `drawing_families`: model might claim `ROV-0311-D-0650-00` is "the CRNA interface card" because the chunks mention both nearby.
With `drawing_families`: model is told "ROV-0311-D-0650 IS: Rainbow Rack" and trace continues correctly.

This is the most important safeguard against hallucination on drawing references.

---

## Layer 3 — Standalone tree HTMLs (offline-static deep navigation)

### Purpose
Four standalone HTML pages that present a **hierarchical browseable tree of drawing assemblies and sub-assemblies**, designed for the case where the engineer wants to explore the drawing tree directly rather than click their way through cards.

### The four files (in `rov-manual/`)

| File | Lines | Tree root |
|---|---|---|
| `drawing-tree.html` | 721 | `ROV-0311-D-0001-00` Hercules MK3 Vehicle Assembly (full system) |
| `control-room-tree.html` | 574 | Control Room subsystem |
| `lars-tree.html` | 658 | LARS subsystem — 10 sub-systems (LCC, latch beam, cursor, etc.) |
| `pdu-tree.html` | 566 | PDU subsystem |

### Data model — embedded in each HTML file

```js
const FILES = {
  'ROV-0300-D-0100-01': 'ROV/Mechanical/Frame and Structure/Frame Assembly ...pdf',
  // ~200 mappings
};

const TREE = {
  id: 'ROV-0311-D-0001-00',
  label: 'Hercules MK3 (3000M) Vehicle Assembly',
  type: 'a',                                   // 'a' = assembly
  children: [
    { id: '...', label: '...', type: 'a', children: [...] },
    // recursive
  ]
};
```

`FILES` is the drawing-number → PDF-path mapping. `TREE` is the recursive structure. Each tree HTML has its own scoped `FILES` + `TREE` — they don't share data.

### UI features (in each tree HTML)
- Recursive expand/collapse of tree nodes
- Search box (filters by drawing number or label, live)
- Match count display
- Breadcrumb navigation
- Click any leaf → opens the PDF (via `BASE` URL)

### KNOWN ISSUE — tree HTMLs are dev-only

The four tree HTML files have **two stacked problems** that together mean they only function in Sean's local dev environment:

**Problem 1 — hardcoded localhost base URL:**
```js
const BASE = 'http://localhost:8765/docs/';
```
All four files reference the local Python http server at port 8765. They cannot load PDFs over `file://`.

**Problem 2 — hierarchical paths only exist in the docs symlink target:**
```js
const FILES = {
  'ROV-0300-D-0100-01': 'ROV/Mechanical/Frame and Structure/Frame Assembly ROV-0300-D-0100-01.pdf',
  ...
};
```
The `FILES` map paths assume a hierarchical folder structure (`ROV/Mechanical/Frame and Structure/...`) that exists in the **reorganised folder** (reached via the `rov-manual/docs` symlink), NOT in the flat `manuals/` folder that ships to the vessel. Even if `BASE` is fixed, the paths still don't resolve.

| Environment | Tree HTMLs work? |
|---|---|
| Sean's Mac, Python http server on 8765, docs symlink resolves | Yes |
| Vessel PC, manual opened via `file://`, flat `manuals/` folder | **No — every PDF link 404s** |
| Railway-served root | No (no `/docs/` route defined) |

### Remediation options — design decision required

1. **Rewrite all four `FILES` maps to flat filenames** matching the actual `manuals/` directory. Combined with `BASE = './manuals/'` (or protocol-detect), trees work over `file://` with no folder duplication. Cost: mechanical work, ~200 entries per file = ~800 entries total. Trade-off: loses the readable hierarchical paths in the code.
2. **Ship the hierarchical folder structure to vessel** alongside the flat `manuals/`. Trees continue to use hierarchical paths. Cost: ~1.4 GB duplication on the vessel drive plus a copy-time step to materialise the symlinked structure.
3. **Accept dev-only** and remove the tree HTML menu links from `index.html` for the vessel build. Vessel engineers use the chatbot's drawing search instead. Cost: feature loss on vessel, but the chatbot already does drawing-number → family-context → contextual search well.

No option chosen yet. This is a deliberate flagged decision for the vessel-deploy planning phase, not a quick fix.

---

## Cross-cutting — how the three layers interact

```
User clicks pod card
  │
  ▼
[Layer 1] POD_ZONES instant render → card_index Supabase overlay
                                          │
                                          ▼
                                      drawings list in sidebar

User types question into chatbot
  │
  ▼
Regex detects drawing number in message
  │
  ▼
[Layer 2] drawing_families RPC → series facts
                                    │
                                    ▼
                       Injected into system prompt
                                    │
                                    ▼
                              Anthropic call

User clicks "Drawing Tree" link in main menu
  │
  ▼
[Layer 3] Loads drawing-tree.html (or one of the subsystem trees)
                │
                ▼
        Hardcoded TREE + FILES → recursive browseable view
                                    │
                                    ▼
                              Click PDF → BASE + path
                                    │
                                    ▼
                  (BREAKS on file:// vessel deploy — see KNOWN ISSUE)
```

The three layers are independent. Layer 1 doesn't know about Layer 2 doesn't know about Layer 3. They can fail independently and the other two keep working.

---

## What's NOT covered by the Drawing Index

- **Free-text drawing search** — typing "show me the LARS cursor drawing" into the chatbot relies on the vector search across `chunks`, not on `drawing_families`. Drawing-family lookup only fires when a *drawing number* is detected, not when a drawing is described semantically.
- **Drawing version diffs** — there's no comparison view between revisions of the same drawing.
- **Drawing → chunk back-reference** — `card_index.chunk_ids` is populated but not currently surfaced in the UI. Could power "show me the manual text for this drawing" in future.

---

## Files touched / owned

| File | Layer | Role |
|---|---|---|
| `rov-manual/index.html` line 745 | 1 | `normKey()` — key normalisation |
| `rov-manual/index.html` lines 1545–1700 | 1 | `POD_ZONES` static data + chassis SVG event handlers |
| `rov-manual/index.html` line 1736 | 1 | `openCardInfo()` — async card click handler |
| `rov-manual/index.html` lines 2472–2492 | 2 | drawing-number regex + RPC call + system-prompt injection |
| `rov-manual/drawing-tree.html` | 3 | Full vehicle tree |
| `rov-manual/control-room-tree.html` | 3 | Control Room tree |
| `rov-manual/lars-tree.html` | 3 | LARS tree |
| `rov-manual/pdu-tree.html` | 3 | PDU tree |
| Supabase `card_index` table | 1 | 30 card mappings |
| Supabase `drawing_families` table | 2 | 70 series definitions |
| Supabase `lookup_drawing_family` RPC | 2 | Series fact lookup |

---

## Open work specific to the Drawing Index

1. **Fix tree HTML `BASE` URLs before vessel deploy** — Option 2 (protocol detection) is the minimal patch.
2. **Populate `card_index` rows for remaining cards** — 30 rows today, more cards exist in `POD_ZONES` than have `card_index` entries; gaps fall back to `POD_ZONES` which is fine but means newly catalogued drawings don't surface.
3. **Surface `card_index.chunk_ids`** in the card sidebar — "Show related manual sections" button that opens chunk excerpts inline.
4. **Add `drawing_families` rows for thinly-covered prefixes** — TMS, longline, cable prefixes have no entries; chatbot hallucinations on those drawings still possible.
5. **Search index of all `FILES` mappings across the tree HTMLs** — currently each tree has its own scoped FILES; a unified search across all four would help engineers find a drawing without knowing which subsystem it lives under.

---

## Why this design

- **Static-first, network-second** is the consistent theme. `POD_ZONES` works offline; `card_index` is enrichment. Hardcoded tree HTML works without any backend; vector search is enrichment. This is appropriate for a vessel where internet may drop.
- **Layer separation** means one layer breaking doesn't cascade. `drawing_families` outage doesn't stop card clicks. `card_index` outage doesn't stop the chatbot. Tree HTML being broken on `file://` doesn't stop anything else.
- **The chatbot is graded against `drawing_families`** in the same way it's graded against `MASTER_KNOWLEDGE.md`. Both exist because the LLM hallucinates confidently about drawing numbers if not corrected.
