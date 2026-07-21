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

## B1 — two LEDs, different rates, fully concurrent

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
> **Observe:** The two LEDs blink at clearly different, independent rates from a single program — something that was awkward to do synchronously. Neither `blink()` blocks the other because each yields at its `await`.

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

## A note on debouncing

Mechanical switches "bounce" — a single press can register as several rapid on/off transitions. The `await asyncio.sleep(0.15)` after a press is a simple debounce: we ignore further changes for 150 ms. Students will need this in the assignment.

> There's also a *hardware* way to debounce, explored in the optional [Part D](05-part-d-hardware-debounce.md).

---

[← Part A](02-part-a-synchronous.md) · [Home](../README.md) · **Next:** [Part C — DotStar →](04-part-c-dotstar.md)
