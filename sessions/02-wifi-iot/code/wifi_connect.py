# ============================================================
# Wi-Fi connect helper (synchronous)
# Python IoT on the TinyPICO : Session 2 (Wi-Fi & IoT)
#
# Usage (after creating secrets.py from secrets_TEMPLATE.py):
#
#   import wifi_connect
#   wifi_connect.connect()
#
# Connecting is the one piece of networking we do synchronously
# even in async programs: nothing useful can happen before the
# network exists, so blocking for a few seconds here is fine.
# ============================================================

import network
import time
import secrets


def connect(timeout_s=15):
    """Join the Wi-Fi network from secrets.py. Returns the WLAN object.
    Raises RuntimeError with a helpful message if it can't connect."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("Already connected. IP:", wlan.ifconfig()[0])
        return wlan

    print("Connecting to '{}' ...".format(secrets.WIFI_SSID))
    # An empty password means an open (or MAC-registered) network
    if secrets.WIFI_PASSWORD:
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    else:
        wlan.connect(secrets.WIFI_SSID)

    deadline = time.ticks_add(time.ticks_ms(), timeout_s * 1000)
    while not wlan.isconnected():
        if time.ticks_diff(deadline, time.ticks_ms()) < 0:
            raise RuntimeError(
                "Could not join '{}' within {} s.\n"
                "Check: SSID spelled right? 2.4 GHz network? "
                "Is this board's MAC registered?".format(
                    secrets.WIFI_SSID, timeout_s))
        time.sleep(0.25)

    ip = wlan.ifconfig()[0]
    print("Connected! IP address:", ip)
    return wlan
