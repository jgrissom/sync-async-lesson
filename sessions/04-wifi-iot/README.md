# Session 4 — Wi-Fi & the Internet of Things

*Part of the [Python IoT on the TinyPICO curriculum](../../README.md).*

Last session you built a two-player reaction game and learned why `await` beats blocking. This session your game **goes online**: every bench reports wins and false starts to a live class leaderboard, projected at the front of the room. Along the way you'll join a Wi-Fi network from code, speak HTTP, parse JSON — and rediscover the blocking problem the moment a slow network call freezes your game.

| | |
|---|---|
| **Duration** | 3.5 hours (210 min) + optional bonus segment |
| **Level** | Intermediate Python (Session 3 required) |
| **Environment** | [Thonny](https://thonny.org/) + MicroPython |
| **Board** | TinyPICO ESP32 — same bench wiring as Session 3 |

---

## Lesson navigation

1. [Session Overview & Timing](lessons/00-overview.md)
2. [Warm-up: Getting on the Network](lessons/01-setup.md) — *25 min*
3. [Part A — Talking HTTP (the blocking way)](lessons/02-part-a-requests.md) — *35 min*
4. [Part B — Async Requests](lessons/03-part-b-async-requests.md) — *40 min*
5. [Part C — Your Game Goes Online](lessons/04-part-c-connected-game.md) — *30 min*
6. [Part D — Your Board as a Web Server (optional)](lessons/05-part-d-web-server.md) — *bonus*
7. [Assignment — The Connected Reaction Game](assignment/README.md) — *45 min, graded*

Something not working? → **[Troubleshooting & FAQ](../../TROUBLESHOOTING.md)** — now with a Wi-Fi & network section.

## Code files

| File | What it is |
|---|---|
| [`code/print_mac.py`](code/print_mac.py) | Prints the board's MAC address (needed for network registration) |
| [`code/secrets_TEMPLATE.py`](code/secrets_TEMPLATE.py) | Copy to `secrets.py`, fill in, upload — **never commit `secrets.py`** |
| [`code/wifi_connect.py`](code/wifi_connect.py) | Wi-Fi join helper — upload to the board like a library |
| [`code/async_http.py`](code/async_http.py) | Tiny async HTTP client (GET/POST JSON) — upload like a library |
| [`code/reaction_game_BASE.py`](code/reaction_game_BASE.py) | The finished Session 3 reaction game — the known-good base for the network grafts (use your own working game if you prefer) |
| [Part C's graft sections](lessons/04-part-c-connected-game.md) | The network additions you graft into the game — copyable code blocks, right in the lesson |
| [`code/web_remote.py`](code/web_remote.py) | Part D: the board serves a control page to your phone |
| [`code/scoreboard_server.py`](code/scoreboard_server.py) | Single-file twin of the class scoreboard (normal Python 3) — the class instance runs in the cloud ([`scoreboard-cloud/`](../../scoreboard-cloud/)); this one is the offline fallback, and yours to run at home |

## What students will be able to do

- Join a Wi-Fi network from MicroPython and diagnose the common failures
- Explain what an HTTP request/response is and make GET and POST requests
- Parse JSON into dicts and navigate real API responses
- Explain why blocking network calls freeze concurrent programs — and fix it with async I/O
- Fire-and-forget background tasks with `asyncio.create_task()`
- Build a connected device that *fails soft* when the network disappears
