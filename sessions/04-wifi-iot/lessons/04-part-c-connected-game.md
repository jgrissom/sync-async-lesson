# Part C — Your Game Goes Online

⏱️ **30 min** *(flows directly into the graded assignment)*

[← Part B](03-part-b-async-requests.md) · [Session home](../README.md) · **Next:** [Part D — Web Server →](05-part-d-web-server.md)

---

Time to connect the thing you actually care about. You'll graft networking onto **your own** finished reaction game from Session 3 — open your `reaction_game_<yourname>.py` next to [`game_online_STARTER.py`](../code/game_online_STARTER.py), which contains every piece with instructions for where it goes.

The plan, in the language of B3:

1. **Report results — fire and forget.** The instant a round is decided, `asyncio.create_task(report_result(...))` launches the POST in the background. The game doesn't wait: feedback plays, the beacon resumes, the next round arms — while the report travels.
2. **Fetch standings — awaited.** The 3-second pause between rounds is dead time; spend it on `await fetch_standings()` and print the class totals.
3. **Fail soft.** Both coroutines wrap their network calls in `try/except OSError`. A dead server means a console note and an unchanged game — **a connected device that dies when the network does is a badly built device.**

## The graft, step by step

Work through `game_online_STARTER.py` top to bottom — it's organized as four grafts:

- **GRAFT 1** — imports (`wifi_connect`, `async_http`, `secrets`) into your game's header.
- **GRAFT 2** — the two coroutines, with **TODO 1** (the POST) and **TODO 2** (the GET + parse) for you to fill using exactly what you did in B1/B2.
- **GRAFT 3** — **TODO 3**: two `create_task` calls in `player()` (win + false start), one `await fetch_standings()` in `referee()`'s pause, and the leader flourish (double-blink the green LED when the round winner's team also leads the class).
- **GRAFT 4** — `wifi_connect.connect()` *before* `asyncio.run(main())`, keeping your `try/finally` cleanup.

> [!TIP]
> **Test as you graft** (Session 3 habit, same reason): after GRAFT 2 + TODO 1, play one round and watch the projector — your bench's row should tick up. Then add TODO 2 and confirm standings print between rounds. Then the flourish. If a stage breaks, the fault is in the piece you just added.

> [!NOTE]
> **Sanity check before you start:** the game itself must still be flawless. If your Session 3 game has a lingering bug, fix that first — networking grafted onto a broken game debugs like a nightmare, because every symptom has two suspects.

## The moment worth noticing

When it works, sit back and count what your ~150-line program is doing *simultaneously*: blinking a wait beacon, timing a random delay, watching two buttons, playing feedback, POSTing results across the room, and fetching a leaderboard — with no thread, no freeze, and every piece readable on one screen. That's what you learned in two sessions.

Finish the TODOs in the [graded assignment →](../assignment/README.md)

---

[← Part B](03-part-b-async-requests.md) · [Session home](../README.md) · **Next:** [Part D — Web Server →](05-part-d-web-server.md)
