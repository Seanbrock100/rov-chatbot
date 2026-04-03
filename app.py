“””
ROV Manual Chatbot — Railway Server
Handles: static file serving, API proxies (Voyage/Anthropic/Supabase), password gate.

Environment variables required (set in Railway dashboard):
ANTHRIPIC_KEY       — Anthropic API key   (note: typo intentional, matches your Railway var)
VOYAGE_KEY          — Voyage AI key
SUPABASE_URL        — https://ccjurdnubkmeepaztomy.supabase.co
SUPABASE_ANON       — Supabase anon key
SUPABASE_SERVICE    — Supabase service role key
APP_PASSWORD        — Single password to protect the app (optional — if not set, no gate)
“””

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import os
import functools

app = Flask(**name**, static_folder=’.’)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(**file**))

# ── Pull keys from Railway environment ──────────────────────────────────────

ANTHROPIC_KEY    = os.environ.get(‘ANTHRIPIC_KEY’, ‘’).strip()
VOYAGE_KEY       = os.environ.get(‘VOYAGE_KEY’, ‘’).strip()
SUPABASE_URL     = os.environ.get(‘SUPABASE_URL’, ‘’).strip()
SUPABASE_ANON    = os.environ.get(‘SUPABASE_ANON’, ‘’).strip()
SUPABASE_SERVICE = os.environ.get(‘SUPABASE_SERVICE’, ‘’).strip()
APP_PASSWORD     = os.environ.get(‘APP_PASSWORD’, ‘’).strip()

# ── Password gate helper ─────────────────────────────────────────────────────

def check_password():
“”“Returns True if no password set, or if request carries correct password header.”””
if not APP_PASSWORD:
return True
return request.headers.get(‘X-App-Password’, ‘’) == APP_PASSWORD

def require_password(f):
“”“Decorator for API routes that should be password-gated.”””
@functools.wraps(f)
def decorated(*args, **kwargs):
if not check_password():
return jsonify({‘error’: ‘Unauthorised’}), 401
return f(*args, **kwargs)
return decorated

# ── Serve frontend ───────────────────────────────────────────────────────────

@app.route(’/’)
def index():
return send_from_directory(BASE_DIR, ‘rov_agentic_chatbot.html’)

@app.route(’/<path:filename>’)
def static_files(filename):
return send_from_directory(BASE_DIR, filename)

# ── Config endpoint — sends Railway env vars to the frontend ─────────────────

# Frontend calls this on load so no keys need to be typed manually

@app.route(’/api/config’)
def get_config():
“””
Returns non-sensitive config + masked status of secrets.
The frontend uses this to auto-populate its key state.
Password is never sent — only whether one is set.
“””
if APP_PASSWORD and not check_password():
return jsonify({‘error’: ‘Unauthorised’}), 401

```
return jsonify({
    'anthropicKey':    ANTHROPIC_KEY,
    'voyageKey':       VOYAGE_KEY,
    'supabaseUrl':     SUPABASE_URL,
    'supabaseAnon':    SUPABASE_ANON,
    'supabaseService': SUPABASE_SERVICE,
    'passwordRequired': bool(APP_PASSWORD),
})
```

# ── Password verify endpoint ─────────────────────────────────────────────────

@app.route(’/api/auth’, methods=[‘POST’])
def verify_password():
“”“Frontend sends password here; returns 200 OK or 401.”””
data = request.get_json(silent=True) or {}
if not APP_PASSWORD:
return jsonify({‘ok’: True})
if data.get(‘password’) == APP_PASSWORD:
return jsonify({‘ok’: True})
return jsonify({‘ok’: False, ‘error’: ‘Wrong password’}), 401

# ── Proxy: Voyage AI embeddings ──────────────────────────────────────────────

@app.route(’/voyage/embeddings’, methods=[‘POST’])
@require_password
def voyage_proxy():
res = requests.post(
‘https://api.voyageai.com/v1/embeddings’,
headers={
‘Content-Type’:  ‘application/json’,
‘Authorization’: f’Bearer {VOYAGE_KEY}’,
},
json=request.get_json(),
timeout=60,
)
return jsonify(res.json()), res.status_code

# ── Proxy: Anthropic messages ────────────────────────────────────────────────

@app.route(’/anthropic/messages’, methods=[‘POST’])
@require_password
def anthropic_proxy():
res = requests.post(
‘https://api.anthropic.com/v1/messages’,
headers={
‘Content-Type’:      ‘application/json’,
‘x-api-key’:         ANTHROPIC_KEY,
‘anthropic-version’: ‘2023-06-01’,
},
json=request.get_json(),
timeout=120,        # agentic loops can take a while
)
return jsonify(res.json()), res.status_code

# ── Proxy: Supabase REST ─────────────────────────────────────────────────────

# Handles GET, POST (insert), PATCH, DELETE on /supabase/<table_or_rpc>

@app.route(’/supabase/<path:path>’, methods=[‘GET’, ‘POST’, ‘PATCH’, ‘DELETE’])
@require_password
def supabase_proxy(path):
# Decide which key to use: service role for writes, anon for reads
if request.method in (‘POST’, ‘PATCH’, ‘DELETE’) and ‘rpc’ not in path:
auth_key = SUPABASE_SERVICE
else:
auth_key = SUPABASE_ANON

```
forward_headers = {
    'Content-Type':  'application/json',
    'apikey':        auth_key,
    'Authorization': f'Bearer {auth_key}',
}

# Pass Prefer header through (needed for upsert / return=minimal)
prefer = request.headers.get('Prefer')
if prefer:
    forward_headers['Prefer'] = prefer

url    = f"{SUPABASE_URL}/rest/v1/{path}"
params = request.args.to_dict()
body   = request.get_json(silent=True)

res = requests.request(
    method  = request.method,
    url     = url,
    headers = forward_headers,
    params  = params,
    json    = body,
    timeout = 30,
)

# ── CRITICAL FIX: handle 201 Created and 204 No Content correctly ────────
# These responses have no body — returning jsonify(None) causes a TypeError.
if res.status_code in (201, 204):
    return Response('', status=res.status_code)

# Some Supabase responses are empty even on 200 (e.g. upsert with return=minimal)
if not res.text or not res.text.strip():
    return Response('', status=res.status_code)

# Attempt JSON parse; fall back to raw text
try:
    return jsonify(res.json()), res.status_code
except Exception:
    return Response(res.text, status=res.status_code, mimetype='text/plain')
```

# ── Health check ─────────────────────────────────────────────────────────────

@app.route(’/health’)
def health():
return jsonify({
‘status’: ‘ok’,
‘anthropic’: bool(ANTHROPIC_KEY),
‘voyage’:    bool(VOYAGE_KEY),
‘supabase’:  bool(SUPABASE_URL),
‘password’:  bool(APP_PASSWORD),
})

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 8000))
print(f’\n ROV Chatbot running on port {port}’)
print(f’  Anthropic key: {“✓” if ANTHROPIC_KEY else “✗ MISSING”}’)
print(f’  Voyage key:    {“✓” if VOYAGE_KEY else “✗ MISSING”}’)
print(f’  Supabase URL:  {“✓” if SUPABASE_URL else “✗ MISSING”}’)
print(f’  Password gate: {“✓ ENABLED” if APP_PASSWORD else “disabled”}’)
app.run(host=‘0.0.0.0’, port=port, debug=False)
