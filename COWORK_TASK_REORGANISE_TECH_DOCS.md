# COWORK TASK — Reorganise Technical Docs Folder

## Objective
Create a new, parallel folder structure at:

`/Users/seanbrock/work documents/3. Technical Docs - Hercules MK3/`

Populate it with **copies** (never moves) of relevant files from the original folder, renamed where needed.

**The original `/Users/seanbrock/work documents/3. Technical Docs/` folder must not be touched.**

PDF files whose names are only drawing numbers are renamed by extracting the English title from the drawing title block.

Example:
- `EQP952-0203-DR-PD-55001.pdf` → `Control Chassis Assembly EQP952-0203-DR-PD-55001.pdf`
- `ROV-0300-D-0420-90.pdf` → `TCU Wiring Diagram ROV-0300-D-0420-90.pdf`

---

## The Script

The script is already written and ready to run:

`/Users/seanbrock/Documents/GitHub/rov-chatbot/reorganise_tech_docs.py`

**Dependencies:** `pdfminer.six` (already installed)

---

## How to Run

### Step 1 — Test run first (REQUIRED)
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
python3 reorganise_tech_docs.py
```

This processes only the Pod Drawings Post MOTC folder (12 EQP952 files) and shows what titles were extracted and what files were renamed.

Review the output at:
`/Users/seanbrock/work documents/3. Technical Docs - Hercules MK3/REORGANISATION_LOG.txt`

**Report the renamed files before proceeding.** Sean needs to confirm the title extraction looks correct.

### Step 2 — Full run (after test confirmed)
```bash
python3 reorganise_tech_docs.py --full
```

This copies and renames all files across the full folder structure. Takes several minutes.

---

## What the Script Does

1. **Creates** the full folder structure under `Technical Docs - Hercules MK3/`
2. **Copies** files from old locations to new locations (read-only on source)
3. **Renames** drawing-number-only PDFs by:
   - Detecting if filename is a pure drawing number (e.g. `EQP952-0203-DR-PD-55001.pdf`)
   - Opening the PDF with pdfminer and reading the title block
   - Renaming to `[Title] [Drawing Number].pdf`
   - If no text extractable: `[OCR NEEDED] [Drawing Number].pdf`
4. **Logs** everything to `REORGANISATION_LOG.txt`

## Safety Rules Built Into Script
- All copies use `shutil.copy2()` — source files never touched
- Duplicate detection — if destination exists, renames copy with `_DUPLICATE` suffix
- Test-first — default run is test only, full run requires `--full` flag

---

## Target Structure
```
Technical Docs - Hercules MK3/
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
  REORGANISATION_LOG.txt
```
