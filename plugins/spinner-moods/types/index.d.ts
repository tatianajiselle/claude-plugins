export type TurnStats = { doneTokens: number; liveChars: number; effort: string | null }

declare module 'claude-code' {
  interface PluginState {
    'spinner-moods': { stats: TurnStats }
  }
}
