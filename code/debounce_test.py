# ============================================================
# Hardware Debounce Test  --  Part D (optional experiment)
# Python IoT on the TinyPICO : Sync vs Async
#
# Counts how many times each button "fires" for a single physical
# press. A perfectly debounced button counts exactly 1 per press;
# a bouncy one counts 2, 3, or more.
#
# Button A has a ceramic capacitor across it (GPIO 18 -> GND).
# Button B has NO capacitor -- and we deliberately remove the
# software debounce here so the bounce is visible for comparison.
#
# Experiment: run this with a 104 cap on Button A, press each
# button 10 times, and compare the totals. Then swap the cap for
# a 103 and a 105 and re-run (Ctrl+F2 in Thonny resets).
# ============================================================

from machine import Pin
import uasyncio as asyncio

btnA = Pin(18, Pin.IN, Pin.PULL_UP)   # capacitor across this one
btnB = Pin(5, Pin.IN, Pin.PULL_UP)   # no capacitor, no software debounce

counts = {"A": 0, "B": 0}


async def raw_counter(btn, name):
    # NO software debounce on purpose -- we want to SEE the bounce.
    prev = 1
    while True:
        now = btn.value()
        if prev == 1 and now == 0:      # falling edge = press
            counts[name] += 1
            print(name, "press count:", counts[name])
        prev = now
        await asyncio.sleep(0.001)      # poll fast to catch bounce


async def main():
    print("Press each button 10 times. Compare the totals.")
    print("Button A = hardware cap | Button B = none")
    asyncio.create_task(raw_counter(btnA, "A"))
    asyncio.create_task(raw_counter(btnB, "B"))
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
