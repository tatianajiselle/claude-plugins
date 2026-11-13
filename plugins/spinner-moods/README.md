# spinner-moods

A Claude Code mod that colors and animates the spinner line by what Claude is doing, so you can tell at a glance whether it's thinking, running tools, or doing something else.

| State | Color | Icon animation |
| --- | --- | --- |
| Inference (thinking, requesting, responding) | magenta | `· ✢ ✳ ✶ ✻ ✽` pulse |
| Tool calls (writing tool input, running a tool) | cyan | `◐ ◓ ◑ ◒` spin |
| Other (status messages such as compacting) | yellow | `◇ ◈ ◆` flicker |

The line reads like `◐ Sauteing… (12s · ↓ ~340 tokens · high)`: the icon and word in the state's color, then the elapsed time, tokens, and effort dimmed. Tokens are exact for finished model requests and estimated (about 4 characters per token) for the one still streaming. Only the main agent's tokens are counted.

Terminal only; the desktop app and VS Code keep their own spinner.

## Install

At the prompt of a Claude Code terminal session:

```
/plugin install spinner-moods --marketplace tatianajiselle/claude-plugins
```

Answer `y` to add the marketplace, then pick a scope.

From a shell:

```
claude plugin install spinner-moods --marketplace tatianajiselle/claude-plugins
```

## Customize

Edit the `STYLES` table in `hooks/register.tsx`. A color is a name (`red`, `cyan`), a hex value (`#ff8800`), or a theme key (`claude`, `warning`, `success`). `frames` is the list of icons the animation cycles through.
