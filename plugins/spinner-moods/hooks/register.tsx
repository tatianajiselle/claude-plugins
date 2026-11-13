import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { TurnStats } from '../types'

type Activity = 'inference' | 'tool' | 'other'

const STYLES: Record<Activity, { color: string; frames: string[] }> = {
  inference: { color: 'magenta', frames: ['·', '✢', '✳', '✶', '✻', '✽', '✻', '✶', '✳', '✢'] },
  tool: { color: 'cyan', frames: ['◐', '◓', '◑', '◒'] },
  other: { color: 'yellow', frames: ['◇', '◈', '◆', '◈'] },
}

const EMPTY: TurnStats = { doneTokens: 0, liveChars: 0, effort: null }
const stats = atom({ plugin: 'spinner-moods', key: 'stats' } as const, EMPTY)

const CHARS_PER_TOKEN = 4
const WRITE_EVERY_CHARS = 40

function activityOf(mode: string, message: string | null): Activity {
  if (message) return 'other'
  if (mode === 'tool-use' || mode === 'tool-input') return 'tool'
  if (mode === 'thinking' || mode === 'requesting' || mode === 'responding') return 'inference'
  return 'other'
}

function formatTokens(n: number): string {
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`
}

export const register: Register = on => {
  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) await update($, stats, () => EMPTY)
    return next(e)
  })

  on('turn.step', async function* ($, e, next) {
    if (e.agentId !== undefined) return yield* next(e)
    const effort = e.effort === undefined ? null : String(e.effort)
    await update($, stats, s => ({ ...s, effort, liveChars: 0 }))
    let chars = 0
    let written = 0
    const stream = next(e)
    while (true) {
      const r = await stream.next()
      if (r.done) return r.value
      const chunk = r.value
      if (chunk.kind === 'text' || chunk.kind === 'thinking') chars += chunk.text.length
      else if (chunk.kind === 'input') chars += chunk.json.length
      if (chunk.kind === 'stop') {
        const exact = chunk.usage?.output_tokens ?? Math.round(chars / CHARS_PER_TOKEN)
        await update($, stats, s => ({ ...s, doneTokens: s.doneTokens + exact, liveChars: 0 }))
      } else if (chars - written >= WRITE_EVERY_CHARS) {
        written = chars
        await update($, stats, s => ({ ...s, liveChars: chars }))
      }
      yield chunk
    }
  })

  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    if (e.surface !== 'terminal') return next(e)
    const { Client } = $.ui.resolve(e)
    const { word, message, suffix, mode } = e.props
    const { color, frames } = STYLES[activityOf(mode, message)]
    const s = await read($, stats)
    const tokens = s.doneTokens + Math.round(s.liveChars / CHARS_PER_TOKEN)
    const extras = [tokens > 0 ? `↓ ~${formatTokens(tokens)} tokens` : null, s.effort].filter(Boolean).join(' · ')
    return (
      <Client
        key="line"
        module="./spinner-icon.tsx"
        props={{ color, frames, text: `${message ?? word}${suffix}`, extras }}
      />
    )
  })
}
