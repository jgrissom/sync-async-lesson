#!/usr/bin/env python3
# ============================================================
# Reaction-Game Scoreboard Server
# Python IoT on the TinyPICO : Session 4 (Wi-Fi & IoT)
#
# Runs on the INSTRUCTOR'S LAPTOP (normal Python 3, not the
# board). Standard library only -- no installs needed.
#
#   Run:            python3 scoreboard_server.py
#   Leaderboard:    http://<laptop-ip>:8000/        (projector!)
#   Boards use:     GET  /scores            all benches (JSON)
#                   GET  /scores/<bench>    one bench (JSON)
#                   POST /result            record a round (JSON body)
#
# POST /result body:
#   {"bench": "3", "player": "Blue", "result": "win"}
#   {"bench": "3", "player": "Yellow", "result": "false_start"}
#
# Scores persist to scoreboard_data.json next to this file.
# Delete that file (or GET /reset from the laptop) to start fresh.
# ============================================================

import json
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "scoreboard_data.json")

PLAYERS = ("Blue", "Yellow")
RESULTS = ("win", "false_start")


def load_scores():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_scores():
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f, indent=2)


scores = load_scores()


def bench_entry(bench):
    return scores.setdefault(str(bench), {
        "Blue": {"wins": 0, "false_starts": 0},
        "Yellow": {"wins": 0, "false_starts": 0},
    })


def totals():
    t = {p: {"wins": 0, "false_starts": 0} for p in PLAYERS}
    for bench in scores.values():
        for p in PLAYERS:
            t[p]["wins"] += bench[p]["wins"]
            t[p]["false_starts"] += bench[p]["false_starts"]
    return t


PAGE = """<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reaction Game Leaderboard</title>
<style>
  body { font-family: -apple-system, Helvetica, Arial, sans-serif;
         text-align: center; background: #111; color: #eee; }
  h1   { margin-top: 1em; }
  .crown { font-size: 1.6em; margin: .5em; min-height: 1.4em; }
  .big { font-size: 2.4em; margin: .2em; }
  .blue   { color: #7ab8ff; }
  .yellow { color: #ffd84d; }
  table { margin: 1.5em auto; border-collapse: collapse; font-size: 1.2em; }
  th, td { padding: .4em 1em; border-bottom: 1px solid #444; }
  th { color: #aaa; font-weight: normal; }
  .note { color: #777; margin-top: 2em; font-size: .9em; }
  .stale { color: #f66; }
</style></head>
<body>
<h1>Reaction Game — Live Leaderboard</h1>
<div class="crown" id="crown">&nbsp;</div>
<div class="big"><span class="blue">Blue <span id="bw">0</span></span>
&nbsp;:&nbsp;
<span class="yellow"><span id="yw">0</span> Yellow</span></div>
<table>
<thead>
<tr><th></th><th class="blue">Blue wins</th><th class="blue">false starts</th>
<th class="yellow">Yellow wins</th><th class="yellow">false starts</th></tr>
</thead>
<tbody id="rows"><tr><td colspan="5">Waiting for first update…</td></tr></tbody>
</table>
<p class="note" id="status">Live · updates every 1.5 s · POST /result · GET /scores</p>
<script>
async function tick() {
  try {
    const r = await fetch('/scores');
    const data = await r.json();
    const t = data.totals, benches = data.benches;
    document.getElementById('bw').textContent = t.Blue.wins;
    document.getElementById('yw').textContent = t.Yellow.wins;
    document.getElementById('crown').innerHTML =
      t.Blue.wins === t.Yellow.wins ? "It's a tie!" :
      (t.Blue.wins > t.Yellow.wins ? "\\uD83D\\uDC51 Team Blue leads!"
                                   : "\\uD83D\\uDC51 Team Yellow leads!");
    const names = Object.keys(benches).sort(
      (a, b) => a.localeCompare(b, undefined, {numeric: true}));
    let html = '';
    for (const b of names) {
      const e = benches[b];
      html += `<tr><td>Bench ${b}</td><td>${e.Blue.wins}</td>` +
              `<td>${e.Blue.false_starts}</td><td>${e.Yellow.wins}</td>` +
              `<td>${e.Yellow.false_starts}</td></tr>`;
    }
    document.getElementById('rows').innerHTML =
      html || '<tr><td colspan="5">No rounds reported yet…</td></tr>';
    document.getElementById('status').textContent =
      'Live · updates every 1.5 s · POST /result · GET /scores';
    document.getElementById('status').classList.remove('stale');
  } catch (err) {
    document.getElementById('status').textContent =
      'Lost contact with server — retrying…';
    document.getElementById('status').classList.add('stale');
  }
}
tick();
setInterval(tick, 1500);
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, code, obj):
        self._send(code, json.dumps(obj))

    def do_GET(self):
        path = self.path.rstrip("/") or "/"
        if path == "/":
            self._send(200, PAGE, "text/html")
        elif path == "/scores":
            self._send_json(200, {"benches": scores, "totals": totals()})
        elif path.startswith("/scores/"):
            bench = path.split("/")[2]
            if bench in scores:
                self._send_json(200, scores[bench])
            else:
                self._send_json(404, {"error": "unknown bench " + bench})
        elif path == "/reset":
            # Convenience for the instructor between classes; browsers
            # only -- boards have no reason to call this.
            scores.clear()
            save_scores()
            self._send_json(200, {"ok": True, "message": "scoreboard reset"})
        else:
            self._send_json(404, {"error": "no such route"})

    def do_POST(self):
        if self.path.rstrip("/") != "/result":
            self._send_json(404, {"error": "no such route"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            bench = str(payload["bench"])
            player = payload["player"]
            result = payload["result"]
            if player not in PLAYERS or result not in RESULTS:
                raise ValueError("bad player or result")
        except (KeyError, ValueError) as exc:
            self._send_json(400, {"error": "bad request: {}".format(exc)})
            return

        entry = bench_entry(bench)
        key = "wins" if result == "win" else "false_starts"
        entry[player][key] += 1
        save_scores()
        print("  bench {} : {} {}".format(bench, player, result))
        self._send_json(200, entry)

    def log_message(self, *args):
        pass  # keep the console readable; we print results ourselves


if __name__ == "__main__":
    import socket
    # Best-effort LAN IP discovery so the instructor can announce it
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        ip = probe.getsockname()[0]
        probe.close()
    except OSError:
        ip = "<your-laptop-ip>"
    print("Scoreboard server running.")
    print("  Leaderboard : http://{}:{}/".format(ip, PORT))
    print("  Boards use  : SCOREBOARD_HOST = \"{}\"".format(ip))
    print("  Stop with Ctrl+C. Scores persist in scoreboard_data.json.")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
