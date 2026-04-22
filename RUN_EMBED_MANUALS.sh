#!/bin/bash
# RUN_EMBED_MANUALS.sh — Run sequence for all unembedded manuals
# Updated: 22 April 2026
# Drive must be fully synced. Each manual takes several minutes (vision pass on diagram pages).
# Run in background: nohup bash RUN_EMBED_MANUALS.sh > /tmp/embed_log.txt 2>&1 &
#
# Changes from 09 Apr version:
#   - Fixed Munk Crane path: "Munk Crane Rov Hanger" (not "ROV Hanger"), recursive scan
#   - Fixed ROV Lights: PDFs are in subfolders, use find; skip already-embedded OR-TE-03338 & drawings
#   - Removed AleronVpSoftware: folder has no PDFs (it's a software repo)
#   - Fixed IXBlue: skip EQP-numbered drawing files (belong in index_drawings.py)
#   - Fixed Lars: TMA01071 already embedded (62 chunks); skip it; OCE-0400 wiring diagrams embedded fresh
#   - tcu.pdf: commented out — already has 1 chunk stub, check manually before re-embedding

DRIVE="/Users/seanbrock/Library/CloudStorage/GoogleDrive-seanbrock100@gmail.com/My Drive/Work Technical Docs"
SCRIPT="/Users/seanbrock/Documents/GitHub/rov-chatbot/embed_manual.py"

echo "=== Loading API keys from Railway ==="
eval $(python3 -c "
import requests
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
print(f'export VOYAGE_KEY={cfg[\"voyageKey\"]}')
print(f'export ANTHROPIC_KEY={cfg[\"anthropicKey\"]}')
print(f'export SUPABASE_SERVICE={cfg[\"supabaseService\"]}')
")
echo "Keys loaded."

echo ""
echo "=== 1  TMA01029 H30 GA Schematics ==="
python3 $SCRIPT \
  --pdf "$DRIVE/Top Level Schematics/H30 - GA Top Level & Schematics Manual - TMA01029.pdf" \
  --name "TMA01029 - H30 GA Top Level & Schematics Manual" \
  || echo "⚠ Section 1 failed, continuing..."

echo ""
echo "=== 2  tcu.pdf — SKIPPED (already has 1-chunk stub; investigate before re-embedding) ==="
# To force re-embed: python3 $SCRIPT --pdf "$DRIVE/tcu/tcu.pdf" --name "TCU Manual" --force

echo ""
echo "=== 3  Cardev Filter ==="
python3 $SCRIPT \
  --pdf "$DRIVE/Cardev/CardevFilter.PDF" \
  --name "Cardev HPU Hydraulic Return Filter" \
  || echo "⚠ Section 3 failed, continuing..."

echo ""
echo "=== 4  Bowman Heat Exchanger ==="
for f in "$DRIVE/Bowman heat exchanger/"*.pdf "$DRIVE/Bowman heat exchanger/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "Bowman Heat Exchanger - $name" \
    || echo "  ⚠ Failed: $name"
done

echo ""
echo "=== 5  SMD Valve Packs ==="
for f in "$DRIVE/SMD Valve packs/"*.pdf "$DRIVE/SMD Valve packs/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "SMD Valve Pack - $name" \
    || echo "  ⚠ Failed: $name"
done

echo ""
echo "=== 6  IXBlue Octans Nano Gyro (manuals only — skipping EQP/EQP958 drawing files) ==="
GYRO_DIR="$DRIVE/IXBlue Octans Nano Gyro Info Seven Oceanic 03.03.2023"
for f in "$GYRO_DIR/"*.pdf "$GYRO_DIR/"*.PDF; do
  [ -f "$f" ] || continue
  fname=$(basename "$f")
  # Skip drawing files — EQP-numbered files belong in index_drawings.py
  if [[ "$fname" == EQP* ]]; then
    echo "  Skipping drawing (use index_drawings.py instead): $fname"
    continue
  fi
  name=$(echo "$fname" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "IXBlue Octans Nano Gyro - $name" \
    || echo "  ⚠ Failed: $name"
done

echo ""
echo "=== 7  Control Room manuals ==="
# Also embed top-level Control Room PDFs (MK3 Software config, MV-1200, Moxa NPort)
for f in "$DRIVE/Control Room/"*.pdf "$DRIVE/Control Room/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: Control Room/$name"
  python3 $SCRIPT --pdf "$f" --name "Control Room - $name" \
    || echo "  ⚠ Failed: $name"
done
# Subfolders
for folder in "Six net" "Joystick" "DataVideo DN700 Manual" "Serve Switch Uno CX switcher" "Survey Monitors"; do
  for f in "$DRIVE/Control Room/$folder/"*.pdf "$DRIVE/Control Room/$folder/"*.PDF; do
    [ -f "$f" ] || continue
    name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
    echo "  Embedding: Control Room/$folder/$name"
    python3 $SCRIPT --pdf "$f" --name "Control Room - $name" \
      || echo "  ⚠ Failed: $name"
  done
done

echo ""
echo "=== 8  Munk Crane Rov Hanger (corrected path, recursive scan) ==="
# Note: folder name is 'Munk Crane Rov Hanger' not 'Munk Crane ROV Hanger'
while IFS= read -r f; do
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "Munk Crane - $name" \
    || echo "  ⚠ Failed: $name"
done < <(find "$DRIVE/Munk Crane Rov Hanger/" \( -name "*.pdf" -o -name "*.PDF" \) | sort)

echo ""
echo "=== 9  ROV Lights (recursive scan, skipping already-embedded & drawing files) ==="
while IFS= read -r f; do
  fname=$(basename "$f")
  # Already embedded as "Hercules MK3 Lighting JB..."
  if [[ "$fname" == *"OR-TE-03338"* ]]; then
    echo "  Skipping already-embedded: $fname"
    continue
  fi
  # Drawing files (ROV-XXXX-D format) — belong in index_drawings.py
  if [[ "$fname" =~ ^ROV-[0-9] ]]; then
    echo "  Skipping drawing (use index_drawings.py instead): $fname"
    continue
  fi
  # FTDI driver guide — not relevant to ROV operations
  if [[ "$fname" == *"FTDI"* ]]; then
    echo "  Skipping FTDI driver guide: $fname"
    continue
  fi
  name=$(echo "$fname" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "ROV Lights - $name" \
    || echo "  ⚠ Failed: $name"
done < <(find "$DRIVE/ROV Lights/" \( -name "*.pdf" -o -name "*.PDF" \) | sort)

echo ""
echo "=== 10  AleronVpSoftware — SKIPPED (no PDFs; folder is a software repo) ==="

echo ""
echo "=== 11  120HP Hydraulic Soft Start ==="
python3 $SCRIPT \
  --pdf "$DRIVE/120HP ROV Hydraulic Soft Start ModificationsTPR03280.pdf" \
  --name "120HP ROV Hydraulic Soft Start TPR03280" \
  || echo "⚠ Section 11 failed, continuing..."

echo ""
echo "=== 12  Lars — OCE-0400 wiring diagrams only (TMA01071 already embedded — 62 chunks) ==="
for f in "$DRIVE/Lars/OCE"*.pdf "$DRIVE/Lars/OCE"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "LARS - $name" \
    || echo "  ⚠ Failed: $name"
done

echo ""
echo "=== 13  Winch manuals ==="
for sub in "H15" "H30"; do
  for f in "$DRIVE/Winch/$sub/"*.pdf "$DRIVE/Winch/$sub/"*.PDF; do
    [ -f "$f" ] || continue
    name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
    echo "  Embedding: Winch/$sub/$name"
    python3 $SCRIPT --pdf "$f" --name "Winch $sub - $name" \
      || echo "  ⚠ Failed: $name"
  done
done

echo ""
echo "=== All embed_manual runs complete ==="
echo "Check Supabase chunks table to verify row counts."
echo ""
echo "NOTE: The following were skipped and may need attention:"
echo "  - tcu/tcu.pdf (1-chunk stub — check if TCU content covered by TMA01031, then --force re-embed)"
echo "  - IXBlue EQP-numbered drawing files (add to RUN_INDEX_DRAWINGS.sh instead)"
echo "  - ROV-0311-D-0510-90 Lighting JB drawing (add to RUN_INDEX_DRAWINGS.sh)"
