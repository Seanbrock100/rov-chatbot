#!/usr/bin/env python3
"""
Embed new PDFs from manuals/ into Supabase chunks table.
Skips files already embedded. Runs via Cowork overnight.

Usage: python3 embed_new_files.py
Logs:  /tmp/embed_new_files.log
"""

import os, sys, json, time, logging, hashlib
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/tmp/embed_new_files.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────────────────────
MANUALS_DIR   = os.path.join(os.path.dirname(__file__), 'rov-manual', 'manuals')
CONFIG_URL    = 'https://rov-chatbot-production-3d66.up.railway.app/api/config'
CHUNK_SIZE    = 800    # characters per chunk
CHUNK_OVERLAP = 100    # overlap between chunks
MAX_FILE_MB   = 150    # skip files larger than this
SLEEP_BETWEEN = 0.3    # seconds between API calls

# ── LOAD CONFIG ───────────────────────────────────────────────────────────────
log.info("Loading config from Railway...")
cfg = requests.get(CONFIG_URL, timeout=15).json()
SB_URL  = cfg['supabaseUrl']
SB_SVC  = cfg['supabaseService']   # service key for write access
VOYAGE  = cfg['voyageKey']

SB_HEADERS = {
    'apikey':        SB_SVC,
    'Authorization': 'Bearer ' + SB_SVC,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal'
}

# ── GET ALREADY-EMBEDDED FILES ────────────────────────────────────────────────
log.info("Fetching already-embedded filenames from Supabase...")
r = requests.get(
    SB_URL + '/rest/v1/chunks?select=manual_name&limit=10000',
    headers={**SB_HEADERS, 'Prefer': ''},
    timeout=30
)
embedded_raw = {row['manual_name'] for row in r.json()}

# Normalise — strip prefixes like "LARS - ", "Winch H15 - " etc
def normalise_name(name):
    for prefix in ['Control Room - ', 'LARS - ', 'ROV Lights - ',
                   'Winch H15 - ', 'Winch H30 - ',
                   'IXBlue Octans Nano Gyro - ', 'Munk Crane - ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    if not name.lower().endswith('.pdf'):
        name += '.pdf'
    return name

embedded_files = {normalise_name(n).lower() for n in embedded_raw}
log.info(f"Already embedded: {len(embedded_files)} files")

# ── GET ALL PDFs IN MANUALS/ ──────────────────────────────────────────────────
all_pdfs = sorted([
    f for f in os.listdir(MANUALS_DIR)
    if f.lower().endswith('.pdf') or f.endswith('.PDF')
])
log.info(f"Total PDFs in manuals/: {len(all_pdfs)}")

to_embed = [
    f for f in all_pdfs
    if f.lower() not in embedded_files
]
log.info(f"Files to embed: {len(to_embed)}")

# ── HELPER: EXTRACT TEXT FROM PDF ────────────────────────────────────────────
def extract_text(path):
    """Extract text from PDF using pdfminer (best for searchable PDFs)."""
    try:
        from pdfminer.high_level import extract_text as pm_extract
        text = pm_extract(path)
        if text and len(text.strip()) > 50:
            return text
    except Exception:
        pass
    # Fallback: pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        pages = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ''
            if t.strip():
                pages.append(f"[Page {i+1}]\n{t}")
        return '\n\n'.join(pages)
    except Exception as e:
        log.warning(f"  PDF extract failed: {e}")
        return ''

# ── HELPER: CHUNK TEXT ────────────────────────────────────────────────────────
def chunk_text(text, filename):
    """Split text into overlapping chunks with page labels."""
    chunks = []
    # Split by page markers first
    import re
    pages = re.split(r'\[Page (\d+)\]', text)
    
    if len(pages) > 1:
        # Has page markers — chunk per page, merge small ones
        current = ''
        current_page = 1
        i = 1
        while i < len(pages):
            page_num = int(pages[i]) if pages[i].isdigit() else current_page
            page_text = pages[i+1] if i+1 < len(pages) else ''
            i += 2
            if page_text.strip():
                current += page_text + '\n'
                current_page = page_num
                if len(current) >= CHUNK_SIZE:
                    chunks.append({
                        'text': current.strip(),
                        'page_label': f'Page {current_page}'
                    })
                    current = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else ''
        if current.strip():
            chunks.append({'text': current.strip(), 'page_label': f'Page {current_page}'})
    else:
        # No page markers — chunk by character count
        text = text.strip()
        pos = 0
        chunk_num = 1
        while pos < len(text):
            end = min(pos + CHUNK_SIZE, len(text))
            chunk = text[pos:end]
            if chunk.strip():
                chunks.append({
                    'text': chunk,
                    'page_label': f'Chunk {chunk_num}'
                })
                chunk_num += 1
            pos += CHUNK_SIZE - CHUNK_OVERLAP
    
    return chunks

# ── HELPER: GET EMBEDDING ─────────────────────────────────────────────────────
def get_embedding(text):
    """Get voyage-3-lite embedding for text."""
    r = requests.post(
        'https://api.voyageai.com/v1/embeddings',
        headers={'Authorization': 'Bearer ' + VOYAGE, 'Content-Type': 'application/json'},
        json={'input': text[:4000], 'model': 'voyage-large-2'},
        timeout=30
    )
    r.raise_for_status()
    return r.json()['data'][0]['embedding']

# ── HELPER: INSERT CHUNKS ─────────────────────────────────────────────────────
def insert_chunk(manual_name, chunk_index, page_label, text, embedding):
    payload = {
        'manual_name': manual_name,
        'chunk_index': chunk_index,
        'page_label':  page_label,
        'text':        text,
        'embedding':   embedding
    }
    r = requests.post(
        SB_URL + '/rest/v1/chunks',
        headers=SB_HEADERS,
        json=payload,
        timeout=15
    )
    if r.status_code not in (200, 201):
        log.error(f"  Insert failed: {r.status_code} {r.text[:100]}")
        return False
    return True

# ── MAIN EMBED LOOP ───────────────────────────────────────────────────────────
log.info("=" * 60)
log.info(f"Starting embed run: {len(to_embed)} files to process")
log.info("=" * 60)

done = 0
skipped = 0
errors = 0

for i, filename in enumerate(to_embed):
    path = os.path.join(MANUALS_DIR, filename)
    size_mb = os.path.getsize(path) / 1024 / 1024
    
    log.info(f"[{i+1}/{len(to_embed)}] {filename} ({size_mb:.1f}MB)")
    
    # Skip very large files
    if size_mb > MAX_FILE_MB:
        log.warning(f"  SKIP: Too large ({size_mb:.1f}MB > {MAX_FILE_MB}MB)")
        skipped += 1
        continue
    
    # Extract text
    text = extract_text(path)
    if not text or len(text.strip()) < 30:
        log.warning(f"  SKIP: No extractable text (likely scanned/image PDF)")
        skipped += 1
        continue
    
    log.info(f"  Extracted {len(text):,} chars")
    
    # Chunk
    chunks = chunk_text(text, filename)
    if not chunks:
        log.warning(f"  SKIP: No chunks produced")
        skipped += 1
        continue
    
    log.info(f"  {len(chunks)} chunks")
    
    # Embed and insert each chunk
    chunk_errors = 0
    for ci, chunk in enumerate(chunks):
        try:
            emb = get_embedding(chunk['text'])
            ok  = insert_chunk(filename, ci, chunk['page_label'], chunk['text'], emb)
            if not ok:
                chunk_errors += 1
            time.sleep(SLEEP_BETWEEN)
        except Exception as e:
            log.error(f"  Chunk {ci} error: {e}")
            chunk_errors += 1
            time.sleep(1)
    
    if chunk_errors == 0:
        log.info(f"  ✓ Done — {len(chunks)} chunks embedded")
        done += 1
    else:
        log.warning(f"  ⚠ Done with {chunk_errors} chunk errors")
        errors += 1

log.info("=" * 60)
log.info(f"COMPLETE: {done} files embedded, {skipped} skipped, {errors} with errors")
log.info("=" * 60)
