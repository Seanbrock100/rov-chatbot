# Hercules MK3 Interactive Manual — V2 Specification
# Date: Apr 2026 | Author: Sean Brock

## Vision

A living technical knowledge system for the Hercules MK3 fleet.
Not a chatbot with a manual attached — an interactive manual with chatbot assistance.

Core principles:
1. **Manual first** — engineers navigate drawings, components, specs
2. **Chatbot assists** — context-aware help without leaving the manual  
3. **Central controlled space** — all drawings, manuals, superseded docs in one place
4. **Self-learning** — engineer corrections stored and used in future answers
5. **Grows with the system** — as the ROV changes, the knowledge base updates

---

## Layout

```
HEADER (unchanged)
──────────────────────────────────────────────────────────────────
│  VIEWER TABS (left, ~70% width)        │  RIGHT SIDEBAR (380px) │
│  ┌──────────────────────────────────┐  │                        │
│  │ POD × │ 55017 × │ 55001 × │ 💬 × │  │  CONTEXT STRIP         │
│  └──────────────────────────────────┘  │  Pod › Ctrl › VideoMUX │
│                                        │  ──────────────────── │
│  [PDF / SVG / Chat renders here]       │  DRAWINGS  │  MANUALS  │
│                                        │  (live from Supabase)  │
│                                        │  click → opens tab     │
│                                        │  ──────────────────── │
│                                        │  FIELD NOTES           │
│                                        │  engineer notes here   │
│                                        │  ──────────────────── │
│                                        │  [💬 OPEN CHAT TAB]    │
└────────────────────────────────────────┴────────────────────────
```

---

## Viewer Tabs

- Strip at top of left viewer area
- Each tab: short label + × close button
- Tab types: PDF (drawings), SVG (pod schematic), CHAT (chatbot)
- Active tab = amber underline
- All drawing links open as tabs (not new browser windows)
- Chat tab is permanent — never closes, persists full session
- Max 8 PDF tabs (oldest closes with warning toast)
- Session-persistent — survive component navigation

---

## Right Sidebar — Three Sections

### 1. Context Strip (top, ~36px)
Shows current navigation path. Updates automatically.
```
📍 Electronics Pod  ›  Control Chassis  ›  Video MUX PCB (PCB-0124)
```
Injected silently into every chatbot message.

### 2. Drawings / Manuals Tabs (middle, flex)
**Live from Supabase** — queries on every component navigation.
Not hardcoded. Results filtered by:
- Current system (e.g. 'Electronics Pod')
- Current component/card name keyword search
- Status: current drawings first, superseded shown below with ⚠️ flag

Drawing items show:
- Drawing number
- Title  
- Status badge: CURRENT / ⚠️ SUPERSEDED (→ superseded_by number)
- Click → opens as viewer tab

Manual items show:
- Manual name
- Relevant page range (from chunks table)
- Click → opens PDF as viewer tab

### 3. Field Notes (bottom, collapsible)
Engineer-added notes for the current component.
- Shows existing notes from component_notes table
- "Add note" button → inline text input → saves to Supabase
- Note types: general / fault / modification / tip / warning
- Shows who added it and when

### 4. Open Chat Tab Button (fixed bottom)
```
[💬 ASK ABOUT THIS COMPONENT]
```
Opens/focuses the chat tab in the viewer area.
Chat tab already has context of what component is selected.

---

## Chat Tab

Full-width viewer tab. Persistent for the session.

### Layout within tab:
```
[CONTEXT BANNER]
Electronics Pod › Control Chassis › Video MUX PCB (PCB-0124)
─────────────────────────────────────────────────────────────
[MESSAGES — scrollable]

  Engineer: show me the wiring diagram
  
  Bot: [DRAWING CARD]
       EQP952-0203-DR-PD-55017
       Control Chassis Wiring Diagram
       [OPEN IN VIEWER TAB]
  
  Engineer: what does the video mux do
  
  Bot: The Video MUX PCB (PCB-0124) routes coaxial Y/C video...
       
       [MANUAL CARD]
       TMA01030 · Pages 22–24
       "The Video MUX Backplane PCB-0124 routes..."
       [OPEN MANUAL]

  Engineer: that's wrong, the connector is 8-pin not 6-pin
  
  Bot: Thank you — I had that wrong. The correct connector is
       8-pin Mini Burton 5929-0207-PE04. 
       Should I save this correction for future reference? [YES] [NO]
─────────────────────────────────────────────────────────────
[  Ask about this component...                            ▶  ]
```

### Context always injected (invisible to engineer):
```
You are the Hercules MK3 ROV technical assistant.
Vessel: Seven Oceanic. Fleet: HE15/HE30.
Current view: {system} › {component} › {card}
Drawing open: {viewer_tab_filename}
Checked corrections first: {any corrections for this component}
Answer concisely. Use exact drawing numbers. 
When asked to show a drawing, call open_drawing().
```

### Chat Tools (agentic):
1. `search_manuals(query)` → chunks table, biased to current system
2. `search_drawings(query)` → drawings table, returns local_file
3. `search_faults(query)` → fault_log + handover_log
4. `check_corrections(component)` → knowledge_corrections table
5. `open_drawing(filename, label)` → opens PDF as viewer tab (client-side action)
6. `save_correction(component, question, wrong, correct)` → writes to knowledge_corrections

### Learning Flow:
When engineer says answer is wrong:
1. Bot acknowledges, asks to save
2. If yes → calls save_correction() → stores in knowledge_corrections
3. Amendment logged in manual_amendments table
4. Next query on same component → check_corrections() runs first
5. Correct answer returned with citation: "Confirmed by [initials] [date]"

---

## Supabase Schema — Current State After Migration

### Tables:
| Table | Purpose |
|-------|---------|
| chunks | Manual text + embeddings (413→800+ chunks when embedding complete) |
| drawings | Drawing metadata + local_file + status + superseded_by |
| fault_log | Sub-engineer fault history 2012–present |
| handover_log | End-of-trip reports 2023–present |
| knowledge_corrections | Engineer corrections to chatbot answers |
| component_notes | Field notes per component |
| manual_amendments | Audit log of all knowledge base changes |

### Drawings status values:
- `current` — live drawing, use this
- `superseded` — replaced, superseded_by shows replacement
- `draft` — not yet approved
- `cancelled` — withdrawn

---

## Build Phases

### Phase 1 — Tabbed Viewer (no chatbot yet)
- Replace l2-viewer with tab strip + pdf.js renderer
- Drawing links across entire manual open as tabs
- Pod SVG = Tab 0 ("POD")
- Chassis detail = Tab 1 ("CTRL" or "PYLD")
- VERIFY: tabs work, PDFs render, tabs close, session persists navigation

### Phase 2 — Live Sidebar (no chatbot yet)  
- Replace hardcoded DRAWINGS/MANUALS lists with live Supabase queries
- Query: drawings WHERE system = current_system AND status = 'current'
- Keyword search on component name for more specific results
- Superseded drawings shown with ⚠️ flag and → replacement link
- Field notes section — read and write to component_notes
- VERIFY: Video MUX shows correct drawings, superseded flagged

### Phase 3 — Chat Tab UI (no AI yet)
- Add chat tab type to viewer
- Context strip wires to navigation events
- Message bubbles render correctly
- Drawing cards and manual cards render in chat
- Input bar works (Enter sends, Shift+Enter newline)
- VERIFY: UI looks right, context updates with navigation

### Phase 4 — Supabase Tool Functions
- search_manuals(), search_drawings(), search_faults()
- check_corrections() — new table
- Test each independently against Supabase
- VERIFY: "Video MUX" returns correct drawings and manual chunks

### Phase 5 — Agentic Loop
- Wire input bar to Anthropic API
- Tool use with streaming
- open_drawing() intercepted client-side → opens tab
- save_correction() flow with confirmation
- VERIFY: full end-to-end flow, correction saves to Supabase

### Phase 6 — Cowork Tasks
- Non-pod component card detail views (TCU, HPU, LARS)
- card_index table population (after TMA01030 fully embedded)
- Drawing status audit (which others are superseded)

---

## Credentials Strategy
Single fetch at startup from Railway config endpoint.
Stored in module-level CONFIG object.
All API calls use CONFIG.anthropicKey, CONFIG.supabaseUrl etc.
No keys hardcoded. Works as long as vessel has internet to Railway.

---

## Files to Update
- rov-manual/index.html — main build target
- No new files needed — single self-contained HTML stays the goal
- descriptions_norm.json — stays as offline fallback
