#!/bin/bash
# embed_manual.py — Run sequence for all unembedded manuals
# Generated: 09 April 2026
# Drive must be fully synced. Each manual takes several minutes (vision pass on diagram pages).
# Can run in background: nohup bash RUN_EMBED_MANUALS.sh > /tmp/embed_log.txt 2>&1 &

DRIVE="/Users/seanbrock/Library/CloudStorage/GoogleDrive-seanbrock100@gmail.com/My Drive/Work Technical Docs"
SCRIPT="/Users/seanbrock/Documents/GitHub/rov-chatbot/embed_manual.py"

set -e

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
  --pdf "$DRIVE/Top Level Schematics/TMA01029 - H30 Schematics Manual.pdf" \
  --name "TMA01029 - H30 GA Top Level & Schematics Manual"

echo ""
echo "=== 2  tcu.pdf (check for duplicate first) ==="
# NOTE: Check Supabase chunks table first — if TCU content already covered by
# Hercules Mk3.pdf or TMA01031, skip this one.
# python3 $SCRIPT --pdf "$DRIVE/tcu/tcu.pdf" --name "TCU Manual"

echo ""
echo "=== 3  Cardev Filter ==="
python3 $SCRIPT \
  --pdf "$DRIVE/Cardev/CardevFilter.PDF" \
  --name "Cardev HPU Hydraulic Return Filter"

echo ""
echo "=== 4  Bowman Heat Exchanger ==="
for f in "$DRIVE/Bowman heat exchanger/"*.pdf "$DRIVE/Bowman heat exchanger/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "Bowman Heat Exchanger - $name"
done

echo ""
echo "=== 5  SMD Valve Packs ==="
for f in "$DRIVE/SMD Valve packs/"*.pdf "$DRIVE/SMD Valve packs/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "SMD Valve Pack - $name"
done

echo ""
echo "=== 6  IXBlue Octans Nano Gyro ==="
for f in "$DRIVE/IXBlue Octans Nano Gyro Info Seven Oceanic 03.03.2023/"*.pdf \
         "$DRIVE/IXBlue Octans Nano Gyro Info Seven Oceanic 03.03.2023/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "IXBlue Octans Nano Gyro - $name"
done

echo ""
echo "=== 7  Control Room manuals ==="
for folder in "Six net" "Joystick" "DataVideo DN700 Manual" "Serve Switch Uno CX switcher" "Survey Monitors"; do
  for f in "$DRIVE/Control Room/$folder/"*.pdf "$DRIVE/Control Room/$folder/"*.PDF; do
    [ -f "$f" ] || continue
    name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
    echo "  Embedding: Control Room/$folder/$name"
    python3 $SCRIPT --pdf "$f" --name "Control Room - $name"
  done
done

echo ""
echo "=== 8  Munk Crane ==="
for f in "$DRIVE/Munk Crane ROV Hanger/"*.pdf "$DRIVE/Munk Crane ROV Hanger/"*.PDF \
         "$DRIVE/Munk Crane ROV Hanger/Munk Crane remote/"*.pdf \
         "$DRIVE/Munk Crane ROV Hanger/Munk Crane remote/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "Munk Crane - $name"
done

echo ""
echo "=== 9  ROV Lights ==="
for f in "$DRIVE/ROV Lights/"*.pdf "$DRIVE/ROV Lights/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "ROV Lights - $name"
done

echo ""
echo "=== 10  Aleron VP Software ==="
for f in "$DRIVE/AleronVpSoftware/"*.pdf "$DRIVE/AleronVpSoftware/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "Aleron VP Software - $name"
done

echo ""
echo "=== 11  120HP Hydraulic Soft Start ==="
for f in "$DRIVE/"*TPR03280*.pdf "$DRIVE/"*TPR03280*.PDF \
         "$DRIVE/"*Soft\ Start*.pdf "$DRIVE/"*Soft\ Start*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "120HP Hydraulic Soft Start - $name"
done

echo ""
echo "=== 12  Lars LARS Tech Manual ==="
for f in "$DRIVE/Lars/"*.pdf "$DRIVE/Lars/"*.PDF; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
  echo "  Embedding: $name"
  python3 $SCRIPT --pdf "$f" --name "LARS - $name"
done

echo ""
echo "=== 13  Winch manuals ==="
for sub in "H15" "H30"; do
  for f in "$DRIVE/Winch/$sub/"*.pdf "$DRIVE/Winch/$sub/"*.PDF; do
    [ -f "$f" ] || continue
    name=$(basename "$f" | sed 's/\.[Pp][Dd][Ff]$//')
    echo "  Embedding: Winch/$sub/$name"
    python3 $SCRIPT --pdf "$f" --name "Winch $sub - $name"
  done
done

echo ""
echo "=== All embed_manual runs complete ==="
echo "Check Supabase chunks table to verify row counts."
