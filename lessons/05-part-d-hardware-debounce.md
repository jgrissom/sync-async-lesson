# Part D — Hardware Debounce Experiment (optional)

⏱️ **~25 min bonus** · *not part of the core 3.5 hours*

[← Part C](04-part-c-dotstar.md) · [Home](../README.md) · **Next:** [Part E — Robust Debounce →](06-part-e-robust-debounce.md)

---

> [!NOTE]
> This is a bonus for groups that finish early, or a warm-up for a future session. It builds directly on the software debouncing from [Part B](03-part-b-asynchronous.md).

In Part B you debounced buttons in **software** with `await asyncio.sleep(0.15)`. A mechanical switch can also be debounced in **hardware** — a small ceramic capacitor across the button smooths out the electrical "bounce" before the pin ever sees it. This segment lets students compare the two approaches, and compare capacitor values against each other.

## 1. First: what does a capacitor actually do?

A capacitor is two metal plates separated by a thin insulator. It **stores electric charge** — think of it as a tiny rechargeable bucket. Two properties matter here:

1. **The voltage across a capacitor cannot jump instantly.** To change it, charge has to physically flow in or out of the plates first.
2. **A resistor in the path limits how fast that charge can flow** — like filling a bucket through a narrow hose. Big bucket (more capacitance) or narrow hose (more resistance) = slower fill.

That combination — *voltage that can only change gradually* — is why capacitors show up everywhere in electronics:

- **Smoothing** power supplies (riding out brief dips and spikes)
- **Filtering** noise out of signals ← *what we're doing today*
- **Timing** circuits (the charge time *is* the delay)
- **Decoupling** — the little cap you'll see parked next to almost every chip on a circuit board, feeding it charge during sudden demand

For debouncing, the intuition is: switch bounce is a burst of very fast voltage spikes. A capacitor is a bucket that fast spikes are too brief to fill or empty — so they vanish. A real, sustained press is slow enough to move the bucket's level all the way.

## 2. The RC filter and τ = R × C

Our circuit has three parts: the ESP32's internal **pull-up resistor** (R) connecting the pin to 3.3 V, the **capacitor** (C) from the pin to GND, and the button across the capacitor. Together R and C form an **RC low-pass filter**: slow changes pass through, fast changes ("high frequencies" — like bounce) are smoothed away.

- **Press:** the button shorts the capacitor to GND — it empties almost instantly, and the pin reads `0` right away. Presses still feel immediate.
- **Bounce:** each bounce glitch opens the contact for only a few *microseconds to a millisecond*. In that blink, the capacitor can only recharge a tiny fraction through the pull-up — nowhere near enough for the pin to read `1`. The glitch is invisible.
- **Release:** the contact stays open, so the capacitor charges steadily through the pull-up until the pin cleanly reads `1` a few milliseconds later.

How fast is "steadily"? That's exactly what the **time constant** measures:

$$\tau = R \times C$$

- **Units check:** ohms × farads = **seconds**. The formula hands you a time.
- **What τ means physically:** after one τ, the capacitor has covered about **63%** of the way to its target voltage; after about **5τ** it's essentially all the way there. (The curve is a rising exponential, $V(t) = V_{max}(1 - e^{-t/\tau})$ — fast at first, then leveling off, like a bucket filling from a hose that slows as pressure equalizes.)

**Worked example** — internal pull-up ≈ 45 kΩ, cap = 100 nF (that's 100 × 10⁻⁹ F):

$$\tau = 45{,}000 \ \Omega \times 0.000\,000\,1 \ \text{F} = 0.0045 \ \text{s} = 4.5 \ \text{ms}$$

Now compare timescales, because that comparison *is* the design: bounce glitches last roughly 0.01–1 ms — much shorter than τ = 4.5 ms, so they're swallowed. A human noticing lag takes ~50+ ms — much longer than 4.5 ms, so the filter is imperceptible. The `104` cap sits in the comfortable gap between the two.

That gap is also the trade-off knob: **bigger C → bigger τ → stronger filtering, but a slower, "rounder" response.** Push τ toward human-noticeable territory (the `105`'s ~45 ms) and presses start to feel laggy. Shrink it toward bounce territory (the `103`'s ~0.45 ms) and glitches sneak through. You'll *feel* both failure modes in the experiment below.

> [!NOTE]
> **Reading capacitor units:** capacitance is measured in farads (F), but a whole farad is enormous — real caps are labeled in **µF** (10⁻⁶), **nF** (10⁻⁹), and **pF** (10⁻¹²). Handy ladder: 1 µF = 1,000 nF = 1,000,000 pF.

## 3. The three caps under test

Ceramic capacitors are marked with a 3-digit code (first two digits + number of zeros, in picofarads). Students will compare:

| Marking | Value | Approx. τ with internal pull-up | Expected feel |
|---|---|---|---|
| `103` | 10 nF | ~0.45 ms | Weak filter — some bounce may slip through |
| `104` | 100 nF | ~4.5 ms | The sweet spot — clean and responsive |
| `105` | 1 µF | ~45 ms | Heavy filter — presses feel slightly laggy/rounded |

> [!TIP]
> **Prediction first:** Before wiring, have each group **write down** which cap they think will feel best and why. Predicting before measuring is the point of the experiment.

## 4. Wiring

Only one small change to the existing circuit — add a capacitor across Button A (between GPIO 18 and GND). Leave Button B with no cap so students have a live software-only comparison right next to it.

- Ceramic caps are **non-polarised** — either leg can go either way, orientation doesn't matter.
- One cap leg into the same breadboard row as the GPIO 18 button leg; the other leg into a GND row.
- Button B stays exactly as it was — software-debounced only.

> [!CAUTION]
> These are tiny signal-level ceramic caps at 3.3 V — completely safe to handle. This is a good moment to mention that larger **electrolytic** caps *are* polarised and can be damaged (or worse) if reversed, which is why the flyback-diode / motor topic belongs in its own later session.

## 5. Test code

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
        await asyncio.sleep(0)         # yield, then look again immediately

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

## 6. The experiment (comparative)

1. Predict which cap (`103` / `104` / `105`) will give the cleanest 1-per-press count. Write it down.
2. With the `104` cap on Button A, press each button 10 times. Record counts for A and B.
3. Swap the `104` for a `103`, reset (Ctrl+F2 in Thonny), and repeat. Record.
4. Swap the `103` for a `105`, reset, and repeat. Record.
5. Compare all three against Button B (no cap) and against your prediction.

## 7. Results table (students fill in)

| Cap on Button A | Presses | A counted | B counted | Cleanest? |
|---|---|---|---|---|
| `103` (10 nF) | 10 | | | |
| `104` (100 nF) | 10 | | | |
| `105` (1 µF) | 10 | | | |

## 8. Discussion — hardware vs. software debounce

Talk these through before opening the answers.

**Q1. Which cap felt best? Did it match your prediction?**

<details>
<summary>Answer</summary>

Most benches land on the `104` (100 nF): its τ ≈ 4.5 ms sits comfortably between bounce (too fast to survive it) and human perception (too slow to notice it). But there's no wrong answer here — the point of the experiment is comparing your prediction against a measurement, and a bench that predicted `105` and then *felt* the lag learned the most.

</details>

**Q2. Why might `105` make presses feel laggy even though it "debounces" well?**

<details>
<summary>Answer</summary>

Its τ ≈ 45 ms is big enough to start delaying the *real* signal, not just the bounce. The filter can't tell a genuine edge from chatter — it slows everything down equally, and at ~45 ms the delay crosses into territory humans can feel. Filtering strength and responsiveness are the same knob turned in opposite directions.

</details>

**Q3. When would you choose hardware debounce over software?**

<details>
<summary>Answer</summary>

Hardware frees the CPU from polling and works even before your code runs (or if it crashes); software is free, instantly tunable, and needs no extra parts. Real designs often use **both** — a small cap to take the edge off, software for correctness.

</details>

**Q4. How does this RC filter relate to the async software debounce from Part B — what is each one actually "ignoring"?**

<details>
<summary>Answer</summary>

The RC filter ignores *fast voltage transitions* — spikes too brief to move the capacitor's charge. The `await asyncio.sleep(0.15)` ignores *state changes for a fixed time* after a detected press. Both make the same bet: bounce is much shorter than the window, real presses are much longer. One averages in analog before the pin sees anything; the other averages in code after it does. (The optional [Part E](06-part-e-robust-debounce.md) adds a third variant: ignore state changes until the pin *proves it's stable*.)

</details>

> [!NOTE]
> **Materials note:** Each group needs one each of `103`, `104`, and `105` caps. With 10 of each value in a standard kit and students working in pairs (~7 groups), that's comfortably enough. If working solo (13 students), have groups share the `105`s since only one is needed at a time per bench.

---

[← Part C](04-part-c-dotstar.md) · [Home](../README.md) · **Next:** [Part E — Robust Debounce →](06-part-e-robust-debounce.md)
