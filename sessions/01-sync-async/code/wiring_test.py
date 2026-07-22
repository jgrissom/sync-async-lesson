# ============================================================
# Wiring Test  --  Warm-up
# Python IoT on the TinyPICO : Sync vs Async
#
# Run this ONCE after wiring the breadboard. It checks every
# component in order and tells you what to watch/listen for:
#
#   1. LED 1 (red)   blinks 3 times
#   2. LED 2 (green) blinks 3 times
#   3. Buzzer beeps twice
#   4. Waits for you to press Button A (beeps to confirm)
#   5. Waits for you to press Button B (beeps to confirm)
#
# If a step fails, fix that one component before moving on --
# see TROUBLESHOOTING.md in the repo.
#
# (The onboard DotStar is NOT tested here -- it needs a library
# you'll install in Part C.)
# ============================================================

from machine import Pin
import time

led1 = Pin(26, Pin.OUT)
led2 = Pin(27, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)
btnB = Pin(5, Pin.IN, Pin.PULL_UP)


def blink(led, name):
    print("[TEST]", name, "-- watch it blink 3 times")
    for _ in range(3):
        led.on()
        time.sleep(0.3)
        led.off()
        time.sleep(0.3)


def wait_press(btn, name):
    if btn.value() == 0:
        print("[WARN]", name, "already reads PRESSED before you touched it.")
        print("       Check its wiring -- the pin may be shorted to GND.")
    print("[TEST] Press", name, "now...")
    while btn.value() == 1:
        time.sleep(0.01)
    print("       ", name, "OK")
    buzzer.on()
    time.sleep(0.1)
    buzzer.off()
    while btn.value() == 0:      # wait for release before moving on
        time.sleep(0.01)
    time.sleep(0.2)


blink(led1, "LED 1 (red, GPIO 26)")
blink(led2, "LED 2 (green, GPIO 27)")

print("[TEST] Buzzer -- listen for two beeps")
for _ in range(2):
    buzzer.on()
    time.sleep(0.15)
    buzzer.off()
    time.sleep(0.25)

wait_press(btnA, "Button A (blue cap, GPIO 18)")
wait_press(btnB, "Button B (yellow cap, GPIO 5)")

print()
print("All wiring checks passed! Your breadboard is ready.")
