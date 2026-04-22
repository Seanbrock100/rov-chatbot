# LINK_AUDIT_REPORT — Hercules MK3 Interactive Manual
**Audited:** 22 Apr 2026 | **Auditor:** Cowork (Claude)
**Working file:** `rov-manual/index.html`
**PDF folder:** `rov-manual/manuals/`

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Total PDFs in manuals/ | 123 | 134 |
| Referenced in index.html | 78 | 134 |
| Broken links (file missing) | 15 | **0** ✅ |
| Unreferenced PDFs | 60 | **0** ✅ |
| PDFs copied from Google Drive | 0 | 11 |

---

## 1. Fixed Links — Path Corrections (5 wrong filenames)

| Old path in HTML | Correct filename | Component |
|------------------|-----------------|-----------|
| `8228_Atlas7r-Manual.pdf` | `8228_Atlas7r Manual.pdf` | atlas_manip manuals |
| `Aleron-VP-Manual.pdf` | `Aleron VP Manual.pdf` | atlas_manip, valve_packs manuals |
| `Hercules-MK3-Lighting-JB.pdf` | `Hercules MK3 Lighting JB with Oceantools Lamps - User Manual OR-TE-03338.pdf` | rov_lights manuals |
| `TMA01030-Interface-Systems.pdf` | `TMA01030 - Interface systems manual.pdf` | electronics_pod, valve_packs, rov_term_can, tcu manuals |
| `TMA01031-Control-System.pdf` | `TMA01031 - Control system manual.pdf` | electronics_pod, tcu, control_console manuals |

---

## 2. Fixed Links — Wrong Subdirectory Paths (7 entries)

These entries used non-existent `manuals/drawings/...` subdirectory paths. All corrected to flat `manuals/` structure.

| Old path | Corrected path |
|----------|---------------|
| `manuals/drawings/EQP952-0203-DR-PD-55006.pdf` | `manuals/EQP952-0203-DR-PD-55006.pdf` |
| `manuals/drawings/EQP952-0203-DR-PD-55007.pdf` | `manuals/EQP952-0203-DR-PD-55007.pdf` |
| `manuals/drawings/EQP952-0203-DR-PD-55018.pdf` | `manuals/EQP952-0203-DR-PD-55018.pdf` |
| `manuals/drawings/EQP952-0203-DR-PD-55019.pdf` | `manuals/EQP952-0203-DR-PD-55019.pdf` |
| `manuals/drawings/Lars/Latch beam Valve Pack OCE-0396-D-0142-92.pdf` | `manuals/Latch beam Valve Pack OCE-0396-D-0142-92.pdf` |
| `manuals/drawings/Lars/OCE-0378-D-0146-90 SHT 1 Model (1).pdf` | `manuals/OCE-0378-D-0146-90 SHT 1 Model (1).pdf` |
| `manuals/drawings/Control Room/Console wiring and Panels/HCV-0030-D-0691-90 sht 1-Layout1.pdf` | `manuals/HCV-0030-D-0691-90 sht 1-Layout1.pdf` |

Also corrected drawing number typo: `OCE-0396-D-0142-90` → `OCE-0396-D-0142-92` (matching actual filename).

---

## 3. PDFs Copied from Google Drive to manuals/

These 11 files were referenced in HTML but not in manuals/. Located on Google Drive and copied to the repo.

| Filename | Source on Drive |
|----------|----------------|
| `HCV-0030-D-0691-90 sht 1-Layout1.pdf` | `Control Room/Console wiring and Panels/` |
| `Latch beam Valve Pack OCE-0396-D-0142-92.pdf` | `Lars/Latch Beam/` |
| `OCE-0378-D-0146-90 SHT 1 Model (1).pdf` | `Lars/Latch Beam/` |
| `PDU-0009-D-0016-90 (1 of 3).pdf` | `PDU-009-D-0016-90/` |
| `PDU-0009-D-0016-90 (2 of 3).pdf` | `PDU-009-D-0016-90/` |
| `PDU-0009-D-0016-90 (3 of 3).pdf` | `PDU-009-D-0016-90/` (also added Sht 3 entry to pdu DATA) |
| `ROV-0300-D-0115-00 Sht 1-2.pdf` | `Herc Drawings/.../Bouyancy/` |
| `ROV-0300-D-0115-01.pdf` | `Herc Drawings/.../Bouyancy/` |
| `ROV-0300-D-0300-00 parts list rev C1.pdf` | `Herc Drawings/.../Term can/` |
| `ROV-0300-D-0300-00 sht 1 rev C1.pdf` | `Herc Drawings/.../Term can/` |
| `ROV-0305-D-0111-01 SHT 1-Model.pdf` | `Herc Drawings/.../ROV-0230/` |

---

## 4. Added Links — New DATA Entries (previously unlinked files)

### electronics_pod drawings (34 new entries)
- EQP952-0203-DR-PD-54001 rc updates sketch p1, p2, p3 (pod change sketches)
- EQP952-0203-DR-PD-54002 rc updates sketch p1, p2, p3
- ROV-0311-D-0203-00/01 (superseded control pen ring sketches)
- ROV-0311-D-0204-00/01 (superseded payload pen ring sketches)
- ROV-0311-D-0208-01/02/03 (valve pack unregulated supply revisions)
- ROV-0311-D-0210-00/01/02/03/04 (band splitter assembly revisions)
- ROV-0311-D-0211-00/01 (pod drawings)
- ROV-0311-D-0212-02 (CWDM assembly rev 02)
- HCV-0015-D-0200-90 Sht 2+3, D-0201-00 Sht 2, D-0201-90 Sht 1+3, D-0202-00 Sht 2, D-0300-00 Sht 1+2, D-0500-00 Sht 1+2

### tcu drawings (2 new entries)
- `ROV-0226-630-90.pdf` — Thruster Cable Drawing
- `tcu.pdf` — TCU Drawing

### hpu drawings (3 new entries)
- `ROV-0300-D-0440-00 sht 1/2/3 rev C9 Hydraulic Diagram.pdf`

### frame drawings (10 new entries)
- SSA-0277-D-0004-01 Sht 1, commented For Order
- SSA-0277-D-0004-00 Sht 1, Amended H15
- ROV-0148-671-04, ROV-0300-D-0100-01, ROV-0300-D-0802-90, ROV-0305-D-0660-90
- Hercules Tool Tray Skid BOM, Hercules Tool Tray Skid Hammer Head

### frame manuals (4 new entries)
- `H30 - GA Top Level & Schematics Manual - TMA01029.pdf`
- `Hercules Mk3.pdf`
- `NIC-OPS-010 - Seven Oceanic Databook.pdf`
- `Seven Oceanic ROV HAndbook.pdf`

### tms manuals (1 new entry)
- `H30 - GA Top Level & Schematics Manual - TMA01029.pdf`

### lars drawings (2 new entries)
- `ROV-0311-D-0620-90 SHT 1-Model.pdf`
- `ROV-0311-D-0620-90 sht 2-Model.pdf`

### lars manuals (1 new entry)
- `TMA01071 - LARS Technical Manual.pdf`

### control_room drawings (2 new entries)
- `HCV-0015-D-0800-90 (2 of 5).pdf` (Sht 2)
- `HCV-0015-D-0800-90 (4 of 5).pdf` (Sht 4)

### pdu drawings (1 new entry)
- `PDU-0009-D-0016-90 (3 of 3).pdf` (Sht 3 — also newly copied from Drive)

---

## 5. Could Not Find Anywhere
None. All previously referenced files were either already in manuals/ (path error only) or found on Google Drive and copied.

---

## 6. Final Verification

```
Referenced: 134 | Missing (broken): 0
Still unreferenced in manuals/: 0
```

JS parse check: **PARSE OK**

**Result: Zero broken links. All 134 PDFs in manuals/ are referenced in the DATA object.**
