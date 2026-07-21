# ============================================================
# Reaction-Timer Game  --  STARTER FILE
# Python IoT on the TinyPICO : Sync vs Async
#
# Fill in the three TODO sections. When finished, save this file
# as  reaction_game_<yourname>.py  and demo it to the instructor.
#
# Wiring:
#   LED 1 (red)   -> GPIO 26 (+ 330 ohm resistor to GND)
#   LED 2 (green) -> GPIO 27 (+ 330 ohm resistor to GND)
#   Buzzer        -> GPIO 25
#   Button A (red cap)   -> GPIO 18  (other leg to GND)
#   Button B (green cap) -> GPIO 5   (other leg to GND)
#   DotStar   -> onboard (no wiring)
# ============================================================

from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar
import random

# --- Hardware setup ---
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
# go          : True once the green GO signal has shown
# over        : True once the round has been decided
# winner      : name of the winning (or false-starting) player
# false_start : True if the round ended on a false start
state = {"go": False, "over": False, "winner": None, "false_start": False}


async def buzz(times, dur=0.1):
    """Beep the buzzer `times` times."""
    for _ in range(times):
        buzzer.on()
        await asyncio.sleep(dur)
        buzzer.off()
        await asyncio.sleep(dur)


async def referee():
    """Runs the round: wait, show GO, then reset after a result."""
    while True:
        # Reset round
        state.update(go=False, over=False, winner=None, false_start=False)
        ds[0] = (255, 0, 0)   # red = wait
        led2.off()

        # ------------------------------------------------------------
        # TODO 1: Wait a RANDOM amount of time between 2 and 5 seconds
        #         before showing the GO signal.
        #   Hint: random.uniform(2, 5) gives a random float.
        #   Hint: use  await asyncio.sleep(...)  so players can still
        #         false-start during the wait.
        # ------------------------------------------------------------

        # Only show GO if nobody false-started during the wait
        if not state["over"]:
            state["go"] = True
            ds[0] = (0, 255, 0)   # green = GO!
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

            # --------------------------------------------------------
            # TODO 2: FALSE START
            #   If the GO signal has NOT shown yet (state["go"] is False)
            #   and the round is not already over, this player loses.
            #   - mark the round over, record the false start + winner name
            #   - set the DotStar to red
            #   - buzz twice   (await buzz(2))
            #   - print a message
            # --------------------------------------------------------

            # --------------------------------------------------------
            # TODO 3: VALID WIN
            #   If the GO signal HAS shown (state["go"] is True) and the
            #   round is not already over, this player wins.
            #   - mark the round over, record the winner name
            #   - set the DotStar to this player's `color`
            #   - buzz once, a bit longer  (await buzz(1, 0.3))
            #   - print a message
            # --------------------------------------------------------

            await asyncio.sleep(0.15)   # debounce
        await asyncio.sleep(0.01)       # yield to other tasks


async def main():
    asyncio.create_task(referee())
    asyncio.create_task(player(btnA, "A", (0, 0, 255)))     # blue
    asyncio.create_task(player(btnB, "B", (255, 0, 255)))   # magenta
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
