# Missing Manuals Report — ROV Chatbot Knowledge Base
Generated: 2026-04-22

## Current Supabase State

| Manual | Chunks |
|--------|--------|
| 011-8239.pdf | 295 |
| 8228_Atlas7r Manual.pdf | 36 |
| 914-0601-00-Model914-X-Series_UserManual.pdf | 86 |
| Aleron VP Manual.pdf | 16 |
| H15- GA Top Level & Schematics Manual - TMA01028.pdf | 29 |
| Hercules MK3 Lighting JB with Oceantools Lamps - User Manual OR-TE-03338.pdf | 14 |
| Hercules Mk3.pdf | 3 |
| NIC-OPS-010 - Seven Oceanic Databook.pdf | 99 |
| ROV Master Knowledge v2.pdf | 10 |
| Seven Oceanic ROV HAndbook.pdf | 6 |
| TMA01031 - Control system manual.pdf | 569 |
| TMA01071 - LARS Technical Manual.pdf | 62 |
| **TMA01030 - Interface systems manual.pdf** | **IN PROGRESS** |

**Total currently stored: 1,225 chunks across 12 manuals**

---

## Missing Manuals — 111 Files

Folder: `/Users/seanbrock/Documents/GitHub/rov-chatbot/rov-manual/manuals/`

Classification:
- **TEXT** = pdfplumber extracts ≥30 words — use `--text-only` flag (fast, free)
- **VISION** = no extractable text — requires Claude vision API call per page

---

### GROUP A: TEXT-ONLY (38 files, ~1–3 pages each)
Embed cheaply with `--text-only`. No Claude API credits consumed.

| File | Pages | Words | Size |
|------|-------|-------|------|
| EQP952-0203-DR-PD-54001 - rc updates sketch p2.pdf | 1 | 706 | 62 KB |
| EQP952-0203-DR-PD-54001 - rc updates sketch page 3.pdf | 1 | 327 | 40 KB |
| EQP952-0203-DR-PD-54001 - rc updates sketch.pdf | 1 | 4,021 | 86 KB |
| EQP952-0203-DR-PD-54002 - rc updates sketch p1.pdf | 1 | 6,301 | 93 KB |
| EQP952-0203-DR-PD-54002 - rc updates sketch p2.pdf | 1 | 5,183 | 87 KB |
| EQP952-0203-DR-PD-54002 - rc updates sketch p3.pdf | 1 | 298 | 35 KB |
| EQP952-0203-DR-PD-55000.pdf | 2 | 339 | 558 KB |
| EQP952-0203-DR-PD-55001.pdf | 2 | 389 | 600 KB |
| EQP952-0203-DR-PD-55002.pdf | 2 | 368 | 997 KB |
| EQP952-0203-DR-PD-55003.pdf | 1 | 188 | 224 KB |
| EQP952-0203-DR-PD-55004.pdf | 1 | 183 | 202 KB |
| EQP952-0203-DR-PD-55006.pdf | 1 | 189 | 149 KB |
| EQP952-0203-DR-PD-55007.pdf | 1 | 194 | 163 KB |
| EQP952-0203-DR-PD-55011.pdf | 1 | 192 | 167 KB |
| EQP952-0203-DR-PD-55016.pdf | 3 | 350 | 1,299 KB |
| EQP952-0203-DR-PD-55017.pdf | 3 | 11,759 | 422 KB |
| EQP952-0203-DR-PD-55018.pdf | 1 | 249 | 110 KB |
| EQP952-0203-DR-PD-55019.pdf | 1 | 249 | 112 KB |
| Hercules Tool Tray Skid BOM.pdf | 1 | 582 | 220 KB |
| Hercules Tool Tray Skid hammer head.pdf | 1 | 812 | 176 KB |
| ROV-0226-420-00 SHEET 1.pdf | 1 | 266 | 145 KB |
| ROV-0226-420-01 SHEET 1.pdf | 1 | 680 | 145 KB |
| ROV-0226-420-01 SHEET 2.pdf | 1 | 832 | 176 KB |
| ROV-0226-420-01 SHEET 3.pdf | 1 | 512 | 147 KB |
| ROV-0300-D-0110-02 sht 1 Frame Protection Acetal .pdf | 1 | 78 | 94 KB |
| ROV-0300-D-0440-00 sht 1 rev C9 Hydraulic Diagram.pdf | 1 | 85 | 481 KB |
| ROV-0300-D-0440-00 sht 2 rev C9 Hydraulic Diagram.pdf | 1 | 87 | 497 KB |
| ROV-0300-D-0440-00 sht 3 rev C9 Hydraulic Diagram.pdf | 1 | 78 | 104 KB |
| ROV-0305-D-0630-90 Sht 1-3.pdf | 3 | 209 | 250 KB |
| ROV-0305-D-0660-00.pdf | 1 | 108 | 76 KB |
| ROV-0305-D-0660-90.pdf | 1 | 60 | 63 KB |
| ROV-0311-D-0213-01 SHT 1 .pdf | 1 | 47 | 60 KB |
| SSA-0277-D-0004-00 sht 1 - Amended H15.pdf | 1 | 582 | 210 KB |
| SSA-0277-D-0004-00 sht 1.pdf | 1 | 582 | 210 KB |
| SSA-0277-D-0004-01 SHT 2 commented For order.pdf | 1 | 1,198 | 220 KB |
| SSA-0277-D-0004-01 SHT 2.pdf | 1 | 1,193 | 81 KB |
| SSA-0277-D-0004-01 sht 1.pdf | 1 | 296 | 76 KB |
| SSA-0277-D-0004-14 SHT 1.pdf | 1 | 325 | 104 KB |

---

### GROUP B: LARGE MANUAL WITH MIXED PAGES (1 file)
Full two-pass pipeline (text + vision). Similar size to TMA01028.

| File | Pages | Text Pages | Diagram Pages | Size |
|------|-------|-----------|---------------|------|
| H30 - GA Top Level & Schematics Manual - TMA01029.pdf | 171 | 66 | 105 | 17.2 MB |

Estimated vision calls: ~105 | Estimated time: ~20–30 min | Estimated chunks: 40–60

---

### GROUP C: VISION-ONLY DRAWINGS (72 files)
Pure raster/diagram PDFs — zero extractable text. Each page requires one Claude vision call.

**Total pages across all 72 files: ~92 pages → ~92 vision calls**

| File | Pages | Size |
|------|-------|------|
| HCV-0015-D-0200-00 (1 of 2).pdf | 1 | 128 KB |
| HCV-0015-D-0200-90 (1 of 3).pdf | 2 | 187 KB |
| HCV-0015-D-0200-90 (2 of 3).pdf | 2 | 246 KB |
| HCV-0015-D-0200-90 (3 of 3).pdf | 2 | 213 KB |
| HCV-0015-D-0201-00 (1 of 2).pdf | 2 | 211 KB |
| HCV-0015-D-0201-00 (2 of 2).pdf | 1 | 111 KB |
| HCV-0015-D-0201-90 (1 of 3).pdf | 2 | 204 KB |
| HCV-0015-D-0201-90 (2 of 3).pdf | 2 | 179 KB |
| HCV-0015-D-0201-90 (3 of 3).pdf | 2 | 96 KB |
| HCV-0015-D-0202-00 (1 of 2).pdf | 1 | 83 KB |
| HCV-0015-D-0202-00 (2 of 2).pdf | 1 | 95 KB |
| HCV-0015-D-0300-00 (1 of 2).pdf | 1 | 86 KB |
| HCV-0015-D-0300-00 (2 of 2).pdf | 1 | 90 KB |
| HCV-0015-D-0500-00 (1 of 2).pdf | 1 | 141 KB |
| HCV-0015-D-0500-00 (2 of 2).pdf | 1 | 74 KB |
| HCV-0015-D-0800-90 (1 of 5).pdf | 1 | 114 KB |
| HCV-0015-D-0800-90 (2 of 5).pdf | 1 | 61 KB |
| HCV-0015-D-0800-90 (3 of 5).pdf | 1 | 79 KB |
| HCV-0015-D-0800-90 (4 of 5).pdf | 1 | 88 KB |
| HCV-0015-D-0800-90 (5 of 5).pdf | 2 | 107 KB |
| PDU-1012-D-0007-90 SHT 1 - 2.4KV Transformer Panel Wiring Diagram.pdf | 1 | 191 KB |
| PDU-1012-D-0017-00 SHT 1.pdf | 1 | 940 KB |
| PDU-1012-D-0017-90 SHT 1.pdf | 1 | 1,250 KB |
| ROV-0148-671-04.pdf | 1 | 867 KB |
| ROV-0226-630-90.pdf | 1 | 80 KB |
| ROV-0226-725-00 SHEET 1.pdf | 1 | 650 KB |
| ROV-0226-725-90 SHEET 1.pdf | 1 | 1,026 KB |
| ROV-0249-D-0050-90.pdf | 1 | 62 KB |
| ROV-0300-D-0100-01.pdf | 1 | 65 KB |
| ROV-0300-D-0111-01 T4 mounting plate (stbd).pdf | 1 | 65 KB |
| ROV-0300-D-0420-00 TCU Assembly.pdf | 1 | 179 KB |
| ROV-0300-D-0420-90 TCU Wiring Diagram.pdf | 1 | 101 KB |
| ROV-0300-D-0802-00.pdf | 1 | 69 KB |
| ROV-0300-D-0802-90.pdf | 1 | 61 KB |
| ROV-0305-D-0100-00 (1).pdf | 3 | 432 KB |
| ROV-0305-D-0450-00.PDF | 1 | 92 KB |
| ROV-0305-D-0470-00 sht 1.pdf | 1 | 587 KB |
| ROV-0311-D-0200-90 Pod bottomside network 1 of 1.pdf | 1 | 95 KB |
| ROV-0311-D-0203-00 SHT 1 rc changes sketch.pdf | 1 | 163 KB |
| ROV-0311-D-0203-01 SHT 1 rc updates sketch.pdf | 1 | 54 KB |
| ROV-0311-D-0204-00 SHT 1 rc updates sketch.pdf | 1 | 149 KB |
| ROV-0311-D-0204-01 SHT 1 rc updates sketch.pdf | 1 | 59 KB |
| ROV-0311-D-0206-00 Pod control earth strip plate 1 of 1.pdf | 2 | 1,267 KB |
| ROV-0311-D-0208-00 Pod valve pack unregulated supply.pdf | 2 | 1,360 KB |
| ROV-0311-D-0208-01.pdf | 1 | 394 KB |
| ROV-0311-D-0208-02.pdf | 1 | 393 KB |
| ROV-0311-D-0208-03.pdf | 1 | 318 KB |
| ROV-0311-D-0208-90.pdf | 1 | 397 KB |
| ROV-0311-D-0210-00.pdf | 2 | 1,301 KB |
| ROV-0311-D-0210-01.pdf | 1 | 401 KB |
| ROV-0311-D-0210-02.pdf | 1 | 354 KB |
| ROV-0311-D-0210-03.pdf | 1 | 325 KB |
| ROV-0311-D-0210-04.pdf | 1 | 365 KB |
| ROV-0311-D-0211-00.pdf | 2 | 1,098 KB |
| ROV-0311-D-0211-01.pdf | 1 | 396 KB |
| ROV-0311-D-0212-00.pdf | 2 | 1,377 KB |
| ROV-0311-D-0212-02.pdf | 1 | 326 KB |
| ROV-0311-D-0300-90 sht 1-Model.pdf | 1 | 115 KB |
| ROV-0311-D-0500-00 SHT 1-Model.pdf | 1 | 211 KB |
| ROV-0311-D-0620-90 SHT 1-Model.pdf | 1 | 302 KB |
| ROV-0311-D-0620-90 sht 2-Model.pdf | 1 | 204 KB |
| ROV-0311-D-0680-00.pdf | 2 | 2,081 KB |
| ROV-0311-D-0680-90.pdf | 1 | 661 KB |
| ROV-0311-D-0800-50 SHT 1-Model.pdf | 1 | 111 KB |
| ROV-0311-D-0800-90 SHT 1 - Control Console Wiring.pdf | 1 | 187 KB |
| ROV-0311-D-0800-90 SHT 2 - Control Console Wiring.pdf | 1 | 79 KB |
| ROV-0311-D-0800-90 SHT 3 - Control Console Wiring.pdf | 1 | 182 KB |
| ROV-0311-D-0800-90 SHT 4 - Control Console Wiring.pdf | 1 | 75 KB |
| ROV-0311-D-0800-90 SHT 5 - Control Console Wiring.pdf | 1 | 68 KB |
| SSA-0277-D-0004-16 Forward Buoyancy 450kgm3.pdf | 1 | 82 KB |
| SSA-0277-D-0004-17 Middle Buoyancy 450kgm3.pdf | 1 | 57 KB |
| tcu.pdf | 5 | 1,344 KB |

---

## Optimised Upload Plan

### Phase 1 — Text-Only Batch (38 files)
**Estimated time: ~10–15 minutes | Claude API cost: $0.00**

Run `batch_upload_phase1.sh`. All 38 files have vector text layers — pdfplumber extracts them directly. No Claude vision API credits consumed. Only Voyage AI embedding cost (~$0.0006/chunk × ~80 estimated chunks = ~$0.05).

### Phase 2 — H30 Full Manual (171 pages)
**Estimated time: 20–30 minutes | Claude API cost: ~$0.50–1.50 (105 vision calls)**

H30 is the Hercules MK3 H30 GA manual — similar in structure to TMA01028 (already embedded). Run `batch_upload_phase2.sh`. Do this during a period when you can monitor it in case of credit issues.

### Phase 3 — Vision Drawing Batch (72 files, ~92 pages)
**Estimated time: ~20–30 minutes | Claude API cost: ~$0.50–1.50 (92 vision calls)**

72 engineering drawings with zero text layers — each page requires one Claude vision call. Run `batch_upload_phase3.sh`. Each file is 1–2 pages so each completes in seconds. The full batch can be left to run unattended.

### Total Estimated Cost
- Voyage AI: ~$0.10–0.20 (all chunks)
- Claude vision: ~$1.00–3.00 (197 vision calls: 105 for H30 + 92 for drawings)
- **Total: ~$1.10–3.20**

### Total Estimated Time (sequential)
- Phase 1: 15 min
- Phase 2: 30 min
- Phase 3: 30 min
- **Total: ~75 minutes** (can overlap Phase 2+3 if running two terminals)

---

## Notes

- TMA01030 (679 pages) re-embed currently in progress as of report generation
- `ROV Master Knowledge v2.pdf` is in Supabase (10 chunks) but its source PDF is not in the manuals folder — this is expected (manually created knowledge document)
- SSA-0277-D-0004-00 sht 1.pdf and SSA-0277-D-0004-00 sht 1 - Amended H15.pdf appear to be two versions of the same drawing (same word count, same size) — both will be embedded separately under their own filename
