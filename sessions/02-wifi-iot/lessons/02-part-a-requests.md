# Part A — Talking HTTP (the blocking way)

⏱️ **35 min**

[← Setup](01-setup.md) · [Session home](../README.md) · **Next:** [Part B — Async Requests →](03-part-b-async-requests.md)

---

HTTP is a conversation: your program sends a **request** ("GET me `/scores`"), the server sends back a **response** (a status code plus a body — often **JSON**, which maps straight onto Python dicts and lists). MicroPython ships a small requests library for exactly this.

## A1 — your first request

```python
import wifi_connect
wifi_connect.connect()

try:
    import urequests as requests   # most MicroPython builds
except ImportError:
    import requests                # newer builds

import secrets

url = "http://{}:{}/scores".format(secrets.SCOREBOARD_HOST,
                                   secrets.SCOREBOARD_PORT)
r = requests.get(url)
print("status:", r.status_code)    # 200 means OK
data = r.json()                    # JSON body -> Python dict
r.close()                          # ALWAYS close -- frees the socket

print(data)
```

> [!TIP]
> **Do this:** run it, then explore `data` at the REPL. It's just a dict:
> ```python
> data["totals"]                        # {'Blue': {...}, 'Yellow': {...}}
> data["totals"]["Blue"]["wins"]        # a plain int
> list(data["benches"].keys())          # which benches have reported
> ```
> Drill this navigation — dict, key, dict, key — until it's boring. Every API you'll ever use is this move repeated.

> [!NOTE]
> **Try a real public API too** (needs internet): the same three lines fetch live weather from [Open-Meteo](https://open-meteo.com/) — no account, no key:
> ```python
> r = requests.get("https://api.open-meteo.com/v1/forecast"
>                  "?latitude=41.88&longitude=-87.63&current_weather=true")
> print(r.json()["current_weather"]["temperature"])
> r.close()
> ```
> Note it's `https` — the requests library handles encryption for you. Skill unlocked: thousands of public APIs now work exactly like the class scoreboard.

## A2 — the freeze: blocking strikes back

`requests.get()` is **blocking**: from the moment you call it until the response arrives — half a second on a good day, ten seconds on a bad network — your program does *nothing else*. You know exactly what that means for a concurrent program. Watch it happen:

```python
from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar
import wifi_connect, secrets

try:
    import urequests as requests
except ImportError:
    import requests

spi = SoftSPI(sck=Pin(TinyPICO.DOTSTAR_CLK),
              mosi=Pin(TinyPICO.DOTSTAR_DATA),
              miso=Pin(TinyPICO.SPI_MISO))
ds = DotStar(spi, 1, brightness=0.3)
TinyPICO.set_dotstar_power(True)

def wheel(pos):
    pos %= 255
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

async def rainbow():
    pos = 0
    while True:
        ds[0] = wheel(pos)
        pos = (pos + 2) % 255
        await asyncio.sleep(0.02)

async def fetch_loop():
    url = "http://{}:{}/scores".format(secrets.SCOREBOARD_HOST,
                                       secrets.SCOREBOARD_PORT)
    while True:
        await asyncio.sleep(4)
        print("fetching...")
        r = requests.get(url)          # <-- BLOCKING, inside a coroutine
        print("Blue wins:", r.json()["totals"]["Blue"]["wins"])
        r.close()

async def main():
    asyncio.create_task(rainbow())
    asyncio.create_task(fetch_loop())
    while True:
        await asyncio.sleep(1)

wifi_connect.connect()
try:
    asyncio.run(main())
finally:
    TinyPICO.set_dotstar_power(False)
```

> [!TIP]
> **Do this:** watch the DotStar. Every four seconds — *freeze*. The rainbow locks solid for the entire network round-trip, because `requests.get()` never yields. It's Session 1's `time.sleep()` disease wearing a networking costume — except now the freeze length is up to the *network*, not you.
>
> Imagine this inside your reaction game: every score report would freeze the wait beacon, the buttons, everything. Unacceptable. Part B fixes it.

## Discussion (5 min)

**Q1. In Session 1 we banned `time.sleep()` from async programs. What's the equivalent rule for networking, and why is it worse?**

<details>
<summary>Answer</summary>

The rule: no blocking I/O (like `requests.get()`) inside coroutines. It's worse than `time.sleep()` because the freeze duration isn't chosen by you — it's chosen by the network, and on a bad day it's seconds long or forever. A `time.sleep(1)` is a predictable pothole; a blocking network call is a pothole of unknown depth.

</details>

**Q2. Why must you call `r.close()` after every request?**

<details>
<summary>Answer</summary>

Each request opens a network socket, and the board only has a handful. Without `close()`, sockets leak until requests start failing with `OSError` — often several successful requests *later*, which makes it a maddening bug to trace back. Close what you open, every time.

</details>

---

[← Setup](01-setup.md) · [Session home](../README.md) · **Next:** [Part B — Async Requests →](03-part-b-async-requests.md)
