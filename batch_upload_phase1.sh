#!/usr/bin/env bash
# Phase 1 — Text-Only Batch Upload (38 files, no Claude vision credits)
# Usage: source /tmp/rov_embed_env.sh && bash batch_upload_phase1.sh
# Run from: /Users/seanbrock/Documents/GitHub/rov-chatbot/

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG="/tmp/phase1_upload.log"
echo "=== Phase 1 Text-Only Upload — $(date) ===" | tee "$LOG"

embed() {
  local pdf="$1"
  echo "" | tee -a "$LOG"
  echo ">>> $pdf" | tee -a "$LOG"
  python3 embed_manual.py \
    --pdf "rov-manual/manuals/$pdf" \
    --name "$pdf" \
    --text-only \
    --force \
    --voyage-key  "$VOYAGE_KEY" \
    --anthropic-key "$ANTHROPIC_KEY" \
    --supabase-url  "$SUPABASE_URL" \
    --supabase-key  "$SUPABASE_SERVICE" \
    2>&1 | tee -a "$LOG"
}

# EQP952 series
embed "EQP952-0203-DR-PD-54001 - rc updates sketch p2.pdf"
embed "EQP952-0203-DR-PD-54001 - rc updates sketch page 3.pdf"
embed "EQP952-0203-DR-PD-54001 - rc updates sketch.pdf"
embed "EQP952-0203-DR-PD-54002 - rc updates sketch p1.pdf"
embed "EQP952-0203-DR-PD-54002 - rc updates sketch p2.pdf"
embed "EQP952-0203-DR-PD-54002 - rc updates sketch p3.pdf"
embed "EQP952-0203-DR-PD-55000.pdf"
embed "EQP952-0203-DR-PD-55001.pdf"
embed "EQP952-0203-DR-PD-55002.pdf"
embed "EQP952-0203-DR-PD-55003.pdf"
embed "EQP952-0203-DR-PD-55004.pdf"
embed "EQP952-0203-DR-PD-55006.pdf"
embed "EQP952-0203-DR-PD-55007.pdf"
embed "EQP952-0203-DR-PD-55011.pdf"
embed "EQP952-0203-DR-PD-55016.pdf"
embed "EQP952-0203-DR-PD-55017.pdf"
embed "EQP952-0203-DR-PD-55018.pdf"
embed "EQP952-0203-DR-PD-55019.pdf"

# Miscellaneous text-bearing docs
embed "Hercules Tool Tray Skid BOM.pdf"
embed "Hercules Tool Tray Skid hammer head.pdf"

# ROV-0226 series (vector text)
embed "ROV-0226-420-00 SHEET 1.pdf"
embed "ROV-0226-420-01 SHEET 1.pdf"
embed "ROV-0226-420-01 SHEET 2.pdf"
embed "ROV-0226-420-01 SHEET 3.pdf"

# ROV-0300 series (text pages)
embed "ROV-0300-D-0110-02 sht 1 Frame Protection Acetal .pdf"
embed "ROV-0300-D-0440-00 sht 1 rev C9 Hydraulic Diagram.pdf"
embed "ROV-0300-D-0440-00 sht 2 rev C9 Hydraulic Diagram.pdf"
embed "ROV-0300-D-0440-00 sht 3 rev C9 Hydraulic Diagram.pdf"

# ROV-0305 series (text pages)
embed "ROV-0305-D-0630-90 Sht 1-3.pdf"
embed "ROV-0305-D-0660-00.pdf"
embed "ROV-0305-D-0660-90.pdf"

# ROV-0311 (one with text)
embed "ROV-0311-D-0213-01 SHT 1 .pdf"

# SSA-0277 series (text pages)
embed "SSA-0277-D-0004-00 sht 1 - Amended H15.pdf"
embed "SSA-0277-D-0004-00 sht 1.pdf"
embed "SSA-0277-D-0004-01 SHT 2 commented For order.pdf"
embed "SSA-0277-D-0004-01 SHT 2.pdf"
embed "SSA-0277-D-0004-01 sht 1.pdf"
embed "SSA-0277-D-0004-14 SHT 1.pdf"

echo "" | tee -a "$LOG"
echo "=== Phase 1 COMPLETE — $(date) ===" | tee -a "$LOG"
