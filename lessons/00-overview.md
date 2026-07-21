# Session Overview & Timing

[← Back to home](../README.md) · **Next:** [Warm-up: Wiring & Setup →](01-setup.md)

---

This session teaches the difference between blocking (synchronous) and non-blocking (asynchronous) code by having students physically feel it. In the synchronous version, a button press is ignored while an LED is mid-blink; in the async version, everything responds at once. Students build up from a single blinking LED to a fully concurrent program driving multiple outputs and reading multiple inputs simultaneously, then complete a graded assignment.

## Time budget (3.5 hours / 210 minutes)

| Block | Activity | Time |
|---|---|---|
| Warm-up | Setup check, wiring the breadboard, blink test | 30 min |
| Part A | Synchronous programming — feel the blocking problem | 35 min |
| Break | Stretch / troubleshoot | 10 min |
| Part B | Asynchronous programming with `uasyncio` | 45 min |
| Part C | Adding the onboard DotStar as a concurrent task | 25 min |
| Break | Stretch | 5 min |
| Assignment | Reaction-timer game (graded, in-class build) | 50 min |
| Wrap-up | Demos, review, Q&A | 10 min |
| *Optional* | *Part D — hardware debounce experiment (if time permits)* | *+15 min* |

> [!TIP]
> Part D is a bonus experiment, **not** part of the core 210 minutes. Run it only if a group finishes the assignment early, or slot it into a future session. It pairs naturally with the software debouncing taught in Part B.

## Learning objectives

By the end of the session, students will be able to:

- Explain, in their own words, what makes `time.sleep()` blocking and why it prevents responsive input handling.
- Structure a program as multiple concurrent coroutines using `uasyncio`.
- Use `await asyncio.sleep()` to yield control instead of freezing the CPU.
- Debounce a momentary switch in software.
- Drive the TinyPICO's onboard DotStar (APA102) RGB LED over SPI.
- Combine multiple inputs and outputs in a single non-blocking event loop.

---

[← Back to home](../README.md) · **Next:** [Warm-up: Wiring & Setup →](01-setup.md)
