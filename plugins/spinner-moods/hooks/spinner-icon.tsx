import type { ClientModule } from 'claude-code'

type LineProps = { color: string; frames: string[]; text: string; extras: string }

const TICK_MS = 120

function formatElapsed(ms: number): string {
  const s = Math.floor(ms / 1000)
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${s % 60}s`
}

const SpinnerLine: ClientModule<LineProps, { frame: number }> = (props, surface) => {
  const { Text } = surface.elements
  if (surface.state === undefined) {
    surface.setState({ frame: 0 })
    surface.every(TICK_MS, () => {
      const frame = surface.state?.frame ?? 0
      surface.setState({ frame: frame + 1 })
    })
  }
  const frame = surface.state?.frame ?? 0
  const icon = props.frames[frame % props.frames.length]
  return Text({
    color: props.color,
    children: [
      Text({ bold: true, children: icon }),
      ` ${props.text} `,
      Text({ dimColor: true, children: `(${[formatElapsed(frame * TICK_MS), props.extras].filter(Boolean).join(' · ')})` }),
    ],
  })
}

export default SpinnerLine
