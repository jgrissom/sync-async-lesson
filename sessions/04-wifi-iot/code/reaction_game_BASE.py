# ============================================================
# Reaction-Timer Game  --  finished Session 3 game
# Python IoT on the TinyPICO : Session 4 (Wi-Fi & IoT)
#
# The canonical base for tonight's network grafts: Session 3's
# starter with its three TODOs filled in -- the same file the
# instructor live-codes in the opening review. Session 4 grafts
# networking onto a KNOWN-GOOD game; that matters, because
# networking grafted onto a buggy game debugs like a nightmare.
#
# Built your own working game in Session 3? Use it instead --
# the grafts are identical. This file is here so nobody has to
# debug two problems at once.
#
# Wiring:
#   LED 1 (red)   -> GPIO 26 (+ 330 ohm resistor to GND)
#   LED 2 (green) -> GPIO 27 (+ 330 ohm resistor to GND)
#   Buzzer        -> GPIO 25
#   Button A (blue cap)   -> GPIO 18  (other leg to GND)
#   Button B (yellow cap) -> GPIO 5   (other leg to GND)
#   DotStar   -> onboard (no wiring)
# ============================================================

from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar
import random

# --- Hardware setup ---
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

# --- Shared game state ---
state = {"go": False, "over": False, "winner": None, "false_start": False}


async def buzz(times, dur=0.1):
    """Beep the buzzer `times` times."""
    for _ in range(times):
        buzzer.on()
        await asyncio.sleep(dur)
        buzzer.off()
        await asyncio.sleep(dur)


async def wait_beacon():
    """Blink the red LED and DotStar together during the wait phase.
    Provided in the starter -- uses shared state to know when the
    round is 'ours' and keeps its hands off otherwise."""
    while True:
        if not state["go"] and not state["over"]:      # wait phase
            led1.on()
            ds[0] = (255, 0, 0)
            await asyncio.sleep(0.25)
            if not state["go"] and not state["over"]:  # still waiting?
                led1.off()
                ds[0] = (0, 0, 0)
                await asyncio.sleep(0.25)
        else:                                          # GO shown or round over
            led1.off()
            await asyncio.sleep(0.01)


async def referee():
    """Runs the round: wait, show GO, then reset after a result."""
    while True:
        # Reset round -- wait_beacon() takes over the red blinking
        state.update(go=False, over=False, winner=None, false_start=False)
        led2.off()

        # ---- TODO 1 (solution) ----------------------------------
        # One await is enough: while the referee sleeps, the player
        # coroutines keep running, so a false start during the wait
        # is caught immediately by player() -- the referee just
        # notices state["over"] afterwards and skips the GO signal.
        await asyncio.sleep(random.uniform(2, 5))
        # ---------------------------------------------------------

        # Only show GO if nobody false-started during the wait
        if not state["over"]:
            state["go"] = True
            ds[0] = (0, 255, 0)   # green = GO!
            led1.off()            # kill the wait blink instantly
            led2.on()

        # Wait for a player coroutine to end the round
        while not state["over"]:
            await asyncio.sleep(0.01)

        # Pause before the next round
        await asyncio.sleep(3)


async def player(btn, name, color):
    """Watches one button and reacts based on game state."""
    while True:
        if btn.value() == 0:   # button pressed

            # ---- TODO 2 (solution): FALSE START -----------------
            if not state["go"] and not state["over"]:
                state["over"] = True
                state["false_start"] = True
                state["winner"] = name          # the offender
                ds[0] = (255, 0, 0)             # red = loss
                print("Player", name, "FALSE START - you lose!")
                await buzz(2)
            # -----------------------------------------------------

            # ---- TODO 3 (solution): VALID WIN -------------------
            elif state["go"] and not state["over"]:
                state["over"] = True
                state["winner"] = name
                ds[0] = color                   # winner's color
                print("Player", name, "WINS!")
                await buzz(1, 0.3)
            # -----------------------------------------------------

            await asyncio.sleep(0.15)   # debounce
        await asyncio.sleep(0.01)       # yield to other tasks


async def main():
    asyncio.create_task(wait_beacon())
    asyncio.create_task(referee())
    asyncio.create_task(player(btnA, "Blue", (0, 0, 255)))       # blue cap
    asyncio.create_task(player(btnB, "Yellow", (255, 255, 0)))   # yellow cap
    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
finally:
    TinyPICO.set_dotstar_power(False)
    led1.off()
    led2.off()
