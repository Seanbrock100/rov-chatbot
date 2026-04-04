#!/usr/bin/env python3
"""
embed_manual.py — ROV Manual Embedding Script
Two-pass pipeline: pdfplumber for text pages, Claude vision for diagram pages.

Usage:
  python embed_manual.py --pdf "TMA01028.pdf" --name "TMA01028 H15 GA Schematics"

Requirements:
  pip install pdfplumber requests
  apt install poppler-utils

Env vars: VOYAGE_KEY, ANTHROPIC_KEY, SUPABASE_URL, SUPABASE_SERVICE
"""

import os, sys, base64, argparse, time, tempfile, subprocess
from pathlib import Path
import requests

try:
    import pdfplumber
except ImportError:
    print('Missing: pip install pdfplumber')
    sys.exit(1)

VOYAGE_KEY       = os.environ.get('VOYAGE_KEY', '').strip()
ANTHROPIC_KEY    = os.environ.get('ANTHROPIC_KEY', '').strip()
SUPABASE_URL     = os.environ.get('SUPABASE_URL', 'https://ccjurdnubkmeepaztomy.supabase.co').strip()
SUPABASE_SERVICE = os.environ.get('SUPABASE_SERVICE', '').strip()

CHUNK_WORDS     = 350
CHUNK_OVERLAP   = 50
MIN_WORDS       = 30
VOYAGE_BATCH    = 8
SUPABASE_BATCH  = 50
IMAGE_DPI       = 120
VOYAGE_MODEL    = 'voyage-large-2'
CLAUDE_MODEL    = 'claude-opus-4-20250514'


def sb_headers():
    return {
        'apikey': SUPABASE_SERVICE,
        'Authorization': f'Bearer {SUPABASE_SERVICE}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }

def manual_exists(name):
    res = requests.get(f'{SUPABASE_URL}/rest/v1/chunks', headers=sb_headers(),
        params={'manual_name': f'eq.{name}', 'limit': '1', 'select': 'id'}, timeout=15)
    d = res.json()
    return isinstance(d, list) and len(d) > 0

def delete_manual(name):
    print(f'  Deleting existing chunks for "{name}"...')
    res = requests.delete(f'{SUPABASE_URL}/rest/v1/chunks', headers=sb_headers(),
        params={'manual_name': f'eq.{name}'}, timeout=30)
    print(f'  Deleted: {res.status_code}')

def insert_chunks(rows):
    res = requests.post(f'{SUPABASE_URL}/rest/v1/chunks', headers=sb_headers(),
        json=rows, timeout=60)
    if res.status_code not in (200, 201, 204):
        print(f'  ⚠ Insert error {res.status_code}: {res.text[:200]}')
    return res.status_code

def voyage_embed(texts, input_type='document'):
    res = requests.post('https://api.voyageai.com/v1/embeddings',
        headers={'Authorization': f'Bearer {VOYAGE_KEY}', 'Content-Type': 'application/json'},
        json={'model': VOYAGE_MODEL, 'input': texts, 'input_type': input_type}, timeout=60)
    if res.status_code != 200:
        raise RuntimeError(f'Voyage error {res.status_code}: {res.text[:300]}')
    return [item['embedding'] for item in res.json()['data']]

def rasterise_page(pdf_path, page_num, dpi, out_dir):
    cmd = ['pdftoppm', '-jpeg', '-r', str(dpi),
           '-f', str(page_num), '-l', str(page_num),
           pdf_path, os.path.join(out_dir, f'page_{page_num:04d}')]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    for suffix in ['-1.jpg', '-01.jpg', '-001.jpg', '-0001.jpg']:
        path = os.path.join(out_dir, f'page_{page_num:04d}{suffix}')
        if os.path.exists(path):
            return path
    prefix = f'page_{page_num:04d}'
    for f in os.listdir(out_dir):
        if f.startswith(prefix) and f.endswith('.jpg'):
            return os.path.join(out_dir, f)
    return None

def claude_read_image(image_path, page_num):
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    prompt = (
        f'This is page {page_num} of an ROV technical manual (Hercules MK3, Subsea 7). '
        'Extract ALL readable technical content: component labels, drawing numbers, '
        'connector pin assignments, cable numbers, wire colours, PCB names, part numbers, '
        'valve numbers, pressure ratings, voltages, table contents, notes, revision history. '
        'Preserve drawing number references exactly. '
        'If this is a blank title page or contains only a border with no technical content, '
        'reply with exactly: BLANK_PAGE'
    )
    res = requests.post('https://api.anthropic.com/v1/messages',
        headers={'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01',
                 'Content-Type': 'application/json'},
        json={'model': CLAUDE_MODEL, 'max_tokens': 2000, 'messages': [{'role': 'user',
            'content': [
                {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': b64}},
                {'type': 'text', 'text': prompt}
            ]}]}, timeout=60)
    if res.status_code != 200:
        print(f'    vision error {res.status_code}')
        return ''
    text = res.json()['content'][0]['text'].strip()
    return '' if text == 'BLANK_PAGE' else text

def extract_pages(pdf_path):
    pages = []
    pdf = pdfplumber.open(pdf_path)
    total = len(pdf.pages)
    print(f'\n  {total} pages in PDF')

    image_pages = []
    text_count = 0

    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ''
        if len(text.split()) >= MIN_WORDS:
            pages.append({'page_num': i, 'text': text, 'method': 'text'})
            text_count += 1
        else:
            pages.append({'page_num': i, 'text': '', 'method': 'pending'})
            image_pages.append(i)

    pdf.close()
    print(f'  Pass 1 complete — text: {text_count}, diagrams: {len(image_pages)}')

    if not image_pages:
        return pages

    if not ANTHROPIC_KEY:
        print('  ⚠ ANTHROPIC_KEY not set — diagram pages skipped (text-only embed)')
        for p in pages:
            if p['method'] == 'pending':
                p['text'] = f'[Diagram page {p["page_num"]} — vision extraction skipped]'
                p['method'] = 'skipped'
        return pages

    print(f'  Pass 2 — reading {len(image_pages)} diagram pages via Claude vision...')

    with tempfile.TemporaryDirectory() as tmp:
        for page_num in image_pages:
            print(f'    Page {page_num}/{total}...', end=' ', flush=True)
            img = rasterise_page(pdf_path, page_num, IMAGE_DPI, tmp)
            if not img:
                pages[page_num-1].update({'text': f'[Rasterise failed p{page_num}]', 'method': 'error'})
                print('rasterise failed')
                continue
            text = claude_read_image(img, page_num)
            if text:
                pages[page_num-1].update({'text': text, 'method': 'vision'})
                print(f'✓ {len(text.split())}w')
            else:
                pages[page_num-1].update({'text': f'[Blank p{page_num}]', 'method': 'blank'})
                print('blank')
            time.sleep(0.4)

    methods = [p['method'] for p in pages]
    print(f'\n  Summary — text:{methods.count("text")} vision:{methods.count("vision")} blank:{methods.count("blank")} error:{methods.count("error")}')
    return pages

def chunk_pages(pages):
    tokens = []
    for p in pages:
        for word in p['text'].split():
            tokens.append((word, p['page_num']))
    if not tokens:
        return []
    chunks, i, cid = [], 0, 0
    while i < len(tokens):
        sl = tokens[i: i+CHUNK_WORDS]
        sp, ep = sl[0][1], sl[-1][1]
        chunks.append({
            'id': cid, 'text': ' '.join(t[0] for t in sl),
            'start_page': sp, 'end_page': ep,
            'page_label': f'Page {sp}' if sp == ep else f'Pages {sp}-{ep}',
        })
        cid += 1
        i += CHUNK_WORDS - CHUNK_OVERLAP
    return chunks

def embed_and_store(pdf_path, manual_name, force=False):
    print(f'\n{"="*60}\n  Manual: {manual_name}\n  File:   {pdf_path}\n{"="*60}')

    missing = [k for k, v in [('VOYAGE_KEY', VOYAGE_KEY), ('SUPABASE_URL', SUPABASE_URL), ('SUPABASE_SERVICE', SUPABASE_SERVICE)] if not v]
    if missing:
        print(f'✗ Missing: {", ".join(missing)}')
        sys.exit(1)

    if manual_exists(manual_name):
        if force:
            delete_manual(manual_name)
        else:
            ans = input(f'  "{manual_name}" exists. Delete and re-embed? [y/N]: ').strip().lower()
            if ans == 'y':
                delete_manual(manual_name)
            else:
                print('  Aborting.')
                return

    print('\n[1/4] Extracting (two-pass: text + vision)...')
    pages = extract_pages(pdf_path)

    print('\n[2/4] Chunking...')
    chunks = chunk_pages(pages)
    print(f'  {len(chunks)} chunks ({CHUNK_WORDS}w, {CHUNK_OVERLAP}w overlap)')
    if not chunks:
        print('  ✗ No content. Check the file.')
        return

    print(f'\n[3/4] Embedding via Voyage AI...')
    texts = [c['text'] for c in chunks]
    embeddings = []
    total_b = (len(texts) + VOYAGE_BATCH - 1) // VOYAGE_BATCH
    for i in range(0, len(texts), VOYAGE_BATCH):
        batch = texts[i: i+VOYAGE_BATCH]
        bn = i//VOYAGE_BATCH + 1
        print(f'  Batch {bn}/{total_b}...', end=' ', flush=True)
        vecs = voyage_embed(batch)
        embeddings.extend(vecs)
        print('✓')
        time.sleep(0.3)

    print(f'\n[4/4] Storing in Supabase...')
    rows = [{'manual_name': manual_name, 'chunk_index': c['id'],
             'start_page': c['start_page'], 'end_page': c['end_page'],
             'page_label': c['page_label'], 'text': c['text'], 'embedding': e}
            for c, e in zip(chunks, embeddings)]

    stored = 0
    total_sb = (len(rows) + SUPABASE_BATCH - 1) // SUPABASE_BATCH
    for i in range(0, len(rows), SUPABASE_BATCH):
        batch = rows[i: i+SUPABASE_BATCH]
        bn = i//SUPABASE_BATCH + 1
        print(f'  Batch {bn}/{total_sb}...', end=' ', flush=True)
        status = insert_chunks(batch)
        if status in (200, 201, 204):
            stored += len(batch)
            print(f'✓ ({stored}/{len(rows)})')
        else:
            print(f'✗ {status}')
        time.sleep(0.2)

    print(f'\n{"="*60}\n  ✓ {stored} chunks stored for "{manual_name}"\n{"="*60}\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf',           required=True)
    parser.add_argument('--name',          required=True)
    parser.add_argument('--force',         action='store_true')
    parser.add_argument('--voyage-key',    default='')
    parser.add_argument('--anthropic-key', default='')
    parser.add_argument('--supabase-url',  default='')
    parser.add_argument('--supabase-key',  default='')
    args = parser.parse_args()

    if args.voyage_key:    VOYAGE_KEY       = args.voyage_key
    if args.anthropic_key: ANTHROPIC_KEY    = args.anthropic_key
    if args.supabase_url:  SUPABASE_URL     = args.supabase_url
    if args.supabase_key:  SUPABASE_SERVICE = args.supabase_key

    if not os.path.exists(args.pdf):
        print(f'✗ Not found: {args.pdf}')
        sys.exit(1)

    embed_and_store(args.pdf, args.name, force=args.force)
