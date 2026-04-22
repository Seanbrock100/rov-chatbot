#!/usr/bin/env bash
# Phase 2 — H30 Full Manual (171 pages, full vision pass)
# Usage: source /tmp/rov_embed_env.sh && bash batch_upload_phase2.sh
# Run from: /Users/seanbrock/Documents/GitHub/rov-chatbot/
# Estimated time: 20–30 min | Estimated Claude vision calls: ~105

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG="/tmp/phase2_upload.log"
echo "=== Phase 2 H30 Full Vision Upload — $(date) ===" | tee "$LOG"

python3 embed_manual.py \
  --pdf  "rov-manual/manuals/H30 - GA Top Level & Schematics Manual - TMA01029.pdf" \
  --name "H30 - GA Top Level & Schematics Manual - TMA01029.pdf" \
  --force \
  --voyage-key  "$VOYAGE_KEY" \
  --anthropic-key "$ANTHROPIC_KEY" \
  --supabase-url  "$SUPABASE_URL" \
  --supabase-key  "$SUPABASE_SERVICE" \
  2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "=== Phase 2 COMPLETE — $(date) ===" | tee -a "$LOG"
