# Troubleshooting — Thonny + TinyPICO

[← Back to home](README.md)

Symptom-first. Find your problem, apply the fix, get back to the lesson. When in doubt, the universal reset is: **click Stop in Thonny, then press Ctrl+F2** (soft-reboots the board and gives you a fresh `>>>` prompt).

---

## Connecting

### Thonny says "Couldn't find the device" or shows no `>>>` prompt

1. **Check the cable.** Charge-only USB cables are the #1 cause — swap for a known data cable.
2. **Check the port.** Tools → Options → Interpreter: interpreter must be *MicroPython (ESP32)* and the port the TinyPICO's serial port (on macOS it looks like `/dev/cu.usbserial-XXXX` or `/dev/cu.SLAB_USBtoUART`; on Windows, a `COM` number that appears when you plug the board in and disappears when you unplug it).
3. Click the **Stop/Restart** button (red stop sign) — Thonny often just needs a nudge to re-open the port.

### "Device is busy" / "Port is in use" / connection drops immediately

Something else is holding the serial port. Close any other serial monitor (Arduino IDE, a second Thonny window, `screen` in a terminal), unplug/replug the board, then Stop/Restart in Thonny.

### The `>>>` prompt appears but the board ignores everything

A program is still running and hogging the CPU (very common with a `while True` loop that never yields). Press **Ctrl+C** to interrupt it; if that doesn't land, **Ctrl+F2**.

---

## Running code

### My async program crashed and now nothing runs right (or `asyncio` behaves strangely on the next run)

After an async program crashes or is interrupted with Ctrl+C, the old event loop and its tasks can be left half-alive — the next `asyncio.run()` may error or inherit zombie tasks (symptoms: `RuntimeError`, tasks from the *previous* run still blinking LEDs).

**Fix: Ctrl+F2 (soft reset) before re-running.** Make this a reflex in Parts B–D: *Stop → Ctrl+F2 → Run*. It takes one second and eliminates a whole class of "my code is broken" that isn't.

### `OSError: 28` when saving or uploading a file

Error 28 = the board's flash filesystem is **full**. The TinyPICO has ~4 MB and old experiments add up.

1. View → Files, look at the *MicroPython device* pane (bottom).
2. Delete files you don't need (right-click → Delete). Keep `micropython_dotstar.py` (and `tinypico.py` if you uploaded it)!
3. Empty a file's contents and re-saving does **not** reclaim space reliably — delete the file itself.

### `ImportError: no module named 'micropython_dotstar'` (or `'tinypico'`)

The helper library isn't on the board. Follow the upload steps in [Part C](sessions/01-sync-async/lessons/04-part-c-dotstar.md) — download from [tinypico/tinypico-micropython](https://github.com/tinypico/tinypico-micropython), then Thonny → View → Files → right-click the file → *Upload to /*. Do **not** rename `micropython_dotstar.py`; the import matches the real filename.

### The board runs an old program every time it powers on, and I can't get a prompt

You (or a previous student) saved a program as **`main.py` on the device** — MicroPython auto-runs it at boot. Connect, press Ctrl+C repeatedly during/after plugging in until you get `>>>`, then delete or rename `main.py` via View → Files. In this course, save work under any other name (e.g. `reaction_game_yourname.py`) and use the Run button instead.

### Thonny says "Backend not responding"

Stop/Restart button. If it persists: unplug the board, close Thonny, plug in, reopen.

---

## Hardware

### An LED never lights

- **Polarity:** long leg (anode) goes to the GPIO side; short leg (cathode) to the resistor, then GND — see the [wiring diagram](sessions/01-sync-async/diagrams/wiring.svg). (Resistor on the anode side works too — it just has to be *somewhere* in the series loop.)
- The 330 Ω resistor must be **in series** (in the same current path), not on a random row.
- Jumper actually in the GPIO's breadboard column? Off-by-one rows are the classic.
- Test the pin from the REPL: `from machine import Pin; Pin(26, Pin.OUT).on()` — if the LED lights now, the problem was the program, not the wiring.

### A button reads pressed (0) all the time — or never reads pressed

- Constant `0`: the GPIO leg and GND leg are probably on the **same** side of the switch (momentary switches have two pairs of legs; opposite corners are safest), or the pin is shorted to GND.
- Never `0`: missing `Pin.PULL_UP` in code (the pin floats), or the button isn't actually bridging to GND. Test at the REPL: `from machine import Pin; b = Pin(18, Pin.IN, Pin.PULL_UP); b.value()` — should print `1` released, `0` held.

### The DotStar stays dark

- Did you call `TinyPICO.set_dotstar_power(True)`? The DotStar's power rail is switched — without this line it shows nothing, with no error.
- The SoftSPI setup must use `TinyPICO.DOTSTAR_CLK` / `TinyPICO.DOTSTAR_DATA` (and a `miso` pin, even though it's unused).
- Setting a color must come *after* both of the above.

### The buzzer clicks weakly instead of beeping

Passive piezo buzzers need a tone (PWM), not a steady on. The buzzers in this course are active (steady `on()` beeps). If yours only clicks, flag the instructor — you likely have a passive one from a different kit.

### The DotStar rainbow stutters (Part C)

That's not a fault — that's the lesson. Something in your code is blocking. Hunt for any `time.sleep()` in a coroutine, or a loop that never `await`s.

---

## Wi-Fi & network (Session 2+)

### The board won't join the Wi-Fi

- **2.4 GHz only.** The ESP32 cannot see 5 GHz-only networks. Confirm the SSID broadcasts on 2.4 GHz.
- **SSID/password typo in `secrets.py`** — case matters.
- **MAC not registered** (school guest network): run `print_mac.py`, check the address against the registered list.
- **Captive portal:** if joining this network on a laptop pops a login page, the board can't use it — boards can't click "Accept." Use the registered/hotspot network instead.

### `ImportError: no module named 'secrets'` (or `wifi_connect`, `async_http`)

The file isn't on the board. These upload like libraries: Thonny → View → Files → right-click → *Upload to /*. Remember `secrets.py` is one you *create* from `secrets_TEMPLATE.py` — the template alone isn't enough.

### Requests fail with `OSError: -202` (or `getaddrinfo` errors)

DNS lookup failed — the board is on Wi-Fi but can't resolve names. Usually: no actual internet on this network (fine for the scoreboard — that's a raw IP), or Wi-Fi dropped. Reconnect with `wifi_connect.connect()`.

### Requests to the scoreboard time out, but the leaderboard works on the laptop

Almost always **client isolation**: the network blocks device-to-device traffic. Test: can a *phone* browser open the leaderboard URL? If not, it's the network, not your code — the class fallback is the instructor's hotspot. (Outbound internet requests still work under isolation; only local traffic is blocked.)

### `OSError: [Errno 104] ECONNRESET` / occasional failed requests

Networks drop connections; it's their hobby. This is exactly why the lesson wraps every network call in `try/except OSError` — confirm yours does, and let the next attempt succeed.

### Requests start failing after several successes

Socket leak — something isn't calling `r.close()` (blocking library) or is bypassing `async_http` (which closes for you). Ctrl+F2 resets the sockets; then fix the leak.

### `ntptime.settime()` times out

The network has no internet (or blocks NTP's port). Skip it — nothing in the session depends on the clock.

---

Still stuck? Ask — but be ready to say what you observed, what you expected, and what you already tried. That sentence is half of debugging.

[← Back to home](README.md)
