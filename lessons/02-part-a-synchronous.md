# Part A — Synchronous Programming

⏱️ **35 min**

[← Setup](01-setup.md) · [Home](../README.md) · **Next:** [Part B — Asynchronous →](03-part-b-asynchronous.md)

---

Synchronous code runs **one line at a time, top to bottom**. When a line says `time.sleep(1)`, the entire program stops there for a full second — the CPU does nothing else, including checking buttons. This is called ***blocking***.

## A1 — a blinking LED that ignores you

```python
from machine import Pin
import time

led1 = Pin(26, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)

print("Press Button A while the LED blinks...")

while True:
    led1.on()
    time.sleep(1)          # <-- blocked here for 1 whole second
    led1.off()
    time.sleep(1)          # <-- blocked here too

    # Button is only ever checked at THIS instant, once every 2s
    if btnA.value() == 0:
        buzzer.on()
        time.sleep(0.2)
        buzzer.off()
```

> [!TIP]
> **Do this:** Run it, then mash Button A repeatedly. The buzzer only fires if you happen to be holding the button at the exact moment execution reaches the check — most presses are missed entirely. That gap is the blocking problem.

## A2 — why "just add more checks" doesn't scale

A common first instinct is to sprinkle button checks between sleeps. It helps a little but gets messy fast, and the LED timing drifts as you add logic:

```python
from machine import Pin
import time

led1 = Pin(26, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)

def responsive_sleep(seconds):
    # Poll the button in small slices instead of one big sleep
    steps = int(seconds / 0.02)
    for _ in range(steps):
        if btnA.value() == 0:
            buzzer.on()
        else:
            buzzer.off()
        time.sleep(0.02)

while True:
    led1.on()
    responsive_sleep(1)
    led1.off()
    responsive_sleep(1)
```

This works — but notice you had to **rewrite sleep itself**. Now imagine two LEDs blinking at different rates plus two buttons plus a buzzer. The hand-rolled polling becomes a tangle. **This is exactly the problem asynchronous programming solves.**

## Discussion (5 min)

Talk these through before opening the answers.

**Q1. What is the longest a button press could be ignored in Example A1?**

<details>
<summary>Answer</summary>

Just under ~2.2 seconds. The button is sampled exactly once per trip around the loop, and a full trip is two `time.sleep(1)` calls — plus, if the previous press *was* caught, another 0.2 s of buzzer sleep. Press a millisecond after the check and your press waits for all of it.

</details>

**Q2. Why does `responsive_sleep()` reduce the problem but not eliminate the underlying awkwardness?**

<details>
<summary>Answer</summary>

It shrinks the deaf window from ~2 s to 20 ms, but the *structure* is wrong: the button logic is now welded inside a sleep function. Every new input or output multiplies the hand-rolled polling (two LEDs at different rates + two buttons + a buzzer would tangle immediately), and the LED timing drifts as the logic inside the loop grows. `responsive_sleep()` is a scheduler, reimplemented badly — Part B replaces it with a real one.

</details>

---

[← Setup](01-setup.md) · [Home](../README.md) · **Next:** [Part B — Asynchronous →](03-part-b-asynchronous.md)
