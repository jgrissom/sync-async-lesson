import { useEffect, useState } from 'react'

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

export default function App() {
  const [scores, setScores] = useState<Scores | null>(null)
  const [stale, setStale] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function tick() {
      try {
        const r = await fetch('/scores')
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const data: Scores = await r.json()
        if (!cancelled) {
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
