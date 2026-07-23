# ============================================================
# Reaction game -- WALKTHROUGH edition (everything commented out)
# Python IoT on the TinyPICO : Session 4 opener
#
# The file from the opening class walkthrough. Re-play it at home:
# uncomment one layer at a time -- main() -> wait_beacon -> referee
# -> players -> the two handler blocks -- and BEFORE each run,
# predict what the board will do. The gap between your prediction
# and what happens is where the learning is.
#
# Finished version: reaction_game_BASE.py (same folder).
# ============================================================
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

        # wait a RANDOM 2-5 seconds before GO
        # await asyncio.sleep(random.uniform(2, 5))

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
            print("pressed:", name)
            # handle false start (pressed before state["go"])
#             if not state["go"] and not state["over"]:
#                 state["over"] = True
#                 state["false_start"] = True
#                 state["winner"] = name          # the offender
#                 ds[0] = (255, 0, 0)             # red = loss
#                 print("Player", name, "FALSE START - you lose!")
#                 await buzz(2)
            # handle a valid win (pressed after GO, round not over)
#             elif state["go"] and not state["over"]:
#                 state["over"] = True
#                 state["winner"] = name
#                 ds[0] = color                   # winner's color
#                 print("Player", name, "WINS!")
#                 await buzz(1, 0.3)
            await asyncio.sleep(0.15)    # debounce
        await asyncio.sleep(0.01)

async def main():
    #asyncio.create_task(wait_beacon())
    #asyncio.create_task(referee())
    #asyncio.create_task(player(btnA, "Blue", (0, 0, 255)))       # blue cap
    #asyncio.create_task(player(btnB, "Yellow", (255, 255, 0)))   # yellow cap
    #while True:
        #await asyncio.sleep(1)
        #pass
    pass

# Cleanup runs even when you stop the program (Ctrl+C / Ctrl+F2)
try:
    #asyncio.run(main())
    pass
finally:
    TinyPICO.set_dotstar_power(False)
    led1.off()
    led2.off()
