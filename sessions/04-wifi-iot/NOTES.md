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
- **The core session needs only *outbound* internet** (revised 2026-07-22;
  originally "zero internet"). The scoreboard moved to the cloud because
  the original design's riskiest dependency was board→laptop traffic on a
  guest network — exactly what client isolation blocks — while outbound
  HTTP is what guest networks permit. The zero-internet capability is
  preserved one rung down: phone hotspot + the local `scoreboard_server.py`
  can still host the entire core lesson, and switching rungs changes only
  `SCOREBOARD_HOST`/`SCOREBOARD_PORT` in `secrets.py`. NTP and open-meteo
  remain skip-safe garnish.
- **Fail-soft is a graded requirement (rubric row 6, 20 pts)** and the
  instructor deliberately kills the server during demos. Connected features
  wrap network calls in `try/except OSError` — a connected device that dies
  with its network is a badly built device. This is the session's second
  thesis.

## Infrastructure decisions

- **The class scoreboard is cloud-hosted (Azure, `scoreboard-cloud/` at the
  repo root; added 2026-07-22).** .NET 10 API + SQLite serving the React
  leaderboard, the classic page, and interactive Scalar docs from one
  origin. Its JSON contract is verified byte-compatible with
  `scoreboard_server.py` (a test battery replays identical requests at
  both, including raw HTTP/1.0), and the one extension — game-name
  registration — is strictly additive (`names` key; boards and the classic
  page ignore it). **If either server's contract changes, the other must
  change with it** — interchangeability is what makes the fallback ladder
  work. Cloud-only classroom extras: `POST /register` (unique
  case-insensitive game names, 409 on conflict — doubles as a status-code
  lesson via Scalar's Test Request) and win confetti on the React page.
- **`scoreboard_server.py` is stdlib-only Python 3** (http.server) — now
  the offline-fallback/run-at-home twin: zero installs, one file, scores
  persist to a JSON file beside it. The leaderboard page polls `/scores`
  via JS every 1.5 s (chosen over meta-refresh for flicker-free projector
  display, over SSE/websockets for simplicity — the same reasoning kept
  the cloud edition on polling instead of SignalR). `/reset` clears
  between classes.
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

- Part C grafts onto a **known-good finished game** —
  `reaction_game_BASE.py` (the Session 3 solution, published) or the
  student's own file if it plays flawlessly. **Reversed 2026-07-23**: the
  original design withheld the base to protect Session 3's assignment
  from look-ahead, at the cost of grafting onto 13 divergent,
  possibly-buggy files ("every symptom has two suspects"). Decision:
  these are paying adults — support simplicity and debugging sanity beat
  solution secrecy. The instructor bundle's copy remains the grading
  reference; a future course run that wants secrecy back just deletes
  the BASE file and restores the private-handoff flow.
- `await` vs `create_task()` (B3's table) is the session's conceptual
  centerpiece: report = fire-and-forget, standings = awaited, and the
  rubric penalizes awaiting the report (it parks the game on timeouts
  exactly when the network is worst).
- Wi-Fi *connection* is done synchronously and the lesson says why —
  reinforces Session 3's "blocking is a choice; sometimes the right one."
- **Grafts are ordered for testability, not reading order** (reordered
  2026-07-23, Jeff's call): imports → Wi-Fi connect → report+wiring →
  standings+wiring → flourish. The original order (connect last, both
  coroutines batched in one graft, wiring batched in another) left the
  middle steps untestable — nothing could reach the network until the
  final graft, and a defined-but-never-called coroutine is only a syntax
  checkpoint. Now each coroutine lands *with* its call site, Wi-Fi is up
  from graft 2 on, and every graft ends with a visible "run it" payoff.
  The instructor bundle's graft-ladder mirrors this order commit-for-
  commit.
- **The grafts live in Part C's page, not a starter .py** (changed
  2026-07-23; `game_online_STARTER.py` deleted). Session 3's starter was
  a runnable scaffold filled in-place — a .py was its natural home.
  Session 4's "starter" was a donor bank of fragments transplanted into
  another file, and comment-formatted instructions in a non-runnable .py
  were the worst medium for that: rendered Markdown with prose between
  copyable fenced blocks follows better and kills the "do I run this
  file?" confusion. TODO structure (1–3) and all rationale comments were
  preserved verbatim in the move.
