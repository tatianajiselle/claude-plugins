import { atom, read, update } from 'claude-code'
import type { Register, Timer } from 'claude-code'

import type { TurnStats } from '../types'
import { PALETTES, SPEEDS, THEMES, pick } from './moods'
import type { Details, Mood } from './moods'

const EMPTY: TurnStats = { doneTokens: 0, liveChars: 0, effort: null, flustered: false }
const stats = atom({ plugin: 'spinner-moods', key: 'stats' } as const, EMPTY)

const CHARS_PER_TOKEN = 4
const WRITE_EVERY_CHARS = 40
const FLUSTERED_MS = 4000
const SLEEPY_AFTER_MS = 60_000

function moodOf(mode: string, message: string | null): Mood {
  if (message) return 'other'
  if (mode === 'tool-use' || mode === 'tool-input') return 'tool'
  if (mode === 'thinking' || mode === 'requesting' || mode === 'responding') return 'inference'
  return 'other'
}

function formatTokens(n: number): string {
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`
}

export const register: Register = (on, options) => {
  const theme = pick(THEMES, options.theme, 'classic')
  const palette = pick(PALETTES, options.palette, 'classic')
  const tickMs = pick(SPEEDS, options.speed, 'normal')
  const details: Details = options.details === 'time' || options.details === 'minimal' ? options.details : 'full'
  const reactions = options.reactions !== false
  let calmDown: Timer | undefined

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

  // A failed tool call flusters the spinner for a few seconds. It watches tool
  // results as they reach the transcript rather than hooking `tool.call`, so
  // the mod never sits in a tool call's path (Code Mode refuses mods that do).
  if (reactions) {
    on('session.append', { door: 'tool-result' }, async ($, e, next) => {
      const r = await next(e)
      const failed = e.message.content.some(b => b.type === 'tool_result' && b.is_error === true)
      if (e.agentId === undefined && failed) {
        await update($, stats, s => ({ ...s, flustered: true }))
        calmDown?.cancel()
        calmDown = $.clock.after(FLUSTERED_MS, () => {
          void update($, stats, s => ({ ...s, flustered: false }))
        })
      }
      return r
    }).catch(($, e, next) => next(e))
  }

  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    if (e.surface !== 'terminal') return next(e)
    const { Client } = $.ui.resolve(e)
    const { word, message, suffix, mode } = e.props
    const s = await read($, stats)
    const mood: Mood = s.flustered ? 'flustered' : moodOf(mode, message)
    const tokens = s.doneTokens + Math.round(s.liveChars / CHARS_PER_TOKEN)
    const extras = details === 'full'
      ? [tokens > 0 ? `↓ ~${formatTokens(tokens)} tokens` : null, s.effort].filter(Boolean).join(' · ')
      : ''
    return (
      <Client
        key="line"
        module="./spinner-icon.tsx"
        props={{
          mood,
          color: palette[mood],
          frames: theme[mood],
          sleepy: reactions && mood !== 'flustered'
            ? { color: palette.sleepy, frames: theme.sleepy, afterMs: SLEEPY_AFTER_MS }
            : null,
          text: `${message ?? word}${suffix}`,
          extras,
          progress: tokens,
          tickMs,
          showTime: details !== 'minimal',
        }}
      />
    )
  })
}
