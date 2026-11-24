"""Render spinner-moods demo frames straight from plugins/spinner-moods/hooks/moods.ts.

Usage: python3 scripts/render-spinner-demo.py OUT_DIR [tour|story] [calm|normal|zippy]
Needs Pillow and macOS fonts (Menlo, Apple Symbols). Then, for a README GIF:
  ffmpeg -framerate 25/3 -i OUT_DIR/%04d.png -vf "scale=760:-1:flags=lanczos,split[a][b];\
    [a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=none" -loop 0 story.gif
-framerate is 1000 / the speed's ms per frame (25/3 for normal's 120 ms).
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

MOODS_TS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'plugins', 'spinner-moods', 'hooks', 'moods.ts')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'frames'

# ---- read THEMES / PALETTES / SPEEDS out of moods.ts ----
src = open(MOODS_TS, encoding='utf-8').read()


def table(name):
    body = re.search(rf'export const {name}[^=]*= (\{{.*?\}})\n\n', src, re.S).group(1)
    body = re.sub(r'//[^\n]*', '', body)
    body = re.sub(r"'", '"', body)
    body = re.sub(r'(\w+):', r'"\1":', body)
    body = re.sub(r',(\s*[}\]])', r'\1', body)
    return json.loads(body)


THEMES, PALETTES, SPEEDS = table('THEMES'), table('PALETTES'), table('SPEEDS')
NAMED = {'magenta': '#d670d6', 'cyan': '#29b8db', 'yellow': '#e5e510', 'red': '#f14c4c'}

# ---- look ----
SCALE = 2
W, H = 760 * SCALE, 210 * SCALE
BG, CHROME, FG, DIM = '#1e1e2e', '#2a2a3c', '#cdd6f4', '#6c7086'
SIZE = 22 * SCALE
FONTS = [
    '/System/Library/Fonts/Menlo.ttc',
    '/System/Library/Fonts/Apple Symbols.ttf',
    '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    '/System/Library/Fonts/Supplemental/STIXGeneral.otf',
]
fonts = [ImageFont.truetype(f, SIZE) for f in FONTS]
SYM = 1.2  # symbols drawn a little larger than text, centred on it
sym_fonts = {f: ImageFont.truetype(f, int(SIZE * SYM)) for f in FONTS}
bold = ImageFont.truetype(FONTS[0], SIZE, index=1)
small = ImageFont.truetype(FONTS[0], 15 * SCALE)
CELL = fonts[0].getlength('M')


def covers(font, ch):
    # A font lacks a glyph when it draws the same box as for a private-use char.
    m, missing = font.getmask(ch), font.getmask('')
    return ch == ' ' or m.size != missing.size or bytes(m) != bytes(missing)


_pick = {}


def font_for(ch, is_bold=False):
    if ch.isascii():
        return bold if is_bold else fonts[0]
    if ch not in _pick:
        _pick[ch] = next((f for f in fonts if covers(f, ch)), fonts[-1])
    return _pick[ch]


def draw_cells(d, x0, y, text, color, is_bold=False, is_icon=False):
    """Draw one char per terminal cell, centring wide symbols in their cell."""
    for i, ch in enumerate(text):
        f = font_for(ch, is_bold)
        if ch.isascii():
            d.text((x0 + i * CELL, y), ch, font=f, fill=color)
            continue
        if not is_icon:
            d.text((x0 + i * CELL + (CELL - f.getlength(ch)) / 2, y), ch, font=f, fill=color)
            continue
        f = sym_fonts[f.path]
        w = f.getlength(ch)
        d.text((x0 + i * CELL + (CELL - w) / 2, y - SIZE * (SYM - 1) / 2), ch, font=f, fill=color)
    return x0 + len(text) * CELL


def color_of(c):
    return FG if c is None else NAMED.get(c, c)


def fmt_elapsed(ms):
    s = int(ms // 1000)
    return f'{s}s' if s < 60 else f'{s // 60}m {s % 60}s'


def frame(theme, palette, mood, word, tick, elapsed_ms, tokens, caption):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    # window chrome
    d.rectangle([0, 0, W, 34 * SCALE], fill=CHROME)
    for i, c in enumerate(['#f38ba8', '#f9e2af', '#a6e3a1']):
        cx, cy, r = (20 + i * 22) * SCALE, 17 * SCALE, 6 * SCALE
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    title = f'spinner-moods · theme: {theme} · palette: {palette}'
    d.text((W / 2 - small.getlength(title) / 2, 8 * SCALE), title, font=small, fill=DIM)
    # prompt context line
    y1 = 62 * SCALE
    draw_cells(d, 28 * SCALE, y1, '> make the onboarding flow cozier', DIM)
    # the spinner line
    y2 = 108 * SCALE
    frames = THEMES[theme][mood]
    # the mod dozes at a quarter of the speed: one sleepy frame per four ticks
    icon = frames[(tick // 4 if mood == 'sleepy' else tick) % len(frames)]
    col = color_of(PALETTES[palette][mood])
    x = draw_cells(d, 28 * SCALE, y2, icon, col, is_bold=True, is_icon=True)
    x = draw_cells(d, x, y2, f' {word}…' + (' zzz' if mood == 'sleepy' else ''), col)
    tail = ' · '.join(p for p in [fmt_elapsed(elapsed_ms), f'↓ ~{tokens / 1000:.1f}k tokens' if tokens >= 1000 else f'↓ ~{tokens} tokens', 'high'] if p)
    draw_cells(d, x, y2, f' ({tail})', DIM)
    # caption
    d.text((28 * SCALE, 160 * SCALE), caption, font=small, fill='#a6adc8')
    return img


# ---- scenes ----
MODE = sys.argv[2] if len(sys.argv) > 2 else 'tour'
SPEED = sys.argv[3] if len(sys.argv) > 3 else 'normal'
TICK = SPEEDS[SPEED]

# (theme, palette, [(mood, word, seconds, caption, jump_ms)])
TOUR_BEATS = [
    ('inference', 'Pondering', 1.6, 'thinking', 0),
    ('tool', 'Brewing', 1.6, 'running a tool', 0),
    ('flustered', 'Brewing', 1.2, 'a tool failed: flustered', 0),
]
SCENES = {
    'tour': [(t, p, TOUR_BEATS) for t, p in
             [('classic', 'classic'), ('sparkle', 'neon'), ('hearts', 'pastel'), ('moon', 'cozy'), ('geometric', 'mono'),
              ('bloom', 'pastel'), ('bars', 'neon'), ('arc', 'cozy'), ('squares', 'classic')]],
    'story': [('moon', 'pastel', [
        ('inference', 'Pondering', 3.2, 'thinking…', 0),
        ('tool', 'Brewing', 3.2, 'running a tool…', 0),
        ('flustered', 'Brewing', 2.6, 'uh oh, the tool failed: flustered', 0),
        ('tool', 'Brewing', 2.0, 'deep breath, trying again…', 0),
        ('sleepy', 'Brewing', 5.2, 'a whole minute with no progress: sleepy', 55_000),
        ('tool', 'Brewing', 2.6, 'and it wakes right back up', 0),
    ])],
}

os.makedirs(OUT, exist_ok=True)
n = 0
for theme, palette, beats in SCENES[MODE]:
    elapsed, tokens = 3000, 240
    for mood, word, secs, caption, jump in beats:
        elapsed += jump
        for t in range(int(secs * 1000 / TICK)):
            elapsed += TICK
            if mood == 'inference':
                tokens += 9
            frame(theme, palette, mood, word, t, elapsed, tokens, caption).save(f'{OUT}/{n:04d}.png')
            n += 1
print(n, 'frames at', TICK, 'ms', f'({SPEED})')
