# Assignment — Reaction-Timer Game

⏱️ **50 min** · 🎯 **Graded — 100 points**

[← Part D](../lessons/05-part-d-hardware-debounce.md) · [Home](../README.md)

---

Build a two-player reaction game that ties everything together. This is **graded** and must run on the hardware. Work individually or in pairs as directed.

## How the game works

1. On start, the DotStar shows **red** and both LEDs are off. Players wait.
2. After a **random delay of 2–5 seconds**, the DotStar turns **green** and LED 2 (the green LED) lights — this is the "GO" signal.
3. The **first player to press** their button (A or B) after GO wins: sound the buzzer and flash the DotStar their color (e.g., Player A = blue, Player B = magenta).
4. If a player presses **before** the green GO signal (a **false start**), they lose immediately — flash the DotStar red and buzz twice.
5. After a result, wait 3 seconds, then reset for another round automatically.

## Requirements (grading rubric)

| # | Requirement | Points |
|---|---|---|
| 1 | Program uses `uasyncio` with at least two concurrent tasks (no blocking `time.sleep` in the main logic) | 25 |
| 2 | Random 2–5 s delay before GO (use the `random` module) | 15 |
| 3 | Correctly detects the first button pressed after GO and names the winner | 20 |
| 4 | False-start detection: pressing before GO loses | 15 |
| 5 | DotStar and buzzer feedback for win, loss, and false start | 15 |
| 6 | Buttons are debounced; no double-triggers | 10 |

**Total: 100 points.**

## Starter scaffold

Fill in the three TODOs. Full file: [`code/reaction_game_STARTER.py`](../code/reaction_game_STARTER.py)

```python
from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar
import random

led2 = Pin(27, Pin.OUT)   # green LED = GO indicator
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)
btnB = Pin(5, Pin.IN, Pin.PULL_UP)

spi = SoftSPI(sck=Pin(TinyPICO.DOTSTAR_CLK),
              mosi=Pin(TinyPICO.DOTSTAR_DATA),
              miso=Pin(TinyPICO.SPI_MISO))
ds = DotStar(spi, 1, brightness=0.3)
TinyPICO.set_dotstar_power(True)

# Shared game state
state = {"go": False, "over": False, "winner": None, "false_start": False}

async def buzz(times, dur=0.1):
    for _ in range(times):
        buzzer.on(); await asyncio.sleep(dur)
        buzzer.off(); await asyncio.sleep(dur)

async def referee():
    while True:
        # Reset round
        state.update(go=False, over=False, winner=None, false_start=False)
        ds[0] = (255, 0, 0)   # red = wait
        led2.off()

        # TODO 1: wait a RANDOM 2-5 seconds before GO
        # (hint: random.uniform, await asyncio.sleep)

        if not state["over"]:            # nobody false-started
            state["go"] = True
            ds[0] = (0, 255, 0)          # green = GO!
            led2.on()

        # Wait for the round to finish, then pause before next round
        while not state["over"]:
            await asyncio.sleep(0.01)
        await asyncio.sleep(3)

async def player(btn, name, color):
    while True:
        if btn.value() == 0:
            # TODO 2: handle false start (pressed before state["go"])
            # TODO 3: handle a valid win (pressed after GO, round not over)
            await asyncio.sleep(0.15)    # debounce
        await asyncio.sleep(0.01)

async def main():
    asyncio.create_task(referee())
    asyncio.create_task(player(btnA, "A", (0, 0, 255)))     # blue
    asyncio.create_task(player(btnB, "B", (255, 0, 255)))   # magenta
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

## Stretch goals (extra credit)

- Add LED 1 (red) as a "wait" light that mirrors the red phase (on while waiting, off at GO), and make both LEDs pulse via PWM instead of on/off.
- Track and print a running best reaction time using `time.ticks_ms()` / `time.ticks_diff()`.
- Best-of-three match: first player to win 2 rounds gets a victory animation on the DotStar.

## Submission

- Save your file as `reaction_game_<yourname>.py`.
- Demonstrate a full round to the instructor: a valid win **and** a false start.
- Submit the `.py` file through the course portal before the end of session.

---

[← Part D](../lessons/05-part-d-hardware-debounce.md) · [Home](../README.md)
