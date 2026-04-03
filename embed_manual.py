#!/usr/bin/env python3
"""
embed_manual.py — ROV Manual Embedding Script
==============================================
Embeds any ROV technical manual PDF into Supabase.

Handles BOTH text-based and image-based PDFs:
  - Text extraction via pdfplumber (fast, free)
  - If page is blank/sparse (<30 words), rasterises with pdftoppm and reads via Claude vision

Usage:
  python embed_manual.py --pdf "TMA01028.pdf" --name "TMA01028 H15 GA Schematics"

Requirements:
  pip install pdfplumber requests pillow
  apt install poppler-utils   (or: brew install poppler on Mac)

Environment variables (or edit CONSTANTS below):
  VOYAGE_KEY         — Voyage AI key
  ANTHROPIC_KEY      — Anthropic key (needed for image pages)
  SUPABASE_URL       — https://ccjurdnubkmeepaztomy.supabase.co
  SUPABASE_SERVICE   — Supabase service role key
"""

import os
import sys
import json
import base64
import argparse
import time
import tempfile
import subprocess
from pathlib import Path

import requests

try:
    import pdfplumber
except ImportError:
    print("Missing: pip install pdfplumber")
    sys.exit(1)

# ── Constants — override via env vars ────────────────────────────────────────
VOYAGE_KEY       = os.environ.get('VOYAGE_KEY', '')
ANTHROPIC_KEY    = os.environ.get('ANTHROPIC_KEY', '')
SUPABASE_URL     = os.environ.get('SUPABASE_URL', 'https://ccjurdnubkmeepaztomy.supabase.co')
SUPABASE_SERVICE = os.environ.get('SUPABASE_SERVICE', '')

CHUNK_WORDS    = 350    # target words per chunk
CHUNK_OVERLAP  = 50     # overlap between chunks
MIN_WORDS      = 30     # pages below this threshold get rasterised
VOYAGE_BATCH   = 8      # embeddings per Voyage API call
SUPABASE_BATCH = 50     # rows per Supabase insert
IMAGE_DPI      = 120    # rasterisation DPI (120 is sufficient for text extraction)

VOYAGE_MODEL   = 'voyage-large-2'
EMBED_DIM      = 1536

ANTHROPIC_MODEL = 'claude-opus-4-20250514'  # vision capable


# ── Supabase helpers ─────────────────────────────────────────────────────────
def sb_headers(service=True):
    key = SUPABASE_SERVICE if service else SUPABASE_SERVICE
    return {
        'apikey':        key,
        'Authorization': f'Bearer {key}',
        'Content-Type':  'application/json',
        'Prefer':        'return=minimal',
    }


def manual_exists(name: str) -> bool:
    """Check whether this manual name is already in Supabase."""
    res = requests.get(
        f'{SUPABASE_URL}/rest/v1/chunks',
        headers=sb_headers(),
        params={'manual_name': f'eq.{name}', 'limit': '1', 'select': 'id'},
        timeout=15,
    )
    data = res.json()
    return isinstance(data, list) and len(data) > 0


def delete_manual(name: str):
    """Remove all existing chunks for this manual name."""
    print(f'  Deleting existing chunks for "{name}"...')
    res = requests.delete(
        f'{SUPABASE_URL}/rest/v1/chunks',
        headers=sb_headers(),
        params={'manual_name': f'eq.{name}'},
        timeout=30,
    )
    print(f'  Delete status: {res.status_code}')


def insert_chunks(rows: list):
    """Insert a batch of chunk rows into Supabase."""
    res = requests.post(
        f'{SUPABASE_URL}/rest/v1/chunks',
        headers=sb_headers(),
        json=rows,
        timeout=60,
    )
    if res.status_code not in (200, 201, 204):
        print(f'  ⚠ Supabase insert error {res.status_code}: {res.text[:200]}')
    return res.status_code


# ── Voyage AI embeddings ──────────────────────────────────────────────────────
def voyage_embed(texts: list[str], input_type: str = 'document') -> list[list[float]]:
    """Embed a batch of texts. Returns list of 1536-dim vectors."""
    res = requests.post(
        'https://api.voyageai.com/v1/embeddings',
        headers={
            'Authorization': f'Bearer {VOYAGE_KEY}',
            'Content-Type':  'application/json',
        },
        json={'model': VOYAGE_MODEL, 'input': texts, 'input_type': input_type},
        timeout=60,
    )
    if res.status_code != 200:
        raise RuntimeError(f'Voyage API error {res.status_code}: {res.text[:300]}')
    data = res.json()
    return [item['embedding'] for item in data['data']]


# ── Claude vision — extract text from image ───────────────────────────────────
def claude_read_image(image_path: str, page_num: int) -> str:
    """
    Send a rasterised page image to Claude and extract readable text.
    Returns extracted text or empty string if page appears blank.
    """
    with open(image_path, 'rb') as f:
        image_b64 = base64.b64encode(f.read()).decode()

    prompt = (
        f"This is page {page_num} of an ROV technical manual (Hercules MK3 work-class ROV). "
        "Extract all readable text from this image. "
        "Include component labels, connector names, drawing numbers, part numbers, wire labels, "
        "and any table content. Preserve the structure where possible. "
        "If the page is a blank title page or contains only a logo/border with no meaningful content, "
        "reply with exactly: BLANK_PAGE"
    )

    res = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key':         ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01',
            'Content-Type':      'application/json',
        },
        json={
            'model':      ANTHROPIC_MODEL,
            'max_tokens': 2000,
            'messages': [{
                'role': 'user',
                'content': [
                    {
                        'type':   'image',
                        'source': {
                            'type':       'base64',
                            'media_type': 'image/jpeg',
                            'data':       image_b64,
                        },
                    },
                    {'type': 'text', 'text': prompt},
                ],
            }],
        },
        timeout=60,
    )

    if res.status_code != 200:
        print(f'    ⚠ Claude vision error page {page_num}: {res.status_code}')
        return ''

    text = res.json()['content'][0]['text'].strip()
    if text == 'BLANK_PAGE':
        return ''
    return text


# ── Rasterise one page via pdftoppm ──────────────────────────────────────────
def rasterise_page(pdf_path: str, page_num: int, dpi: int, out_dir: str) -> str | None:
    """
    Rasterise a single page (1-indexed) to JPEG using pdftoppm.
    Returns path to JPEG file or None on failure.
    """
    # pdftoppm uses 0-indexed first/last page flags: -f and -l
    cmd = [
        'pdftoppm',
        '-jpeg',
        '-r', str(dpi),
        '-f', str(page_num),
        '-l', str(page_num),
        pdf_path,
        os.path.join(out_dir, f'page_{page_num:04d}'),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'    ⚠ pdftoppm failed page {page_num}: {result.stderr[:100]}')
        return None

    # pdftoppm appends -1.jpg (or zero-padded)
    for suffix in ['-1.jpg', '-01.jpg', '-001.jpg', '-0001.jpg']:
        path = os.path.join(out_dir, f'page_{page_num:04d}{suffix}')
        if os.path.exists(path):
            return path

    # Fallback: find any jpeg in dir matching our prefix
    prefix = f'page_{page_num:04d}'
    for f in os.listdir(out_dir):
        if f.startswith(prefix) and f.endswith('.jpg'):
            return os.path.join(out_dir, f)

    return None


# ── PDF text extraction ───────────────────────────────────────────────────────
def extract_pages(pdf_path: str) -> list[dict]:
    """
    Extract text from all pages.
    Pages below MIN_WORDS threshold are rasterised and sent to Claude.
    Returns list of {page_num, text, method} dicts.
    """
    pages = []
    pdf = pdfplumber.open(pdf_path)
    total = len(pdf.pages)
    print(f'\n  {total} pages found in PDF')

    image_pages = []
    text_pages  = []

    # First pass — extract text
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ''
        words = len(text.split())
        if words >= MIN_WORDS:
            pages.append({'page_num': i, 'text': text, 'method': 'text'})
            text_pages.append(i)
        else:
            pages.append({'page_num': i, 'text': '', 'method': 'pending_image'})
            image_pages.append(i)

    pdf.close()

    print(f'  Text extracted: {len(text_pages)} pages')
    print(f'  Image pages to rasterise: {len(image_pages)} pages')

    if not image_pages:
        return pages

    # Second pass — rasterise and read image pages
    if not ANTHROPIC_KEY:
        print('  ⚠ No ANTHROPIC_KEY — skipping image pages (set key to extract schematic text)')
        for p in pages:
            if p['method'] == 'pending_image':
                p['text'] = f'[Image page {p["page_num"]} — text extraction skipped]'
                p['method'] = 'skipped'
        return pages

    with tempfile.TemporaryDirectory() as tmp:
        for page_num in image_pages:
            print(f'  → Rasterising page {page_num}/{total}...', end=' ', flush=True)
            img_path = rasterise_page(pdf_path, page_num, IMAGE_DPI, tmp)
            if not img_path:
                pages[page_num - 1]['text'] = f'[Rasterisation failed page {page_num}]'
                pages[page_num - 1]['method'] = 'error'
                print('rasterise failed')
                continue

            text = claude_read_image(img_path, page_num)
            if text:
                pages[page_num - 1]['text'] = text
                pages[page_num - 1]['method'] = 'vision'
                print(f'extracted {len(text.split())} words')
            else:
                pages[page_num - 1]['text'] = f'[Blank page {page_num}]'
                pages[page_num - 1]['method'] = 'blank'
                print('blank')

            # Small delay to avoid Claude rate limits on large PDFs
            time.sleep(0.5)

    return pages


# ── Chunking ──────────────────────────────────────────────────────────────────
def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Flatten page text into overlapping word-level chunks.
    Each chunk records start_page and end_page for citation.
    """
    chunks = []

    # Build token list: (word, page_num)
    tokens = []
    for p in pages:
        words = p['text'].split()
        for w in words:
            tokens.append((w, p['page_num']))

    if not tokens:
        return []

    i = 0
    chunk_id = 0
    while i < len(tokens):
        slice_tokens = tokens[i: i + CHUNK_WORDS]
        text       = ' '.join(t[0] for t in slice_tokens)
        start_page = slice_tokens[0][1]
        end_page   = slice_tokens[-1][1]
        label      = f'Page {start_page}' if start_page == end_page else f'Pages {start_page}–{end_page}'

        chunks.append({
            'id':          chunk_id,
            'text':        text,
            'start_page':  start_page,
            'end_page':    end_page,
            'label':       label,
        })
        chunk_id += 1
        i += CHUNK_WORDS - CHUNK_OVERLAP

    return chunks


# ── Main pipeline ─────────────────────────────────────────────────────────────
def embed_and_store(pdf_path: str, manual_name: str, force: bool = False):
    print(f'\n{"="*60}')
    print(f'  Manual:  {manual_name}')
    print(f'  File:    {pdf_path}')
    print(f'{"="*60}')

    # Validate keys
    missing = []
    if not VOYAGE_KEY:       missing.append('VOYAGE_KEY')
    if not SUPABASE_URL:     missing.append('SUPABASE_URL')
    if not SUPABASE_SERVICE: missing.append('SUPABASE_SERVICE')
    if missing:
        print(f'\n✗ Missing environment variables: {", ".join(missing)}')
        sys.exit(1)

    # Check for existing data
    if manual_exists(manual_name):
        if force:
            delete_manual(manual_name)
        else:
            print(f'\n  "{manual_name}" already exists in Supabase.')
            ans = input('  Delete and re-embed? [y/N]: ').strip().lower()
            if ans == 'y':
                delete_manual(manual_name)
            else:
                print('  Aborting.')
                return

    # Extract text
    print('\n[1/4] Extracting text from PDF...')
    pages = extract_pages(pdf_path)
    non_blank = [p for p in pages if p['text'] and 'Blank' not in p['text'][:10]]
    print(f'  Extracted text from {len(non_blank)}/{len(pages)} pages')

    # Chunk
    print('\n[2/4] Chunking...')
    chunks = chunk_pages(pages)
    print(f'  Created {len(chunks)} chunks ({CHUNK_WORDS} words, {CHUNK_OVERLAP} overlap)')

    if not chunks:
        print('  ✗ No text extracted from this PDF. Check the file and try again.')
        return

    # Embed
    print(f'\n[3/4] Embedding via Voyage AI ({VOYAGE_MODEL})...')
    texts = [c['text'] for c in chunks]
    embeddings = []
    total_batches = (len(texts) + VOYAGE_BATCH - 1) // VOYAGE_BATCH

    for batch_i in range(0, len(texts), VOYAGE_BATCH):
        batch_texts = texts[batch_i: batch_i + VOYAGE_BATCH]
        batch_num   = batch_i // VOYAGE_BATCH + 1
        print(f'  Batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)...', end=' ', flush=True)
        try:
            vecs = voyage_embed(batch_texts, input_type='document')
            embeddings.extend(vecs)
            print(f'✓ dim={len(vecs[0])}')
        except Exception as e:
            print(f'✗ ERROR: {e}')
            raise
        time.sleep(0.3)  # rate limit headroom

    print(f'  Total embeddings: {len(embeddings)}')

    # Store
    print(f'\n[4/4] Storing in Supabase ({SUPABASE_BATCH} rows/batch)...')
    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append({
            'manual_name': manual_name,
            'chunk_index': chunk['id'],
            'start_page':  chunk['start_page'],
            'end_page':    chunk['end_page'],
            'page_label':  chunk['label'],
            'text':        chunk['text'],
            'embedding':   embedding,
        })

    total_stored = 0
    for batch_i in range(0, len(rows), SUPABASE_BATCH):
        batch = rows[batch_i: batch_i + SUPABASE_BATCH]
        batch_num = batch_i // SUPABASE_BATCH + 1
        total_batches_sb = (len(rows) + SUPABASE_BATCH - 1) // SUPABASE_BATCH
        print(f'  Batch {batch_num}/{total_batches_sb}...', end=' ', flush=True)
        status = insert_chunks(batch)
        if status in (200, 201, 204):
            total_stored += len(batch)
            print(f'✓ ({total_stored}/{len(rows)})')
        else:
            print(f'✗ status {status}')
        time.sleep(0.2)

    print(f'\n{"="*60}')
    print(f'  ✓ Complete: {total_stored} chunks stored for "{manual_name}"')
    print(f'{"="*60}\n')


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Embed ROV manual PDF into Supabase')
    parser.add_argument('--pdf',   required=True, help='Path to PDF file')
    parser.add_argument('--name',  required=True, help='Manual name (stored in Supabase)')
    parser.add_argument('--force', action='store_true', help='Delete and re-embed without prompting')

    # Allow inline key override without env vars
    parser.add_argument('--voyage-key',    default='', help='Voyage AI key (or set VOYAGE_KEY env var)')
    parser.add_argument('--anthropic-key', default='', help='Anthropic key (or set ANTHROPIC_KEY env var)')
    parser.add_argument('--supabase-url',  default='', help='Supabase URL')
    parser.add_argument('--supabase-key',  default='', help='Supabase service key')

    args = parser.parse_args()

    # CLI args override env vars
    if args.voyage_key:    VOYAGE_KEY       = args.voyage_key
    if args.anthropic_key: ANTHROPIC_KEY    = args.anthropic_key
    if args.supabase_url:  SUPABASE_URL     = args.supabase_url
    if args.supabase_key:  SUPABASE_SERVICE = args.supabase_key

    if not os.path.exists(args.pdf):
        print(f'✗ File not found: {args.pdf}')
        sys.exit(1)

    embed_and_store(args.pdf, args.name, force=args.force)
