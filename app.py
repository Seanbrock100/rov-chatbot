"""
ROV Manual Chatbot — Cloud Server
Deployed on Railway. Proxies requests to Voyage AI, Anthropic, and Supabase.
Serves the frontend HTML.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='static')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Serve frontend ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'rov_agentic_chatbot.html')


@app.route('/<path:filename>')
def static_files(filename):
return send_from_directory(BASE_DIR, filename)

# ── Proxy: Voyage AI ──────────────────────────────────────────────────────────
@app.route('/voyage/embeddings', methods=['POST'])
def voyage_proxy():
    auth = request.headers.get('Authorization', '')
    res  = requests.post(
        'https://api.voyageai.com/v1/embeddings',
        headers={'Content-Type': 'application/json', 'Authorization': auth},
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
            'x-api-key':         request.headers.get('x-api-key', ''),
            'anthropic-version': '2023-06-01',
        },
        json=request.get_json(),
        timeout=60,
    )
    return jsonify(res.json()), res.status_code

# ── Proxy: Supabase (generic pass-through) ────────────────────────────────────
@app.route('/supabase/<path:path>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def supabase_proxy(path):
    supabase_url = request.headers.get('x-supabase-url', '')
    if not supabase_url:
        return jsonify({'error': 'x-supabase-url header required'}), 400

    # Forward all headers except host
    forward_headers = {
        'Content-Type':  'application/json',
        'apikey':        request.headers.get('apikey', ''),
        'Authorization': request.headers.get('Authorization', ''),
        'Prefer':        request.headers.get('Prefer', ''),
    }

    url    = f"{supabase_url}/rest/v1/{path}"
    params = request.args.to_dict()

    res = requests.request(
        method  = request.method,
        url     = url,
        headers = forward_headers,
        params  = params,
        json    = request.get_json(silent=True),
        timeout = 30,
    )
if res.text:
    try:
        return jsonify(res.json()), res.status_code
    except:
        return res.text, res.status_code
return '', res.status_code


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f'\n ROV Chatbot running on port {port}')
    app.run(host='0.0.0.0', port=port)
