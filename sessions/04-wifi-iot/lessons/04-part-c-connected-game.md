# Part C — Your Game Goes Online

⏱️ **30 min** *(flows directly into the graded assignment)*

[← Part B](03-part-b-async-requests.md) · [Session home](../README.md) · **Next:** [Part D — Web Server →](05-part-d-web-server.md)

---

Time to connect the thing you actually care about: the reaction game. Your starting point is a **known-good finished game** — either your own `reaction_game_<yourname>.py` from Session 3 (if it plays flawlessly), or [`reaction_game_BASE.py`](../code/reaction_game_BASE.py), the same file the instructor live-coded in the opening review. Everything you'll add is on this page, organized as **four grafts** — copy each into your game where the graft says, fill in the TODOs, and test as you go.

(Your board needs `secrets.py`, `wifi_connect.py`, and `async_http.py` uploaded — all done in the warm-up and Part B.)

The plan, in the language of B3:

1. **Report results — fire and forget.** The instant a round is decided, `asyncio.create_task(report_result(...))` launches the POST in the background. The game doesn't wait: feedback plays, the beacon resumes, the next round arms — while the report travels.
2. **Fetch standings — awaited.** The 3-second pause between rounds is dead time; spend it on `await fetch_standings()` and print the class totals.
3. **Fail soft.** Both coroutines wrap their network calls in `try/except OSError`. A dead server means a console note and an unchanged game — **a connected device that dies when the network does is a badly built device.**

> [!NOTE]
> **Sanity check before you start:** the game itself must be flawless *before* the first graft — networking grafted onto a broken game debugs like a nightmare, because every symptom has two suspects. If your Session 3 game has any lingering quirk, don't fix it on the clock: start from [`reaction_game_BASE.py`](../code/reaction_game_BASE.py). That's what it's for.

## GRAFT 1 — imports

Add the three new imports to the top of your game (`uasyncio` is already there):

```python
import wifi_connect
import async_http
import secrets
```

## GRAFT 2 — two new coroutines

Copy both into your game — anywhere above `main()`; next to `buzz()` is a fine home. Then fill in **TODO 1** and **TODO 2** using exactly what you did in B2 and B1.

```python
async def report_result(player, result):
    """POST one round result to the class scoreboard.
    Wrapped in try/except so a dead network NEVER crashes the game --
    connected features should fail soft."""
    try:
        # ------------------------------------------------------
        # TODO 1: POST the result to the scoreboard.
        #   The payload dict:
        #     {"bench": secrets.BENCH, "player": player, "result": result}
        #   The call:
        #     status, data = await async_http.post_json(
        #         secrets.SCOREBOARD_HOST, "/result", payload,
        #         port=secrets.SCOREBOARD_PORT)
        #   Then print the status so you can see it worked (200 = OK).
        # ------------------------------------------------------
        pass
    except OSError as e:
        print("(scoreboard unreachable:", e, "-- playing on)")


async def fetch_standings():
    """GET the class-wide totals, print them, and return the totals
    dict (or None if the scoreboard is unreachable)."""
    try:
        # ------------------------------------------------------
        # TODO 2: GET /scores from the scoreboard.
        #   status, data = await async_http.get_json(
        #       secrets.SCOREBOARD_HOST, "/scores",
        #       port=secrets.SCOREBOARD_PORT)
        #   data["totals"] looks like:
        #     {"Blue": {"wins": 3, ...}, "Yellow": {"wins": 5, ...}}
        #   Print it like:   CLASS STANDINGS -- Blue 3 : 5 Yellow
        #   and  return data["totals"]
        # ------------------------------------------------------
        pass
    except OSError as e:
        print("(scoreboard unreachable:", e, ")")
        return None
```

> [!TIP]
> **Test the first half now:** fill in TODO 1, add GRAFT 3a and GRAFT 4 below, play one round, and watch the projector — your bench's row should tick up. *Then* come back for TODO 2 and the rest. If a stage breaks, the fault is in the piece you just added. (Session 3 habit, same reason.)

## GRAFT 3 — wire them into the game (TODO 3)

**a) Report from `player()` — the moment a round is decided.** One line at the end of each branch, *after* the feedback:

```python
            # ...end of the VALID WIN branch:
            asyncio.create_task(report_result(name, "win"))
```

```python
            # ...end of the FALSE START branch:
            asyncio.create_task(report_result(name, "false_start"))
```

Why `create_task()` and not `await`? The round is over and the player's coroutine has feedback still to give — we want the POST to happen **in the background** while the game carries on. Fire and forget.

**b) Fetch standings from `referee()` — in the pause between rounds.** The 3-second pause is dead time; spend it:

```python
        # Pause before the next round -- and use it
        totals = await fetch_standings()
        await asyncio.sleep(3)
```

This one we **do** `await` — we want the standings printed before the next round starts, and nothing else is happening anyway.

**c) Leader flourish.** After fetching: if the team that just won this round *also* leads the class standings, double-blink the green LED in celebration:

```python
        if totals and totals["Blue"]["wins"] > totals["Yellow"]["wins"]:
            ...   # double-blink if Blue just won this round
        # (and the mirror case for Yellow)
```

The `if totals` guard matters: `fetch_standings()` returns `None` when the scoreboard is unreachable, and the flourish must fail soft with everything else.

## GRAFT 4 — connect before the game starts

Replace the bottom of your game — Wi-Fi comes up *before* the scheduler starts:

```python
wifi_connect.connect()      # BEFORE asyncio.run -- blocking on
                            # purpose: no network, no scoreboard
try:
    asyncio.run(main())
finally:
    ...                     # your existing cleanup stays as-is
```

## The moment worth noticing

When it works, sit back and count what your ~150-line program is doing *simultaneously*: blinking a wait beacon, timing a random delay, watching two buttons, playing feedback, POSTing results across the internet, and fetching a leaderboard — with no thread, no freeze, and every piece readable on one screen. That's what you learned in two sessions.

Finish the TODOs in the [graded assignment →](../assignment/README.md)

---

[← Part B](03-part-b-async-requests.md) · [Session home](../README.md) · **Next:** [Part D — Web Server →](05-part-d-web-server.md)
