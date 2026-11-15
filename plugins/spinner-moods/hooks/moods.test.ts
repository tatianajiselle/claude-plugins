import { describe, expect, mock, test } from 'claude-code/testing'

const THINKING = { word: 'Sauteing', message: null, suffix: '…', mode: 'thinking' } as const
const TOOL = { ...THINKING, mode: 'tool-use' } as const

const mount = ($: any, props: object) =>
  $.ui.mount({ plugin: 'spinner-moods', surface: 'terminal', component: 'Spinner', props })

async function line(ui: any): Promise<any> {
  return ui.drawn({ in: 'line' })
}

function text(node: any): string {
  if (typeof node === 'string') return node
  if (!node) return ''
  const kids = node.props?.children ?? node.children ?? []
  return (Array.isArray(kids) ? kids : [kids]).map(text).join('')
}

// A tool's result as the engine appends it to the transcript.
const toolResult = ({ isError = false, agentId }: { isError?: boolean; agentId?: string } = {}) =>
  ({
    message: {
      type: 'user',
      role: 'user',
      content: [{ type: 'tool_result', tool_use_id: 'toolu_1', content: 'boom', is_error: isError }],
    },
    door: 'tool-result',
    origin: { kind: 'tool', tool: 'Bash' },
    uuid: crypto.randomUUID(),
    ...(agentId === undefined ? {} : { agentId }),
  }) as never

describe('spinner-moods', () => {
  test('classic theme by default: magenta thinking, cyan tools', async $ => {
    const ui = await mount($, THINKING)
    const drawn = await line(ui)
    expect(drawn.props.color).toBe('magenta')
    expect(text(drawn)).toContain('· Sauteing…')
    await ui.redraw(TOOL)
    expect((await line(ui)).props.color).toBe('cyan')
  })

  test('theme and palette options change icon and color', { options: { theme: 'sparkle', palette: 'pastel' } }, async $ => {
    const ui = await mount($, THINKING)
    expect(text(await line(ui))).toMatch(/^˚ Sauteing/)
    expect((await line(ui)).props.color).toBe('#f5a9d0')
  })

  test('minimal details shows only the icon and word', { options: { details: 'minimal' } }, async $ => {
    const ui = await mount($, THINKING)
    expect(text(await line(ui))).toBe('· Sauteing…')
  })

  test('mono palette uses the terminal color', { options: { palette: 'mono' } }, async $ => {
    const ui = await mount($, THINKING)
    expect((await line(ui)).props?.color).toBeUndefined()
  })

  test('gets sleepy after a minute with no progress', { options: { theme: 'moon' } }, async $ => {
    const ui = await mount($, TOOL)
    await ui.advance(30_000)
    expect(text(await line(ui))).not.toContain('zzz')
    await ui.advance(31_000)
    const drawn = await line(ui)
    expect(text(drawn)).toContain('zzz')
    expect(text(drawn)).toMatch(/^[☾☽]/)
    expect(drawn.props.color).toBe('#8a8a8a')
  })

  test('no reactions when turned off', { options: { reactions: false } }, async $ => {
    const ui = await mount($, TOOL)
    await ui.advance(61_000)
    expect(text(await line(ui))).not.toContain('zzz')
  })

  test('a failed tool call flusters, then calms down', async ($, on) => {
    const clock = mock.clock(on)
    const ui = await mount($, TOOL)
    await $.session.append(toolResult({ isError: true }))
    expect((await line(ui)).props.color).toBe('red')
    expect(text(await line(ui))).toMatch(/^[✗✘]/)
    await clock.advance(4_000)
    expect((await line(ui)).props.color).toBe('cyan')
  })

  test("a successful result or a subagent's failure stays calm", async $ => {
    const ui = await mount($, TOOL)
    await $.session.append(toolResult())
    await $.session.append(toolResult({ isError: true, agentId: 'a1' }))
    expect((await line(ui)).props.color).toBe('cyan')
  })
})
