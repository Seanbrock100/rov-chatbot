# COWORK TASK — Reorganise Technical Docs Folder

## Objective
Reorganise `/Users/seanbrock/work documents/3. Technical Docs` to match the structure of the Hercules MK3 Interactive Manual.

Additionally, **rename PDF files whose names are only drawing numbers** by opening each one, reading the title block text, and prepending the English title.

Example:
- `EQP952-0203-DR-PD-55001.pdf` → `Control Chassis Assembly EQP952-0203-DR-PD-55001.pdf`
- `ROV-0300-D-0420-90.pdf` → `TCU Wiring Diagram ROV-0300-D-0420-90.pdf`

---

## Target Folder Structure

Create this structure inside `/Users/seanbrock/work documents/3. Technical Docs/`:

```
Longlines/
Control Room/
PDU/
ROV/
  Electrical/
    Electronics Pod/
    Term Can/
    Lights/
  Hydraulic/
    HPU - Pump and Tank/
    Valve Packs/
    TCU - Thruster Control/
    Pan and Tilt/
    Thrusters - Curvetech/
  Mechanical/
    Frame and Structure/
TMS/
  H15/
  H30/
LARS/
  LCC Winch/
  Latch Beam/
  Latch Beam Winch/
  Cursor/
  Sliding Weight/
  LARS HPU/
  Moonpool Doors/
  Service Winch/
  Service Winch Slip Ring/
  Tether/
Manipulators/
  T4 - Schilling/
  Atlas - Schilling/
Reference/
  Cables/
  All Drawings/
Ancillary and Tooling/   (existing content not in ROV manual scope)
Archive/                 (anything that doesn't fit above)
```

---

## Step 1 — Create the New Folder Structure

Create all folders listed above under `/Users/seanbrock/work documents/3. Technical Docs/`.

---

## Step 2 — Migrate Existing Files

Move files from old locations to new structure according to the mapping below.

### Drawing Number Reference (to help categorise)
| Drawing prefix | Goes to |
|---------------|---------|
| EQP952-0203-DR-PD-550xx | ROV/Electrical/Electronics Pod/ |
| ROV-0300-D-0300, HCV-0009 | ROV/Electrical/Term Can/ |
| ROV-0311-D-0680, OR-TE-03338 | ROV/Electrical/Lights/ |
| ROV-0249, ROV-0300-D-0440, TMA00974 | ROV/Hydraulic/HPU - Pump and Tank/ |
| ROV-0305-D-0450, ROV-0311-D-0208, Aleron | ROV/Hydraulic/Valve Packs/ |
| ROV-0300-D-0420, TMA01031 | ROV/Hydraulic/TCU - Thruster Control/ |
| ROV-0305-D-0630, ROV-0305-D-0660 | ROV/Hydraulic/Pan and Tilt/ |
| Curvetech HTE, ROV-0226-630 | ROV/Hydraulic/Thrusters - Curvetech/ |
| ROV-0300-D-01xx, ROV-0305-D-01xx, SSA-0277, buoyancy | ROV/Mechanical/Frame and Structure/ |
| TMA01028, FORUM MK2B, OME-0501, H15 drawings | TMS/H15/ |
| TMA01029, TMS 41-45, TMS 51, H30 drawings | TMS/H30/ |
| OCE-0400-DR-055x/056x, TMA01071, LARS LCC | LARS/LCC Winch/ |
| OCE-0400-DR-014x, latch beam | LARS/Latch Beam/ |
| OCE-0400-DR-030x, LB winch | LARS/Latch Beam Winch/ |
| OCE-0400-DR-013x, cursor | LARS/Cursor/ |
| Sliding Weight | LARS/Sliding Weight/ |
| OCE-0400-DR-0306, LARS HPU | LARS/LARS HPU/ |
| OCE-0400-DR-0124, moonpool | LARS/Moonpool Doors/ |
| OCE-0400-DR-071x/072x/081x/082x, service winch | LARS/Service Winch/ |
| Slip ring drawings | LARS/Service Winch Slip Ring/ |
| Tether/umbilical drawings | LARS/Tether/ |
| 011-8239, 101-xxxx, Titan, T4, Schilling, 8212, 8239 | Manipulators/T4 - Schilling/ |
| Atlas, SP-011, IVP, 8228, 8242 | Manipulators/Atlas - Schilling/ |
| Longline, EQP952-021x, EQP952-023x | Longlines/ |
| HCV-001x, HCV-003x, control console, joystick, PDU-0009 | Control Room/ |
| PDU-1012 | PDU/ |
| CAB-xxxx cables index | Reference/Cables/ |

### Old folder → New folder mapping
| Old folder | New location |
|-----------|-------------|
| ROV/Herc Mk 3 manuals/Pod Drawings Post MOTC/ | ROV/Electrical/Electronics Pod/ |
| ROV/MK3 Termination JB Drawings/ | ROV/Electrical/Term Can/ |
| ROV/Herc 15-30 MK III xx/HPU Drawings/ | ROV/Hydraulic/HPU - Pump and Tank/ |
| ROV/Thrusters/Curvetech HTE380/ | ROV/Hydraulic/Thrusters - Curvetech/ |
| ROV/Thrusters/TCU/ | ROV/Hydraulic/TCU - Thruster Control/ |
| ROV/Tool Tray/ | ROV/Mechanical/Frame and Structure/ |
| ROV/Vehicle Buoyancy/ | ROV/Mechanical/Frame and Structure/ |
| TMS/H15/ | TMS/H15/ |
| TMS/H30/ | TMS/H30/ |
| LARS/ (all sub-folders) | LARS/ (sort by sub-system per mapping above) |
| Manips/Titan/ | Manipulators/T4 - Schilling/ |
| Manips/Atlas Manips/ | Manipulators/Atlas - Schilling/ |
| Longline Drawings/ | Longlines/ |
| Control Room/ | Control Room/ |
| PDU/ | PDU/ |
| Lights/ | ROV/Electrical/Lights/ |
| Ancillary Tooling/ | Ancillary and Tooling/ |
| Fibre Optics/ | ROV/Electrical/Electronics Pod/ |
| Cables/ | Reference/Cables/ |

**Anything that doesn't match** goes to `Archive/` — do NOT delete anything.

---

## Step 3 — Rename Drawing-Number-Only Files

### Which files need renaming
A file needs renaming if its name (excluding extension) matches a drawing number pattern:
- Starts with `EQP`, `ROV-`, `OCE-`, `HCV-`, `PDU-`, `SSA-`, `CAB-`, `OME-`, `TMA`, `011-`, `101-`, `SP-`
- And has **no other descriptive words** after the drawing number

Examples:
- `EQP952-0203-DR-PD-55001.pdf` → RENAME (pure drawing number)
- `ROV-0300-D-0420-90.pdf` → RENAME (pure drawing number)
- `TCU Wiring Diagram ROV-0300-D-0420-90.pdf` → SKIP (already has title)
- `Curvetech HTE380 Thruster Manual.pdf` → SKIP (already descriptive)

### How to get the title
1. Open each PDF using `pdfminer` to extract text
2. Look for the title block — it is usually in the first 2 pages
3. The title is typically the **largest text** or found near the drawing number in the header/title block
4. Common patterns to find: lines containing "TITLE:", lines above the drawing number, text in ALL CAPS near the drawing number

### Rename format
`[Title from drawing] [Drawing Number].pdf`

Keep the drawing number at the end so files still sort by number within a folder.

Example titles to expect:
| Drawing Number | Expected Title |
|---------------|---------------|
| EQP952-0203-DR-PD-55000 | Electronics Pod Assembly GA |
| EQP952-0203-DR-PD-55001 | Control Chassis Assembly |
| EQP952-0203-DR-PD-55002 | Payload Chassis Assembly |
| EQP952-0203-DR-PD-55003 | Control Penetrator Ring GA |
| EQP952-0203-DR-PD-55004 | Payload Penetrator Ring GA |
| EQP952-0203-DR-PD-55016 | Payload Chassis Wiring Diagram |
| EQP952-0203-DR-PD-55017 | Control Chassis Wiring Diagram |
| ROV-0300-D-0420-00 | TCU Assembly |
| ROV-0300-D-0420-90 | TCU Wiring Diagram |
| ROV-0300-D-0440-00 | Hydraulic Schematic |
| ROV-0305-D-0450-00 | Curvetech Valve Pack GA |
| OCE-0400-DR-0551-90 | LARS Port LCC Wiring Diagram |
| OCE-0400-DR-0561-90 | LARS Stbd LCC Wiring Diagram |

If the title cannot be extracted from the PDF (scanned/image PDF), add a note `[OCR NEEDED]` prefix instead:
`[OCR NEEDED] EQP952-0203-DR-PD-55001.pdf`

### Script approach
```python
import os, re
from pdfminer.high_level import extract_text

DRAWING_PATTERN = re.compile(
    r'^(EQP|ROV-|OCE-|HCV-|PDU-|SSA-|CAB-|OME-|TMA|011-|101-|SP-)',
    re.IGNORECASE
)

def is_drawing_number_only(filename):
    """Returns True if filename is just a drawing number with no descriptive words"""
    name = os.path.splitext(filename)[0]
    # Remove sheet suffixes like "SHT 1", "sht 1-3", "(1 of 2)" etc
    name_clean = re.sub(r'\s*(SHT|sht|Sheet)[\s\d-]+.*$', '', name).strip()
    name_clean = re.sub(r'\s*\(\d+\s*of\s*\d+\).*$', '', name_clean).strip()
    # Check if what remains is purely a drawing number
    return bool(DRAWING_PATTERN.match(name_clean)) and len(name_clean.split()) <= 2

def extract_title_from_pdf(path):
    """Extract title from drawing title block"""
    try:
        text = extract_text(path, page_numbers=[0, 1])
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
        # Look for TITLE: field
        for i, line in enumerate(lines):
            if line.upper().startswith('TITLE:'):
                title = line[6:].strip()
                if title:
                    return title
            if 'TITLE' in line.upper() and i+1 < len(lines):
                next_line = lines[i+1]
                if not re.match(r'^[A-Z0-9-]{5,}$', next_line):
                    return next_line
        # Fallback: look for descriptive ALL CAPS or Title Case lines that aren't drawing numbers
        for line in lines[:30]:
            if len(line) > 8 and not DRAWING_PATTERN.match(line):
                if re.match(r'^[A-Z][A-Z\s/&-]+$', line) or re.match(r'^[A-Z][a-z]+(\s[A-Za-z]+)+$', line):
                    if not any(skip in line.upper() for skip in ['SUBSEA 7', 'SHEET', 'REV', 'DATE', 'SCALE', 'DRG NO', 'CHECKED', 'DRAWN']):
                        return line
        return None
    except Exception:
        return None
```

---

## Step 4 — Log Everything

Create a log file at:
`/Users/seanbrock/work documents/3. Technical Docs/REORGANISATION_LOG.txt`

Log format:
```
=== REORGANISATION LOG ===
Date: [date]

FOLDERS CREATED:
  [list]

FILES MOVED:
  [old path] → [new path]

FILES RENAMED:
  [old name] → [new name]
  Title extracted from: page 1, line N

FILES THAT NEED OCR:
  [list]

FILES NOT CATEGORISED → Archive/:
  [list]
```

---

## Important Rules

1. **Never delete any file** — move to `Archive/` if uncertain
2. **Never overwrite** — if destination file exists, rename with `_DUPLICATE` suffix
3. **Keep sub-folders** within each new section — don't flatten everything
4. **Don't touch** `Ancillary Tooling/`, `Survey/`, `Work Instructions and checklists/` — move as-is to `Ancillary and Tooling/`
5. **Scanned PDFs** (no extractable text) — rename with `[OCR NEEDED]` prefix, still move to correct location
6. **Run on the actual folder** — `/Users/seanbrock/work documents/3. Technical Docs/`
7. **Test on one subfolder first** — run on `ROV/Herc Mk 3 manuals/Pod Drawings Post MOTC/` first and report results before proceeding with the full reorganisation

---

## Files NOT in scope (leave in place)
- Survey equipment docs
- Rigging docs
- Ancillary tooling (move as a block to Ancillary and Tooling/)
- Work instructions and checklists
- Swagelok, Clear-Com, Air Con, Oil Reclaim (move to Archive/)
