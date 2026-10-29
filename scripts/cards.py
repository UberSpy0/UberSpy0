"""Project cards: one SVG per project so each can be its own link in the README."""

import base64
import re
from dataclasses import dataclass, field
from pathlib import Path

from kit import (
    AMBER, CYAN, DISPLAY, GREEN, INK, MONO, MUTED, PINK, REDUCED_MOTION, ROOT,
    VIOLET, esc, font_face, write,
)
from timeline import Timeline

ICONS = ROOT / ".cache" / "icons"
RUST = "#FF5F57"


@dataclass
class Card:
    file: str
    title: str
    event: str
    status: list[tuple[str, str]]  # (kind, label); kind: shipped, medal, building, planning
    body: str
    role: str = ""
    chips: list[str] = field(default_factory=list)
    accent: str = CYAN
    logo: str = ""  # "png:<path>", "icon:<slug>:<color>", "check"
    width: int = 600
    height: int = 360
    link: str = "view repo"
    visual: str = ""  # "sort" draws the algorithm animation on the right


CARDS = [
    Card(
        file="card-mlpath.svg",
        title="ML Path",
        event="Learning platform · flagship · in development",
        status=[("building", "Building")],
        body=(
            "An interactive course that takes a first-year student to an ML internship: "
            "a phased roadmap, lessons with quizzes, real Python right in the browser "
            "(NumPy, pandas, scikit-learn on Pyodide), first-year university math and an "
            "algorithms track where every step is animated next to the code in Python and C++."
        ),
        chips=["Python", "Pyodide", "JavaScript", "C++", "CodeMirror", "MathJax"],
        accent=VIOLET,
        logo="icon:python:#A78BFA",
        width=1200,
        height=380,
        link="",
        visual="sort",
    ),
    Card(
        file="card-saluteagent.svg",
        title="SaluteAgent",
        event="ShortHack × SberTech · Sep 2026",
        status=[("medal", "2nd place"), ("shipped", "Shipped")],
        body=(
            "AI tech-support assistant: drafts an answer from the knowledge base, then "
            "fact-checks every claim against its sources before the user sees it. "
            "A support chat plus an operator console."
        ),
        role=(
            "All of the frontend and UI design; built and fine-tuned the ticket "
            "classifier on YandexGPT-5-Pro and wired it in. Team of 4."
        ),
        chips=["YandexGPT 5 Pro", "Fine-tuning", "FastAPI", "React", "RAG"],
        accent=GREEN,
        logo="check",
    ),
    Card(
        file="card-hotel.svg",
        title="One Step to the Perfect Hotel",
        event="Ostrovok Hackathon · Oct 2026",
        status=[("shipped", "Shipped")],
        body=(
            "Finds what hotel listings never mention: sea view, real quiet, beach "
            "access, mountain sun. Every fact keeps its source and confidence. "
            "Sochi coast and Krasnaya Polyana."
        ),
        role=(
            "Geo-analytics: street-noise model per facade, floor and hour, checked "
            "against guest reviews; beach routes, ski-in/ski-out, room picks. Team of 5."
        ),
        chips=["Python", "GeoPandas", "OpenStreetMap", "SQLite", "MapLibre"],
        accent=CYAN,
        logo="png:assets/src/ostrovok.png",
        link="",  # the hackathon org repo is private
    ),
    Card(
        file="card-vst.svg",
        title="Rust VST Plugin",
        event="Audio DSP · for Ableton & FL Studio",
        status=[("planning", "Planning")],
        body="A music plugin written in Rust: real-time audio processing, shipped as VST3 / CLAP.",
        chips=["Rust", "DSP", "VST3"],
        accent=RUST,
        logo="icon:rust:#FF5F57",
        height=250,
    ),
    Card(
        file="card-mlpractice.svg",
        title="ML Practice",
        event="Exercises & experiments",
        status=[("planning", "Starting")],
        body="A sandbox for the hands-on part of the ML path: models, notebooks and experiments.",
        chips=["Python", "NumPy", "scikit-learn"],
        accent=PINK,
        logo="icon:scikitlearn:#F472B6",
        height=250,
    ),
]

STATUS = {
    "shipped": GREEN,
    "medal": "#D7DEE8",
    "building": AMBER,
    "planning": VIOLET,
}


def wrap(text: str, size: float, width: float, em: float = 0.53) -> list[str]:
    limit = int(width / (size * em))
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > limit and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    lines.append(cur)
    return lines


def logo_svg(spec: str, x: float, y: float, size: float) -> str:
    if spec.startswith("png:"):
        data = base64.b64encode((ROOT / spec[4:]).read_bytes()).decode()
        return (
            f'<clipPath id="lg"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="14"/></clipPath>'
            f'<image href="data:image/png;base64,{data}" x="{x}" y="{y}" width="{size}" height="{size}" clip-path="url(#lg)"/>'
        )
    if spec == "check":
        s = size / 32
        return (
            f'<g transform="translate({x} {y}) scale({s})"><rect width="32" height="32" rx="8" fill="#188730"/>'
            f'<path d="M9 17.5l4.5 4.5L23 12.5" stroke="#fff" stroke-width="3.2" stroke-linecap="round" '
            f'stroke-linejoin="round" fill="none" pathLength="1" class="tick"/></g>'
        )
    _, slug, color = spec.split(":")
    d = re.search(r' d="([^"]+)"', (ICONS / f"{slug}.svg").read_text()).group(1)
    pad = size * 0.22
    s = (size - pad * 2) / 24
    return (
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="14" fill="{color}" fill-opacity=".12" '
        f'stroke="{color}" stroke-opacity=".35"/>'
        f'<g transform="translate({x + pad} {y + pad}) scale({s:.3f})"><path d="{d}" fill="{color}"/></g>'
    )


def pill(kind: str, label: str, x: float, y: float) -> tuple[str, float]:
    """Status pill ending at x (right-aligned); returns svg and its left edge."""
    color = STATUS[kind]
    w = len(label) * 7.8 + 44
    x0 = x - w
    if kind == "medal":
        icon = (
            f'<path d="M{x0 + 14} {y + 4} l3 8 h6 l3 -8 z" fill="{PINK}" opacity=".9"/>'
            f'<circle cx="{x0 + 20}" cy="{y + 17}" r="7" fill="url(#silver)"/>'
            f'<text x="{x0 + 20}" y="{y + 20.5}" text-anchor="middle" class="medal">2</text>'
        )
    elif kind == "shipped":
        icon = (
            f'<circle cx="{x0 + 20}" cy="{y + 14}" r="7" fill="{color}" fill-opacity=".18"/>'
            f'<path d="M{x0 + 16.5} {y + 14} l2.5 2.5 l4.5 -5" stroke="{color}" stroke-width="2" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    elif kind == "building":
        icon = (
            f'<circle class="ping" cx="{x0 + 20}" cy="{y + 14}" r="4.5" fill="none" stroke="{color}"/>'
            f'<circle class="breath" cx="{x0 + 20}" cy="{y + 14}" r="4.5" fill="{color}"/>'
        )
    else:
        icon = f'<circle class="orbit" cx="{x0 + 20}" cy="{y + 14}" r="5" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="4 3"/>'
    return (
        f'<rect x="{x0}" y="{y}" width="{w}" height="28" rx="14" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".4"/>'
        f'{icon}<text x="{x0 + 34}" y="{y + 18.5}" class="pill" fill="{color}">{esc(label.upper())}</text>',
        x0,
    )


def sort_visual(x: float, y: float, w: float, h: float) -> tuple[str, str]:
    """Insertion sort on bars: bars slide into place, compared pair glows."""
    values = [7, 3, 10, 1, 8, 5, 12, 2, 9, 4, 11, 6]
    arr = list(values)
    frames = [(list(arr), -1, -1)]
    for i in range(1, len(arr)):
        j = i
        while j > 0 and arr[j - 1] > arr[j]:
            frames.append((list(arr), j - 1, j))
            arr[j - 1], arr[j] = arr[j], arr[j - 1]
            j -= 1
            frames.append((list(arr), -1, -1))
    frames += [(list(arr), -2, -2)] * 6  # hold sorted, all bars lit
    step = 0.32
    tl = Timeline(len(frames) * step, "s")
    n = len(values)
    gap = 8
    bw = (w - gap * (n - 1)) / n
    rules, bars = [], []
    for v in values:
        xs, fills = [], []
        for arr_f, a, b in frames:
            pos = arr_f.index(v)
            xs.append(x + pos * (bw + gap))
            if a == -2:
                fills.append(GREEN)
            elif pos in (a, b):
                fills.append(PINK)
            else:
                fills.append(VIOLET)
        name = f"bar{v}"
        kf = []
        for k, (bx, fc) in enumerate(zip(xs, fills)):
            kf.append(f"{tl.pct(k * step)}{{transform:translateX({bx:.1f}px);fill:{fc}}}")
        kf.append(f"100%{{transform:translateX({xs[0]:.1f}px);fill:{fills[0]}}}")
        rules.append(f"@keyframes {name}{{{''.join(kf)}}}")
        bh = 24 + v / max(values) * (h - 40)
        bars.append(
            f'<rect x="0" y="{y + h - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" '
            f'style="animation:{name} {tl.period:.2f}s cubic-bezier(.6,0,.3,1) infinite"/>'
        )
    css = "\n".join(rules)
    svg = (
        f'<text x="{x}" y="{y - 18}" class="mono">algo-viz <tspan fill="{MUTED}">· insertion sort · step by step</tspan></text>'
        f'<line x1="{x}" x2="{x + w}" y1="{y + h + 1}" y2="{y + h + 1}" stroke="#fff" stroke-opacity=".12"/>'
        f'<g opacity=".95">{"".join(bars)}</g>'
    )
    return css, svg


def render(c: Card) -> None:
    W, H = c.width, c.height
    pad = 34
    logo_size = 56
    text_w = (W * 0.5 if c.visual else W) - pad * 2
    title_size = 30 if len(c.title) < 20 else 22

    body = wrap(c.body, 16, text_w)
    role = wrap(c.role, 14.5, text_w - 70) if c.role else []

    y = pad + logo_size + 40
    body_svg = "".join(
        f'<text x="{pad}" y="{y + i * 24}" class="body">{esc(line)}</text>' for i, line in enumerate(body)
    )
    y += len(body) * 24 + 10
    role_svg = ""
    if role:
        role_svg = f'<text x="{pad}" y="{y + 4}" class="label" fill="{c.accent}">MY PART</text>' + "".join(
            f'<text x="{pad + 70}" y="{y + 4 + i * 21}" class="role">{esc(line)}</text>' for i, line in enumerate(role)
        )

    chips, cx = [], pad
    for chip in c.chips:
        cw = len(chip) * 7.4 + 26
        chips.append(
            f'<rect x="{cx}" y="{H - pad - 28}" width="{cw}" height="28" rx="9" fill="#fff" fill-opacity=".05" stroke="#fff" stroke-opacity=".1"/>'
            f'<text x="{cx + 13}" y="{H - pad - 9.5}" class="chip">{esc(chip)}</text>'
        )
        cx += cw + 8

    pills, px = [], W - pad
    for kind, label in c.status:
        svg_p, px = pill(kind, label, px, pad + 2)
        pills.append(svg_p)
        px -= 10

    link = ""
    if c.link:
        link = (
            f'<text x="{W - pad}" y="{pad + 52}" text-anchor="end" class="link" fill="{c.accent}">{esc(c.link)} ↗</text>'
        )

    vis_css = vis_svg = ""
    if c.visual == "sort":
        vis_css, vis_svg = sort_visual(W * 0.56, 110, W * 0.44 - pad, H - 110 - pad - 10)

    text = c.title + c.event + c.body + c.role + "".join(c.chips) + c.link + "↗MY PART2" + "".join(
        label.upper() for _, label in c.status
    ) + "algo-viz · insertion sort · step by step"
    rim = f"M22,0 H{W - 22} A22,22 0 0 1 {W},22 V{H - 22} A22,22 0 0 1 {W - 22},{H} H22 A22,22 0 0 1 0,{H - 22} V22 A22,22 0 0 1 22,0 Z"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 {W + 2} {H + 2}" width="{W + 2}" height="{H + 2}" role="img" aria-label="{esc(c.title)} — {esc(c.event)}">
<title>{esc(c.title)}</title>
<style>
{font_face(DISPLAY, 700, c.title + "2")}
{font_face(DISPLAY, 500, c.body + c.role)}
{font_face(MONO, 500, text)}
.title{{font:700 {title_size}px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.5px}}
.event{{font:500 13.5px '{MONO}',monospace;fill:{MUTED}}}
.body{{font:500 16px '{DISPLAY}',sans-serif;fill:#C8CDE0}}
.role{{font:500 14.5px '{DISPLAY}',sans-serif;fill:{MUTED}}}
.label{{font:500 11px '{MONO}',monospace;letter-spacing:1.5px}}
.chip{{font:500 12.5px '{MONO}',monospace;fill:#B9BFD8}}
.pill{{font:500 12px '{MONO}',monospace;letter-spacing:1.2px}}
.mono{{font:500 13px '{MONO}',monospace;fill:{INK}}}
.link{{font:500 13px '{MONO}',monospace}}
.medal{{font:700 9px '{DISPLAY}',sans-serif;fill:#1B2030}}
.comet{{fill:none;stroke:url(#comet);stroke-width:2;stroke-linecap:round;stroke-dasharray:.16 .84;animation:run 7s linear infinite}}
@keyframes run{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
.glow{{animation:glow 8s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes glow{{from{{opacity:.55;transform:scale(1)}}to{{opacity:1;transform:scale(1.15) translate(-20px,10px)}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 1.8s ease-out infinite}}
@keyframes ping{{from{{transform:scale(1);opacity:.9}}to{{transform:scale(3);opacity:0}}}}
.breath{{animation:breath 1.8s ease-in-out infinite}}
@keyframes breath{{50%{{opacity:.45}}}}
.orbit{{transform-box:fill-box;transform-origin:center;animation:spin 6s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.tick{{stroke-dasharray:1;stroke-dashoffset:1;animation:tick .9s ease-out .4s forwards}}
@keyframes tick{{to{{stroke-dashoffset:0}}}}
{vis_css}
{REDUCED_MOTION}
</style>
<defs>
<radialGradient id="aura" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c.accent}" stop-opacity=".22"/><stop offset="1" stop-color="{c.accent}" stop-opacity="0"/></radialGradient>
<radialGradient id="aura2" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{PINK if c.accent != PINK else CYAN}" stop-opacity=".12"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
<linearGradient id="comet" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{c.accent}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="silver" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F7FB"/><stop offset="1" stop-color="#9AA4B5"/></linearGradient>
<clipPath id="frame"><path d="{rim}"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="#0C0F1E"/>
  <ellipse class="glow" cx="{W * 0.12}" cy="{H * 0.1}" rx="{max(W * 0.45, 260)}" ry="{H * 0.75}" fill="url(#aura)"/>
  <ellipse class="glow" cx="{W * 0.95}" cy="{H}" rx="{max(W * 0.35, 220)}" ry="{H * 0.6}" fill="url(#aura2)" style="animation-delay:-4s"/>
</g>
<path d="{rim}" fill="none" stroke="#fff" stroke-opacity=".09"/>
<path d="{rim}" pathLength="1" class="comet"/>
{logo_svg(c.logo, pad, pad, logo_size)}
<text x="{pad + logo_size + 18}" y="{pad + 25}" class="title">{esc(c.title)}</text>
<text x="{pad + logo_size + 18}" y="{pad + 50}" class="event">{esc(c.event)}</text>
{''.join(pills)}
{body_svg}
{role_svg}
{''.join(chips)}
{link}
{vis_svg}
</svg>
"""
    write(c.file, svg)


def cards() -> None:
    for c in CARDS:
        render(c)


if __name__ == "__main__":
    cards()
