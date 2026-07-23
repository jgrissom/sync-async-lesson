# Opening Walkthrough — How the Reaction Game Works

⏱️ **15 min** · 🧑‍🏫 *instructor-led*

[← Overview](00-overview.md) · [Session home](../README.md) · **Next:** [Warm-up: Getting on the Network →](02-setup.md)

---

Before your reaction game goes online tonight, we make sure everyone owns how it works — because everything you add in Part C grafts onto exactly this code.

The instructor drives [`reaction_game_walkthrough.py`](../code/reaction_game_walkthrough.py): the finished Session 3 game with **everything commented out**. One layer gets uncommented at a time — `main()` → the wait beacon → the referee → the random delay → the players → the false-start and win handlers — and before *every* run, the room predicts what the board will do.

**Your job is to predict out loud — and be wrong in public.** The gap between what you expected and what the board does is where the learning is. Nothing here is graded; wrong guesses are the point.

## The ideas to walk out with

- **`asyncio.create_task(...)` schedules a coroutine — it does not run it.** Nothing runs until the scheduler gets control.
- **`await` is where your task is allowed to pause** — and while it's paused, the scheduler runs every other task that's ready. A `while True:` loop with no `await` starves everything else (you'll see this happen).
- **The tasks never call each other — they coordinate through the shared `state` dict** (`go`, `over`, `winner`, `false_start`). Press Ctrl+C at any moment and type `state` at the REPL to see the game's brain, frozen mid-thought.
- **The guards are load-bearing.** Why both branches check `not state["over"]`, and why the round is decided *before* the buzzer plays — every `await` is a door the other tasks walk through.

## Replay it yourself

The walkthrough file is yours: [`reaction_game_walkthrough.py`](../code/reaction_game_walkthrough.py). Re-run the ladder at home — uncomment one layer, predict, run, repeat. The finished version is [`reaction_game_BASE.py`](../code/reaction_game_BASE.py), which is also the base your game goes online from tonight.

---

[← Overview](00-overview.md) · [Session home](../README.md) · **Next:** [Warm-up: Getting on the Network →](02-setup.md)
