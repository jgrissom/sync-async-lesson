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

Here the DotStar becomes a third output task, smoothly cycling colors while LEDs blink and buttons stay responsive. Pressing a button flashes it white.

```python
from machine import Pin, SoftSPI
import uasyncio as asyncio
import tinypico as TinyPICO
from micropython_dotstar import DotStar

led1 = Pin(26, Pin.OUT)
led2 = Pin(27, Pin.OUT)
buzzer = Pin(25, Pin.OUT)
btnA = Pin(18, Pin.IN, Pin.PULL_UP)
btnB = Pin(5, Pin.IN, Pin.PULL_UP)

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

async def blink(led, rate):
    while True:
        led.value(not led.value())
        await asyncio.sleep(rate)

async def rainbow():
    pos = 0
    while True:
        ds[0] = wheel(pos)
        pos = (pos + 2) % 255
        await asyncio.sleep(0.02)   # smooth = ~50 fps

async def watch_button(btn):
    while True:
        if btn.value() == 0:
            buzzer.on()
            ds[0] = (255, 255, 255)  # flash white on press
            await asyncio.sleep(0.15)
            buzzer.off()
            await asyncio.sleep(0.15)
        await asyncio.sleep(0.01)

async def main():
    asyncio.create_task(blink(led1, 0.5))
    asyncio.create_task(blink(led2, 0.9))
    asyncio.create_task(rainbow())
    asyncio.create_task(watch_button(btnA))
    asyncio.create_task(watch_button(btnB))
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

> [!NOTE]
> **Teaching payoff:** Two LEDs blink at different rates, the DotStar glides through a rainbow, and both buttons respond instantly — all concurrently. If you drop a `time.sleep(1)` into any coroutine, the rainbow stutters visibly. That stutter is the whole lesson in one glance.

---

[← Part B](03-part-b-asynchronous.md) · [Home](../README.md) · **Next:** [Part D — Hardware Debounce →](05-part-d-hardware-debounce.md)
