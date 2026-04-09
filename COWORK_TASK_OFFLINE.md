# COWORK TASK — Make ROV Manual Fully Offline (No Server, No Internet)

## YOUR MISSION
Convert `rov-manual/index.html` from a server-dependent app into a single 
fully standalone HTML file that opens directly from a Windows network drive 
in Edge with zero internet and zero web server required.

## REPO
github.com/Seanbrock100/rov-chatbot
Working directory: `rov-manual/`

---

## BACKGROUND (read before starting)

The manual currently has TWO external dependencies that break on file://

### Problem 1 — pdf.js loaded from CDN
In the <head>:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
```
And in renderRingPDF():
```js
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
```
These fail with no internet. The ring GA PDF won't render.

### Problem 2 — descriptions_norm.json loaded via fetch()
```js
fetch('descriptions_norm.json').then(r => r.json()).then(d => {
  DESCRIPTIONS = d;
```
`fetch()` is blocked on file:// protocol (CORS). Descriptions won't load.
Card clicks will show the fallback message instead of AI descriptions.

---

## WHAT YOU MUST DO

### Fix 1 — Embed descriptions_norm.json inline
Replace the fetch() call with the JSON data embedded directly as a JS variable.

Current code (lines ~622-627 in index.html):
```js
let DESCRIPTIONS = {};
fetch('descriptions_norm.json').then(r => r.json()).then(d => {
  DESCRIPTIONS = d;
  console.log('Descriptions loaded:', Object.keys(d).length, 'entries');
}).catch(e => console.warn('descriptions_norm.json not found:', e));
```

Replace with:
```js
const DESCRIPTIONS = << PASTE FULL CONTENTS OF descriptions_norm.json HERE AS A JS OBJECT LITERAL >>;
```

To do this: read `rov-manual/descriptions_norm.json`, parse it, and write its 
contents directly into index.html as a const assignment. The file is ~108KB 
of JSON. Result will be something like:
```js
const DESCRIPTIONS = {
  "control_chassis/psu 1 - sle124": "The PSU 1...",
  "control_chassis/psu 2 - sle112": "The PSU 2...",
  ... all 53 entries ...
};
```

### Fix 2 — Download pdf.js and embed it locally
Download these two files from cdnjs and save them into rov-manual/manuals/:
- https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js
  → save as: rov-manual/manuals/pdf.min.js
- https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js
  → save as: rov-manual/manuals/pdf.worker.min.js

Then update index.html:

Change the <head> script tag from:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
```
To:
```html
<script src="manuals/pdf.min.js"></script>
```

Change the workerSrc line in renderRingPDF() from:
```js
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
```
To:
```js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'manuals/pdf.worker.min.js';
```

---

## VERIFICATION STEPS (you must check all of these)

1. **JS parses cleanly** — run this check after every edit:
```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('rov-manual/index.html', 'utf8');
const s = html.lastIndexOf('<script>');
const e = html.lastIndexOf('</script>');
try { new Function(html.slice(s+8, e)); console.log('PARSE OK'); }
catch(err) { console.log('PARSE ERROR:', err.message); }
"
```

2. **Descriptions embedded** — confirm the JSON data is inline:
```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('rov-manual/index.html', 'utf8');
const match = html.match(/const DESCRIPTIONS = \{/);
console.log('Descriptions inline:', !!match);
const count = (html.match(/control_chassis\//g)||[]).length;
console.log('Control chassis entries visible:', count);
"
```

3. **pdf.js local** — confirm the CDN URLs are gone:
```bash
grep -c "cdnjs.cloudflare.com" rov-manual/index.html
# Must output: 0
```

4. **pdf.js files exist**:
```bash
ls -lh rov-manual/manuals/pdf.min.js rov-manual/manuals/pdf.worker.min.js
# Both files must exist, each roughly 300-900KB
```

5. **No fetch() calls remain**:
```bash
grep "fetch(" rov-manual/index.html
# Must return nothing
```

6. **File size check** — the final index.html should be larger than before 
   (because descriptions JSON is now inline):
```bash
wc -c rov-manual/index.html
# Original was 107341 bytes. Should now be ~215000+ bytes
```

---

## COMMIT WHEN DONE
```bash
cd /Users/seanbrock/Documents/GitHub/rov-chatbot
git add rov-manual/index.html rov-manual/manuals/pdf.min.js rov-manual/manuals/pdf.worker.min.js
git commit -m "Manual: fully offline — embed descriptions inline, bundle pdf.js locally"
git push origin main
```

---

## WHAT NOT TO TOUCH
- Do NOT modify any drawing file paths
- Do NOT modify POD_ZONES data or card definitions
- Do NOT modify CSS, HTML structure, or any visual layout
- Do NOT modify buildChassisSVG, openCardInfo, or fetchCardDescription logic
- Do NOT add any new dependencies
- The ONLY changes are: inline the JSON, localise pdf.js

---

## EXPECTED FINAL STATE
- `rov-manual/index.html` — larger file, self-contained, no CDN, no fetch()
- `rov-manual/manuals/pdf.min.js` — pdf.js library (local copy)
- `rov-manual/manuals/pdf.worker.min.js` — pdf.js worker (local copy)
- Opening index.html directly from a Windows network drive in Edge works 
  with zero internet connection and zero web server
