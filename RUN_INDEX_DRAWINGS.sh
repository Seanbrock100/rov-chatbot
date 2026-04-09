#!/bin/bash
# index_drawings.py — Run sequence for all unindexed drawing folders
# Generated: 09 April 2026
# Run from Mac terminal. Drive must be fully synced before running.

set -e  # stop on first error

echo "=== Loading API keys from Railway ==="
eval $(python3 -c "
import requests, json
cfg = requests.get('https://rov-chatbot-production-3d66.up.railway.app/api/config').json()
print(f'export VOYAGE_KEY={cfg[\"voyageKey\"]}')
print(f'export ANTHROPIC_KEY={cfg[\"anthropicKey\"]}')
print(f'export SUPABASE_SERVICE={cfg[\"supabaseService\"]}')
")
echo "Keys loaded."

echo ""
echo "=== 1/6  HCV-0015 ==="
python3 /Users/seanbrock/index_drawings.py --folder "HCV-0015"

echo ""
echo "=== 2/6  PDU-009-D-0016-90 ==="
python3 /Users/seanbrock/index_drawings.py --folder "PDU-009-D-0016-90"

echo ""
echo "=== 3/6  ROV-300-D-0420-90 ==="
python3 /Users/seanbrock/index_drawings.py --folder "ROV-300-D-0420-90"

echo ""
echo "=== 4/6  ROV-0305-D-0470 ==="
python3 /Users/seanbrock/index_drawings.py --folder "ROV-0305-D-0470"

echo ""
echo "=== 5/6  ROV-311 ==="
python3 /Users/seanbrock/index_drawings.py --folder "ROV-311"

echo ""
echo "=== 6/6  Pan & Tilit ==="
python3 /Users/seanbrock/index_drawings.py --folder "Pan & Tilit"

echo ""
echo "=== All drawing folders complete ==="
echo "Next: run RUN_INDEX_DRAWINGS_BATCH2.sh for Control Room, Lars, Winch, TMS"
