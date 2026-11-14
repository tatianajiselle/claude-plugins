export type TurnStats = { doneTokens: number; liveChars: number; effort: string | null; flustered: boolean }

declare module 'claude-code' {
  interface PluginState {
    'spinner-moods': { stats: TurnStats }
  }
}
