# Part D — Your Board as a Web Server (optional)

⏱️ **~25 min bonus** · *not part of the core 3.5 hours*

[← Part C](04-part-c-connected-game.md) · [Session home](../README.md) · **Next:** [Assignment →](../assignment/README.md)

---

All day your board has been a **client** — asking servers for things. Flip it: [`web_remote.py`](../code/web_remote.py) makes the TinyPICO a **server** that hosts its own web page. Your phone browses to the board, taps buttons, and the bench's LEDs and buzzer obey.

## Run it

1. Board needs: `secrets.py`, `wifi_connect.py`, plus the Session 1 DotStar libraries.
2. Run `web_remote.py`. It prints something like `>>> Open http://10.1.4.27/ <<<`.
3. On a phone or laptop **on the same network**, open that address. Tap away.

While you tap, watch the DotStar: the rainbow never misses a frame. The board is animating, listening for connections, and serving pages concurrently — `asyncio.start_server()` is just more of the same scheduler you've been using all along. Skim `handle_client()` in the file: an HTTP *server* turns out to be "read one line, look at the path, send text back."

> [!IMPORTANT]
> **If the phone can't load the page, it's probably not your code.** Many guest/school networks enforce *client isolation* — devices can reach the internet but not each other. Your board can still do everything in Parts A–C (those connect *outward*), but incoming connections get silently dropped. The test: if the instructor's laptop can't be reached from a phone browser either, it's isolation.
>
> **Fallback that always works:** a phone hotspot. Put the board and the phone on the hotspot (no internet needed — this page never leaves the room) and it will load. This is also why today's *graded* work only ever connects outward.

## Ideas to riff on (if time allows)

- Add a `/rainbow/off` and `/rainbow/on` route pair.
- Make `/` show the bench's current win counts (your server + the scoreboard's data: fetch it with `async_http` inside the handler).
- Change the page's HTML — it's just a string in the file. View-source on your phone and confirm it's exactly what the board sent.

## Discussion

**Q1. Your board is a server and the scoreboard laptop is a server. Your board is also a client of the scoreboard. What do "client" and "server" actually name?**

<details>
<summary>Answer</summary>

Roles in one conversation, not kinds of machine. Whoever opens the connection and asks is the client; whoever listens and answers is the server. The same device can be both at once — your board serving a phone while POSTing to the laptop is exactly that.

</details>

**Q2. Why does the graded assignment avoid depending on anything connecting *inward* to the board?**

<details>
<summary>Answer</summary>

Because inbound connections are the first casualty of real-world networks — client isolation, firewalls, NAT all block them. Outbound requests almost always work. Designing the required path outbound-only makes the assignment robust on any network; the inbound demo lives here in the optional part, with a hotspot fallback.

</details>

---

[← Part C](04-part-c-connected-game.md) · [Session home](../README.md) · **Next:** [Assignment →](../assignment/README.md)
