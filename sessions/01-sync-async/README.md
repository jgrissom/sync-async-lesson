# Session 1 — Synchronous vs. Asynchronous Programming

*Part of the [Python IoT on the TinyPICO curriculum](../../README.md).*

A hands-on 3.5-hour session that teaches the difference between **blocking (synchronous)** and **non-blocking (asynchronous)** code by letting students *physically feel* it: in the synchronous version a button press is ignored while an LED is mid-blink; in the async version everything responds at once.

| | |
|---|---|
| **Duration** | 3.5 hours (210 min) + optional bonus segment |
| **Level** | Intermediate Python |
| **Environment** | [Thonny](https://thonny.org/) + MicroPython |
| **Board** | TinyPICO ESP32 |

---

## Lesson navigation

Work through these in order:

1. [Session Overview & Timing](lessons/00-overview.md)
2. [Warm-up: Wiring & Setup](lessons/01-setup.md) — *30 min*
3. [Part A — Synchronous Programming](lessons/02-part-a-synchronous.md) — *35 min*
4. [Part B — Asynchronous Programming](lessons/03-part-b-asynchronous.md) — *45 min*
5. [Part C — The Onboard DotStar](lessons/04-part-c-dotstar.md) — *25 min*
6. [Part D — Hardware Debounce Experiment (optional)](lessons/05-part-d-hardware-debounce.md) — *bonus*
7. [Part E — Robust Debouncing in Software (optional)](lessons/06-part-e-robust-debounce.md) — *bonus*
8. [Assignment — Reaction-Timer Game](assignment/README.md) — *50 min, graded*

Something not working? → **[Troubleshooting & FAQ](../../TROUBLESHOOTING.md)** (wrong COM port, `OSError: 28`, crashed async loops, dark DotStar, and more).

## Code files

| File | What it is |
|---|---|
| [`code/wiring_test.py`](code/wiring_test.py) | Warm-up: guided check of every component after wiring |
| [`code/reaction_game_STARTER.py`](code/reaction_game_STARTER.py) | Scaffold students fill in (three TODOs) |
| [`code/debounce_test.py`](code/debounce_test.py) | Part D hardware-debounce test code |

---

## What students will be able to do

- Explain what makes `time.sleep()` blocking and why it prevents responsive input handling
- Structure a program as multiple concurrent coroutines using `uasyncio`
- Use `await asyncio.sleep()` to yield control instead of freezing the CPU
- Debounce a momentary switch in software (and, optionally, in hardware)
- Drive the TinyPICO's onboard DotStar (APA102) RGB LED over SPI
- Combine multiple inputs and outputs in a single non-blocking event loop

## Hardware needed

TinyPICO ESP32, breadboard, 2× LEDs + 330 Ω resistors, 2× momentary switches, buzzer, jumper wires. The optional Part D also uses ceramic capacitors (103 / 104 / 105). A printable [wiring diagram](diagrams/wiring.svg) is in the setup guide.

> [!NOTE]
> Before class, verify the GPIO pins in [the setup guide](lessons/01-setup.md) against your TinyPICO's usable-pin map, and make sure each board has the TinyPICO helper libraries. On the official firmware `tinypico` is usually built in, but the DotStar driver (`micropython_dotstar.py`) generally needs to be uploaded — [Part C](lessons/04-part-c-dotstar.md) has step-by-step instructions.
