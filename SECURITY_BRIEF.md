# Security Brief — Hercules MK3 ROV Manual

**For:** Claude Designer session, or any AI / engineer working on this project
**Snapshot date:** 13 May 2026
**Companion to:** `PROJECT_STATUS.md`, `SESSION_HANDOFF.md`, `DRAWING_INDEX.md`, `FILE_INVENTORY.md`

> Read this BEFORE proposing any change that touches `app.py`, the chatbot fetch flow in `index.html`, environment variables, or the password overlay. Everything else is fair game.

---

## Why this brief exists

This project went through a focused security session on 13 May 2026. Before that day, `GET /api/config` on the Railway proxy was returning the Anthropic API key, Voyage API key, and the Supabase service role JWT in cleartext to anyone who hit the URL. That has now been fixed, with two password gates added, server-side proxy hardening, and key rotation. **But there are decisions and constraints from that session that shouldn't be casually undone.**

If you're reading this with a UI/UX hat on, the punchline is: **the password overlay UI is yours to redesign, the security mechanism behind it is not.** Same for the admin overlay.

---

## What's protected and how

### Two-gate architecture

| Gate | Env var | Where validated | Persistence | When prompted |
|---|---|---|---|---|
| App-wide | `APP_PASSWORD` | Flask `/api/auth` using `hmac.compare_digest` | `sessionStorage` (cleared on browser exit) | Once per browser session, on page load |
| Admin only | `ADMIN_PASSWORD` | Flask `/api/admin-auth` using `hmac.compare_digest` | **Never persisted** | Every time the admin overlay opens |

### Default behaviours when env vars are unset

Asymmetric and intentional:

- `APP_PASSWORD` unset → app **bypasses** the gate (dev mode, useful for local testing)
- `ADMIN_PASSWORD` unset → admin **denies by default** (destructive operations must never silently grant access)

### What's behind each gate

- **App gate** protects every paid-API proxy call: `/anthropic/messages` (chatbot), `/voyage/embeddings` (query embedding), `/supabase/<path>` (any service-role-requiring write). All require `X-App-Password` header.
- **Admin gate** protects destructive admin overlay operations: move/remove drawings, save `data_patch.js`, etc. The frontend currently calls `/api/admin-auth` and only displays admin UI on success.

### What's deliberately NOT behind a gate

- `GET /api/config` — has to be reachable so the browser can learn whether to prompt for a password. Returns only public-by-design values: `supabaseUrl`, `supabaseAnon`, `passwordRequired`, `adminRequired`. **No secrets.**
- Direct browser → Supabase reads using the anon key (`chat_log` writes, `card_index` lookup, `match_chunks` RPC, `lookup_drawing_family` RPC). The anon key is public-by-design.

### Why direct Supabase reads stay direct (not proxied)

Tempting to think every Supabase call should go through Flask for "consistency". Don't. Reasons:
1. Direct anon-key reads are ~300ms faster (no Flask round-trip on Railway free tier)
2. Anon key is public-by-design — proxying adds no security value
3. The chatbot's perceived responsiveness depends on `match_chunks` being fast
4. The Supabase anon key is what's returned by `/api/config` precisely so the browser can use it directly

If you want to move all Supabase access behind the app gate later, that's a defensible architectural call, but it's a perf trade-off, not a security improvement.

---

## What's accepted residual risk — tracked tech debt

**The `SUPABASE_SERVICE` JWT was NOT rotated on 13 May 2026.** Why:

Supabase has deprecated the simple legacy "regenerate JWT secret" rotation. The current rotation path requires migrating from `anon` / `service_role` JWTs to the new `sb_publishable` / `sb_secret` keys. That migration needs code changes in both `app.py` and `index.html` (~5-6 locations where direct Supabase calls construct `Authorization: Bearer` headers that the new keys reject).

Deferred deliberately to avoid mixing big code changes with a focused security pass while parallel design work was running. **Risk accepted:** anyone who captured the `service_role` JWT from `/api/config` before 13 May 2026 can still use it to bypass RLS and read/write/delete any row in any Supabase table. The leak window is closed (no new exposure) but the captured-key risk remains until full migration.

**If you're considering Supabase-related changes:** see `PROJECT_STATUS.md` → "Tracked tech debt — Supabase key migration" for the full migration scope. Don't try to be clever and rotate just the service_role JWT — the dashboard no longer supports it independently.

---

## What we learned today (and you shouldn't have to)

**Railway env var changes auto-trigger a redeploy — but from whatever source Railway has cached, not necessarily from the latest GitHub commit.**

On 13 May, the Railway-GitHub integration had silently lost its `main` branch connection over a week earlier. Every push to GitHub was being ignored. When `APP_PASSWORD` and rotated API keys were added to Railway env vars, Railway dutifully redeployed — but from a stale cached snapshot of the codebase, not from the latest commit. Result: the brand-new keys were leaked again through the old `/api/config` response shape that should have been replaced by the security fix.

**Operational takeaway:** after any Railway env var change OR git push, verify Railway is serving the EXPECTED commit:

```bash
curl -s https://rov-chatbot-production-3d66.up.railway.app/health | python3 -m json.tool
```

The `/health` shape changes when the code changes. If you add a new field to `/health` and your curl shows the old shape, Railway is serving stale code regardless of what its dashboard says.

The Source / Branch connection is at: Railway → Project → Settings → Source. Confirm `Seanbrock100/rov-chatbot` + branch `main` + auto-deploy enabled.

---

## Hard constraints — preserve these in any redesign

If a proposed change touches any of these, stop and confirm with Sean before implementing:

1. **`/api/config` MUST NEVER return Anthropic, Voyage, or Supabase service keys.** Adding "convenience" passthrough is the original bug. If a future frontend feature seems to need it, the right answer is a new gated proxy route, not loosening `/api/config`.
2. **`hmac.compare_digest` for password comparison.** Don't replace with `==` even if it "looks cleaner". The constant-time property is the point.
3. **Service role key never reaches the browser.** Even temporarily, even "for debugging". Any service-role-requiring Supabase write goes through `/supabase/<path>` proxy with `X-App-Password` header.
4. **App password is the same on every request.** Don't add per-user sessions, JWT issuing, or any complexity. This is a vessel tool with a shared crew password — overengineering would just create new failure modes.
5. **Admin password is never persisted client-side.** The re-prompt-every-time pattern is deliberate, not a UX oversight to "improve".
6. **Wrong-password is a silent reject, no lockout.** Brief red border flash + clear field is the pattern. Don't add error messages, don't add attempt counters, don't add cooldowns. A vessel engineer mistyping at 3am shouldn't get locked out of the manual.
7. **`sessionStorage`, not `localStorage`.** Re-prompt on browser restart is deliberate for a shared-PC environment.
8. **The `X-App-Password` header on every Railway fetch.** Already wired in `index.html` around line 2467. If you add new chatbot or proxy fetch calls, they need this header too.

---

## Fair game — redesign welcomed

These are pure UX/UI surfaces that can be redesigned without touching the security model:

- **The app password overlay visual design.** Currently a centred card with the `HERCULES MK3 ROV MANUAL` title and orange (`#e8a44a`) accent. Type, layout, theming all yours.
- **The admin password overlay visual design.** Currently `⚙ MANUAL ADMIN — RESTRICTED ACCESS`. Same — visuals are yours.
- **The whole admin panel layout.** Three-pane drawing management is functional but ugly. Open for reimagining provided the destructive operations stay behind `/api/admin-auth`.
- **The chatbot UI surface.** Could be inline, side panel, floating widget, voice, etc. Provided every Anthropic and Voyage call goes through Flask with the `X-App-Password` header.
- **Card click flow / sidebar / drawing tabs.** Card sidebar populated from `card_index` is open for redesign (see `DRAWING_INDEX.md` for what data is available).
- **Onboarding for first-time users.** Currently zero — they drop straight onto the menu after the password prompt.
- **Mobile / tablet responsive layout.** Vessel PCs are desktop but tablet use on deck has been discussed.
- **The error/empty states.** Currently terse "Not connected" type messages. Could be much friendlier without compromising security.

---

## Smoke test before committing any change

If you touch `app.py`, `index.html` chatbot fetch flow, `/api/config`, or any auth path:

1. **Curl `/api/config`:**
   ```bash
   curl -s https://rov-chatbot-production-3d66.up.railway.app/api/config | python3 -m json.tool
   ```
   **MUST return ONLY** `supabaseUrl`, `supabaseAnon`, `passwordRequired`, `adminRequired`. If Anthropic, Voyage, or service keys appear → ABORT, you've introduced the original bug.

2. **Curl `/health`:**
   ```bash
   curl -s https://rov-chatbot-production-3d66.up.railway.app/health | python3 -m json.tool
   ```
   Should show `"password": true` and `"admin": true` (env vars set) and `status: "ok"`.

3. **Browser flow:**
   - Fresh browser session → password prompt should appear
   - Wrong password → silent reject (clear field + brief red border, no error message)
   - Correct password → manual loads → ask chatbot a question → it should answer
   - Click ⚙ → admin password prompt → wrong rejected with visible error → correct loads admin

4. **JS parse check** (the project's canonical pre-push check):
   ```bash
   python3 -c "html=open('rov-manual/index.html').read(); script=html[html.rfind('<script>')+8:html.rfind('</script>')]; open('/tmp/vc.js','w').write('// test\n'+script)" && node --check /tmp/vc.js && echo "PARSE OK"
   ```

If all four pass, you haven't broken the security model.

---

## Where the security work lives in code

| Location | Purpose |
|---|---|
| `app.py` lines 13-19 | Env var reading (ANTHROPIC_KEY, VOYAGE_KEY, SUPABASE_URL, SUPABASE_ANON, SUPABASE_SERVICE, APP_PASSWORD, ADMIN_PASSWORD) |
| `app.py` lines 23-29 | `check_password()` with `hmac.compare_digest` |
| `app.py` lines 32-38 | `@require_password` decorator |
| `app.py` lines 51-63 | `/api/config` — must stay free of secrets |
| `app.py` lines 66-75 | `/api/auth` — app password validation |
| `app.py` lines 78-93 | `/api/admin-auth` — admin password validation (deny-by-default) |
| `app.py` lines 96+ | Gated proxies: voyage, anthropic, supabase |
| `rov-manual/index.html` line 207-220 | App-login overlay CSS |
| `rov-manual/index.html` line ~2078 | `/api/config` fetch handler — must not read non-existent fields |
| `rov-manual/index.html` line ~2092-2150 | App password prompt functions: `showAppLogin`, `appLoginSubmit`, `handleAuthExpired` |
| `rov-manual/index.html` line ~2467 | `X-App-Password` header injection on Anthropic proxy fetch |
| `rov-manual/index.html` line ~2540 | 401 handling on Anthropic proxy → triggers re-prompt |
| `rov-manual/index.html` near bottom of body | `#app-login` overlay HTML |
| `rov-manual/index.html` admin overlay section | `admTryLogin` — POSTs to `/api/admin-auth` |

Line numbers shift as edits happen. Grep for `hmac.compare_digest`, `X-App-Password`, `appLoginSubmit`, `admTryLogin` to find the current locations.

---

## Open security work — for future sessions, not this design pass

1. **Supabase key migration** to `sb_publishable` / `sb_secret`. ~30-45 min focused work. See `PROJECT_STATUS.md`.
2. **`knowledge_corrections` review workflow.** Table exists; no review queue yet. Before exposing the engineer-correction flow to vessel users, add a `status` column (`pending`/`approved`/`rejected`) and an admin queue UI.
3. **Rate limiting on the proxy.** Currently none. A determined attacker with `APP_PASSWORD` could rack up Anthropic spend. Defence: spending caps in Anthropic console (already set?) + add per-IP or per-session rate limit on `/anthropic/messages`.
4. **Audit logging.** All access through the gates is logged by Railway request logs but not in-app. A simple `auth_log` table that records every `/api/auth` and `/api/admin-auth` attempt (success and failure) would aid forensics later.
5. **The `/` route in `app.py` references `rov_agentic_chatbot.html` which no longer exists** — cosmetic orphan, but worth fixing.

None of these are blockers for design work. They're future engineering items.

---

## Quick reference — what just happened (one paragraph version)

The Anthropic, Voyage, and Supabase service role keys were leaked publicly via `/api/config` for an unknown duration prior to 13 May 2026. On that date the leak was plugged, two server-side password gates added (app + admin), constant-time comparison adopted, and the Anthropic + Voyage keys rotated. Supabase service_role rotation was deferred as tracked tech debt because Supabase's rotation model has changed and requires a planned migration session. Mid-rotation, a separate Railway-GitHub integration failure was discovered that had been silently breaking deploys for over a week — that's been fixed too. End state: gates live, paid-API keys fresh, Supabase service_role on the deferred-rotation list, deploy plumbing repaired.
