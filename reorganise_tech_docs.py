#!/usr/bin/env python3
"""
reorganise_tech_docs.py
=======================
Cowork task: Create a new parallel folder structure at
  /Users/seanbrock/work documents/3. Technical Docs - Hercules MK3/

Copies (never moves) relevant files from the original Technical Docs folder,
renames drawing-number-only PDFs by extracting the English title from the
drawing title block, and logs everything.

Run:
  python3 reorganise_tech_docs.py

Log:
  /Users/seanbrock/work documents/3. Technical Docs - Hercules MK3/REORGANISATION_LOG.txt

SAFETY: The original folder is opened READ-ONLY. No files are moved or deleted.
"""

import os, re, shutil, datetime
from pathlib import Path
from pdfminer.high_level import extract_text

# ── PATHS ──────────────────────────────────────────────────────────────────────
SRC  = Path("/Users/seanbrock/work documents/3. Technical Docs")
DEST = Path("/Users/seanbrock/work documents/3. Technical Docs - Hercules MK3")
LOG  = DEST / "REORGANISATION_LOG.txt"

# ── TARGET FOLDER STRUCTURE ────────────────────────────────────────────────────
FOLDERS = [
    "Longlines",
    "Control Room",
    "PDU",
    "ROV/Electrical/Electronics Pod",
    "ROV/Electrical/Term Can",
    "ROV/Electrical/Lights",
    "ROV/Hydraulic/HPU - Pump and Tank",
    "ROV/Hydraulic/Valve Packs",
    "ROV/Hydraulic/TCU - Thruster Control",
    "ROV/Hydraulic/Pan and Tilt",
    "ROV/Hydraulic/Thrusters - Curvetech",
    "ROV/Mechanical/Frame and Structure",
    "TMS/H15",
    "TMS/H30",
    "LARS/LCC Winch",
    "LARS/Latch Beam",
    "LARS/Latch Beam Winch",
    "LARS/Cursor",
    "LARS/Sliding Weight",
    "LARS/LARS HPU",
    "LARS/Moonpool Doors",
    "LARS/Service Winch",
    "LARS/Service Winch Slip Ring",
    "LARS/Tether",
    "Manipulators/T4 - Schilling",
    "Manipulators/Atlas - Schilling",
    "Reference/Cables",
    "Reference/All Drawings",
]

# ── DRAWING PREFIX → DESTINATION FOLDER ───────────────────────────────────────
# Each tuple: (regex pattern, destination folder relative to DEST)
# Checked in order — first match wins
DRAWING_RULES = [
    # Electronics Pod (EQP952-0203-DR-PD-55xxx + related)
    (r'^EQP952-0203-DR-PD-55',        "ROV/Electrical/Electronics Pod"),
    (r'^EQP952-0203-DR-PD-54',        "ROV/Electrical/Electronics Pod"),
    # Fibre optics (CWDM, band splitter, optical transceiver)
    (r'^ROV-0311-D-021',              "ROV/Electrical/Electronics Pod"),
    (r'^ROV-0311-D-0206',             "ROV/Electrical/Electronics Pod"),
    (r'^ROV-0311-D-0208',             "ROV/Hydraulic/Valve Packs"),
    (r'^ROV-0311-D-0213',             "ROV/Electrical/Electronics Pod"),
    # Term Can
    (r'^ROV-0300-D-0300',             "ROV/Electrical/Term Can"),
    (r'^ROV-0311-D-0301',             "ROV/Electrical/Term Can"),
    (r'^HCV-0009',                    "ROV/Electrical/Term Can"),
    (r'^CAB-1043',                    "ROV/Electrical/Term Can"),
    (r'^CAB-1044',                    "ROV/Electrical/Term Can"),
    (r'^EQP950-0200',                 "ROV/Electrical/Term Can"),
    # Lights
    (r'^ROV-0311-D-0680',             "ROV/Electrical/Lights"),
    (r'^OR-TE-03338',                 "ROV/Electrical/Lights"),
    (r'^CAB-1060',                    "ROV/Electrical/Lights"),
    # HPU
    (r'^ROV-0249',                    "ROV/Hydraulic/HPU - Pump and Tank"),
    (r'^ROV-0300-D-0440',             "ROV/Hydraulic/HPU - Pump and Tank"),
    (r'^ROV-0211-45',                 "ROV/Hydraulic/HPU - Pump and Tank"),
    (r'^ROV-0211-451',                "ROV/Hydraulic/HPU - Pump and Tank"),
    (r'^ROV-0226-455',                "ROV/Hydraulic/HPU - Pump and Tank"),
    (r'^ROV-0226-415',                "ROV/Hydraulic/HPU - Pump and Tank"),
    (r'^EQP952-0200',                 "ROV/Hydraulic/HPU - Pump and Tank"),
    # Valve Packs
    (r'^ROV-0305-D-0450',             "ROV/Hydraulic/Valve Packs"),
    (r'^ROV-0305-D-0470',             "ROV/Hydraulic/Valve Packs"),
    (r'^ROV-0311-D-0208',             "ROV/Hydraulic/Valve Packs"),
    # TCU
    (r'^ROV-0300-D-0420',             "ROV/Hydraulic/TCU - Thruster Control"),
    (r'^ROV-0148-671',                "ROV/Hydraulic/TCU - Thruster Control"),
    # Pan & Tilt
    (r'^ROV-0305-D-0630',             "ROV/Hydraulic/Pan and Tilt"),
    (r'^ROV-0305-D-0660',             "ROV/Hydraulic/Pan and Tilt"),
    # Thrusters
    (r'^ROV-0226-630',                "ROV/Hydraulic/Thrusters - Curvetech"),
    (r'^ROV-0305-D-04(?!50|70)',      "ROV/Hydraulic/Thrusters - Curvetech"),
    # Frame & Structure
    (r'^ROV-0300-D-01',               "ROV/Mechanical/Frame and Structure"),
    (r'^ROV-0305-D-01',               "ROV/Mechanical/Frame and Structure"),
    (r'^ROV-0305-D-012',              "ROV/Mechanical/Frame and Structure"),
    (r'^ROV-0226-115',                "ROV/Mechanical/Frame and Structure"),
    (r'^ROV-0148-707',                "ROV/Mechanical/Frame and Structure"),
    (r'^ROV-0148-030',                "ROV/Mechanical/Frame and Structure"),
    (r'^ROV-0230',                    "ROV/Mechanical/Frame and Structure"),
    (r'^SSA-0277',                    "ROV/Mechanical/Frame and Structure"),
    (r'^SSA-0173',                    "ROV/Mechanical/Frame and Structure"),
    (r'^SSA-0381',                    "ROV/Mechanical/Frame and Structure"),
    (r'^EQP959',                      "ROV/Mechanical/Frame and Structure"),
    # TMS H15
    (r'^ROV-0311-D-0500',             "TMS/H15"),
    (r'^ROV-0311-D-0800-50',          "TMS/H15"),
    (r'^OME-0501',                    "TMS/H15"),
    (r'^OME-0032',                    "TMS/H15"),
    (r'^EQP958',                      "TMS/H15"),
    # TMS H30 (no specific drawing prefix — handled by folder mapping)
    # LARS LCC
    (r'^OCE-0400-DR-055',             "LARS/LCC Winch"),
    (r'^OCE-0400-DR-056',             "LARS/LCC Winch"),
    (r'^OCE-0400-DR-100',             "LARS/LCC Winch"),
    (r'^CAB-0849',                    "LARS/LCC Winch"),
    (r'^V313',                        "LARS/LCC Winch"),
    (r'^OCE-0378-D-0145',             "LARS/LCC Winch"),
    (r'^OCE-0378-D-0122',             "LARS/LCC Winch"),
    (r'^AB-T-PR',                     "LARS/LCC Winch"),
    (r'^OCE-0205-265',                "LARS/LCC Winch"),
    # LARS Latch Beam
    (r'^OCE-0400-DR-014',             "LARS/Latch Beam"),
    (r'^OCE-0400-DR-003',             "LARS/Latch Beam"),
    (r'^OCE-0400-DR-005',             "LARS/Latch Beam"),
    (r'^OCE-0400-DR-011',             "LARS/Latch Beam"),
    (r'^OCE-0396-D-014',              "LARS/Latch Beam"),
    (r'^OCE-0396-D-012',              "LARS/Latch Beam"),
    (r'^OCE-0378-D-0143',             "LARS/Latch Beam"),
    (r'^OCE-0378-D-0146',             "LARS/Latch Beam"),
    (r'^OCE-0273-D-0241',             "LARS/Latch Beam"),
    (r'^OCE-0186-103',                "LARS/Latch Beam"),
    (r'^ROV-0186-103',                "LARS/Latch Beam"),
    (r'^CAB-0846',                    "LARS/Latch Beam"),
    # LARS Latch Beam Winch
    (r'^OCE-0400-DR-030[0-3]',        "LARS/Latch Beam Winch"),
    # LARS Cursor
    (r'^OCE-0400-DR-013',             "LARS/Cursor"),
    (r'^OCE-0400-DR-0131',            "LARS/Cursor"),
    (r'^OCE-0400-DR-0133',            "LARS/Cursor"),
    (r'^OCE-0400-DR-0135',            "LARS/Cursor"),
    (r'^OCE-0205-246',                "LARS/Cursor"),
    (r'^OCE-0273-D-0244',             "LARS/Cursor"),
    (r'^OCE-0273-D-0402',             "LARS/Cursor"),
    (r'^OME-0501-D-0042',             "LARS/Cursor"),
    # LARS HPU
    (r'^OCE-0400-DR-0306',            "LARS/LARS HPU"),
    (r'^OCE-0400-DR-0304',            "LARS/Service Winch"),
    # LARS Moonpool Doors
    (r'^OCE-0400-DR-0124',            "LARS/Moonpool Doors"),
    # LARS Service Winch
    (r'^OCE-0400-DR-07',              "LARS/Service Winch"),
    (r'^OCE-0400-DR-08',              "LARS/Service Winch"),
    # T4 Manipulator
    (r'^011-8239',                    "Manipulators/T4 - Schilling"),
    (r'^101-',                        "Manipulators/T4 - Schilling"),
    (r'^9161',                        "Manipulators/T4 - Schilling"),
    (r'^9170',                        "Manipulators/T4 - Schilling"),
    # Atlas Manipulator
    (r'^SP-011',                      "Manipulators/Atlas - Schilling"),
    (r'^CAB-0988',                    "Manipulators/Atlas - Schilling"),
    (r'^CAB-1040',                    "Manipulators/Atlas - Schilling"),
    (r'^CAB-1041',                    "Manipulators/Atlas - Schilling"),
    (r'^ROV-0226-004',                "Manipulators/Atlas - Schilling"),
    (r'^ROV-0226-005',                "Manipulators/Atlas - Schilling"),
    # Longlines
    (r'^EQP952-021',                  "Longlines"),
    (r'^EQP952-023',                  "Longlines"),
    # Control Room
    (r'^HCV-001',                     "Control Room"),
    (r'^HCV-003',                     "Control Room"),
    (r'^PDU-0009',                    "Control Room"),
    (r'^PCB-0202',                    "Control Room"),
    (r'^PCB-0203',                    "Control Room"),
    # PDU
    (r'^PDU-1012',                    "PDU"),
    # Cables
    (r'^CAB-',                        "Reference/Cables"),
    (r'^ROV-0226-725',                "Reference/Cables"),
]

# ── FOLDER → DESTINATION mapping (for whole-folder copies) ────────────────────
FOLDER_MAP = [
    # (source subfolder relative to SRC, dest folder relative to DEST)
    ("ROV/Herc Mk 3 manuals/Pod Drawings Post MOTC",  "ROV/Electrical/Electronics Pod"),
    ("ROV/MK3 Termination JB Drawings",               "ROV/Electrical/Term Can"),
    ("ROV/Herc 15-30 MK III xx/HPU Drawings",         "ROV/Hydraulic/HPU - Pump and Tank"),
    ("ROV/Herc 15-30 MK III xx/Herc 15-30 MK III Manuals", "ROV/Hydraulic/TCU - Thruster Control"),
    ("ROV/Herc Mk 3 manuals/Hydraulic",               "ROV/Hydraulic/HPU - Pump and Tank"),
    ("ROV/Thrusters/Curvetech HTE380",                 "ROV/Hydraulic/Thrusters - Curvetech"),
    ("ROV/Thrusters/TCU",                              "ROV/Hydraulic/TCU - Thruster Control"),
    ("ROV/Thrusters/Frame repair - Mod",               "ROV/Hydraulic/Thrusters - Curvetech"),
    ("ROV/Tool Tray",                                  "ROV/Mechanical/Frame and Structure"),
    ("ROV/Vehicle Buoyancy",                           "ROV/Mechanical/Frame and Structure"),
    ("ROV/Anode",                                      "ROV/Mechanical/Frame and Structure"),
    ("TMS/H15",                                        "TMS/H15"),
    ("TMS/H30",                                        "TMS/H30"),
    ("TMS/TMS Topside Upgrade",                        "TMS/H15"),
    ("LARS/Latch Beam",                                "LARS/Latch Beam"),
    ("LARS/Latch beam winch drawings",                 "LARS/Latch Beam Winch"),
    ("LARS/LB Winch Brakes",                           "LARS/Latch Beam Winch"),
    ("LARS/Cursor",                                    "LARS/Cursor"),
    ("LARS/Limits",                                    "LARS/LCC Winch"),
    ("LARS/5yr Load test drawings",                    "LARS/LCC Winch"),
    ("LARS/Flag Sheave",                               "LARS/Latch Beam Winch"),
    ("LARS/Latch beam wiring",                         "LARS/Latch Beam"),
    ("LARS/Brake Calliper Shim Drawings",              "LARS/Latch Beam"),
    ("LARS/Sheave line out encoder",                   "LARS/Service Winch"),
    ("Manips/Titan",                                   "Manipulators/T4 - Schilling"),
    ("Manips/Atlas Manips",                            "Manipulators/Atlas - Schilling"),
    ("Longline Drawings",                              "Longlines"),
    ("Control Room",                                   "Control Room"),
    ("PDU",                                            "PDU"),
    ("Lights",                                         "ROV/Electrical/Lights"),
    ("Fibre Optics",                                   "ROV/Electrical/Electronics Pod"),
    ("Cables",                                         "Reference/Cables"),
    ("Sliprings",                                      "LARS/Service Winch Slip Ring"),
    ("Tether",                                         "LARS/Tether"),
    ("Skidding System",                                "LARS/Sliding Weight"),
    ("Moon pool Doors",                                "LARS/Moonpool Doors"),
]

# ── DRAWING DETECTION ──────────────────────────────────────────────────────────
DRG_PATTERN = re.compile(
    r'^(EQP|ROV-|OCE-|HCV-|PDU-|SSA-|CAB-|OME-|TMA|011-|101-|SP-)',
    re.IGNORECASE
)
SKIP_WORDS = {'SUBSEA', 'SHEET', 'REV', 'DATE', 'SCALE', 'DRG', 'CHECKED', 'DRAWN',
              'APPROVED', 'COPYRIGHT', 'PROPRIETARY', 'CONFIDENTIAL', 'HERCULES',
              'SEVEN', 'OCEANIC', 'SUBSEA7', 'REMOTE', 'TECHNOLOGY', 'GROUP'}

def is_drawing_number_only(filename):
    """Returns True if filename is just a drawing number with no descriptive words."""
    name = os.path.splitext(filename)[0]
    # Strip sheet suffixes
    name = re.sub(r'\s*(SHT|sht|Sheet|Sht)[\s\d\-\.]+.*$', '', name).strip()
    name = re.sub(r'\s*\(\d+\s*(?:of|OF)\s*\d+\).*$', '', name).strip()
    name = re.sub(r'\s*SHT\s*\d.*$', '', name, flags=re.IGNORECASE).strip()
    # Check it starts with a drawing prefix and has no descriptive words
    if not DRG_PATTERN.match(name):
        return False
    # Split remaining parts after first drawing-number segment
    parts = name.split()
    # If only 1-2 tokens (drawing number + maybe revision), it's drawing-only
    return len(parts) <= 2

def extract_title_from_pdf(path):
    """Extract English title from PDF title block. Returns None if not found."""
    try:
        text = extract_text(str(path), page_numbers=[0, 1])
        if not text or len(text.strip()) < 20:
            return None
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 4]

        # 1. Look for explicit TITLE: field
        for i, line in enumerate(lines[:60]):
            if re.match(r'^TITLE\s*:', line, re.IGNORECASE):
                title = re.sub(r'^TITLE\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                if title and len(title) > 3:
                    return clean_title(title)
            if line.upper() == 'TITLE' and i + 1 < len(lines):
                candidate = lines[i + 1]
                if not DRG_PATTERN.match(candidate) and len(candidate) > 3:
                    return clean_title(candidate)

        # 2. Look for Subsea 7 / RTG title block pattern:
        # Often: "Procedure Title:" or the title is near "DESCRIPTION" label
        for i, line in enumerate(lines[:80]):
            if 'DESCRIPTION' in line.upper() and i + 1 < len(lines):
                candidate = lines[i + 1]
                if not DRG_PATTERN.match(candidate) and len(candidate) > 5:
                    return clean_title(candidate)

        # 3. Heuristic: find a descriptive ALL-CAPS or Title Case line in first 40 lines
        for line in lines[:40]:
            if len(line) < 5 or len(line) > 100:
                continue
            if DRG_PATTERN.match(line):
                continue
            # Skip lines that are clearly not titles
            if any(skip in line.upper() for skip in SKIP_WORDS):
                continue
            if re.match(r'^[\d\s\-\.\/]+$', line):
                continue
            # ALL CAPS descriptive line
            if re.match(r'^[A-Z][A-Z\s\/\(\)\-\&]+$', line) and len(line) > 5:
                return clean_title(line)
            # Title Case descriptive line (multiple words)
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', line):
                return clean_title(line)

        return None
    except Exception as e:
        return None

def clean_title(title):
    """Clean extracted title for use in filename."""
    # Remove characters invalid in filenames
    title = re.sub(r'[\\/:*?"<>|]', '', title)
    # Collapse whitespace
    title = ' '.join(title.split())
    # Truncate to sensible length
    if len(title) > 60:
        title = title[:60].rsplit(' ', 1)[0]
    return title.strip()

def get_dest_for_file(filename):
    """Match filename against drawing rules. Returns dest folder or None."""
    for pattern, dest in DRAWING_RULES:
        if re.match(pattern, filename, re.IGNORECASE):
            return dest
    return None

def safe_dest_path(dest_folder, filename, log_lines):
    """Return a destination path that doesn't overwrite existing files."""
    dest = DEST / dest_folder / filename
    if not dest.exists():
        return dest
    # Add _DUPLICATE suffix
    stem = dest.stem
    suffix = dest.suffix
    i = 1
    while True:
        new_dest = dest.with_name(f"{stem}_DUPLICATE{i}{suffix}")
        if not new_dest.exists():
            log_lines.append(f"  DUPLICATE: {filename} → {new_dest.name}")
            return new_dest
        i += 1

def copy_file(src_path, dest_folder, log_lines, rename=True):
    """
    Copy a single file to dest_folder, optionally renaming drawing-number-only files.
    Returns the final destination path.
    """
    filename = src_path.name
    final_name = filename

    if rename and is_drawing_number_only(filename):
        title = extract_title_from_pdf(src_path)
        if title:
            final_name = f"{title} {filename}"
            log_lines.append(f"  RENAMED: {filename} → {final_name}")
            log_lines.append(f"    (title extracted from PDF)")
        else:
            final_name = f"[OCR NEEDED] {filename}"
            log_lines.append(f"  OCR NEEDED: {filename}")

    dest_path = safe_dest_path(dest_folder, final_name, log_lines)
    shutil.copy2(str(src_path), str(dest_path))
    log_lines.append(f"  COPIED: {src_path} → {dest_path}")
    return dest_path

def copy_folder(src_folder_rel, dest_folder_rel, log_lines, recursive=True):
    """Copy all PDFs from a source subfolder to a destination folder."""
    src_folder = SRC / src_folder_rel
    if not src_folder.exists():
        log_lines.append(f"  SKIP (not found): {src_folder_rel}")
        return

    pattern = "**/*.pdf" if recursive else "*.pdf"
    files = list(src_folder.glob(pattern)) + list(src_folder.glob(pattern.replace('.pdf', '.PDF')))

    for f in sorted(files):
        if f.is_file():
            copy_file(f, dest_folder_rel, log_lines)

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main(test_only=False):
    log_lines = [
        "=== REORGANISATION LOG ===",
        f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source: {SRC}",
        f"Destination: {DEST}",
        f"Mode: {'TEST (Pod Drawings only)' if test_only else 'FULL RUN'}",
        "",
    ]

    # Step 1: Create folder structure
    log_lines.append("=== STEP 1: CREATE FOLDER STRUCTURE ===")
    for folder in FOLDERS:
        path = DEST / folder
        path.mkdir(parents=True, exist_ok=True)
        log_lines.append(f"  CREATED: {path}")
    log_lines.append("")

    if test_only:
        # ── TEST RUN: Only Pod Drawings Post MOTC ─────────────────────────────
        log_lines.append("=== TEST RUN: ROV/Herc Mk 3 manuals/Pod Drawings Post MOTC ===")
        test_src = SRC / "ROV/Herc Mk 3 manuals/Pod Drawings Post MOTC"
        test_dest = "ROV/Electrical/Electronics Pod"
        files = sorted(list(test_src.glob("*.pdf")) + list(test_src.glob("*.PDF")))
        print(f"\nTEST: Processing {len(files)} files from Pod Drawings Post MOTC...")
        for f in files:
            copy_file(f, test_dest, log_lines)
        log_lines.append("")
        log_lines.append("=== TEST COMPLETE — Review renamed files above then run with test_only=False ===")

    else:
        # ── FULL RUN ──────────────────────────────────────────────────────────
        log_lines.append("=== STEP 2: COPY FILES FROM FOLDER MAP ===")
        for src_rel, dest_rel in FOLDER_MAP:
            log_lines.append(f"\n  Folder: {src_rel} → {dest_rel}")
            copy_folder(src_rel, dest_rel, log_lines)

        # Step 3: Scan ROV root and top-level files by drawing number
        log_lines.append("\n=== STEP 3: SCAN FOR DRAWING-NUMBER FILES NOT CAUGHT BY FOLDER MAP ===")
        scan_folders = [
            "ROV",
            "ROV/Herc 15-30 MK III xx",
            "ROV/Herc 15-30 MK III xx/Herc15-30-MK III Drawings",
            "LARS",
            "Manips",
            "Longline Drawings",
            "Fibre Optics",
            "Cables",
            "PDU",
            "Control Room",
        ]
        for scan_rel in scan_folders:
            scan_path = SRC / scan_rel
            if not scan_path.exists():
                continue
            for f in sorted(scan_path.glob("*.pdf")) + sorted(scan_path.glob("*.PDF")):
                if not f.is_file():
                    continue
                dest_folder = get_dest_for_file(f.name)
                if dest_folder:
                    # Check it hasn't already been copied
                    already = list((DEST / dest_folder).glob(f"*{f.stem.split()[0]}*"))
                    if not already:
                        log_lines.append(f"\n  File: {f.name}")
                        copy_file(f, dest_folder, log_lines)

        log_lines.append("\n=== FULL RUN COMPLETE ===")

    # Write log
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text('\n'.join(log_lines), encoding='utf-8')
    print(f"\nLog written to: {LOG}")
    print(f"Total log lines: {len(log_lines)}")

    # Print summary to console
    copies  = sum(1 for l in log_lines if l.strip().startswith('COPIED:'))
    renames = sum(1 for l in log_lines if l.strip().startswith('RENAMED:'))
    ocr     = sum(1 for l in log_lines if l.strip().startswith('OCR NEEDED:'))
    dups    = sum(1 for l in log_lines if l.strip().startswith('DUPLICATE:'))
    print(f"\nSummary:")
    print(f"  Files copied:    {copies}")
    print(f"  Files renamed:   {renames}")
    print(f"  OCR needed:      {ocr}")
    print(f"  Duplicates:      {dups}")

if __name__ == '__main__':
    import sys
    # Default: test run only
    # Pass --full to run the full reorganisation
    if '--full' in sys.argv:
        print("FULL RUN — this will copy all files to the new structure.")
        print(f"Source (READ ONLY): {SRC}")
        print(f"Destination (NEW):  {DEST}")
        print("Starting in 3 seconds... Ctrl+C to abort.")
        import time; time.sleep(3)
        main(test_only=False)
    else:
        print("TEST RUN — processing Pod Drawings Post MOTC only.")
        print(f"Source (READ ONLY): {SRC}")
        print(f"Destination (NEW):  {DEST}")
        main(test_only=True)
        print("\nReview the renamed files in the log, then run with --full to process everything.")
