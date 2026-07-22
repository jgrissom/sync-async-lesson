# Session Overview & Timing

[← Back to session home](../README.md) · **Next:** [Warm-up: Getting on the Network →](01-setup.md)

---

Session 3's reaction game becomes a connected device: every round's result is POSTed to a live class leaderboard, and every bench fetches the standings between rounds. The arc mirrors Session 3 on purpose — first do networking the blocking way and *feel* it freeze the game, then do it the async way and watch the game stay alive.

## Time budget (3.5 hours / 210 minutes)

| Block | Activity | Time |
|---|---|---|
| Review | Session 3 assignment — live-code the solution from the starter | 10 min |
| Warm-up | Join the Wi-Fi, `secrets.py`, NTP time | 30 min |
| Part A | HTTP + JSON with blocking `urequests` — feel the freeze | 35 min |
| Break | Stretch / troubleshoot | 10 min |
| Part B | Async requests — GET and POST without freezing | 40 min |
| Part C | Graft networking into *your* reaction game | 30 min |
| Break | Stretch | 5 min |
| Assignment | Finish the connected game, demo on the live leaderboard | 45 min |
| Wrap-up | Standings ceremony, Q&A | 5 min |
| *Optional* | *Part D — your board as a web server (if time permits)* | *+25 min* |

> [!TIP]
> Parts A–C and the assignment need only the **scoreboard server on the classroom network** — no internet required. The internet-flavored extras (NTP, a real public weather API) are seasoning: if the school network is uncooperative, skip them and nothing downstream breaks.

## Learning objectives

By the end of the session, students will be able to:

- Connect MicroPython to Wi-Fi and read the board's IP and MAC address.
- Make HTTP GET/POST requests and parse JSON responses into dicts.
- Demonstrate why a blocking network call freezes every concurrent task.
- Use an async HTTP client so network waits yield to the scheduler.
- Choose between `await` (need the answer now) and `asyncio.create_task()` (fire and forget).
- Build connected features that fail soft when the network is unavailable.

---

[← Back to session home](../README.md) · **Next:** [Warm-up: Getting on the Network →](01-setup.md)
