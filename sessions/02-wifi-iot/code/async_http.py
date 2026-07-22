# ============================================================
# Tiny async HTTP client for MicroPython (uasyncio)
# Python IoT on the TinyPICO : Session 2 (Wi-Fi & IoT)
#
# Provides:
#   await async_http.get_json(host, path, port=80)
#   await async_http.post_json(host, path, obj, port=80)
#
# Both return (status_code, parsed_json_or_None).
#
# Why this exists: the `urequests` library is BLOCKING -- while
# it waits for the network, nothing else in your program runs
# (your DotStar animation freezes, buttons go dead). This client
# is built on uasyncio streams, so every network wait is an
# `await` that lets your other tasks keep running.
#
# Plain http:// only (no TLS) -- which is exactly what the class
# scoreboard server speaks. Upload this file to the board like a
# library; import it, don't edit it.
# ============================================================

import uasyncio as asyncio
import json

TIMEOUT_S = 10


async def _request(host, port, request_bytes):
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port), TIMEOUT_S)
    try:
        writer.write(request_bytes)
        await asyncio.wait_for(writer.drain(), TIMEOUT_S)

        # Status line, e.g.  b"HTTP/1.0 200 OK\r\n"
        status_line = await asyncio.wait_for(reader.readline(), TIMEOUT_S)
        status = int(status_line.split(b" ")[1])

        # Skip the response headers
        while True:
            line = await asyncio.wait_for(reader.readline(), TIMEOUT_S)
            if line == b"\r\n" or not line:
                break

        # HTTP/1.0 + Connection: close => body ends at EOF
        body = await asyncio.wait_for(reader.read(-1), TIMEOUT_S)
    finally:
        writer.close()
        await writer.wait_closed()

    try:
        return status, json.loads(body)
    except ValueError:
        return status, None


async def get_json(host, path, port=80):
    """Async HTTP GET. Returns (status, parsed JSON or None)."""
    req = ("GET {} HTTP/1.0\r\n"
           "Host: {}\r\n"
           "Connection: close\r\n"
           "\r\n").format(path, host)
    return await _request(host, port, req.encode())


async def post_json(host, path, obj, port=80):
    """Async HTTP POST of a JSON body. Returns (status, parsed JSON or None)."""
    body = json.dumps(obj)
    req = ("POST {} HTTP/1.0\r\n"
           "Host: {}\r\n"
           "Content-Type: application/json\r\n"
           "Content-Length: {}\r\n"
           "Connection: close\r\n"
           "\r\n"
           "{}").format(path, host, len(body), body)
    return await _request(host, port, req.encode())
