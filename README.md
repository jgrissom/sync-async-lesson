# Python IoT on the TinyPICO — Curriculum

A six-session, hands-on curriculum for intermediate Python students: real hardware, real concurrency, real internet — on the TinyPICO ESP32 with MicroPython and [Thonny](https://thonny.org/).

Each session is self-contained in its own folder, with lessons, a graded assignment, and runnable code.

## Sessions

| # | Session | Duration | Status |
|---|---|---|---|
| 1 | [Synchronous vs. Asynchronous Programming](sessions/01-sync-async/README.md) — feel the difference between blocking and non-blocking code with LEDs, buttons, and a reaction game | 3.5 h | ✅ Ready |
| 2 | [Wi-Fi & the Internet of Things](sessions/02-wifi-iot/README.md) — connect to Wi-Fi, fetch and parse live JSON without freezing your program, and serve a web page *from* the board | 3.5 h | ✅ Ready |
| 3 | *Coming soon* | 3.5 h | — |
| 4 | *Coming soon* | 3.5 h | — |
| 5 | *Coming soon* | 3.5 h | — |
| 6 | *Coming soon* | 3.5 h | — |

## Shared hardware

Every session uses the same bench: TinyPICO ESP32, breadboard, 2× LEDs + 330 Ω resistors, 2× momentary switches (blue + yellow caps), buzzer, jumper wires. Session 1's [wiring diagram](sessions/01-sync-async/diagrams/wiring.svg) is the reference build — later sessions reuse it as-is.

## When something breaks

→ **[Troubleshooting & FAQ](TROUBLESHOOTING.md)** — symptom-first fixes for Thonny, the board, the wiring, and Wi-Fi.

## A note on secrets

Session 2 onward uses a `secrets.py` file for Wi-Fi credentials. It is gitignored and must never be committed — each bench creates its own from the provided template.
