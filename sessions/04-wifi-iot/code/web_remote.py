# ============================================================
# TinyPICO Web Remote  --  Part D (optional)
# Python IoT on the TinyPICO : Session 4 (Wi-Fi & IoT)
#
# Your board becomes the SERVER: it hosts a tiny web page.
# Anyone on the same network can open it and control the bench.
#
#   1. Create secrets.py (from secrets_TEMPLATE.py) + upload
#      wifi_connect.py to the board.
#   2. Run this file. It prints  http://<board-ip>/
#   3. Open that address in a phone/laptop browser ON THE SAME
#      NETWORK.
#
# The DotStar rainbow runs the whole time -- living proof the
# server is async: the board animates, listens, and serves all
# at once. (If your phone can't load the page, that's usually
# the network blocking device-to-device traffic ("client
# isolation"), not your code -- see the lesson's fallback notes.)
# ============================================================

import uasyncio as asyncio
from machine import Pin, SoftSPI
import tinypico as TinyPICO
from micropython_dotstar import DotStar
import wifi_connect

led1 = Pin(26, Pin.OUT)
led2 = Pin(27, Pin.OUT)
buzzer = Pin(25, Pin.OUT)

spi = SoftSPI(sck=Pin(TinyPICO.DOTSTAR_CLK),
              mosi=Pin(TinyPICO.DOTSTAR_DATA),
              miso=Pin(TinyPICO.SPI_MISO))
ds = DotStar(spi, 1, brightness=0.3)
TinyPICO.set_dotstar_power(True)

PAGE = """HTTP/1.0 200 OK\r
Content-Type: text/html\r
Connection: close\r
\r
<!doctype html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TinyPICO Remote</title>
<style>
 body { font-family: sans-serif; text-align: center; padding-top: 2em; }
 a { display: inline-block; margin: .4em; padding: .8em 1.6em;
     border-radius: .5em; background: #eee; color: #222;
     text-decoration: none; font-size: 1.2em; }
</style></head><body>
<h1>TinyPICO Remote</h1>
<p><a href="/led1/on">Red LED ON</a> <a href="/led1/off">Red LED OFF</a></p>
<p><a href="/led2/on">Green LED ON</a> <a href="/led2/off">Green LED OFF</a></p>
<p><a href="/beep">Beep!</a></p>
<p style="color:#888">Served live from a microcontroller —<br>
the rainbow never stops while I serve this page.</p>
</body></html>
"""


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
        await asyncio.sleep(0.02)


async def handle_client(reader, writer):
    # First line of an HTTP request:  b"GET /led1/on HTTP/1.1"
    request_line = await reader.readline()
    # Drain the rest of the request headers
    while True:
        line = await reader.readline()
        if line == b"\r\n" or not line:
            break

    parts = request_line.split(b" ")
    path = parts[1] if len(parts) > 1 else b"/"
    print("request:", path.decode())

    if path == b"/led1/on":
        led1.on()
    elif path == b"/led1/off":
        led1.off()
    elif path == b"/led2/on":
        led2.on()
    elif path == b"/led2/off":
        led2.off()
    elif path == b"/beep":
        buzzer.on()
        await asyncio.sleep(0.15)
        buzzer.off()

    writer.write(PAGE.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def main():
    asyncio.create_task(rainbow())
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Web remote running -- open the address above on your phone.")
    while True:
        await asyncio.sleep(1)


wlan = wifi_connect.connect()
print()
print(">>> Open  http://{}/  in a browser on the same network <<<".format(
    wlan.ifconfig()[0]))
print()
try:
    asyncio.run(main())
finally:
    TinyPICO.set_dotstar_power(False)
    led1.off()
    led2.off()
    buzzer.off()
