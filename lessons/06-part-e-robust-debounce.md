# Part E — Robust Debouncing in Software (optional)

⏱️ **~10 min bonus** · *not part of the core 3.5 hours*

[← Part D](05-part-d-hardware-debounce.md) · [Home](../README.md) · **Next:** [Assignment →](../assignment/README.md)

---

> [!NOTE]
> A bonus for groups that finish early, or for anyone whose bench caught the "extra count on release" anomaly in [Part B's B3 experiment](03-part-b-asynchronous.md#b3--see-the-bounce-for-yourself). This part builds the fix that B3's note only described.

## 1. Recap: what the one-liner can't see

B3's fix — `await asyncio.sleep(0.15)` after a detected press — **ignores time**: it goes deaf for 150 ms and hopes the bounce is over when it wakes up. That guards the press, but nothing guards the *release*. If release chatter flickers the pin `1` → `0` after the counter has re-armed, that's a fresh falling edge, and it counts as a phantom press.

## 2. The idea: don't ignore time — require stability

The robust algorithm flips the logic: instead of *waiting a fixed time*, it *watches the pin until it proves itself stable*. Only re-arm after the pin has read **released (`1`) several polls in a row**. Chatter can't fake that — by definition, chatter doesn't hold still.

## 3. The algorithm

Upgrade B3's counter. Same immediate response on press; the change is entirely in how it re-arms:

```python
from machine import Pin
import uasyncio as asyncio

btnA = Pin(18, Pin.IN, Pin.PULL_UP)
count = 0

async def count_presses_robust():
    global count
    while True:
        # 1. Wait for a press
        while btnA.value() == 1:
            await asyncio.sleep(0.01)

        count += 1
        print("press", count)          # respond immediately, like B3

        # 2. Re-arm ONLY after a STABLE release:
        #    two consecutive released reads = released for a full 20 ms.
        #    Any bounce back to 0 resets the count to zero.
        stable = 0
        while stable < 2:
            await asyncio.sleep(0.01)
            stable = stable + 1 if btnA.value() == 1 else 0

asyncio.run(count_presses_robust())
```

The whole trick is the `stable` counter: a `1` reading earns a point, any `0` reading resets to zero, and only two points in a row unlock the next press. Release chatter — brief `1`s interrupted by `0`s — can never bank two in a row.

> [!TIP]
> **Do this: try to trick it.** Press 10 times fast. Press 10 times slowly with gentle releases (the case that fooled the one-liner). Hold it, wiggle your finger, roll off the button sideways. The count should match your presses every time. Then, for contrast, re-run B3's version and roll off the button sideways a few times.

## 4. Which debounce, when?

You now know three debounce strategies. None of them is "the best" — they solve different problems:

| Strategy | How it works | Choose it when |
|---|---|---|
| Time-based (B3's one-liner) | Go deaf for 150 ms after a press | Only the *first* press matters — like the reaction game, where a phantom edge after the round is decided breaks nothing |
| Stability-based (this part) | Re-arm only after N consecutive stable reads | *Every* edge matters — counters, toggles (a phantom edge flips a light back off!), menu navigation |
| Hardware RC filter ([Part D](05-part-d-hardware-debounce.md)) | A capacitor absorbs the chatter before the pin sees it | The CPU can't afford to poll, or the signal must be clean before your code even runs |

Real products routinely combine them — a small cap to take the edge off, plus stability logic for correctness.

## 5. Discussion

Talk these through before opening the answers.

**Q1. Why can't chatter ever satisfy the `stable` counter? What physical assumption is that relying on?**

<details>
<summary>Answer</summary>

Chatter *is* rapid alternation — by definition it can't hold `1` across two consecutive 10 ms polls, so it can never bank two points in a row. The physical assumption: contacts stop vibrating within a few milliseconds, so a *genuine* release eventually sits still longer than the 20 ms window. If a truly broken switch chattered forever, the counter would simply never re-arm — it fails safe (missed presses), never wrong (phantom presses).

</details>

**Q2. Our stability window is 2 reads × 10 ms = 20 ms. What breaks if you make it 2 × 100 ms?**

<details>
<summary>Answer</summary>

Nothing ever *miscounts* — stability is stability. But the button goes deaf for 200 ms after each release, so fast double-presses get swallowed. It's the same trade-off as Part D's over-sized `105` cap: more filtering, less responsiveness — one knob, two directions.

</details>

**Q3. The hardware cap and the `stable` counter are secretly the same idea. What does each one "average"?**

<details>
<summary>Answer</summary>

The capacitor averages *voltage* over time — spikes too brief to move its charge vanish. The counter averages *readings* over time — states too brief to survive consecutive polls vanish. One is analog and works before the pin ever sees the signal; the other is digital and works after. Same low-pass filter, two implementations.

</details>

**Q4. Refactor challenge: extract the logic into a reusable `async def clean_press(btn)` helper any program could call.**

<details>
<summary>One possible answer</summary>

```python
async def clean_press(btn):
    """Wait for one press. Returns only after the button has been
    pressed AND has sat stably released again."""
    while btn.value() == 1:          # wait for the press
        await asyncio.sleep(0.01)
    stable = 0                       # then require a stable release
    while stable < 2:
        await asyncio.sleep(0.01)
        stable = stable + 1 if btn.value() == 1 else 0

async def main():
    count = 0
    while True:
        await clean_press(btnA)
        count += 1
        print("press", count)
```

One subtlety: this version reports the press only after the *release* completes, because `clean_press` doesn't return until the pin is stable. If you need to react the instant the press lands (like the reaction game does), keep the "respond immediately" line between the two waits, as in Section 3 — the helper trades a little immediacy for a lot of reusability.

</details>

---

[← Part D](05-part-d-hardware-debounce.md) · [Home](../README.md) · **Next:** [Assignment →](../assignment/README.md)
