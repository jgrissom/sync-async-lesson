# Warm-up: Getting on the Network

⏱️ **35 min**

[← Overview](00-overview.md) · [Session home](../README.md) · **Next:** [Part A — Talking HTTP →](02-part-a-requests.md)

---

Same breadboard as Session 3 — nothing to wire today. The new hardware is invisible: the ESP32's built-in Wi-Fi radio.

> [!IMPORTANT]
> **Two facts about ESP32 Wi-Fi that cause most failures:**
> 1. It speaks **2.4 GHz only**. A 5 GHz-only network is invisible to the board.
> 2. It cannot handle **login pages** (captive portals) or enterprise username/password logins. Our network uses per-device registration instead — every board's MAC address was registered before class.

## 1. Create your `secrets.py`

Network credentials never go in your main program (or in git!). Open [`code/secrets_TEMPLATE.py`](../code/secrets_TEMPLATE.py), **save a copy as `secrets.py`**, and fill in the values announced in class:

- `WIFI_SSID` / `WIFI_PASSWORD` — the class network (empty password if it's open)
- `SCOREBOARD_HOST` / `SCOREBOARD_PORT` — the class scoreboard's address; the template already carries the normal values (change only if a fallback is announced)
- `BENCH` — your bench number

Upload `secrets.py` **and** [`wifi_connect.py`](../code/wifi_connect.py) to the board (Thonny → View → Files → right-click → *Upload to /*, same as the DotStar library last session).

## 2. First connection

At the REPL (or as a tiny script):

```python
import wifi_connect
wifi_connect.connect()
```

Expected output ends with `Connected! IP address: 10.x.x.x`. That IP is your board's address *on this network* — every bench gets a different one.

> [!NOTE]
> **Why is connecting synchronous?** `wifi_connect.connect()` blocks for up to a few seconds — on purpose. Until the network exists, no other part of a networked program has anything useful to do. Blocking is a *choice*; here it's the right one. (Sound familiar? Same judgment call as B3's test rig last session.)

**If it fails:** the error message tells you what to check — SSID spelling, 2.4 GHz, MAC registration. More in the [Troubleshooting & FAQ](../../../TROUBLESHOOTING.md).

## 3. Your board knows what time it is

The board has no battery-backed clock — it boots thinking it's the year 2000. One tiny protocol fixes that, and it's your first taste of the board using the internet:

```python
import ntptime, time
ntptime.settime()          # asks an internet time server (NTP)
print(time.localtime())    # (year, month, day, hour, min, sec, ...)
```

The time is **UTC** — expect it to be offset from wall-clock time here. (Networks without internet access will fail this step with a timeout — that's fine, nothing today depends on it.)

## 4. Meet the scoreboard

The class scoreboard is a real cloud API, running on Azure at **`false-start.azurewebsites.net`** (a fitting name — you'll meet plenty of those tonight). Three faces of the same server:

- **[https://false-start.azurewebsites.net/](https://false-start.azurewebsites.net/)** — the live leaderboard on the projector, about to fill up with your rounds.
- **[https://false-start.azurewebsites.net/scalar](https://false-start.azurewebsites.net/scalar)** — the API's interactive documentation. Every endpoint your board will use tonight is described here, and you can call them straight from the page.
- **[http://false-start.azurewebsites.net/scores](http://false-start.azurewebsites.net/scores)** — the raw JSON your board will actually read. Open it and look: no magic, just text.

Your board will talk to that same server — which is the whole point of today: **a web page, a phone, a cloud server, and a microcontroller are all just devices exchanging HTTP.**

### Name your game 🏷️

Your bench's Session 3 creation deserves a title. On a phone, open **[false-start.azurewebsites.net/scalar](https://false-start.azurewebsites.net/scalar)**, find **"Name your game"** (`POST /register`), hit **Test Request**, and send:

```json
{ "bench": "3", "name": "Your Game Title Here" }
```

with your bench number and your title (40 characters max). A `200` means it's yours — watch the projector. A `409 Conflict` means another bench beat you to that name: read the error, pick a better one. That's your first hand-made API call — your board automates the same thing all evening.

> [!NOTE]
> Want to run the whole scoreboard yourself at home? A single-file Python version with the same API lives in the repo — [`scoreboard_server.py`](../code/scoreboard_server.py). Point `SCOREBOARD_HOST` at your own laptop and everything tonight works against it.

---

[← Overview](00-overview.md) · [Session home](../README.md) · **Next:** [Part A — Talking HTTP →](02-part-a-requests.md)
