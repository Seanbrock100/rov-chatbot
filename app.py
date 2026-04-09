from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import os
import functools

app = Flask(__name__, static_folder='.')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ANTHROPIC_KEY    = os.environ.get('ANTHROPIC_KEY', '').strip()
VOYAGE_KEY       = os.environ.get('VOYAGE_KEY', '').strip()
SUPABASE_URL     = os.environ.get('SUPABASE_URL', '').strip()
SUPABASE_ANON    = os.environ.get('SUPABASE_ANON', '').strip()
SUPABASE_SERVICE = os.environ.get('SUPABASE_SERVICE', '').strip()
APP_PASSWORD     = os.environ.get('APP_PASSWORD', '').strip()


def check_password():
    if not APP_PASSWORD:
        return True
    return request.headers.get('X-App-Password', '') == APP_PASSWORD


def require_password(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not check_password():
            return jsonify({'error': 'Unauthorised'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'rov_agentic_chatbot.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route('/api/config')
def get_config():
    if APP_PASSWORD and not check_password():
        return jsonify({'error': 'Unauthorised'}), 401
    return jsonify({
        'anthropicKey':    ANTHROPIC_KEY,
        'voyageKey':       VOYAGE_KEY,
        'supabaseUrl':     SUPABASE_URL,
        'supabaseAnon':    SUPABASE_ANON,
        'supabaseService': SUPABASE_SERVICE,
        'passwordRequired': bool(APP_PASSWORD),
    })


@app.route('/api/auth', methods=['POST'])
def verify_password():
    data = request.get_json(silent=True) or {}
    if not APP_PASSWORD:
        return jsonify({'ok': True})
    if data.get('password') == APP_PASSWORD:
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'Wrong password'}), 401


@app.route('/voyage/embeddings', methods=['POST'])
@require_password
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


@app.route('/anthropic/messages', methods=['POST'])
@require_password
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


@app.route('/supabase/<path:path>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@require_password
def supabase_proxy(path):
    if request.method in ('POST', 'PATCH', 'DELETE') and 'rpc' not in path:
        auth_key = SUPABASE_SERVICE
    else:
        auth_key = SUPABASE_ANON

    forward_headers = {
        'Content-Type':  'application/json',
        'apikey':        auth_key,
        'Authorization': f'Bearer {auth_key}',
    }

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

    if res.status_code in (201, 204):
        return Response('', status=res.status_code)

    if not res.text or not res.text.strip():
        return Response('', status=res.status_code)

    try:
        return jsonify(res.json()), res.status_code
    except Exception:
        return Response(res.text, status=res.status_code, mimetype='text/plain')


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'anthropic': bool(ANTHROPIC_KEY),
        'voyage':    bool(VOYAGE_KEY),
        'supabase':  bool(SUPABASE_URL),
        'password':  bool(APP_PASSWORD),
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
