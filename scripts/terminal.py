"""The terminal window: four looping scenes (ML, Rust, web, Claude Code).

Left half types commands and prints output; right half shows what the
command does. Scene content lives in SCENES; panels are drawn per scene.
"""

import math
import re
from pathlib import Path

from kit import (
    AMBER, AQUA, BG, CYAN, DIM, DISPLAY, GREEN, INK, MONO, MUTED, PINK,
    REDUCED_MOTION, VIOLET, esc, font_face, write,
)
from timeline import Timeline

W, H = 1200, 560
SCENE = 8.0
SIZE = 17
CW = SIZE * 0.6
LH = 28
X0, Y0 = 52, 112
RUST = "#FF5F57"
CLAUDE = "#D97757"

COLORS = {
    "k": PINK, "f": CYAN, "s": GREEN, "n": AMBER, "c": DIM, "m": MUTED,
    "v": VIOLET, "o": GREEN, "r": RUST, "w": INK, "a": AQUA, "x": CLAUDE,
}

# (kind, text). kind: cmd = typed after a prompt, out = printed line,
# code = fast listing line, gap = blank line. [x]...[/] colors a span.
SCENES = [
    {
        "tab": "train.py",
        "title": "artem@misis: ~/ml",
        "lines": [
            ("cmd", "whoami"),
            ("out", "[w]artem krupa[/] [m]·[/] ml engineer in the making"),
            ("gap", ""),
            ("cmd", "python train.py --task tickets --base yandexgpt-5-pro"),
            ("out", "[m]›[/] fine-tuning classifier head [m]· deep learning[/]"),
            ("out", "epoch [n]1[/][m]/4[/]  [v]███[/][c]░░░░░░░[/]  loss [n]1.284[/]"),
            ("out", "epoch [n]2[/][m]/4[/]  [v]█████[/][c]░░░░░[/]  loss [n]0.611[/]"),
            ("out", "epoch [n]3[/][m]/4[/]  [v]████████[/][c]░░[/]  loss [n]0.342[/]"),
            ("out", "epoch [n]4[/][m]/4[/]  [v]██████████[/]  loss [n]0.198[/]"),
            ("out", "[o]✓[/] saved [m]→[/] checkpoints/classifier.pt"),
        ],
    },
    {
        "tab": "lib.rs",
        "title": "artem@misis: ~/vst-plugin",
        "lines": [
            ("cmd", "cat src/lib.rs"),
            ("code", "[k]fn[/] [f]process[/](&[k]mut[/] self, buf: &[k]mut[/] [a]Buffer[/]) {"),
            ("code", "    [k]for[/] s [k]in[/] buf.[f]iter_samples[/]() {"),
            ("code", "        *s = (*s * self.gain).[f]tanh[/](); [c]// soft clip[/]"),
            ("code", "    }"),
            ("code", "}"),
            ("gap", ""),
            ("cmd", "cargo build --release"),
            ("out", "   [o]Compiling[/] vst-plugin v0.1.0"),
            ("out", "    [o]Finished[/] release [m][optimized][/]"),
            ("out", "[o]✓[/] bundled [m]→[/] VST3 · CLAP [m](ableton · fl studio)[/]"),
        ],
    },
    {
        "tab": "Card.tsx",
        "title": "artem@misis: ~/web",
        "lines": [
            ("cmd", "cat Card.tsx"),
            ("code", "[k]export const[/] [f]Card[/] = ({ title }) => ("),
            ("code", "  <[r]article[/] [a]className[/]=[s]\"glass glow\"[/]>"),
            ("code", "    <[r]h3[/]>{title}</[r]h3[/]>"),
            ("code", "    <[r]button[/]>[w]Open[/]</[r]button[/]>"),
            ("code", "  </[r]article[/]>"),
            ("code", ");"),
            ("gap", ""),
            ("cmd", "npm run dev"),
            ("out", "  [o]VITE[/] ready in [n]312[/] ms [m]→[/] [a]localhost:5173[/]"),
        ],
    },
    {
        "tab": "claude",
        "title": "artem@misis: ~/hotel-search",
        "lines": [
            ("cmd", "claude \"model street noise per facade\""),
            ("out", "[x]✻[/] plan [m]·[/] read 14 files [m]·[/] 3 steps"),
            ("out", "[v]●[/] Edit geo/noise.py          [o]+128[/] [r]-12[/]"),
            ("out", "[v]●[/] Edit eval/noise_reviews.py [o]+64[/]"),
            ("out", "[v]●[/] Bash uv run pytest         [o]42 passed[/]"),
            ("out", "[o]✓[/] done [m]·[/] diff ready for review"),
        ],
    },
]


def spans(markup: str) -> str:
    out, pos = [], 0
    for m in re.finditer(r"\[(\w)\](.*?)\[/\]", markup):
        if m.start() > pos:
            out.append(esc(markup[pos:m.start()]))
        out.append(f'<tspan fill="{COLORS[m.group(1)]}">{esc(m.group(2))}</tspan>')
        pos = m.end()
    out.append(esc(markup[pos:]))
    return "".join(out)


def plain(markup: str) -> str:
    return re.sub(r"\[(\w)\](.*?)\[/\]", r"\2", markup)


def scene_lines(tl: Timeline, idx: int, start: float) -> tuple[str, list[float]]:
    """Left column of one scene; returns svg and the time each line appeared."""
    svg, times = [], []
    t, y = start + 0.35, Y0
    for kind, text in SCENES[idx]["lines"]:
        if kind == "gap":
            y += LH * 0.55
            times.append(t)
            continue
        if kind == "cmd":
            n = len(text)
            dur = n * 0.034
            cid = f"cl{idx}_{len(times)}"
            x = X0 + CW * 2
            svg.append(
                f'<clipPath id="{cid}"><rect x="{x}" y="{y - SIZE}" width="{n * CW + 2:.1f}" height="{LH}" '
                f'style="transform-origin:{x}px 0;{tl.typed(t, dur, n)}"/></clipPath>'
                f'<g style="{tl.appear(t, 0.15, 0)}"><text class="t" x="{X0}" y="{y}" fill="{CYAN}">$</text>'
                f'<text class="t" x="{x}" y="{y}" fill="{INK}" clip-path="url(#{cid})">{esc(text)}</text></g>'
            )
            times.append(t)
            t += dur + 0.45
        else:
            svg.append(f'<text class="t" x="{X0}" y="{y}" fill="{MUTED}" style="{tl.appear(t, 0.22, 4)}">{spans(text)}</text>')
            times.append(t)
            t += 0.11 if kind == "code" else 0.34
        y += LH
    return "".join(svg), times


def loss_panel(tl: Timeline, times: list[float]) -> str:
    x0, x1, y0, y1 = 780, 1140, 150, 440
    pts = []
    for i in range(61):
        f = i / 60
        loss = 0.14 + 0.86 * math.exp(-3.4 * f) + 0.035 * math.sin(i * 1.9) * (1 - f)
        pts.append((x0 + f * (x1 - x0), y1 - loss * (y1 - y0)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = d + f" L{x1},{y1} L{x0},{y1} Z"
    a, b = times[4], times[8]
    ex, ey = pts[-1]
    grid = "".join(
        f'<line x1="{x0}" x2="{x1}" y1="{y0 + k * (y1 - y0) / 4:.0f}" y2="{y0 + k * (y1 - y0) / 4:.0f}" stroke="#fff" stroke-opacity=".06" stroke-dasharray="3 5"/>'
        for k in range(4)
    )
    ticks = "".join(
        f'<text class="s" x="{x0 + k * (x1 - x0) / 4:.0f}" y="{y1 + 24}" text-anchor="middle">{k}</text>' for k in range(5)
    )
    return f"""
<text class="s" x="{x0}" y="{y0 - 30}" fill="{INK}">loss <tspan fill="{MUTED}">· fine-tune · classifier</tspan></text>
{grid}
<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#fff" stroke-opacity=".18"/>
{ticks}
<path d="{area}" fill="url(#lossArea)" style="{tl.appear(b, 0.8, 0)}"/>
<path d="{d}" pathLength="1" fill="none" stroke="url(#lossLine)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="stroke-dasharray:1;{tl.draw(a, b - a + 0.3)}"/>
<g style="{tl.appear(b + 0.3, 0.3, 0)}">
  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{GREEN}"/>
  <circle class="ring" cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="none" stroke="{GREEN}"/>
  <text class="s" x="{ex - 12:.1f}" y="{ey - 16:.1f}" text-anchor="end" fill="{GREEN}">0.198</text>
</g>"""


def wave(x0: float, x1: float, y: float, amp: float, period: float, drive: float) -> str:
    pts = []
    x = x0
    while x <= x1:
        v = math.sin((x - x0) / period * 2 * math.pi)
        if drive:
            v = math.tanh(v * drive) / math.tanh(drive)
        pts.append(f"{x:.1f},{y - v * amp:.1f}")
        x += 3
    return "M" + " L".join(pts)


def vst_panel(tl: Timeline, times: list[float], start: float) -> str:
    x0, x1, per = 770, 1150, 95
    dry = wave(x0, x1 + per * 2, 205, 34, per, 0)
    wet = wave(x0, x1 + per * 2, 330, 40, per, 3.2)
    knobs = []
    for k, (label, val) in enumerate([("GAIN", 0.72), ("DRIVE", 0.58), ("MIX", 0.86)]):
        cx, cy, r = 830 + k * 130, 450, 24
        # 280° sweep from bottom-left, clockwise to bottom-right
        p0 = (cx + r * math.cos(math.radians(130)), cy + r * math.sin(math.radians(130)))
        p1 = (cx + r * math.cos(math.radians(50)), cy + r * math.sin(math.radians(50)))
        arc = f"M{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 1 1 {p1[0]:.1f},{p1[1]:.1f}"
        knobs.append(
            f'<path d="{arc}" fill="none" stroke="#fff" stroke-opacity=".1" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="{arc}" pathLength="1" fill="none" stroke="url(#knob)" stroke-width="5" stroke-linecap="round" '
            f'style="stroke-dasharray:1;{tl.draw(times[8] + k * 0.15, 0.9, round(1 - val, 2))}"/>'
            f'<text class="s" x="{cx}" y="{cy + 5}" text-anchor="middle" fill="{INK}">{int(val * 100)}</text>'
            f'<text class="s" x="{cx}" y="{cy + 46}" text-anchor="middle">{label}</text>'
        )
    return f"""
<text class="s" x="{x0}" y="120" fill="{INK}">process() <tspan fill="{MUTED}">· 48 kHz · stereo</tspan></text>
<clipPath id="waveClip"><rect x="{x0}" y="140" width="{x1 - x0}" height="250"/></clipPath>
<text class="s" x="{x0}" y="160">dry</text>
<text class="s" x="{x0}" y="282">wet</text>
<g clip-path="url(#waveClip)">
  <path class="scroll" d="{dry}" fill="none" stroke="{MUTED}" stroke-opacity=".55" stroke-width="2"/>
  <g style="{tl.appear(times[8], 0.6, 0)}">
    <path class="scroll" d="{wet}" fill="none" stroke="url(#wet)" stroke-width="6" stroke-opacity=".25" filter="url(#soft)"/>
    <path class="scroll" d="{wet}" fill="none" stroke="url(#wet)" stroke-width="2.6"/>
  </g>
</g>
{''.join(knobs)}"""


def web_panel(tl: Timeline, times: list[float]) -> str:
    bx, by, bw, bh = 770, 92, 380, 420
    ready = times[9]
    skel = "".join(
        f'<rect class="skel" x="{bx + 40}" y="{by + 90 + k * 46}" width="{[300, 230, 260, 160][k]}" height="22" rx="6"/>'
        for k in range(4)
    )
    cx, cy, cw, ch = bx + 40, by + 78, 300, 290
    btn_x, btn_y = cx + 24, cy + 220
    return f"""
<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="#0E1124" stroke="#fff" stroke-opacity=".1"/>
<path d="M{bx} {by + 16} a16 16 0 0 1 16 -16 h{bw - 32} a16 16 0 0 1 16 16 v20 h-{bw} z" fill="#fff" fill-opacity=".04"/>
<circle cx="{bx + 20}" cy="{by + 18}" r="4.5" fill="#fff" fill-opacity=".2"/><circle cx="{bx + 36}" cy="{by + 18}" r="4.5" fill="#fff" fill-opacity=".2"/><circle cx="{bx + 52}" cy="{by + 18}" r="4.5" fill="#fff" fill-opacity=".2"/>
<rect x="{bx + 110}" y="{by + 8}" width="180" height="20" rx="10" fill="#fff" fill-opacity=".06"/>
<text class="s" x="{bx + 200}" y="{by + 22}" text-anchor="middle">localhost:5173</text>
<g style="{tl.window(times[0], ready + 0.3, 0.3)}">{skel}</g>
<g style="{tl.appear(ready, 0.6, 14)}">
  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="18" fill="#fff" fill-opacity=".05" stroke="url(#cardEdge)" stroke-width="1.5"/>
  <clipPath id="cardTop"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="18"/></clipPath>
  <g clip-path="url(#cardTop)">
    <rect x="{cx}" y="{cy}" width="{cw}" height="130" fill="url(#cardSky)"/>
    <circle class="orb" cx="{cx + 70}" cy="{cy + 60}" r="60" fill="{CYAN}" fill-opacity=".55" filter="url(#soft)"/>
    <circle class="orb orb2" cx="{cx + 220}" cy="{cy + 70}" r="55" fill="{PINK}" fill-opacity=".55" filter="url(#soft)"/>
  </g>
  <text x="{cx + 24}" y="{cy + 172}" class="h">Glass card</text>
  <rect x="{cx + 24}" y="{cy + 186}" width="190" height="8" rx="4" fill="#fff" fill-opacity=".12"/>
  <rect x="{btn_x}" y="{btn_y}" width="104" height="38" rx="19" fill="url(#btn)"/>
  <rect x="{btn_x}" y="{btn_y}" width="104" height="38" rx="19" fill="url(#btn)" filter="url(#soft)" opacity=".7"/>
  <text class="s" x="{btn_x + 52}" y="{btn_y + 24}" text-anchor="middle" fill="#0A0C16" font-weight="700">Open</text>
  <circle cx="{btn_x + 60}" cy="{btn_y + 22}" r="16" fill="#fff" fill-opacity=".5" style="transform-box:fill-box;transform-origin:center;{tl.pulse(ready + 2.3, 0.8)}"/>
</g>
<g style="{tl.appear(ready + 0.6, 0.3, 0)}">
  <g style="{tl.move(ready + 0.9, 1.3, bx + bw - 30, by + bh - 20, btn_x + 54, btn_y + 16)}">
    <path d="M0 0 L0 20 L5.5 15 L9.5 23.5 L13 22 L9 13.5 L16 13.5 Z" fill="#fff" stroke="#0A0C16" stroke-width="1.2"/>
  </g>
</g>"""


def claude_panel(tl: Timeline, times: list[float]) -> str:
    logo = Path(__file__).resolve().parent.parent / ".cache" / "icons" / "claude.svg"
    path = re.search(r' d="([^"]+)"', logo.read_text()).group(1)
    steps = [
        ("plan", "read 14 files", times[1]),
        ("edit", "geo/noise.py", times[2]),
        ("edit", "eval/noise_reviews.py", times[3]),
        ("test", "42 passed", times[4]),
        ("ship", "ready for review", times[5]),
    ]
    nodes = []
    x, y0, gap = 812, 196, 62
    for k, (name, note, at) in enumerate(steps):
        y = y0 + k * gap
        color = GREEN if name in ("test", "ship") else VIOLET
        if k:
            nodes.append(
                f'<path d="M{x},{y - gap + 12} L{x},{y - 12}" pathLength="1" stroke="{color}" stroke-width="2" '
                f'style="stroke-dasharray:1;{tl.draw(at - 0.25, 0.3)}"/>'
            )
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="10" fill="none" stroke="#fff" stroke-opacity=".15" stroke-width="2"/>'
            f'<g style="{tl.appear(at, 0.25, 0)}"><circle cx="{x}" cy="{y}" r="7" fill="{color}"/></g>'
            f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{color}" style="transform-box:fill-box;transform-origin:center;{tl.pulse(at)}"/>'
            f'<text class="s" x="{x + 26}" y="{y + 5}" fill="{INK}" style="{tl.appear(at, 0.3, 0)}">{name} '
            f'<tspan fill="{MUTED}">· {esc(note)}</tspan></text>'
        )
    return f"""
<g transform="translate(784 92) scale(2.1)"><path class="spin" d="{path}" fill="{CLAUDE}"/></g>
<text class="s" x="848" y="112" fill="{INK}">Claude Code <tspan fill="{MUTED}">· agentic workflow</tspan></text>
<text class="s" x="848" y="134">plan → edit → test → review</text>
{''.join(nodes)}
<rect x="790" y="{y0 + 5 * gap - 6}" width="340" height="6" rx="3" fill="#fff" fill-opacity=".08"/>
<rect x="790" y="{y0 + 5 * gap - 6}" width="340" height="6" rx="3" fill="url(#lossLine)" style="transform-origin:790px 0;{tl.grow(times[1], times[5] - times[1])}"/>"""


def terminal() -> None:
    period = SCENE * len(SCENES)
    tl = Timeline(period, "k")
    scenes, tabs = [], []
    all_text = ""
    for i, sc in enumerate(SCENES):
        start, end = i * SCENE, (i + 1) * SCENE
        lines, times = scene_lines(tl, i, start)
        panel = [loss_panel, None, web_panel, claude_panel][i]
        right = vst_panel(tl, times, start) if i == 1 else panel(tl, times)
        scenes.append(
            f'<g style="{tl.window(start, end, 0.4)}">'
            f'<text class="s" x="{W - 56}" y="50" text-anchor="end">{esc(sc["title"])}</text>'
            f"{lines}{right}</g>"
        )
        tx = 128 + i * 118
        tabs.append(
            f'<rect x="{tx}" y="28" width="108" height="30" rx="8" fill="#fff" fill-opacity=".07" style="{tl.window(start, end, 0.3)}"/>'
            f'<rect x="{tx + 14}" y="56" width="80" height="2" rx="1" fill="url(#lossLine)" style="{tl.window(start, end, 0.3)}"/>'
            f'<text class="s" x="{tx + 54}" y="48" text-anchor="middle" fill="{INK}">{esc(sc["tab"])}</text>'
        )
        all_text += sc["title"] + sc["tab"] + "".join(plain(t) for _, t in sc["lines"])
    all_text += "$0123456789loss·fine-tuneclassifierprocess()48kHzstereodrywetGAINDRIVEMIXlocalhost:5173OpenClaude Codeagenticworkflowplaneditestshipreview→,I own the diff" + "".join(s for s in "abcdefghijklmnopqrstuvwxyz")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal: training an ML model, building a Rust VST plugin, a React component and a Claude Code session">
<title>terminal</title>
<style>
{font_face(MONO, 500, all_text)}
{font_face(DISPLAY, 700, "Glass card")}
.t{{font:500 {SIZE}px '{MONO}',monospace;white-space:pre}}
.s{{font:500 13px '{MONO}',monospace;fill:{MUTED};white-space:pre}}
.h{{font:700 26px '{DISPLAY}',sans-serif;fill:{INK}}}
.scroll{{animation:scroll 2.2s linear infinite}}
@keyframes scroll{{to{{transform:translateX(-190px)}}}}
.skel{{fill:#fff;fill-opacity:.07;animation:shim 1.2s ease-in-out infinite alternate}}
@keyframes shim{{to{{fill-opacity:.16}}}}
.orb{{animation:orb 6s ease-in-out infinite alternate}} .orb2{{animation-duration:7s;animation-direction:alternate-reverse}}
@keyframes orb{{to{{transform:translate(40px,14px)}}}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 14s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 1.8s ease-out infinite}}
@keyframes ring{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3.2);opacity:0}}}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.glowbg{{animation:breathe 9s ease-in-out infinite alternate}}
@keyframes breathe{{to{{opacity:.55}}}}
{tl.css()}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="lossLine" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{GREEN}"/></linearGradient>
<linearGradient id="lossArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<linearGradient id="wet" x1="0" x2="1"><stop offset="0" stop-color="{RUST}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="knob" x1="0" x2="1"><stop offset="0" stop-color="{RUST}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
<linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="cardEdge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".7"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="{PINK}" stop-opacity=".7"/></linearGradient>
<linearGradient id="cardSky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16204A"/><stop offset="1" stop-color="#2A1640"/></linearGradient>
<radialGradient id="g1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="g2"><stop offset="0" stop-color="{PINK}" stop-opacity=".3"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="{PINK}" stop-opacity=".55"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<rect x="20" y="16" width="{W - 40}" height="{H - 32}" rx="20" fill="#0C0F1E" fill-opacity=".96" stroke="url(#edge)" stroke-width="1.4"/>
<path d="M20 36 a20 20 0 0 1 20 -20 h{W - 80} a20 20 0 0 1 20 20 v34 h-{W - 40} z" fill="#fff" fill-opacity=".03"/>
<line x1="20" x2="{W - 20}" y1="70" y2="70" stroke="#fff" stroke-opacity=".07"/>
<circle cx="50" cy="43" r="7" fill="#FF5F57"/><circle cx="74" cy="43" r="7" fill="#FEBC2E"/><circle cx="98" cy="43" r="7" fill="#28C840"/>
{''.join(tabs)}
<line x1="736" x2="736" y1="86" y2="{H - 34}" stroke="#fff" stroke-opacity=".07"/>
{''.join(scenes)}
</svg>
"""
    write("terminal.svg", svg)


if __name__ == "__main__":
    terminal()
