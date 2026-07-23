import { useEffect, useRef, useState } from 'react'
import confetti from 'canvas-confetti'

// Shapes come from the scoreboard contract — identical between the stdlib
// classroom server and the cloud API. See GET /scores in either.
type PlayerScore = { wins: number; false_starts: number }
type BenchEntry = { Blue: PlayerScore; Yellow: PlayerScore }
type Scores = {
  benches: Record<string, BenchEntry>
  totals: BenchEntry
  // Cloud-only additive key: game titles from POST /register.
  // Absent when polling the classroom stdlib server — always optional.
  names?: Record<string, string>
}

const POLL_MS = 1500

// One burst per team per poll, sized by how many wins that team gained in
// the window. A lone blue win is a solid blue burst; simultaneous wins mix
// in proportion. Each team celebrates from its own side of the header.
const CONFETTI = {
  Blue: { color: '#7ab8ff', x: 0.25 },
  Yellow: { color: '#ffd84d', x: 0.75 },
} as const

// Main-thread renderer: the default export renders from a web worker via
// OffscreenCanvas, which headless browsers (tests/screenshots) fail to
// capture. At our particle counts the main thread doesn't notice.
const burst = confetti.create(undefined, { resize: true, useWorker: false })

function celebrate(deltas: { Blue: number; Yellow: number }) {
  for (const team of ['Blue', 'Yellow'] as const) {
    const wins = deltas[team]
    if (wins <= 0) continue // increments only: /reset stays silent
    burst({
      particleCount: Math.min(80 * wins, 240),
      spread: 70,
      startVelocity: 45,
      origin: { x: CONFETTI[team].x, y: 0.6 },
      colors: [CONFETTI[team].color, '#ffffff'],
    })
  }
}

export default function App() {
  const [scores, setScores] = useState<Scores | null>(null)
  const [stale, setStale] = useState(false)
  const prevTotals = useRef<BenchEntry | null>(null)

  useEffect(() => {
    let cancelled = false
    async function tick() {
      try {
        const r = await fetch('/scores')
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const data: Scores = await r.json()
        if (!cancelled) {
          // Diff against the previous poll; never fire on the first one,
          // so opening the page mid-game doesn't celebrate stale wins.
          const prev = prevTotals.current
          if (prev) {
            celebrate({
              Blue: data.totals.Blue.wins - prev.Blue.wins,
              Yellow: data.totals.Yellow.wins - prev.Yellow.wins,
            })
          }
          prevTotals.current = data.totals
          setScores(data)
          setStale(false)
        }
      } catch {
        if (!cancelled) setStale(true)
      }
    }
    tick()
    const id = setInterval(tick, POLL_MS)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  const totals = scores?.totals
  const crown = !totals
    ? ' '
    : totals.Blue.wins === totals.Yellow.wins
      ? "It's a tie!"
      : totals.Blue.wins > totals.Yellow.wins
        ? '👑 Team Blue leads!'
        : '👑 Team Yellow leads!'

  const benchNames = scores
    ? Object.keys(scores.benches).sort((a, b) =>
        a.localeCompare(b, undefined, { numeric: true }),
      )
    : []

  return (
    <main>
      <h1>Reaction Game — Live Leaderboard</h1>
      <div className="crown">{crown}</div>
      <div className="big">
        <span className="blue">Blue {totals?.Blue.wins ?? 0}</span>
        <span className="sep">:</span>
        <span className="yellow">{totals?.Yellow.wins ?? 0} Yellow</span>
      </div>
      <table>
        <thead>
          <tr>
            <th></th>
            <th className="blue">Blue wins</th>
            <th className="blue">false starts</th>
            <th className="yellow">Yellow wins</th>
            <th className="yellow">false starts</th>
          </tr>
        </thead>
        <tbody>
          {!scores ? (
            <tr>
              <td colSpan={5}>Waiting for first update…</td>
            </tr>
          ) : benchNames.length === 0 ? (
            <tr>
              <td colSpan={5}>No rounds reported yet…</td>
            </tr>
          ) : (
            benchNames.map((b) => {
              const e = scores.benches[b]
              return (
                <tr key={b}>
                  <td className="game">{scores.names?.[b] ?? `Bench ${b}`}</td>
                  <td>{e.Blue.wins}</td>
                  <td>{e.Blue.false_starts}</td>
                  <td>{e.Yellow.wins}</td>
                  <td>{e.Yellow.false_starts}</td>
                </tr>
              )
            })
          )}
        </tbody>
      </table>
      <p className={stale ? 'note stale' : 'note'}>
        {stale
          ? 'Lost contact with server — retrying…'
          : 'Live · updates every 1.5 s · POST /result · GET /scores'}
      </p>
    </main>
  )
}
