# COWORK TASK — Systematic Link Audit & Error Catalogue

## YOUR MISSION
Perform a complete audit of every drawing and manual link in the Hercules MK3
interactive manual. For each link: verify the file exists in manuals/, confirm
it opens correctly, and catalogue all errors. Then fix broken paths and add
missing links for the 60 unlinked files sitting in manuals/.

Produce a written report at the end: LINK_AUDIT_REPORT.md

---

## REPO
github.com/Seanbrock100/rov-chatbot
Working file: rov-manual/index.html
PDF folder:   rov-manual/manuals/ (123 PDFs, flat structure)

---

## CURRENT STATE (from pre-audit scan, 22 Apr 2026)

### Referenced in index.html
- 63 files referenced AND present in manuals/ ✅
- 15 files referenced but MISSING from manuals/ ❌

### In manuals/ but NOT referenced in index.html
- 60 files present in manuals/ but not linked anywhere

---

## PART 1 — AUDIT EXISTING LINKS

### Step 1A: Extract all file references
Run this Python script to get the complete picture:

```python
import os, re, json

manuals_dir = 'rov-manual/manuals'
html_path = 'rov-manual/index.html'

with open(html_path) as f:
    content = f.read()

local_files = set(f for f in os.listdir(manuals_dir) if f.lower().endswith('.pdf'))
file_refs = re.findall(r"file:\s*['\"]([^'\"]+\.pdf)['\"]", content, re.IGNORECASE)
file_refs += re.findall(r"openDoc\(['\"]([^'\"]+\.pdf)['\"]", content, re.IGNORECASE)
file_refs += re.findall(r"openViewerTab\(['\"]([^'\"]+\.pdf)['\"]", content, re.IGNORECASE)
file_refs += re.findall(r"manuals/([^'\">\s]+\.pdf)", content, re.IGNORECASE)

normalised = sorted(set(r.split('/')[-1] for r in file_refs))
missing = [f for f in normalised if f not in local_files]
present = [f for f in normalised if f in local_files]
unreferenced = sorted(local_files - set(normalised))

print(f"Referenced: {len(normalised)} | Present: {len(present)} | Missing: {len(missing)}")
print(f"Unreferenced in manuals/: {len(unreferenced)}")

print("\nMISSING FILES:")
for f in missing: print(f"  MISSING: {f}")

print("\nUNREFERENCED FILES:")
for f in unreferenced: print(f"  UNLINKED: {f}")
```

### Step 1B: The 15 missing files (referenced in HTML but not in manuals/)
These will show broken/empty viewer when clicked. FIX THEM:

| Referenced As | Likely Actual Filename | Action |
|---------------|------------------------|--------|
| `8228_Atlas7r-Manual.pdf` | `8228_Atlas7r Manual.pdf` | Fix path in DATA (space vs hyphen) |
| `Aleron-VP-Manual.pdf` | `Aleron VP Manual.pdf` | Fix path in DATA (space vs hyphen) |
| `HCV-0030-D-0691-90 sht 1-Layout1.pdf` | Not in manuals/ | Find on Google Drive or remove link |
| `Hercules-MK3-Lighting-JB.pdf` | `Hercules MK3 Lighting JB with Oceantools Lamps - User Manual OR-TE-03338.pdf` | Fix path |
| `Latch beam Valve Pack OCE-0396-D-0142-92.pdf` | Not in manuals/ | Find on Google Drive or remove |
| `OCE-0378-D-0146-90 SHT 1 Model (1).pdf` | Not in manuals/ | Find on Google Drive or remove |
| `PDU-0009-D-0016-90 (1 of 3).pdf` | Not in manuals/ | Find on Google Drive or remove |
| `PDU-0009-D-0016-90 (2 of 3).pdf` | Not in manuals/ | Find on Google Drive or remove |
| `ROV-0300-D-0115-00 Sht 1-2.pdf` | Not in manuals/ | Find on Google Drive or remove |
| `ROV-0300-D-0115-01.pdf` | Not in manuals/ | Find on Google Drive or remove |
| `ROV-0300-D-0300-00 parts list rev C1.pdf` | Not in manuals/ | Find on Google Drive or remove |
| `ROV-0300-D-0300-00 sht 1 rev C1.pdf` | Not in manuals/ | Find on Google Drive or remove |
| `ROV-0305-D-0111-01 SHT 1-Model.pdf` | Not in manuals/ | Find on Google Drive or remove |
| `TMA01030-Interface-Systems.pdf` | `TMA01030 - Interface systems manual.pdf` | Fix path (hyphen vs space+dash) |
| `TMA01031-Control-System.pdf` | `TMA01031 - Control system manual.pdf` | Fix path |

**Priority: Fix the easy ones first (path mismatches), then attempt Google Drive download for the rest.**

---

## PART 2 — ADD MISSING LINKS FOR UNLINKED FILES

60 files in manuals/ are not linked anywhere. Add them to the correct
component in the DATA object in index.html.

### Step 2A: Mapping — which component each file belongs to

**Electronics Pod / Control chassis:**
- `TMA01030 - Interface systems manual.pdf` → electronics_pod, MANUALS section
- `TMA01031 - Control system manual.pdf` → electronics_pod, MANUALS section
- `EQP952-0203-DR-PD-54001 - rc updates sketch.pdf` → electronics_pod (RC update sketches)
- `EQP952-0203-DR-PD-54001 - rc updates sketch p2.pdf` → electronics_pod
- `EQP952-0203-DR-PD-54001 - rc updates sketch page 3.pdf` → electronics_pod
- `EQP952-0203-DR-PD-54002 - rc updates sketch p1.pdf` → electronics_pod
- `EQP952-0203-DR-PD-54002 - rc updates sketch p2.pdf` → electronics_pod
- `EQP952-0203-DR-PD-54002 - rc updates sketch p3.pdf` → electronics_pod
- `ROV-0311-D-0203-00 SHT 1 rc changes sketch.pdf` → electronics_pod (superseded pen ring)
- `ROV-0311-D-0203-01 SHT 1 rc updates sketch.pdf` → electronics_pod
- `ROV-0311-D-0204-00 SHT 1 rc updates sketch.pdf` → electronics_pod
- `ROV-0311-D-0204-01 SHT 1 rc updates sketch.pdf` → electronics_pod
- `ROV-0311-D-0208-01.pdf` to `ROV-0311-D-0208-03.pdf` → electronics_pod (unregulated supply revisions)
- `ROV-0311-D-0210-00.pdf` to `ROV-0311-D-0210-04.pdf` → electronics_pod (band splitter revisions)
- `ROV-0311-D-0211-00.pdf` to `ROV-0311-D-0211-01.pdf` → electronics_pod
- `ROV-0311-D-0212-02.pdf` → electronics_pod (CWDM revision)

**Hydraulics / HPU:**
- `ROV-0300-D-0440-00 sht 1 rev C9 Hydraulic Diagram.pdf` → hpu, DRAWINGS
- `ROV-0300-D-0440-00 sht 2 rev C9 Hydraulic Diagram.pdf` → hpu, DRAWINGS
- `ROV-0300-D-0440-00 sht 3 rev C9 Hydraulic Diagram.pdf` → hpu, DRAWINGS
- `ROV-0311-D-0210-00.pdf` through `ROV-0311-D-0210-04.pdf` → hpu (valve pack supply)

**LARS / Launch & Recovery:**
- `TMA01071 - LARS Technical Manual.pdf` → lars_overview, MANUALS
- `ROV-0311-D-0620-90 SHT 1-Model.pdf` → lars_overview, DRAWINGS (already in manuals/)
- `ROV-0311-D-0620-90 sht 2-Model.pdf` → lars_overview, DRAWINGS

**H30 / TMS:**
- `H30 - GA Top Level & Schematics Manual - TMA01029.pdf` → tms_h30 or frame, MANUALS
- `HCV-0015-D-0200-90 (2 of 3).pdf` → electronics_pod (additional pod sheets)
- `HCV-0015-D-0200-90 (3 of 3).pdf` → electronics_pod
- `HCV-0015-D-0201-00 (2 of 2).pdf` → electronics_pod
- `HCV-0015-D-0201-90 (1 of 3).pdf` → electronics_pod
- `HCV-0015-D-0201-90 (3 of 3).pdf` → electronics_pod
- `HCV-0015-D-0202-00 (2 of 2).pdf` → electronics_pod
- `HCV-0015-D-0300-00 (1 of 2).pdf` → electronics_pod
- `HCV-0015-D-0300-00 (2 of 2).pdf` → electronics_pod
- `HCV-0015-D-0500-00 (1 of 2).pdf` → electronics_pod
- `HCV-0015-D-0500-00 (2 of 2).pdf` → electronics_pod
- `HCV-0015-D-0800-90 (2 of 5).pdf` → control_console
- `HCV-0015-D-0800-90 (4 of 5).pdf` → control_console

**ROV General / Frame:**
- `Hercules MK3 Lighting JB with Oceantools Lamps - User Manual OR-TE-03338.pdf` → rov_lights, MANUALS
- `Hercules Mk3.pdf` → frame (general ROV overview)
- `Hercules Tool Tray Skid BOM.pdf` → tooling
- `Hercules Tool Tray Skid hammer head.pdf` → tooling
- `NIC-OPS-010 - Seven Oceanic Databook.pdf` → reference (add to a Reference section)
- `Seven Oceanic ROV HAndbook.pdf` → reference
- `ROV-0148-671-04.pdf` → frame
- `ROV-0226-630-90.pdf` → tcu (thruster cable drawing)
- `ROV-0300-D-0100-01.pdf` → frame
- `ROV-0300-D-0802-90.pdf` → frame
- `ROV-0305-D-0660-90.pdf` → frame
- `SSA-0277-D-0004-00 sht 1 - Amended H15.pdf` → frame (buoyancy)
- `SSA-0277-D-0004-00 sht 1.pdf` → frame (buoyancy)
- `SSA-0277-D-0004-01 SHT 2 commented For order.pdf` → frame (buoyancy)
- `SSA-0277-D-0004-01 sht 1.pdf` → frame (buoyancy)
- `8228_Atlas7r Manual.pdf` → atlas_manip, MANUALS
- `Aleron VP Manual.pdf` → valve_packs, MANUALS
- `tcu.pdf` → tcu, DRAWINGS (verify what this is first)

---

## PART 3 — HOW TO FIND THE DATA OBJECT IN index.html

The DATA object maps component keys to their drawing/manual lists.
Find it at around line 700 in index.html. Structure:

```javascript
const DATA = {
  tcu: {
    drawings: [
      { num: 'ROV-0226-420-00', title: 'TCU General Arrangement', file: 'manuals/ROV-0226-420-00 SHEET 1.pdf' },
      ...
    ],
    manuals: [
      { title: 'TCU Manual TMA01031', file: 'manuals/TMA01031 - Control system manual.pdf' },
      ...
    ]
  },
  hpu: { drawings: [...], manuals: [...] },
  ...
}
```

**To add a missing link:** Find the correct component key and add an entry
to its drawings[] or manuals[] array with the exact filename from manuals/.

**To fix a broken path:** Find the old filename string and replace it with
the correct filename (e.g. change `8228_Atlas7r-Manual.pdf` to
`8228_Atlas7r Manual.pdf`).

---

## PART 4 — VERIFICATION STEPS

After making all fixes, run this verification:

```python
import os, re

manuals_dir = 'rov-manual/manuals'
html_path = 'rov-manual/index.html'

with open(html_path) as f:
    content = f.read()

local_files = set(f for f in os.listdir(manuals_dir) if f.lower().endswith('.pdf'))
file_refs = re.findall(r"file:\s*['\"]([^'\"]+\.pdf)['\"]", content, re.IGNORECASE)
file_refs += re.findall(r"openDoc\(['\"]([^'\"]+\.pdf)['\"]", content, re.IGNORECASE)
file_refs += re.findall(r"manuals/([^'\">\s]+\.pdf)", content, re.IGNORECASE)
normalised = sorted(set(r.split('/')[-1] for r in file_refs))

missing = [f for f in normalised if f not in local_files]
still_unreferenced = sorted(local_files - set(normalised))

print(f"Missing (broken links): {len(missing)}")
for f in missing: print(f"  ❌ {f}")
print(f"\nStill unreferenced: {len(still_unreferenced)}")
for f in still_unreferenced: print(f"  ⚠️  {f}")
```

**Target: missing = 0**

---

## PART 5 — JS PARSE CHECK (run after every edit)

```bash
python3 -c "
html = open('rov-manual/index.html').read()
script = html[html.rfind('<script>')+8:html.rfind('</script>')]
open('/tmp/vc.js','w').write('// test\n'+script)
" && node --check /tmp/vc.js && echo "PARSE OK"
```

---

## PART 6 — PRODUCE THE AUDIT REPORT

Create `LINK_AUDIT_REPORT.md` in the repo root with:

1. **Summary table** — total links, broken, fixed, still broken, unlinked files added
2. **Fixed links** — list of path corrections made
3. **Added links** — list of new entries added to DATA
4. **Could not find** — files referenced but not in manuals/ AND not on Google Drive
5. **Skipped / unclassified** — files in manuals/ where correct component is unclear

---

## COMMIT WHEN DONE

```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
git add rov-manual/index.html LINK_AUDIT_REPORT.md
git commit -m "Link audit: fix broken paths, add missing drawing/manual links"
git push origin main
```

---

## DO NOT
- Do not delete any files from manuals/
- Do not modify any CSS, layout, or non-DATA JavaScript
- Do not rename any PDF files
- Do not re-embed any manuals into Supabase (separate task)
- Run JS parse check after every edit — do not commit broken JS
