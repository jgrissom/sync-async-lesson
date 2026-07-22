# Assignment — Reaction-Timer Game

⏱️ **50 min** · 🎯 **Graded — 100 points**

[← Part E](../lessons/06-part-e-robust-debounce.md) · [Home](../README.md)

---

Build a two-player reaction game that ties everything together. Work individually or in pairs.

## How the game works

1. On start, the DotStar and the **red LED blink red together** — the wait phase. Players hover, fingers ready.
2. After a **random delay of 2–5 seconds**, the blinking stops: the DotStar turns **solid green** and LED 2 (the green LED) lights — this is the "GO" signal.
3. The **first player to press** their button after GO wins: sound the buzzer and flash the DotStar the winner's **cap color** — Player Blue's button has the blue cap, Player Yellow's the yellow cap, and the DotStar flashes that exact color. (Red and green are deliberately reserved: red always means *wait/lose*, green always means *GO*.)
4. If a player presses **before** the green GO signal (a **false start**), they lose immediately — flash the DotStar red and buzz twice.
5. After a result, wait 3 seconds, then reset for another round automatically.

## Requirements (grading rubric)

| #   | Requirement                                                                                             | Points |
| --- | ------------------------------------------------------------------------------------------------------- | ------ |
| 1   | Program uses `uasyncio` with at least two concurrent tasks (no blocking `time.sleep` in the main logic) | 25     |
| 2   | Random 2–5 s delay before GO (use the `random` module)                                                  | 15     |
| 3   | Correctly detects the first button pressed after GO and names the winner                                | 20     |
| 4   | False-start detection: pressing before GO loses                                                         | 15     |
| 5   | DotStar and buzzer feedback for win, loss, and false start                                              | 15     |
| 6   | Buttons are debounced; no double-triggers                                                               | 10     |

**Total: 100 points.**

## Starter scaffold

Fill in the three TODOs. Full file: [`code/reaction_game_STARTER.py`](../code/reaction_game_STARTER.py)

```python
from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar
import random

led1 = Pin(26, Pin.OUT)   # red LED = wait beacon
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

async def wait_beacon():
    # Provided: blinks red LED + DotStar during the wait phase,
    # hands-off otherwise (same shared-state move as Part C's flag)
    while True:
        if not state["go"] and not state["over"]:      # wait phase
            led1.on();  ds[0] = (255, 0, 0)
            await asyncio.sleep(0.25)
            if not state["go"] and not state["over"]:  # still waiting?
                led1.off();  ds[0] = (0, 0, 0)
                await asyncio.sleep(0.25)
        else:
            led1.off()
            await asyncio.sleep(0.01)

async def referee():
    while True:
        # Reset round -- wait_beacon() takes over the red blinking
        state.update(go=False, over=False, winner=None, false_start=False)
        led2.off()

        # TODO 1: wait a RANDOM 2-5 seconds before GO
        # (hint: random.uniform, await asyncio.sleep)

        if not state["over"]:            # nobody false-started
            state["go"] = True
            ds[0] = (0, 255, 0)          # green = GO!
            led1.off()                   # kill the wait blink instantly
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
    asyncio.create_task(wait_beacon())
    asyncio.create_task(referee())
    asyncio.create_task(player(btnA, "Blue", (0, 0, 255)))       # blue cap
    asyncio.create_task(player(btnB, "Yellow", (255, 255, 0)))   # yellow cap
    while True:
        await asyncio.sleep(1)

# Cleanup runs even when you stop the program (Ctrl+C / Ctrl+F2)
try:
    asyncio.run(main())
finally:
    TinyPICO.set_dotstar_power(False)
    led1.off()
    led2.off()
```

## Stretch goals (extra credit)

- Make the wait beacon *pulse* smoothly via PWM instead of blinking on/off (and dim the GO LED to a comfortable brightness while you're at it).
- Track and print a running best reaction time using `time.ticks_ms()` / `time.ticks_diff()`.
- Best-of-three match: first player to win 2 rounds gets a victory animation on the DotStar.

---

[← Part E](../lessons/06-part-e-robust-debounce.md) · [Home](../README.md)
