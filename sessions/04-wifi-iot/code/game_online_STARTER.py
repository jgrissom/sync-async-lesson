# ============================================================
# Go Online!  --  network additions for YOUR reaction game
# Python IoT on the TinyPICO : Session 4 (Wi-Fi & IoT)
#
# This file is NOT a complete program. It holds the pieces you
# graft into your own finished reaction game from Session 3.
# Open your reaction_game_<yourname>.py next to this file and:
#
#   GRAFT 1 -- add the imports below to the top of your game
#   GRAFT 2 -- copy in the two coroutines (fill in TODO 1 + 2)
#   GRAFT 3 -- wire them into player()/referee() (TODO 3)
#   GRAFT 4 -- connect to Wi-Fi BEFORE the game starts (shown
#              at the bottom)
#
# Files your board needs: secrets.py (from secrets_TEMPLATE.py),
# wifi_connect.py, async_http.py -- plus your game.
# ============================================================

# ---- GRAFT 1: add to your imports --------------------------
import uasyncio as asyncio
import wifi_connect
import async_http
import secrets


# ---- GRAFT 2: add these two coroutines to your game --------

async def report_result(player, result):
    """POST one round result to the class scoreboard.
    Wrapped in try/except so a dead network NEVER crashes the game --
    connected features should fail soft."""
    try:
        # ------------------------------------------------------
        # TODO 1: POST the result to the scoreboard.
        #   The payload dict:
        #     {"bench": secrets.BENCH, "player": player, "result": result}
        #   The call:
        #     status, data = await async_http.post_json(
        #         secrets.SCOREBOARD_HOST, "/result", payload,
        #         port=secrets.SCOREBOARD_PORT)
        #   Then print the status so you can see it worked (200 = OK).
        # ------------------------------------------------------
        pass
    except OSError as e:
        print("(scoreboard unreachable:", e, "-- playing on)")


async def fetch_standings():
    """GET the class-wide totals, print them, and return the totals
    dict (or None if the scoreboard is unreachable)."""
    try:
        # ------------------------------------------------------
        # TODO 2: GET /scores from the scoreboard.
        #   status, data = await async_http.get_json(
        #       secrets.SCOREBOARD_HOST, "/scores",
        #       port=secrets.SCOREBOARD_PORT)
        #   data["totals"] looks like:
        #     {"Blue": {"wins": 3, ...}, "Yellow": {"wins": 5, ...}}
        #   Print it like:   CLASS STANDINGS -- Blue 3 : 5 Yellow
        #   and  return data["totals"]
        # ------------------------------------------------------
        pass
    except OSError as e:
        print("(scoreboard unreachable:", e, ")")
        return None


# ---- GRAFT 3: wire into your game (TODO 3) -----------------
#
#  a) In player(), report each result the moment it happens:
#       after the VALID WIN feedback:
#           asyncio.create_task(report_result(name, "win"))
#       after the FALSE START feedback:
#           asyncio.create_task(report_result(name, "false_start"))
#
#     Why create_task() and not await? The round is over and the
#     player's coroutine has feedback still to give -- we want the
#     POST to happen IN THE BACKGROUND while the game carries on.
#     Fire and forget.
#
#  b) In referee(), during the 3-second pause between rounds:
#           totals = await fetch_standings()
#
#     This one we DO await -- the pause is dead time anyway, and
#     we want the standings before the next round starts.
#
#  c) Leader flourish: after fetching, if the team that just won
#     also leads the class standings, double-blink the green LED:
#           if totals and totals["Blue"]["wins"] > totals["Yellow"]["wins"]:
#               ...  (and the mirror case for Yellow)


# ---- GRAFT 4: replace the bottom of your game --------------
#
#   wifi_connect.connect()      # BEFORE asyncio.run -- blocking on
#                               # purpose: no network, no scoreboard
#   try:
#       asyncio.run(main())
#   finally:
#       ...your existing cleanup...
