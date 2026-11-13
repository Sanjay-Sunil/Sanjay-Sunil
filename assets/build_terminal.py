#!/usr/bin/env python3
"""Builds assets/terminal.svg and assets/footer.svg: animated terminal sessions for the profile README.

Edit SESSION / FOOTER below and run:  python3 assets/build_terminal.py
The neofetch logo is drawn from assets/avatar.jpg (needs ImageMagick's `magick`).
"""
import colorsys
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

W, PAD, LH, CHAR = 900, 26, 21, 8.45  # width, left padding, line height, approx monospace char width
TOP = 64                              # baseline of the first line (below the title bar)
TYPE_SPEED = 0.035                    # seconds per typed character
LINE_GAP = 0.07                       # seconds between output lines
PAUSE = 0.45                          # pause after a command finishes / before the next prompt

# Tokyo Night palette
C = {
    "bg": "#1a1b26", "bar": "#16161e", "border": "#2f334d", "fg": "#c0caf5", "dim": "#565f89",
    "red": "#f7768e", "orange": "#ff9e64", "yellow": "#e0af68", "green": "#9ece6a",
    "cyan": "#7dcfff", "blue": "#7aa2f7", "magenta": "#bb9af7", "white": "#a9b1d6",
}

# neofetch logo: my avatar (assets/avatar.jpg) as coloured ASCII, like `jp2a --colors`.
AVATAR = Path(__file__).with_name("avatar.jpg")
ART_LINES = 18                        # terminal lines the logo spans
ART_FONT, ART_LH = 7.0, 7.7           # the logo uses a small font, like a zoomed-out terminal
ART_CW = ART_FONT * 0.6               # monospace character width at that size
ART_W = 380                           # logo width in px
ART_COLS = int(ART_W / ART_CW)
ART_ROWS = int(ART_LINES * LH / ART_LH)
ART_CROP = "357x400+43+0"             # region of the 400x400 avatar around the dragon
RAMP = ":-=+*#%@"                     # dark -> bright
MIN_LIGHT = 0.30                      # lift colours darker than this (0-1)
BG_FADE = 0.45                        # how much of a light streak's colour to keep (0-1)

def avatar_ascii():
    """Brighter spots get denser characters, each in that spot's colour. Dark colours are lifted so the black
    dragon shows on the dark terminal, and the blue/white light streaks are faded so the dragon stands out."""
    raw = subprocess.run(["magick", str(AVATAR), "-crop", ART_CROP, "+repage", "-sigmoidal-contrast", "4,45%",
                          "-resize", f"{ART_COLS}x{ART_ROWS}!", "-depth", "8", "rgb:-"],
                         capture_output=True, check=True).stdout
    bg = [int(C["bg"][k:k + 2], 16) for k in (1, 3, 5)]
    rows = []
    for r in range(ART_ROWS):
        row = []
        for c in range(ART_COLS):
            i = (r * ART_COLS + c) * 3
            rgb = list(raw[i:i + 3])
            h, sat, val = colorsys.rgb_to_hsv(*(v / 255 for v in rgb))
            luma = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
            ch = RAMP[min(len(RAMP) - 1, int(luma * len(RAMP)))]
            gold = 0.07 < h < 0.17 and 0.3 < sat < 0.9 and val < 0.85
            if luma < MIN_LIGHT:                      # dragon body: lift so it's visible
                lift = (MIN_LIGHT - luma) * 255
                rgb = [min(255, int(v + lift * 0.9)) for v in (rgb[0], rgb[1], rgb[2] + 12)]
            elif not gold:                            # light streaks: fade toward the background
                rgb = [int(b + (v - b) * BG_FADE) for v, b in zip(rgb, bg)]
            row.append((ch, "#" + "".join(f"{v:02x}" for v in rgb)))
        rows.append(row)
    return rows

def art_line(i, y):
    """The logo rows that fall on terminal line i (so the logo prints line by line)."""
    top = y - 15 - i * LH  # top of the logo
    out = []
    for r in range(ART_ROWS):
        if int(r * ART_LH // LH) != i:
            continue
        spans, run, col = [], "", None
        for ch, c in ART[r] + [("", None)]:
            if c != col and run:
                spans.append(f'<tspan fill="{col}">{escape(run)}</tspan>')
                run = ""
            run, col = run + ch, c
        out.append(f'<text x="{PAD}" y="{top + (r + 1) * ART_LH - 1.5:.1f}" class="art" textLength="{ART_W}" '
                   f'lengthAdjust="spacingAndGlyphs">{"".join(spans)}</text>')
    return out

def kv(k, v, kc="blue"):
    return [(k + ": ", kc + " b"), (v, "fg")]

INFO = [
    [("sanjay", "green b")],
    [("-" * 6, "dim")],
    kv("OS", "human · kerala, india"),
    kv("Host", "iiit kottayam, ai & data science"),
    kv("WM", "hyprland (btw)"),
    kv("Stack", "python, pytorch, onnx, typescript"),
    kv("Into", "edge ai · speech / asr · medical imaging"),
    kv("Fuel", "chai, way too much of it"),
    [],
    "COLORS",
]

def neofetch():
    # each row: ("NEO", logo line index or None, right-hand segments or "COLORS")
    return [("NEO", i if i < ART_LINES else None, INFO[i] if i < len(INFO) else [])
            for i in range(max(ART_LINES, len(INFO)))]

def log(when, unit, msg):
    if not unit:  # continuation line
        return [(" " * 9, "fg"), (msg, "fg")]
    return [(f"{when:<9}", "dim"), (unit, "magenta"), (": ", "dim"), (msg, "fg")]

def ls(perm, name, note, is_dir=True):
    return [(perm + "  ", "dim"), (f"{name:<16}", "blue b" if is_dir else "green b"), ("# " + note, "dim")]

SESSION = [
    ("neofetch", neofetch()),
    ("cat now_playing.txt", [
        [("→ ", "magenta b"), ("teaching small models to understand hinglish", "fg")],
        [("→ ", "magenta b"), ("squeezing a medical imaging model onto a raspberry pi", "fg")],
        [("→ ", "magenta b"), ("calling \"one more epoch\" a plan", "fg")],
    ]),
]

FOOTER = [
    ("exit", [
        [("logout", "fg")],
        [("thanks for stopping by, see ya", "magenta")],
    ]),
]

PROMPT = [("~ ", "blue b"), ("❯ ", "magenta b")]
PROMPT_LEN = sum(len(t) for t, _ in PROMPT)

def tspans(segs):
    out = []
    for text, cls in segs:
        classes = " ".join(cls.split())
        out.append(f'<tspan class="{classes}">{escape(text)}</tspan>')
    return "".join(out)

def build(session, name, final_prompt=True):
    body, t, y = [], 0.4, TOP
    for cmd, output in session:
        # prompt appears, then the command is "typed" by sliding a cover off it
        body.append(f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="{PAD}" y="{y}">{tspans(PROMPT)}'
                    f'<tspan class="fg">{escape(cmd)}</tspan></text>')
        cx, cw = PAD + PROMPT_LEN * CHAR, len(cmd) * CHAR + 12
        dur = len(cmd) * TYPE_SPEED
        body.append(f'<rect x="{cx:.1f}" y="{y - 15}" width="{cw:.1f}" height="20" fill="{C["bg"]}" class="type" '
                    f'style="--w:{cw:.1f}px;animation-duration:{dur:.2f}s;animation-delay:{t + 0.25:.2f}s;'
                    f'animation-timing-function:steps({len(cmd)})"/></g>')
        t += 0.25 + dur + PAUSE
        y += LH
        for row in output:
            if isinstance(row, tuple) and row[0] == "NEO":
                _, art_i, right = row
                parts = []
                if art_i is not None:
                    parts += art_line(art_i, y)
                x0 = PAD + ART_W + 3 * CHAR
                if right == "COLORS":
                    parts += [f'<rect x="{x0 + i * 26:.1f}" y="{y - 14}" width="24" height="16" rx="2" fill="{C[k]}"/>'
                              for i, k in enumerate(["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "white"])]
                elif right:
                    parts.append(f'<text x="{x0:.1f}" y="{y}">{tspans(right)}</text>')
                body.append(f'<g class="ln" shape-rendering="crispEdges" style="animation-delay:{t:.2f}s">{"".join(parts)}</g>')
            elif row:
                body.append(f'<text x="{PAD}" y="{y}" class="ln" style="animation-delay:{t:.2f}s">{tspans(row)}</text>')
            t += LINE_GAP
            y += LH
        t += PAUSE
        y += LH // 2
    if final_prompt:
        # final prompt with a blinking cursor
        body.append(f'<text x="{PAD}" y="{y}" class="ln" style="animation-delay:{t:.2f}s">{tspans(PROMPT)}</text>')
        body.append(f'<rect x="{PAD + PROMPT_LEN * CHAR:.1f}" y="{y - 14}" width="9" height="18" fill="{C["fg"]}" '
                    f'class="cursor" style="animation-delay:{t:.2f}s"/>')
    else:
        y -= LH // 2 + LH  # no trailing prompt: trim the gap after the last output line
    H = y + 26

    style = f"""
    text {{ font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "DejaVu Sans Mono", monospace;
           font-size: 14px; fill: {C['fg']}; white-space: pre; }}
    .b {{ font-weight: 700; }}
    .art {{ font-size: {ART_FONT}px; font-weight: 700; }}
    {' '.join(f'.{k} {{ fill: {v}; }}' for k, v in C.items() if k not in ('bg', 'bar', 'border'))}
    .ln {{ opacity: 0; animation: show .01s linear forwards; }}
    @keyframes show {{ to {{ opacity: 1; }} }}
    .type {{ animation-name: type; animation-fill-mode: forwards; }}
    @keyframes type {{ to {{ transform: translateX(var(--w)); width: 0; }} }}
    .cursor {{ opacity: 0; animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    """
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" xml:space="preserve" role="img" aria-label="Terminal session for Sanjay">
<style>{style}</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{C['bg']}" stroke="{C['border']}"/>
<path d="M1 11a10 10 0 0 1 10-10h{W - 22}a10 10 0 0 1 10 10v26H1z" fill="{C['bar']}"/>
<line x1="1" y1="37" x2="{W - 1}" y2="37" stroke="{C['border']}"/>
<circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/><circle cx="62" cy="19" r="6" fill="#28c840"/>
<text x="{W / 2}" y="24" text-anchor="middle" class="dim">sanjay — zsh — {W // 9}×{(H - 40) // LH}</text>
{chr(10).join(body)}
</svg>
"""
    out = Path(__file__).with_name(name)
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({W}x{H}, animation {t:.1f}s)")

if __name__ == "__main__":
    ART = avatar_ascii()
    build(SESSION, "terminal.svg")
    build(FOOTER, "footer.svg", final_prompt=False)
