# Assignment — The Connected Reaction Game

⏱️ **45 min** · 🎯 **Graded — 100 points**

[← Part D](../lessons/05-part-d-web-server.md) · [Session home](../README.md)

---

Finish what Part C started: **your** Session 3 reaction game, fully online. Every round reports to the class scoreboard, standings print between rounds, and the game shrugs off network failures. Work at your Session 3 bench pairing.

## What the finished game does

1. On startup it connects to Wi-Fi (clear success message with its IP) — then plays exactly like Session 3: blinking red wait beacon, green GO, cap-color win flashes, false-start detection.
2. The moment a round is decided, the result is POSTed to the scoreboard **in the background** — the beacon, buttons, and feedback never hesitate.
3. During the 3-second pause between rounds, the class standings are fetched and printed: `CLASS STANDINGS -- Blue 12 : 9 Yellow`.
4. **Leader flourish:** if the team that just won this round also leads the class standings, the green LED double-blinks in celebration.
5. If the scoreboard is unreachable, the game prints one calm console note and keeps playing perfectly. No crash, no freeze, no drama.

## Requirements (grading rubric)

| # | Requirement | Points |
|---|---|---|
| 1 | Connects to Wi-Fi at startup with a clear success/failure message | 10 |
| 2 | Game plays flawlessly with networking active — wait beacon stays smooth while requests are in flight (async only; no blocking `urequests` inside the running game) | 25 |
| 3 | Every win and false start POSTed with correct bench, player, and result — visible on the class leaderboard | 20 |
| 4 | Standings fetched between rounds (awaited, in the pause) and printed readably | 15 |
| 5 | Leader flourish on the green LED when the round winner's team leads the class | 10 |
| 6 | **Fail-soft:** with the scoreboard stopped, the game keeps playing with a clear console note — no crash, no stall | 20 |

**Total: 100 points.**

> [!NOTE]
> Row 6 is worth as much as the POST itself. The instructor **will** stop the scoreboard server during your demo. A connected device that survives its network is the difference between a project and a product.

## Where to work

All the scaffolding is in [`game_online_STARTER.py`](../code/game_online_STARTER.py) — grafts 1–4 and TODOs 1–3, exactly as Part C walked through. Board also needs `secrets.py`, `wifi_connect.py`, and `async_http.py`.

Lost your Session 3 game? Tell the instructor — don't rebuild it from scratch on the clock.

## Stretch goals (extra credit)

- **Reaction-time telemetry:** measure each win's reaction time with `time.ticks_diff()` (Session 3 stretch) and include it in the POST payload as `"ms"`. (The server ignores unknown fields today — telemetry that's ready before the backend is happens in real teams too.)
- **Match point:** first team to 5 wins on the *class* standings triggers a DotStar rainbow celebration on every bench that notices it during a standings fetch.
- **Startup health check:** on boot, GET `/scores` once and beep twice if the scoreboard is reachable — a self-test before the first round.

## Submission

- Save as `reaction_game_online_<yourname>.py`.
- Demo to the instructor: one win and one false start landing on the projector leaderboard, then a full round played *after* the instructor stops the server (fail-soft proof).
- Submit through the course portal before end of session.

---

[← Part D](../lessons/05-part-d-web-server.md) · [Session home](../README.md)
