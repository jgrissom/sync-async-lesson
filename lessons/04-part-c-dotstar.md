# Part C — The Onboard DotStar

⏱️ **25 min**

[← Part B](03-part-b-asynchronous.md) · [Home](../README.md) · **Next:** [Part D — Hardware Debounce →](05-part-d-hardware-debounce.md)

---

The TinyPICO has a built-in **DotStar** (APA102) RGB LED — no wiring required. It's driven over SPI, and TinyPICO's helper library exposes the correct pins so students never hardcode them. It makes an excellent *smooth status animation*: any blocking in your code makes the animation visibly stutter, so it's a living proof that your async loop is healthy.

> [!IMPORTANT]
> **Before this part, both boards need the TinyPICO helper libraries.** On UnexpectedMaker's official TinyPICO firmware, `tinypico.py` is usually frozen into the firmware (so `import tinypico` just works), but the DotStar driver is not — you'll need to add `micropython_dotstar.py` yourself. If `import tinypico` fails too, add both files.

**Getting the libraries (once, on your computer):**

1. Go to [github.com/tinypico/tinypico-micropython](https://github.com/tinypico/tinypico-micropython).
2. Click the green **Code** button → **Download ZIP**, then unzip it.
3. Open the `tinypico-helper` folder. The two files you may need are `micropython_dotstar.py` and `tinypico.py`.

**Uploading to each TinyPICO (via Thonny):**

1. Plug in the board and connect Thonny to the MicroPython interpreter.
2. Turn on the file browser: **View → Files** (shows your computer on top, the board below).
3. In the top pane, open the `tinypico-helper` folder.
4. Right-click `micropython_dotstar.py` → **Upload to /**. If needed, do the same for `tinypico.py`.
5. Verify at the REPL: `import micropython_dotstar` and `import tinypico` should both return with no error.

> [!NOTE]
> The import in the code below is `from micropython_dotstar import DotStar` — matching the file's real name. Don't rename the file to `dotstar.py`; keep the name and the import in sync.

## C1 — set the DotStar to a color

```python
from machine import Pin, SoftSPI
import tinypico as TinyPICO
from micropython_dotstar import DotStar

spi = SoftSPI(sck=Pin(TinyPICO.DOTSTAR_CLK),
              mosi=Pin(TinyPICO.DOTSTAR_DATA),
              miso=Pin(TinyPICO.SPI_MISO))   # miso unused but required
ds = DotStar(spi, 1, brightness=0.3)         # 1 pixel, 30% brightness
TinyPICO.set_dotstar_power(True)             # enable DotStar power

ds[0] = (255, 0, 0)    # red   (R, G, B)
# ds[0] = (0, 255, 0)  # green
# ds[0] = (0, 0, 0)    # off
```

## C2 — DotStar as a concurrent rainbow heartbeat

Here the DotStar becomes another concurrent task: smoothly cycling colors while LEDs blink and buttons stay responsive. Build it in three stages, **testing after each one** — if a stage breaks, the fault is in the code you just added.

### C2A — the rainbow, alone

Start a fresh file with the DotStar setup from C1, plus two new pieces: `wheel()`, which converts a position on a 0–254 color wheel into an (R, G, B) tuple, and a `rainbow()` coroutine that nudges along that wheel 50 times a second.

```python
from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar

spi = SoftSPI(sck=Pin(TinyPICO.DOTSTAR_CLK),
              mosi=Pin(TinyPICO.DOTSTAR_DATA),
              miso=Pin(TinyPICO.SPI_MISO))
ds = DotStar(spi, 1, brightness=0.3)
TinyPICO.set_dotstar_power(True)

def wheel(pos):
    pos %= 255
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

async def rainbow():
    pos = 0
    while True:
        ds[0] = wheel(pos)
        pos = (pos + 2) % 255
        await asyncio.sleep(0.02)   # 50 updates/sec = smooth glide

asyncio.run(rainbow())
```

> [!TIP]
> **Test:** the DotStar should glide seamlessly through the spectrum — no steps, no flicker. Memorize how *smooth* looks; that smoothness is about to become your instrument.

### C2B — add the blinking LEDs

Three additions to the same file — the LEDs near the top, `blink()` next to `rainbow()`, and a `main()` that schedules all three tasks **replacing** the `asyncio.run(rainbow())` line at the bottom:

```python
# near the top, with the other setup:
led1 = Pin(26, Pin.OUT)
led2 = Pin(27, Pin.OUT)

# alongside rainbow():
async def blink(led, rate):
    while True:
        led.value(not led.value())
        await asyncio.sleep(rate)

# REPLACE  asyncio.run(rainbow())  at the bottom with:
async def main():
    asyncio.create_task(blink(led1, 0.5))
    asyncio.create_task(blink(led2, 0.9))
    asyncio.create_task(rainbow())
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

> [!TIP]
> **Test:** both LEDs blink at their own rates *and the rainbow is exactly as smooth as before*. Three tasks, zero interference — stare at the DotStar while the LEDs blink and confirm it never hiccups.

### C2C — add the buttons… then sabotage everything

Last additions: buzzer and buttons, and a `watch_button()` coroutine that beeps and flashes the DotStar white on a press. But there's a wrinkle worth understanding *before* you type it.

**Two tasks now want the same pixel.** If `watch_button()` simply wrote white to `ds[0]`, you'd barely see it: `rainbow()` repaints that pixel every 20 ms, so the white would survive for at most one frame before the rainbow overwrote it. When concurrent tasks share a resource, they have to *coordinate* — here, with a shared `flashing` flag that the rainbow checks before painting. (Remember this move: the reaction-game assignment is built entirely on tasks coordinating through shared state.)

```python
# near the top, with the other setup:
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)
btnB = Pin(5, Pin.IN, Pin.PULL_UP)
flashing = False   # True while a button flash owns the DotStar

# ONE CHANGE inside rainbow(): paint only when no flash is active
async def rainbow():
    pos = 0
    while True:
        if not flashing:
            ds[0] = wheel(pos)
            pos = (pos + 2) % 255
        await asyncio.sleep(0.02)

# alongside the other coroutines:
async def watch_button(btn):
    global flashing
    while True:
        if btn.value() == 0:
            flashing = True
            buzzer.on()
            ds[0] = (255, 255, 255)   # flash white on press
            await asyncio.sleep(0.15)
            buzzer.off()
            flashing = False
            await asyncio.sleep(0.15)
        await asyncio.sleep(0.01)

# two more lines inside main(), with the other create_task calls:
    asyncio.create_task(watch_button(btnA))
    asyncio.create_task(watch_button(btnB))
```

> [!TIP]
> **Test:** two LEDs blinking at different rates, a gliding rainbow, and both buttons answering instantly with a beep and a white flash — five concurrent tasks from one program. This is everything Part A couldn't do.
>
> **Now break it on purpose.** Add `import time` at the top, and in `blink()` change `await asyncio.sleep(rate)` to `time.sleep(rate)`. Run it and watch the DotStar: the glide collapses into a stuttering slideshow, and the buttons go dead — one blocking call in *one* coroutine starves *every* task, because the scheduler never gets control back. Change it back and watch health return. **That stutter is the whole lesson in one glance** — and from now on, a stuttering status animation in any async program tells you something, somewhere, is blocking.

---

[← Part B](03-part-b-asynchronous.md) · [Home](../README.md) · **Next:** [Part D — Hardware Debounce →](05-part-d-hardware-debounce.md)
