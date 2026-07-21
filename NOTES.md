# Design-Decision Log (NOTES.md)

Rationale behind the choices in this lesson, so future maintainers (and future
AI-assistant sessions) don't have to reconstruct it. This file is safe for the
public repo — it contains no solution code.

**Context:** Session in a six-part Python IoT curriculum. 3.5 hours, intermediate
Python students, TinyPICO ESP32 + MicroPython in Thonny. Class of ~13, usually
working in pairs (~7 benches).

---

## 1. The core pedagogical bet

The lesson is built so students *physically feel* blocking, not just read about
it. Every design choice serves that:

- **Part A deliberately ships broken UX** — A1's button is unresponsive *on
  purpose*, and A2 ("rewrite sleep yourself") is shown to be a dead end before
  async is introduced. Don't "fix" A1; its badness is the lesson.
- **The DotStar rainbow in Part C doubles as a diagnostic instrument**: any
  blocking call anywhere makes the ~50 fps animation visibly stutter. It's a
  living "is my event loop healthy?" meter, which is why it runs at 0.02 s
  frame time rather than something slower.
- Everything hinges on the contrast `time.sleep()` (blocks the CPU) vs.
  `await asyncio.sleep()` (yields to the scheduler). Keep that contrast pure:
  **no `time.sleep()` may appear in any async example**, even for tiny delays.
- **Problems are demonstrated before they're solved.** B3 makes switch bounce
  visible (undebounced counter over-counts 10 presses) *before* the debounce
  line is explained — same show-then-fix move as Part A's broken button. B3's
  counter is deliberately the same rig as Part D's `debounce_test.py`, so the
  optional hardware segment starts on familiar code.

## 2. Pin assignments — and why these exact pins

| Component | GPIO | Rationale |
|---|---|---|
| LED 1 (red) | 26 | Free general-purpose output on the TinyPICO header; no boot-time role. |
| LED 2 (green) | 27 | Same. |
| Buzzer | 25 | Same; also DAC-capable (25/26), leaving the door open for tone/PWM work in a later session. |
| Button A (red cap) | 18 | Plain GPIO, safe for input with pull-up. |
| Button B (green cap) | 5 | Safe **with a caveat — see below**. |
| DotStar | onboard | Never hardcode its pins; use `TinyPICO.DOTSTAR_CLK` / `DOTSTAR_DATA` constants so the library owns them. |

Pins deliberately **avoided**:

- **GPIO 34–39**: input-only and no internal pull-ups — would break the
  "buttons need no external resistor" simplification.
- **GPIO 0, 2, 12, 15**: ESP32 strapping pins with genuinely risky boot
  interactions (and on the TinyPICO, 2 and 12 are the DotStar data/clock).

**The GPIO 5 caveat:** GPIO 5 is also technically a strapping pin (it sets
SDIO slave timing at boot). It's acceptable for Button B because the internal
pull-up holds it high at boot and a momentary button only pulls it low while
physically held — the failure mode is limited to "someone holds Button B
during a reset," which is harmless in practice here. But this is why the setup
guide tells instructors to verify the pin map, and why GPIO 5 should not be
reassigned to an output or to anything that sits low at boot.

## 3. Electrical / wiring decisions

- **Buttons: internal pull-ups (`Pin.PULL_UP`), wired to GND → active-low
  (0 = pressed).** Chosen to keep the breadboard minimal (no external
  resistors on buttons) and to introduce the "pressed reads 0" idiom, which
  students will meet constantly in real hardware. All code and prose must stay
  consistent with active-low.
- **LEDs: 330 Ω series resistors on the cathode (GND) side** — GPIO → anode,
  cathode → resistor → GND. Electrically identical to anode-side (series loop),
  but documented this way round because it matches the instructor bench build;
  keep diagram and prose consistent with it.
- **Wire with USB unplugged** — stated in setup; keep it in any new wiring steps.

## 4. Library decisions (verified against the official repos)

- **DotStar import is `from micropython_dotstar import DotStar`** — matching
  the actual filename in UnexpectedMaker's `tinypico-micropython` repo
  (`tinypico-helper/micropython_dotstar.py`). **Do not rename the file to
  `dotstar.py`** or "simplify" the import; the file name and import must stay
  in sync, and we match upstream so students can re-download it themselves.
- **DotStar power enable is `TinyPICO.set_dotstar_power(True)`** — verified
  function name; the DotStar has switched power on the TinyPICO and shows
  nothing without this call.
- `tinypico.py` is usually frozen into the official TinyPICO MicroPython
  firmware; `micropython_dotstar.py` usually is not and must be uploaded via
  Thonny (View → Files → Upload to /). Part C documents this.
- **`import uasyncio as asyncio`** — the `uasyncio` name with the `asyncio`
  alias, so code reads like CPython asyncio while staying explicit that this
  is the MicroPython port.
- The SoftSPI constructor needs a `miso` pin even though the DotStar never
  uses MISO — that's why `TinyPICO.SPI_MISO` appears; it's not a mistake.

## 5. Why Parts D and E are optional

- The core 210 minutes are already full; Part D is ~25 min for groups that
  finish early, or a warm-up for a later session. (Originally 15 min; grew
  when capacitor fundamentals and the τ = R × C walkthrough were added —
  sections 1–2 are teachable theory, not just a skim.)
- It requires extra parts (ceramic caps `103`/`104`/`105`) that not every kit
  bench needs for the graded work — nothing in the assignment depends on it.
- Pedagogically it's a *comparison* experiment (predict → measure → compare
  caps against the software-debounced button), which only lands after software
  debouncing is understood from Part B.
- Cap math assumes the ESP32 internal pull-up ≈ 45 kΩ, so τ ≈ 0.45 ms / 4.5 ms
  / 45 ms for `103`/`104`/`105`. The `104` is the intended "sweet spot."
- Ceramic caps were chosen partly because they're non-polarised and safe at
  3.3 V; the polarised-electrolytic / flyback-diode discussion is explicitly
  deferred to a future (motor) session.
- **Part E (robust software debounce, ~10 min)** implements the stability-
  counter algorithm that B3's release-bounce note only describes (re-arm after
  N consecutive released reads). Kept out of Part B to protect the sync-vs-
  async spine — a second debounce algorithm mid-lesson dilutes the core arc.
  Its "which debounce, when" table (time-based / stability-based / hardware)
  is the intended capstone summary if both bonus parts get taught.

## 6. Assignment decisions

- **The reaction game is the integration test for the whole session**: it
  needs concurrency (referee + two players), random delay, shared state,
  debouncing, and DotStar/buzzer feedback — every rubric row maps to a lesson
  segment.
- **Starter scaffold with exactly three TODOs** (random delay, false start,
  valid win). The architecture (shared `state` dict, referee/player tasks) is
  *given*, because 50 minutes is enough to reason about game logic but not to
  invent an async architecture from scratch.
- Rubric weights concurrency correctness (25 pts) highest, on purpose.
- **The GO indicator is LED 2 (green, GPIO 27)**, so the physical LED color
  matches the DotStar turning green (red = wait, green = go). LED 1 (red) is
  reserved for the stretch goal ("wait" light / PWM pulsing).
- **Race-condition subtlety that the design accepts:** two "simultaneous"
  presses are serialized by the cooperative scheduler, so whoever's coroutine
  checks `state["over"]` first wins — that's fine, and can even be a
  discussion point. Don't add locking to the starter; it would bury the
  lesson.

## 7. Repo & solutions policy

- Public GitHub repo: `README.md` (landing) → `lessons/` → `assignment/` →
  `code/`, plus `TROUBLESHOOTING.md` (symptom-first FAQ) and
  `diagrams/wiring.svg` (printable, hand-authored SVG — edit the XML directly,
  keep white background for printing). All student-facing.
- **The instructor bundle lives at `../sync-async-lesson-instructor/`** — a
  sibling folder on disk, deliberately outside this repo. It holds
  `reaction_game_SOLUTION.py` (starter + TODOs filled, diff-friendly) and
  `ANSWER_KEY.md` (rubric guide, demo checklist, discussion answers).
- **The reaction-game solution and the instructor answer key must NEVER enter
  this repo** — students can see the git history. They live in a separate
  instructor-only bundle distributed outside GitHub. `.gitignore` blocks
  `*SOLUTION*`, `*instructor*`, `*answer_key*` variants as a backstop, but the
  real rule is: solution files are never created inside this folder at all.
- Lesson pages carry back/next navigation links; keep them consistent when
  inserting or renaming pages.
- Discussion questions carry collapsible `<details>` answers in the public
  pages (self-checkable without spoiling predict-first questions). These are
  fine publicly — the never-public rule covers only the graded assignment
  solution and answer key. Instructor framing stays in the answer key.

## 8. Standing to-dos / open items

- Repo is not yet `git init`-ed; when it is, verify `.gitignore` took effect
  **before** the first commit.
- Instructors must verify each board has `micropython_dotstar.py` uploaded
  before class (Part C setup takes real minutes per board).
- Six-session curriculum context: flyback diodes / motors and PWM tone on the
  buzzer are deliberately parked for later sessions.
