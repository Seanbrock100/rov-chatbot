#!/bin/bash
# index_drawings.py — Batch 2: Control Room, Lars, Winch, TMS, Longline
# Generated: 09 April 2026
# Run after Batch 1 completes and Drive is fully synced.

set -e

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
echo "=== 1/11  Control Room/Console wiring and Panels ==="
python3 /Users/seanbrock/index_drawings.py --folder "Control Room/Console wiring and Panels"

echo ""
echo "=== 2/11  Lars/Latch Beam ==="
python3 /Users/seanbrock/index_drawings.py --folder "Lars/Latch Beam"

echo ""
echo "=== 3/11  Lars/Latch beam winch ==="
python3 /Users/seanbrock/index_drawings.py --folder "Lars/Latch beam winch"

echo ""
echo "=== 4/11  Winch/H15 ==="
python3 /Users/seanbrock/index_drawings.py --folder "Winch/H15"

echo ""
echo "=== 5/11  Winch/H30 ==="
python3 /Users/seanbrock/index_drawings.py --folder "Winch/H30"

echo ""
echo "=== 6/11  TMS/H15 ==="
python3 /Users/seanbrock/index_drawings.py --folder "TMS/H15"

echo ""
echo "=== 7/11  TMS/H30 ==="
python3 /Users/seanbrock/index_drawings.py --folder "TMS/H30"

echo ""
echo "=== 8/11  TMS/topside ==="
python3 /Users/seanbrock/index_drawings.py --folder "TMS/topside"

echo ""
echo "=== 9/11  TMS/TMS protection frame ==="
python3 /Users/seanbrock/index_drawings.py --folder "TMS/TMS protection frame"

echo ""
echo "=== 10/11  TMS/TMS Topside Upgrade ==="
python3 /Users/seanbrock/index_drawings.py --folder "TMS/TMS Topside Upgrade"

echo ""
echo "=== 11/11  Longline Drawings ==="
python3 /Users/seanbrock/index_drawings.py --folder "Longline Drawings"

echo ""
echo "=== Batch 2 complete ==="
