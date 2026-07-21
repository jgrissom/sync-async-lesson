# Part D — Hardware Debounce Experiment (optional)

⏱️ **~15 min bonus** · *not part of the core 3.5 hours*

[← Part C](04-part-c-dotstar.md) · [Home](../README.md) · **Next:** [Assignment →](../assignment/README.md)

---

> [!NOTE]
> This is a bonus for groups that finish early, or a warm-up for a future session. It builds directly on the software debouncing from [Part B](03-part-b-asynchronous.md).

In Part B you debounced buttons in **software** with `await asyncio.sleep(0.15)`. A mechanical switch can also be debounced in **hardware** — a small ceramic capacitor across the button smooths out the electrical "bounce" before the pin ever sees it. This segment lets students compare the two approaches, and compare capacitor values against each other.

## 1. The idea: RC filtering

A capacitor placed between the GPIO pin and GND, together with the ESP32's internal pull-up resistor, forms an **RC low-pass filter**. Rapid bounce transitions get "averaged out" so the pin reads one clean press. The key quantity is the time constant, `τ = R × C`:

$$\tau = R \times C$$

With the internal pull-up (~45 kΩ) and a 100 nF cap: τ ≈ 45,000 × 0.0000001 ≈ 4.5 ms — long enough to swallow the bounce, short enough that a real press still feels instant. Bigger cap = more filtering, but too big and quick presses get rounded off.

## 2. The three caps under test

Ceramic capacitors are marked with a 3-digit code (first two digits + number of zeros, in picofarads). Students will compare:

| Marking | Value | Approx. τ with internal pull-up | Expected feel |
|---|---|---|---|
| `103` | 10 nF | ~0.45 ms | Weak filter — some bounce may slip through |
| `104` | 100 nF | ~4.5 ms | The sweet spot — clean and responsive |
| `105` | 1 µF | ~45 ms | Heavy filter — presses feel slightly laggy/rounded |

> [!TIP]
> **Prediction first:** Before wiring, have each group **write down** which cap they think will feel best and why. Predicting before measuring is the point of the experiment.

## 3. Wiring

Only one small change to the existing circuit — add a capacitor across Button A (between GPIO 18 and GND). Leave Button B with no cap so students have a live software-only comparison right next to it.

- Ceramic caps are **non-polarised** — either leg can go either way, orientation doesn't matter.
- One cap leg into the same breadboard row as the GPIO 18 button leg; the other leg into a GND row.
- Button B stays exactly as it was — software-debounced only.

> [!CAUTION]
> These are tiny signal-level ceramic caps at 3.3 V — completely safe to handle. This is a good moment to mention that larger **electrolytic** caps *are* polarised and can be damaged (or worse) if reversed, which is why the flyback-diode / motor topic belongs in its own later session.

## 4. Test code

This counts how many times each button "fires" for a single physical press. A perfectly debounced button counts exactly 1 per press; a bouncy one counts 2, 3, or more. Run it, press each button 10 times, and compare the counts.

📄 Full file: [`code/debounce_test.py`](../code/debounce_test.py)

```python
from machine import Pin
import uasyncio as asyncio

# Button A has a hardware cap; Button B does NOT.
btnA = Pin(18, Pin.IN, Pin.PULL_UP)   # capacitor across this one
btnB = Pin(5, Pin.IN, Pin.PULL_UP)    # no capacitor, no software debounce

counts = {"A": 0, "B": 0}

async def raw_counter(btn, name):
    # NO software debounce here on purpose -- we want to SEE the bounce.
    prev = 1
    while True:
        now = btn.value()
        if prev == 1 and now == 0:     # detect press edge
            counts[name] += 1
            print(name, "press count:", counts[name])
        prev = now
        await asyncio.sleep(0.001)     # poll fast to catch bounce

async def main():
    print("Press each button 10 times. Compare the totals.")
    asyncio.create_task(raw_counter(btnA, "A"))   # hardware-debounced
    asyncio.create_task(raw_counter(btnB, "B"))   # not debounced
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

> [!TIP]
> **What to look for:** Button B (no cap) will often over-count — one press registers as 2+ because the software debounce has been removed. Button A with a `104` cap should stay much closer to a clean 1-per-press. Then swap A's cap for `103` and `105` and re-run to feel the difference.

## 5. The experiment (comparative)

1. Predict which cap (`103` / `104` / `105`) will give the cleanest 1-per-press count. Write it down.
2. With the `104` cap on Button A, press each button 10 times. Record counts for A and B.
3. Swap the `104` for a `103`, reset (Ctrl+F2 in Thonny), and repeat. Record.
4. Swap the `103` for a `105`, reset, and repeat. Record.
5. Compare all three against Button B (no cap) and against your prediction.

## 6. Results table (students fill in)

| Cap on Button A | Presses | A counted | B counted | Cleanest? |
|---|---|---|---|---|
| `103` (10 nF) | 10 | | | |
| `104` (100 nF) | 10 | | | |
| `105` (1 µF) | 10 | | | |

## 7. Discussion — hardware vs. software debounce

- Which cap felt best? Did it match your prediction?
- Why might `105` make presses feel laggy even though it "debounces" well? *(Its ~45 ms time constant starts delaying the real signal.)*
- When would you choose hardware debounce over software? *(Hardware frees the CPU from polling and works even before your code runs; software is free, tunable, and needs no extra parts. Real designs often use **both**.)*
- How does this RC filter relate to the async software debounce from Part B — what is each one actually "ignoring"?

> [!NOTE]
> **Materials note:** Each group needs one each of `103`, `104`, and `105` caps. With 10 of each value in a standard kit and students working in pairs (~7 groups), that's comfortably enough. If working solo (13 students), have groups share the `105`s since only one is needed at a time per bench.

---

[← Part C](04-part-c-dotstar.md) · [Home](../README.md) · **Next:** [Assignment →](../assignment/README.md)
