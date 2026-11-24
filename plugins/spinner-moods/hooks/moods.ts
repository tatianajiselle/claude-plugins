// The lanes a person picks in the config menu: each table's keys are the
// `options` of the matching `userConfig` field in plugin.json.

export type Mood = 'inference' | 'tool' | 'other' | 'flustered' | 'sleepy'

export const THEMES: Record<string, Record<Mood, string[]>> = {
  classic: {
    inference: ['·', '✢', '✳', '✶', '✻', '✽', '✻', '✶', '✳', '✢'],
    tool: ['◐', '◓', '◑', '◒'],
    other: ['◇', '◈', '◆', '◈'],
    flustered: ['✗', '✘', '✕', '×', '✕', '✘'],
    sleepy: ['z', 'z', 'Z', 'Z'],
  },
  sparkle: {
    inference: ['˚', '⋆', '✧', '✦', '✶', '✦', '✧', '⋆'],
    tool: ['✶', '✷', '✸', '✹', '✺', '✹', '✸', '✷'],
    other: ['⋆', '˚', '⋆', '˚'],
    flustered: ['✕', '⁎', '✱', '✲', '✱', '⁎'],
    sleepy: ['⋆', '˚', '.', '˚'],
  },
  // Every hearts frame is two cells wide so the text never shifts.
  hearts: {
    inference: ['· ', '♡ ', '♥ ', '♥ ', '♡ ', '· '],
    tool: ['♥˙', '♡·', '♥.', '.♡', '·♥', '˙♡'],
    other: ['♡ ', 'ღ ', '♡ ', '· '],
    flustered: ['♥ ', ' ♡', '♥ ', ' ♡'],
    sleepy: ['♡ ', '♡ ', '♡ᶻ', '♡ᶻ'],
  },
  moon: {
    inference: ['○', '◔', '◑', '◕', '●'],
    tool: ['◐', '◓', '◑', '◒'],
    other: ['○', '◌'],
    flustered: ['◍', '◌', '◎', '○', '◎', '◌'],
    sleepy: ['☾', '☾', '☽', '☽'],
  },
  geometric: {
    inference: ['□', '◧', '◩', '■', '◪', '◨'],
    tool: ['▲', '▶', '▼', '◀'],
    other: ['◇', '◆'],
    flustered: ['✕', '□', '⊠', '■', '⊠', '□'],
    sleepy: ['▫', '▫', '▪', '▪'],
  },
  bloom: {
    inference: ['·', '✿', '❀', '❁', '✾'],
    tool: ['✽', '✾', '❀', '❁'],
    other: ['❀', '❁', '✿', '✾'],
    flustered: ['✿', '✕', '✿', '✕'],
    sleepy: ['❀', '❀', '✿', '·'],
  },
  bars: {
    inference: ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'],
    tool: ['▏', '▎', '▍', '▌', '▋', '▊', '▉', '█'],
    other: ['▂', '▄', '▆', '█'],
    flustered: ['█', '▁', '█', '▁'],
    sleepy: ['▃', '▂', '▁', '▁'],
  },
  arc: {
    inference: ['◜', '◠', '◝', '◞', '◡', '◟'],
    tool: ['◜', '◝', '◞', '◟'],
    other: ['◟', '◡', '◞', '◝', '◠', '◜'],
    flustered: ['◠', '◡', '◠', '◡'],
    sleepy: ['◠', '◡', '◡', '◡'],
  },
  squares: {
    inference: ['◰', '◳', '◲', '◱'],
    tool: ['◱', '◲', '◳', '◰'],
    other: ['□', '◰', '◧', '■'],
    flustered: ['⊠', '□', '⊠', '□'],
    sleepy: ['■', '◧', '◰', '□'],
  },
}

// null draws in the terminal's own text color.
export const PALETTES: Record<string, Record<Mood, string | null>> = {
  classic: { inference: 'magenta', tool: 'cyan', other: 'yellow', flustered: 'red', sleepy: '#8a8a8a' },
  pastel: { inference: '#f5a9d0', tool: '#a8d8ea', other: '#ffe5a5', flustered: '#ff9aa2', sleepy: '#c3b1e1' },
  neon: { inference: '#ff2bd6', tool: '#00f0ff', other: '#faff00', flustered: '#ff3131', sleepy: '#7a5cff' },
  cozy: { inference: '#e9a178', tool: '#8fb996', other: '#e6c27a', flustered: '#c8553d', sleepy: '#a38f85' },
  mono: { inference: null, tool: null, other: null, flustered: null, sleepy: null },
}

export const SPEEDS: Record<string, number> = { calm: 200, normal: 120, zippy: 90 }

export type Details = 'full' | 'time' | 'minimal'

export function pick<T>(table: Record<string, T>, key: unknown, fallback: string): T {
  return (typeof key === 'string' && table[key]) || (table[fallback] as T)
}
