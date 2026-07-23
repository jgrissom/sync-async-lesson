# Part B — Async Requests

⏱️ **40 min**

[← Part A](02-part-a-requests.md) · [Session home](../README.md) · **Next:** [Part C — Your Game Goes Online →](04-part-c-connected-game.md)

---

The fix for A2's freeze is the same idea as Session 3's: **turn every wait into an `await`.** A network request is mostly waiting — for the connection, for the server, for the bytes — and every one of those waits can yield to the scheduler instead of hogging it.

Upload [`async_http.py`](../code/async_http.py) to your board (like a library — import it, don't edit it). It gives you two coroutines:

```python
status, data = await async_http.get_json(host, path, port=80)
status, data = await async_http.post_json(host, path, payload, port=80)
```

> [!NOTE]
> Under the hood it opens a raw socket with `asyncio.open_connection()` and speaks HTTP by hand — the request is literally a few lines of text. Skim the file later; there's less magic in HTTP than you'd think. One honest trade-off: this client speaks plain `http://` only. Encrypted `https://` needs the blocking library (for now) — real engineering is full of trades like this.

## B1 — the freeze, cured

Take your A2 program and change **only** `fetch_loop()`:

```python
import async_http

async def fetch_loop():
    while True:
        await asyncio.sleep(4)
        print("fetching...")
        status, data = await async_http.get_json(
            secrets.SCOREBOARD_HOST, "/scores",
            port=secrets.SCOREBOARD_PORT)
        print("Blue wins:", data["totals"]["Blue"]["wins"])

# (also delete the urequests import -- this file no longer needs it)
```

> [!TIP]
> **Do this:** run it and watch both the DotStar and the shell through several fetches. No freeze — and the starvation detector you added in A2 **goes silent**. Think about what that proves: the fetch still takes the same few hundred milliseconds on the same network to the same server — the *cost didn't change*. What changed is where the waiting happens: inside `await`, where the scheduler can hand the time to the rainbow instead of burning it. Put A2's `>> rainbow starved for 384 ms!` next to B1's quiet shell: *that* is the whole session.

## B2 — POST: your board changes the world

GET reads; **POST writes**. Get the leaderboard on the projector, then run this:

```python
import uasyncio as asyncio
import wifi_connect, async_http, secrets

async def main():
    payload = {"bench": secrets.BENCH,
               "player": "Blue",
               "result": "win"}
    status, data = await async_http.post_json(
        secrets.SCOREBOARD_HOST, "/result", payload,
        port=secrets.SCOREBOARD_PORT)
    print("status:", status)
    print("my bench now:", data)

wifi_connect.connect()
asyncio.run(main())
```

> [!TIP]
> **Do this:** run it and watch the projector. Within two seconds, your bench's row updates for the whole class to see. Your microcontroller just wrote to a shared system — that's the "T" in IoT. (Now be honest and don't farm fake wins. The game will earn them properly in Part C.)

## B3 — `await` vs. fire-and-forget

You now face a choice you'll use forever. Two ways to launch a network call from inside a program:

| | Code | Meaning | Use when |
|---|---|---|---|
| **Wait for it** | `data = await fetch()` | *This* coroutine pauses (others still run) until the answer arrives | You need the result to continue — e.g. standings before announcing them |
| **Fire and forget** | `asyncio.create_task(report())` | The call runs in the background; you move on *immediately* | The result doesn't change what you do next — e.g. reporting a score |

The reaction game uses both, deliberately: reporting a result is fire-and-forget (the round is over; nothing waits on the server's reply), while fetching standings during the between-round pause is awaited (the announcement needs the data).

## Discussion (5 min)

**Q1. In B1, the network round-trip still takes just as long. Where did the freeze go?**

<details>
<summary>Answer</summary>

Nowhere — the *waiting* still happens, but it happens inside `await`s, where the scheduler lends the CPU to every other task. The rainbow doesn't run *instead of* the request; they interleave. Async never makes the network faster — it makes the waiting useful.

</details>

**Q2. What could go wrong with fire-and-forget reporting if the network is slow and rounds are fast?**

<details>
<summary>Answer</summary>

Reports can pile up — three rounds played, three POST tasks still in flight. Usually harmless (each is independent), but it's why fail-soft error handling in each task matters: ten stacked tasks all crashing on the same dead server must not take the game down. Production systems bound this with queues; our game just keeps each task small and self-contained.

</details>

---

[← Part A](02-part-a-requests.md) · [Session home](../README.md) · **Next:** [Part C — Your Game Goes Online →](04-part-c-connected-game.md)
