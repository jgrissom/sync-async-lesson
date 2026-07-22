# Prints this TinyPICO's Wi-Fi MAC address.
# Run once per board -- the school guest network needs each MAC
# registered before the board can join.

import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = wlan.config("mac")
print("MAC address:", ":".join("{:02X}".format(b) for b in mac))
