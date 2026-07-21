# Warm-up: Wiring & Setup

⏱️ **30 min**

[← Overview](00-overview.md) · [Home](../README.md) · **Next:** [Part A — Synchronous →](02-part-a-synchronous.md)

---

## 1. Pin map

> [!IMPORTANT]
> Verify these against your TinyPICO's usable-GPIO map before class — a couple of ESP32 pins are input-only or strapping pins. The choices below avoid known trouble pins.

| Component | TinyPICO GPIO | Wiring notes |
|---|---|---|
| LED 1 (red) | GPIO 26 | Anode → 330 Ω → GPIO 26; cathode → GND |
| LED 2 (green) | GPIO 27 | Anode → 330 Ω → GPIO 27; cathode → GND |
| Buzzer | GPIO 25 | + leg → GPIO 25; – leg → GND |
| Button A (red cap) | GPIO 18 | One leg → GPIO 18; opposite leg → GND |
| Button B (green cap) | GPIO 5 | One leg → GPIO 5; opposite leg → GND |
| DotStar | onboard | No wiring — built into the TinyPICO |

> [!NOTE]
> **Why pull-ups?** Buttons are wired to GND and use the ESP32's internal pull-up resistor (`Pin.PULL_UP`). The pin reads `1` when released and `0` when pressed. No external resistor needed.

### Wiring diagram

![Wiring diagram: TinyPICO GPIOs 26/27 through 330 Ω resistors to the red and green LEDs, GPIO 25 to the buzzer, GPIOs 18/5 to buttons A and B, all returning to the GND rail](../diagrams/wiring.svg)

*Printable version: open [`diagrams/wiring.svg`](../diagrams/wiring.svg) directly and print it — one per bench is handy.*

## 2. Setup checklist

1. Connect the TinyPICO via USB and open Thonny.
2. In Thonny: **Tools → Options → Interpreter** → select "MicroPython (ESP32)" and the correct COM/serial port.
3. Confirm the REPL responds: type `print('hello')` at the `>>>` prompt.
4. Build the circuit on the breadboard following the pin map above, with power **off** (USB unplugged) while wiring.

> [!TIP]
> Thonny won't connect, no `>>>` prompt, or the board seems possessed? The [Troubleshooting & FAQ](../TROUBLESHOOTING.md) covers the common failures — starting with charge-only USB cables and the wrong COM port.

## 3. Blink test — confirm your wiring

Run this first. If LED 1 blinks, your output wiring and toolchain are good.

```python
from machine import Pin
import time

led1 = Pin(26, Pin.OUT)

for _ in range(6):
    led1.on()
    time.sleep(0.25)
    led1.off()
    time.sleep(0.25)

print("Blink test complete")
```

> [!WARNING]
> **No blink?** Check LED polarity (long leg = anode = resistor side), confirm the resistor is in series, and make sure the jumper reaches the correct GPIO column on the breadboard.

---

[← Overview](00-overview.md) · [Home](../README.md) · **Next:** [Part A — Synchronous →](02-part-a-synchronous.md)
