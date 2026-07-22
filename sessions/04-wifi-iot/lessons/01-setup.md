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
- `SCOREBOARD_HOST` — the instructor laptop's IP, on the board/projector
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

The instructor's laptop is running the class scoreboard (one plain-Python file — [`scoreboard_server.py`](../code/scoreboard_server.py), yours to keep and run at home). Open **`http://<SCOREBOARD_HOST>:8000/`** in the bench laptop's browser: that's the live leaderboard, and it's about to fill up with your rounds.

Your board will talk to that same address — which is the whole point of today: **a web page, a laptop, and a microcontroller are all just devices exchanging HTTP on a network.**

---

[← Overview](00-overview.md) · [Session home](../README.md) · **Next:** [Part A — Talking HTTP →](02-part-a-requests.md)
