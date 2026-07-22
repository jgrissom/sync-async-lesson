# Design-Decision Log — Session 4 (Wi-Fi & IoT)

Companion to Session 3's [NOTES.md](../03-sync-async/NOTES.md); same purpose,
safe for the public repo.

## The core bet

The session is built around **the students' own reaction game going online**
(instead of a generic weather/data project). Reasons: continuity and
ownership; a live class leaderboard on the projector; POST + GET + JSON all
arise naturally; and blocking has *stakes* — a blocking call visibly freezes
the game students built. The A2→B1 freeze/cure pair is Session 3's
`time.sleep()` argument restaged with the network as the villain.

## Network-resilience decisions (load-bearing)

- **The graded path is outbound-only.** Boards only ever *open* connections
  (to the scoreboard, to public APIs). Inbound connections (Part D's web
  server) are the first thing real networks block (client isolation), so
  inbound lives exclusively in the optional part. Never move it into the
  graded path.
- **The core session needs zero internet.** The scoreboard runs on the
  instructor's laptop; a phone hotspot with no upstream connectivity can
  host the entire core lesson. Internet-dependent bits (NTP, open-meteo)
  are explicitly skip-safe garnish.
- **Fail-soft is a graded requirement (rubric row 6, 20 pts)** and the
  instructor deliberately kills the server during demos. Connected features
  wrap network calls in `try/except OSError` — a connected device that dies
  with its network is a badly built device. This is the session's second
  thesis.

## Infrastructure decisions

- **`scoreboard_server.py` is stdlib-only Python 3** (http.server) — zero
  installs on the school laptop, one file, scores persist to a JSON file
  beside it. The leaderboard page polls `/scores` via JS every 1.5 s (chosen
  over meta-refresh for flicker-free projector display, over
  SSE/websockets for simplicity). `/reset` clears between classes.
- **The server lives in the public repo** — it's infrastructure, not a
  solution; students can run their own at home.
- **API surface kept tiny on purpose:** `GET /scores`, `GET /scores/<bench>`,
  `POST /result {bench, player, result}`. Player names must match the
  Session 3 cap colors ("Blue"/"Yellow") — the server validates them.
- **Bench identity lives in `secrets.py`** (`BENCH`) alongside Wi-Fi
  credentials and `SCOREBOARD_HOST` — one per-bench file holds everything
  bench-specific; code files stay identical on every board.
- **`secrets.py` is gitignored at the repo root**; only
  `secrets_TEMPLATE.py` is committed. Protects the school's network
  credentials from student forks.

## Library / API decisions (verified 2026-07-22)

- **Open-Meteo** is the public-API example: keyless, tiny JSON (~500 B),
  and verified to work over **both** `https` (for `urequests`) and plain
  `http` (for the raw-socket async client). Response shape documented in
  Part A matches a live capture.
- **worldtimeapi.org was rejected** — unreachable in pre-build testing
  (twice). Do not reintroduce it; it has a history of flakiness.
- **wttr.in is the documented emergency alternate** (plain http, ~40 KB
  JSON for `?format=j1` — large but fine with the TinyPICO's PSRAM).
- **`async_http.py` speaks HTTP/1.0 with `Connection: close`** on purpose:
  no chunked encoding, body ends at EOF, ~80 teachable lines. Plain http
  only — TLS-on-streams in MicroPython isn't classroom-stable, and the
  lesson names the trade-off honestly (B's note).
- **`urequests` import pattern**: `try: import urequests / except:
  import requests` — covers firmware variation; pre-class checklist
  verifies, `mip.install` is the fallback.

## Pedagogy notes

- Part C **grafts onto each student's own Session 3 game** rather than
  shipping a complete game in the repo — a complete base game would leak
  the Session 3 solution publicly. Students without their file get the
  instructor solution privately (answer key notes this).
- `await` vs `create_task()` (B3's table) is the session's conceptual
  centerpiece: report = fire-and-forget, standings = awaited, and the
  rubric penalizes awaiting the report (it parks the game on timeouts
  exactly when the network is worst).
- Wi-Fi *connection* is done synchronously and the lesson says why —
  reinforces Session 3's "blocking is a choice; sometimes the right one."
