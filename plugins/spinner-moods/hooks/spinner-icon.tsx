import type { ClientModule } from 'claude-code'

type Look = { color: string | null; frames: string[] }

type LineProps = Look & {
  mood: string
  sleepy: (Look & { afterMs: number }) | null
  text: string
  extras: string
  progress: number
  tickMs: number
  showTime: boolean
}

// `since` is when the mood or token count last changed: no change for
// `sleepy.afterMs` and the line dozes off until something happens.
type LineState = { ticks: number; key: string; since: number }

function formatElapsed(ms: number): string {
  const s = Math.floor(ms / 1000)
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${s % 60}s`
}

const SpinnerLine: ClientModule<LineProps, LineState> = (props, surface) => {
  const { Text } = surface.elements
  const key = `${props.mood}|${props.text}|${props.progress}`
  if (surface.state === undefined) {
    surface.setState({ ticks: 0, key, since: 0 })
    surface.every(props.tickMs, () => {
      const s = surface.state
      if (s) surface.setState({ ...s, ticks: s.ticks + 1 })
    })
  } else if (surface.state.key !== key) {
    surface.setState({ ...surface.state, key, since: surface.state.ticks })
  }
  const ticks = surface.state?.ticks ?? 0
  const since = surface.state?.key === key ? surface.state.since : ticks
  const dozing = props.sleepy !== null && (ticks - since) * props.tickMs >= props.sleepy.afterMs
  const look: Look = dozing && props.sleepy ? props.sleepy : props
  const icon = look.frames[(dozing ? Math.floor(ticks / 4) : ticks) % look.frames.length]
  const tail = [props.showTime ? formatElapsed(ticks * props.tickMs) : null, props.extras || null]
    .filter(Boolean)
    .join(' · ')
  return Text({
    ...(look.color ? { color: look.color } : {}),
    children: [
      Text({ bold: true, children: icon }),
      ` ${props.text}${dozing ? ' zzz' : ''}`,
      tail ? Text({ dimColor: true, children: ` (${tail})` }) : '',
    ],
  })
}

export default SpinnerLine
