# Part B — Asynchronous Programming

⏱️ **45 min**

[← Part A](02-part-a-synchronous.md) · [Home](../README.md) · **Next:** [Part C — DotStar →](04-part-c-dotstar.md)

---

MicroPython includes `uasyncio`, a cooperative scheduler. You write independent **coroutines** (async functions), and each one voluntarily hands control back to the scheduler whenever it hits `await`. While one coroutine is "sleeping," others run. Nothing is truly frozen.

## B0 — three key ideas

| Syntax | Meaning |
|---|---|
| `async def foo():` | Defines a coroutine — a function that can pause and resume. |
| `await asyncio.sleep(t)` | Pause **this** coroutine for `t` seconds and let others run. Non-blocking. |
| `asyncio.create_task(foo())` | Schedule a coroutine to run concurrently with others. |

## B1A — one LED, your first coroutine

Start by translating Part A's blink, line for line, into async form. Three mechanical changes: `def` becomes `async def`, `time.sleep()` becomes `await asyncio.sleep()`, and `asyncio.run()` starts it.

```python
from machine import Pin
import uasyncio as asyncio

led1 = Pin(26, Pin.OUT)

async def blink(led, rate):
    while True:
        led.value(not led.value())   # toggle
        await asyncio.sleep(rate)    # yield — though nothing else is running... yet

asyncio.run(blink(led1, 0.5))
```

> [!NOTE]
> **Run it — and notice it's completely unimpressive.** One LED, blinking, exactly like Part A. With a single coroutine there's nobody to hand control *to*, so all this ceremony buys nothing yet. That's the honest truth about async: one task alone gains nothing. The payoff needs a second task — next.

## B1B — a second LED, a different rate, fully concurrent

Now the one genuinely new idea: `asyncio.create_task()` schedules a coroutine to run *alongside* whatever else is running. Same `blink()` function as B1A — called twice, with different LEDs and rates:

```python
from machine import Pin
import uasyncio as asyncio

led1 = Pin(26, Pin.OUT)
led2 = Pin(27, Pin.OUT)

async def blink(led, rate):
    while True:
        led.value(not led.value())   # toggle
        await asyncio.sleep(rate)     # yield — others run meanwhile

async def main():
    asyncio.create_task(blink(led1, 0.5))   # fast
    asyncio.create_task(blink(led2, 0.9))   # slow
    while True:
        await asyncio.sleep(1)              # keep the loop alive

asyncio.run(main())
```

> [!NOTE]
> **Observe:** The two LEDs blink at clearly different, independent rates from a single program — something that was awkward to do synchronously. Neither `blink()` blocks the other because each yields at its `await`. Try writing this with `time.sleep()` in your head: whose sleep goes first? That's the tangle A2 warned about, dissolved.

## B2 — add responsive buttons and a buzzer

Now buttons get their own coroutine. Because everything yields, presses are caught almost instantly — no missed inputs, no rewritten sleep.

```python
from machine import Pin
import uasyncio as asyncio

led1 = Pin(26, Pin.OUT)
led2 = Pin(27, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)
btnB = Pin(5, Pin.IN, Pin.PULL_UP)

async def blink(led, rate):
    while True:
        led.value(not led.value())
        await asyncio.sleep(rate)

async def watch_button(btn):
    while True:
        if btn.value() == 0:          # pressed
            buzzer.on()
            await asyncio.sleep(0.15)
            buzzer.off()
            await asyncio.sleep(0.15) # crude debounce
        await asyncio.sleep(0.01)     # poll ~100x/sec, yields each time

async def main():
    asyncio.create_task(blink(led1, 0.5))
    asyncio.create_task(blink(led2, 0.9))
    asyncio.create_task(watch_button(btnA))
    asyncio.create_task(watch_button(btnB))
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

> [!TIP]
> **Do this:** Run it and press either button while both LEDs blink. The buzzer responds immediately every time — contrast this directly with Example A1, where presses were dropped.

## B3 — see the bounce for yourself

B2's button coroutine contains a mysterious `await asyncio.sleep(0.15)` labeled "crude debounce." Before trusting it, let's *see* the problem it solves. Mechanical switches don't close cleanly — the metal contacts physically vibrate for a few milliseconds, producing a burst of rapid on/off transitions called **bounce**. Your code polls fast enough to catch them all.

This counter has **no debounce at all**. It counts every press it detects:

```python
from machine import Pin
import uasyncio as asyncio

btnA = Pin(18, Pin.IN, Pin.PULL_UP)
count = 0

async def count_presses():
    global count
    prev = 1
    while True:
        now = btnA.value()
        if prev == 1 and now == 0:   # falling edge = a "press"
            count += 1
            print("press", count)
        prev = now
        await asyncio.sleep(0.001)   # poll fast enough to catch bounce

asyncio.run(count_presses())
```

> [!TIP]
> **Do this:** Press Button A exactly 10 times, counting out loud. Watch the printed count race past you — 13, 17, sometimes 25. Every extra count is one physical press registering as several electrical ones. *(If your button happens to be unusually clean, press slower and softer — a gentle release bounces more.)*
>
> **Now fix it with one line:** add `await asyncio.sleep(0.15)` directly under the `print(...)` line and run it again. Ten presses, count of ten. That single line ignores the pin for 150 ms after each detected press — longer than any bounce burst, shorter than any intentional second press.

> [!NOTE]
> **Still catching an occasional extra count even with the fix?** Nothing is broken — you've discovered that *releases* bounce too. Walk through the code: the 150 ms sleep starts when a **press** is detected. By the time you let go, the counter is re-armed and watching again — and if the release chatter happens to flicker the pin `1` then `0` between two polls, that's a brand-new falling edge, indistinguishable from a press. The one-liner ignores bounce *after a detection*, but nothing guards the moment of release.
>
> A fully robust debounce closes that gap by refusing to re-arm until the pin has sat **stable at released (`1`)** for some time — ignoring *state changes*, not just time. We stick with the one-liner here because it's one line, and in the reaction game a round ends on the first press anyway, so a phantom edge at release has nothing left to break. But if you saw this happen on your bench, you now understand debouncing better than the fix does — and the optional [Part E](06-part-e-robust-debounce.md) lets you build the bulletproof version yourself.

## A note on debouncing

What you just saw is why B2's button coroutine sleeps for 0.15 s after each press — and why the reaction-game assignment's rubric has a "no double-triggers" row. Debouncing isn't optional polish; an undebounced button in the game would register one press as several and instantly decide rounds twice.

> There's also a *hardware* way to debounce — smoothing the bounce out with a capacitor before the pin ever sees it — explored in the optional [Part D](05-part-d-hardware-debounce.md). It reuses this exact counter, so you've already met the test rig.

---

[← Part A](02-part-a-synchronous.md) · [Home](../README.md) · **Next:** [Part C — DotStar →](04-part-c-dotstar.md)
