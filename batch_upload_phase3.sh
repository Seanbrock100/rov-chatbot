#!/usr/bin/env bash
# Phase 3 — Vision-Only Drawings (72 files, ~92 vision calls)
# Usage: source /tmp/rov_embed_env.sh && bash batch_upload_phase3.sh
# Run from: /Users/seanbrock/Documents/GitHub/rov-chatbot/
# Estimated time: 20–30 min | Estimated Claude API cost: ~$0.50–1.50

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG="/tmp/phase3_upload.log"
echo "=== Phase 3 Vision Drawing Upload — $(date) ===" | tee "$LOG"

embed() {
  local pdf="$1"
  echo "" | tee -a "$LOG"
  echo ">>> $pdf" | tee -a "$LOG"
  python3 embed_manual.py \
    --pdf "rov-manual/manuals/$pdf" \
    --name "$pdf" \
    --force \
    --voyage-key  "$VOYAGE_KEY" \
    --anthropic-key "$ANTHROPIC_KEY" \
    --supabase-url  "$SUPABASE_URL" \
    --supabase-key  "$SUPABASE_SERVICE" \
    2>&1 | tee -a "$LOG"
}

# HCV-0015 series (all pure raster diagrams)
embed "HCV-0015-D-0200-00 (1 of 2).pdf"
embed "HCV-0015-D-0200-90 (1 of 3).pdf"
embed "HCV-0015-D-0200-90 (2 of 3).pdf"
embed "HCV-0015-D-0200-90 (3 of 3).pdf"
embed "HCV-0015-D-0201-00 (1 of 2).pdf"
embed "HCV-0015-D-0201-00 (2 of 2).pdf"
embed "HCV-0015-D-0201-90 (1 of 3).pdf"
embed "HCV-0015-D-0201-90 (2 of 3).pdf"
embed "HCV-0015-D-0201-90 (3 of 3).pdf"
embed "HCV-0015-D-0202-00 (1 of 2).pdf"
embed "HCV-0015-D-0202-00 (2 of 2).pdf"
embed "HCV-0015-D-0300-00 (1 of 2).pdf"
embed "HCV-0015-D-0300-00 (2 of 2).pdf"
embed "HCV-0015-D-0500-00 (1 of 2).pdf"
embed "HCV-0015-D-0500-00 (2 of 2).pdf"
embed "HCV-0015-D-0800-90 (1 of 5).pdf"
embed "HCV-0015-D-0800-90 (2 of 5).pdf"
embed "HCV-0015-D-0800-90 (3 of 5).pdf"
embed "HCV-0015-D-0800-90 (4 of 5).pdf"
embed "HCV-0015-D-0800-90 (5 of 5).pdf"

# PDU-1012 series
embed "PDU-1012-D-0007-90 SHT 1 - 2.4KV Transformer Panel Wiring Diagram.pdf"
embed "PDU-1012-D-0017-00 SHT 1.pdf"
embed "PDU-1012-D-0017-90 SHT 1.pdf"

# ROV-0148
embed "ROV-0148-671-04.pdf"

# ROV-0226 (raster sheets)
embed "ROV-0226-630-90.pdf"
embed "ROV-0226-725-00 SHEET 1.pdf"
embed "ROV-0226-725-90 SHEET 1.pdf"

# ROV-0249
embed "ROV-0249-D-0050-90.pdf"

# ROV-0300 (raster pages)
embed "ROV-0300-D-0100-01.pdf"
embed "ROV-0300-D-0111-01 T4 mounting plate (stbd).pdf"
embed "ROV-0300-D-0420-00 TCU Assembly.pdf"
embed "ROV-0300-D-0420-90 TCU Wiring Diagram.pdf"
embed "ROV-0300-D-0802-00.pdf"
embed "ROV-0300-D-0802-90.pdf"

# ROV-0305 (raster)
embed "ROV-0305-D-0100-00 (1).pdf"
embed "ROV-0305-D-0450-00.PDF"
embed "ROV-0305-D-0470-00 sht 1.pdf"

# ROV-0311 series (all raster wiring/schematic diagrams)
embed "ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf"
embed "ROV-0311-D-0203-00 SHT 1 rc changes sketch.pdf"
embed "ROV-0311-D-0203-01 SHT 1 rc updates sketch.pdf"
embed "ROV-0311-D-0204-00 SHT 1 rc updates sketch.pdf"
embed "ROV-0311-D-0204-01 SHT 1 rc updates sketch.pdf"
embed "ROV-0311-D-0206-00 Pod control earth strip plate 1 of 1.pdf"
embed "ROV-0311-D-0208-00 Pod valve pack unregulated supply.pdf"
embed "ROV-0311-D-0208-01.pdf"
embed "ROV-0311-D-0208-02.pdf"
embed "ROV-0311-D-0208-03.pdf"
embed "ROV-0311-D-0208-90.pdf"
embed "ROV-0311-D-0210-00.pdf"
embed "ROV-0311-D-0210-01.pdf"
embed "ROV-0311-D-0210-02.pdf"
embed "ROV-0311-D-0210-03.pdf"
embed "ROV-0311-D-0210-04.pdf"
embed "ROV-0311-D-0211-00.pdf"
embed "ROV-0311-D-0211-01.pdf"
embed "ROV-0311-D-0212-00.pdf"
embed "ROV-0311-D-0212-02.pdf"
embed "ROV-0311-D-0300-90 sht 1-Model.pdf"
embed "ROV-0311-D-0500-00 SHT 1-Model.pdf"
embed "ROV-0311-D-0620-90 SHT 1-Model.pdf"
embed "ROV-0311-D-0620-90 sht 2-Model.pdf"
embed "ROV-0311-D-0680-00.pdf"
embed "ROV-0311-D-0680-90.pdf"
embed "ROV-0311-D-0800-50 SHT 1-Model.pdf"
embed "ROV-0311-D-0800-90 SHT 1 - Control Console Wiring.pdf"
embed "ROV-0311-D-0800-90 SHT 2 - Control Console Wiring.pdf"
embed "ROV-0311-D-0800-90 SHT 3 - Control Console Wiring.pdf"
embed "ROV-0311-D-0800-90 SHT 4 - Control Console Wiring.pdf"
embed "ROV-0311-D-0800-90 SHT 5 - Control Console Wiring.pdf"

# SSA-0277 (raster buoyancy drawings)
embed "SSA-0277-D-0004-16 Forward Buoyancy 450kgm3.pdf"
embed "SSA-0277-D-0004-17 Middle Buoyancy 450kgm3.pdf"

# tcu (mostly raster)
embed "tcu.pdf"

echo "" | tee -a "$LOG"
echo "=== Phase 3 COMPLETE — $(date) ===" | tee -a "$LOG"
