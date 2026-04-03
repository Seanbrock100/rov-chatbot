"""
ROV Manual Chatbot — Cloud Server
Deployed on Railway. Proxies requests to Voyage AI, Anthropic, and Supabase.
All API keys loaded from Railway environment variables — no key entry in browser.
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='static')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Load keys from Railway environment variables ──────────────────────────────
ANTHROPIC_KEY    = os.environ.get('ANTHRIPIC_KEY', '')      # matches Railway var name
VOYAGE_KEY       = os.environ.get('VOYAGE_KEY', '')
SUPABASE_URL     = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON    = os.environ.get('SUPABASE_ANON', '')
SUPABASE_SERVICE = os.environ.get('SUPABASE_SERVICE', '')

# ── Serve frontend ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'rov_agentic_chatbot2.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

# ── Config endpoint — sends keys to frontend so it needs no key screen ────────
@app.route('/config')
def config():
    """Returns server-side config to the frontend. Keys never exposed in source code."""
    return jsonify({
        'anthropicKey':    ANTHROPIC_KEY,
        'voyageKey':       VOYAGE_KEY,
        'supabaseUrl':     SUPABASE_URL,
        'supabaseAnon':    SUPABASE_ANON,
        'supabaseService': SUPABASE_SERVICE,
    })

# ── Proxy: Voyage AI ──────────────────────────────────────────────────────────
@app.route('/voyage/embeddings', methods=['POST'])
def voyage_proxy():
    res = requests.post(
        'https://api.voyageai.com/v1/embeddings',
        headers={
            'Content-Type':  'application/json',
            'Authorization': f'Bearer {VOYAGE_KEY}',
        },
        json=request.get_json(),
        timeout=60,
    )
    return jsonify(res.json()), res.status_code

# ── Proxy: Anthropic ──────────────────────────────────────────────────────────
@app.route('/anthropic/messages', methods=['POST'])
def anthropic_proxy():
    res = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'Content-Type':      'application/json',
            'x-api-key':         ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01',
        },
        json=request.get_json(),
        timeout=120,
    )
    return jsonify(res.json()), res.status_code

# ── Proxy: Supabase REST (chunks save/load) ───────────────────────────────────
@app.route('/supabase/chunks', methods=['GET', 'POST'])
def supabase_chunks():
    method  = request.method
    params  = request.args.to_dict()
    payload = request.get_json(silent=True)

    # Use service key for writes, anon key for reads
    key = SUPABASE_SERVICE if method == 'POST' else SUPABASE_ANON

    headers = {
        'Content-Type':  'application/json',
        'apikey':        key,
        'Authorization': f'Bearer {key}',
    }
    if method == 'POST':
        headers['Prefer'] = 'return=minimal'

    res = requests.request(
        method  = method,
        url     = f'{SUPABASE_URL}/rest/v1/chunks',
        headers = headers,
        params  = params,
        json    = payload,
        timeout = 30,
    )

    # Return empty response for 201/204 (successful save with no body)
    if res.status_code in (201, 204) or not res.text:
        return Response('', status=res.status_code)

    # Try JSON, fall back to plain text
    try:
        return jsonify(res.json()), res.status_code
    except Exception:
        return Response(res.text, status=res.status_code, mimetype='text/plain')

# ── Proxy: Supabase RPC (vector search) ──────────────────────────────────────
@app.route('/supabase/rpc/match_chunks', methods=['POST'])
def supabase_rpc():
    res = requests.post(
        f'{SUPABASE_URL}/rest/v1/rpc/match_chunks',
        headers={
            'Content-Type':  'application/json',
            'apikey':        SUPABASE_ANON,
            'Authorization': f'Bearer {SUPABASE_ANON}',
        },
        json=request.get_json(),
        timeout=30,
    )
    try:
        return jsonify(res.json()), res.status_code
    except Exception:
        return Response(res.text, status=res.status_code, mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f'\n ROV Chatbot — port {port}')
    print(f' Anthropic key: {"set" if ANTHROPIC_KEY else "MISSING"}')
    print(f' Voyage key:    {"set" if VOYAGE_KEY else "MISSING"}')
    print(f' Supabase URL:  {"set" if SUPABASE_URL else "MISSING"}')
    app.run(host='0.0.0.0', port=port)
