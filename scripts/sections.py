"""Section headers, achievements timeline, tech stack, contact button, footer."""

import random
import re

from kit import (
    AMBER, AQUA, BG, CYAN, DISPLAY, GREEN, INK, MONO, MUTED, PINK, REDUCED_MOTION,
    ROOT, VIOLET, esc, font_face, write,
)
from timeline import Timeline

ICONS = ROOT / ".cache" / "icons"
BRONZE = "#E3A46F"
SILVER = "#D7DEE8"


def icon_path(slug: str) -> str:
    return re.search(r' d="([^"]+)"', (ICONS / f"{slug}.svg").read_text()).group(1)


# 24×24 line icons for section headers (stroke paths).
GLYPHS = {
    "about": "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z M4 21c1.2-4 4.3-6 8-6s6.8 2 8 6",
    "projects": "M12 3 3 7.5l9 4.5 9-4.5L12 3Z M3 12l9 4.5 9-4.5 M3 16.5 12 21l9-4.5",
    "lab": "M9 3h6 M10 3v6l-5.5 9.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3 M7.5 15h9",
    "achievements": "M8 21h8 M12 17v4 M7 4h10v5a5 5 0 0 1-10 0V4Z M7 6H4a3 3 0 0 0 3 4 M17 6h3a3 3 0 0 1-3 4",
    "stack": "M7 7h10v10H7z M10 3v4 M14 3v4 M10 17v4 M14 17v4 M3 10h4 M3 14h4 M17 10h4 M17 14h4",
    "github": "M4 20V10 M10 20V4 M16 20v-7 M22 20H2",
    "now": "M3 12h4l3-8 4 16 3-8h4",
    "contact": "M22 2 11 13 M22 2l-7 20-4-9-9-4 20-7Z",
}


def header(key: str, title: str) -> None:
    W, H = 1200, 72
    tw = len(title) * 17.5
    x_line = 78 + tw + 24
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
{font_face(DISPLAY, 700, title)}
.t{{font:700 32px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.5px}}
.ic{{fill:none;stroke:url(#ink);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.6s ease-out .2s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.line{{animation:grow 1.4s cubic-bezier(.2,.8,.2,1) .4s both;transform-origin:{x_line}px 0}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.spark{{animation:run 5s cubic-bezier(.5,0,.5,1) 1.8s infinite;opacity:0}}
@keyframes run{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}80%{{opacity:1}}100%{{transform:translateX({W - 20 - x_line}px);opacity:0}}}}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="ink" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".7"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<radialGradient id="sp"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
</defs>
<rect x="8" y="14" width="46" height="46" rx="13" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".1"/>
<g transform="translate(17 23) scale(1.17)"><path class="ic" pathLength="1" d="{GLYPHS[key]}"/></g>
<text class="t" x="76" y="49">{esc(title)}</text>
<rect class="line" x="{x_line}" y="37" width="{W - 20 - x_line}" height="1.5" fill="url(#rule)"/>
<circle class="spark" cx="{x_line}" cy="37.7" r="6" fill="url(#sp)"/>
</svg>
"""
    write(f"h-{key}.svg", svg)


ACHIEVEMENTS = [
    ("2023", "RoboFinist", "3rd place ×2", BRONZE, ["Underwater robotics", "MGBot × R:ED Habitat"]),
    ("2024", "RoboFinist", "3rd place", BRONZE, ["Habitat: Exploring", "the Red Planet"]),
    ("Sep 2026", "ShortHack × SberTech", "2nd place", SILVER, ["SaluteAgent ·", "AI support agent"]),
    ("Oct 2026", "Ostrovok Hackathon", "Prototype shipped", CYAN, ["Hotel facts search ·", "noise & geo models"]),
    ("2026", "ICPC", "1/8 stage", AMBER, ["Competitive", "programming"]),
]


def achievements() -> None:
    W, H = 1200, 340
    period = 16.0
    tl = Timeline(period, "a")
    x0, x1, ly = 70, 1130, 118
    step = (x1 - x0 - 140) / (len(ACHIEVEMENTS) - 1)
    items = []
    for i, (when, name, result, color, detail) in enumerate(ACHIEVEMENTS):
        x = x0 + 70 + i * step
        at = 0.9 + i * 0.55
        size = 19 if len(name) > 14 else 22
        medal = ""
        if color in (BRONZE, SILVER):
            medal = (
                f'<path d="M{x - 6} {ly - 12} l3 6 h6 l3 -6 z" fill="{PINK}" opacity=".9"/>'
                f'<circle cx="{x}" cy="{ly}" r="9" fill="url(#{"bronze" if color == BRONZE else "silver"})"/>'
            )
        else:
            medal = f'<circle cx="{x}" cy="{ly}" r="7" fill="{color}"/>'
        rw = len(result) * 7.6 + 24
        items.append(
            f'<g style="{tl.window(at, period - 0.6, 0.4)}">'
            f'<text x="{x}" y="{ly - 34}" text-anchor="middle" class="when" fill="{color}">{esc(when)}</text>'
            f'<circle cx="{x}" cy="{ly}" r="18" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".35"/>'
            f"{medal}"
            f'<text x="{x}" y="{ly + 58}" text-anchor="middle" class="name" style="font-size:{size}px">{esc(name)}</text>'
            f'<rect x="{x - rw / 2}" y="{ly + 74}" width="{rw}" height="26" rx="13" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".45"/>'
            f'<text x="{x}" y="{ly + 91.5}" text-anchor="middle" class="res" fill="{color}">{esc(result.upper())}</text>'
            + "".join(
                f'<text x="{x}" y="{ly + 128 + k * 19}" text-anchor="middle" class="det">{esc(d)}</text>'
                for k, d in enumerate(detail)
            )
            + "</g>"
            f'<circle cx="{x}" cy="{ly}" r="10" fill="none" stroke="{color}" stroke-width="2" '
            f'style="transform-box:fill-box;transform-origin:center;{tl.pulse(at, 1.1)}"/>'
        )
    text = "".join(a[0] + a[2].upper() + "".join(a[4]) for a in ACHIEVEMENTS) + "×robot assembly · Arduino / C++ modules · RoboFinist is on Russia's official olympiad list"
    names = "".join(a[1] for a in ACHIEVEMENTS)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Achievements: RoboFinist 2023 3rd place twice, RoboFinist 2024 3rd place, ShortHack x SberTech 2nd place, Ostrovok Hackathon, ICPC 1/8 stage">
<title>achievements</title>
<style>
{font_face(DISPLAY, 700, names)}
{font_face(MONO, 500, text)}
.when{{font:500 14px '{MONO}',monospace;letter-spacing:1px}}
.name{{font:700 22px '{DISPLAY}',sans-serif;fill:{INK}}}
.res{{font:500 11.5px '{MONO}',monospace;letter-spacing:1.2px}}
.det{{font:500 12.5px '{MONO}',monospace;fill:{MUTED}}}
.note{{font:500 12px '{MONO}',monospace;fill:#5D6488}}
{tl.css()}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="track" x1="0" x2="1"><stop offset="0" stop-color="{BRONZE}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
<linearGradient id="bronze" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F6C9A0"/><stop offset="1" stop-color="#A8663A"/></linearGradient>
<linearGradient id="silver" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F7FB"/><stop offset="1" stop-color="#9AA4B5"/></linearGradient>
<filter id="soft" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="#0C0F1E" stroke="#fff" stroke-opacity=".08"/>
<line x1="{x0}" x2="{x1}" y1="{ly}" y2="{ly}" stroke="#fff" stroke-opacity=".08" stroke-width="2"/>
<path d="M{x0},{ly} H{x1}" pathLength="1" stroke="url(#track)" stroke-width="6" stroke-opacity=".5" filter="url(#soft)" style="stroke-dasharray:1;{tl.draw(0.2, 3.2)}"/>
<path d="M{x0},{ly} H{x1}" pathLength="1" stroke="url(#track)" stroke-width="2" style="stroke-dasharray:1;{tl.draw(0.2, 3.2)}"/>
{''.join(items)}
<text x="{W / 2}" y="{H - 22}" text-anchor="middle" class="note">robot assembly · Arduino / C++ modules · RoboFinist is on Russia's official olympiad list</text>
</svg>
"""
    write("achievements.svg", svg)


STACK = [
    ("python", "Python"), ("pytorch", "PyTorch"), ("scikitlearn", "sklearn"), ("numpy", "NumPy"),
    ("pandas", "pandas"), ("jupyter", "Jupyter"), ("rust", "Rust"), ("cplusplus", "C++"),
    ("arduino", "Arduino"), ("typescript", "TS"), ("javascript", "JS"), ("react", "React"),
    ("vite", "Vite"), ("tailwindcss", "Tailwind"), ("html5", "HTML"), ("css", "CSS"),
    ("figma", "Figma"), ("fastapi", "FastAPI"), ("sqlite", "SQLite"), ("postgresql", "Postgres"),
    ("docker", "Docker"), ("git", "Git"), ("linux", "Linux"), ("claude", "Claude"),
]

TOKENS = ["{", "}", "=>", "fn", "0x", "λ", "∑", "//", "</>", "01", "::", "&&", "[]", "#", "%", "=", ";", "*", "Δ", "≠", "→", "def", "let", "<<"]


def stack() -> None:
    cols, rows = 12, 2
    cell_w, cell_h = 92, 118
    W = 1200
    H = rows * cell_h + 70
    ox = (W - cols * cell_w) / 2
    oy = 34
    period = 18.0
    tl = Timeline(period, "m")
    rnd = random.Random(5)
    palette = [CYAN, VIOLET, PINK, AQUA]
    cells, glyph_chars = [], ""
    for i, (slug, label) in enumerate(STACK):
        r, c = divmod(i, cols)
        cx = ox + c * cell_w + cell_w / 2
        cy = oy + r * cell_h + 40
        at = 1.4 + (c + r * 2) * 0.13 + rnd.uniform(0, 0.15)
        color = palette[(c + r) % len(palette)]
        noise = []
        for _ in range(7):
            tok = rnd.choice(TOKENS)
            glyph_chars += tok
            nx, ny = cx + rnd.uniform(-30, 30), cy + rnd.uniform(-26, 30)
            fl = rnd.uniform(0.08, 0.22)
            noise.append(
                f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" class="nz" fill="{rnd.choice(palette)}" '
                f'style="{tl.window(at - 1.2 + rnd.uniform(0, 0.4), at + 0.15, 0.15)}">'
                f'<tspan class="fl" style="animation-duration:{fl:.2f}s;animation-delay:-{rnd.uniform(0, .3):.2f}s">{esc(tok)}</tspan></text>'
            )
        s = 40 / 24
        d = icon_path(slug)
        cells.append(
            "".join(noise)
            + f'<g style="{tl.window(at, period - 0.8 - (cols - c) * 0.03, 0.35)}">'
            f'<g transform="translate({cx - 20:.1f} {cy - 20:.1f}) scale({s:.3f})">'
            f'<path d="{d}" fill="{color}" opacity=".55" filter="url(#bloom)" class="flash" style="animation-delay:{at:.2f}s"/>'
            f'<path d="{d}" fill="{INK}"/></g>'
            f'<text x="{cx:.1f}" y="{cy + 48:.1f}" text-anchor="middle" class="lb">{esc(label)}</text></g>'
        )
    labels = "".join(lb for _, lb in STACK)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack: {', '.join(lb for _, lb in STACK)}">
<title>stack</title>
<style>
{font_face(MONO, 500, labels + glyph_chars)}
.nz{{font:500 15px '{MONO}',monospace}}
.fl{{animation:fl .15s steps(2) infinite}}
@keyframes fl{{50%{{opacity:.15}}}}
.lb{{font:500 12px '{MONO}',monospace;fill:{MUTED}}}
.flash{{animation:flash 2.2s ease-out both}}
@keyframes flash{{0%{{opacity:1}}100%{{opacity:.28}}}}
.scan{{animation:scan {period}s linear infinite}}
@keyframes scan{{0%,30%{{transform:translateX(-260px);opacity:0}}32%{{opacity:1}}48%{{transform:translateX({W + 60}px);opacity:1}}49%,100%{{opacity:0}}}}
{tl.css()}
{REDUCED_MOTION}
</style>
<defs>
<filter id="bloom" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".16"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
<clipPath id="fr"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="#0C0F1E" stroke="#fff" stroke-opacity=".08"/>
<g clip-path="url(#fr)"><rect class="scan" x="0" y="0" width="220" height="{H}" fill="url(#beam)"/></g>
{''.join(cells)}
</svg>
"""
    write("stack.svg", svg)


def contact_button() -> None:
    W, H = 460, 76
    d = icon_path("telegram")
    text = "Message me on Telegram@fab_butt"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Message me on Telegram: @fab_butt">
<title>Telegram @fab_butt</title>
<style>
{font_face(DISPLAY, 700, text)}
{font_face(MONO, 500, text)}
.a{{font:700 20px '{DISPLAY}',sans-serif;fill:{INK}}}
.b{{font:500 13px '{MONO}',monospace;fill:{CYAN}}}
.sheen{{animation:sheen 4.5s ease-in-out infinite}}
@keyframes sheen{{0%,55%{{transform:translateX(-160px)}}100%{{transform:translateX({W + 40}px)}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2.6s ease-out infinite}}
@keyframes ping{{from{{transform:scale(1);opacity:.7}}to{{transform:scale(1.5);opacity:0}}}}
.edge{{stroke-dasharray:.22 .78;animation:run 5s linear infinite}}
@keyframes run{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="fill" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".16"/><stop offset="1" stop-color="{PINK}" stop-opacity=".16"/></linearGradient>
<linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" x2="{W}"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="pill"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="{(H - 4) / 2}"/></clipPath>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="{(H - 4) / 2}" fill="#0C0F1E"/>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="{(H - 4) / 2}" fill="url(#fill)" stroke="#fff" stroke-opacity=".12"/>
<rect class="edge" x="2" y="2" width="{W - 4}" height="{H - 4}" rx="{(H - 4) / 2}" fill="none" stroke="url(#edge)" stroke-width="2" pathLength="1"/>
<g clip-path="url(#pill)"><rect class="sheen" x="0" y="0" width="120" height="{H}" fill="url(#sh)"/></g>
<circle cx="{H / 2 + 2}" cy="{H / 2}" r="17" fill="#fff"/>
<g transform="translate({H / 2 - 22} {H / 2 - 24}) scale(2)"><path d="{d}" fill="#26A5E4"/></g>
<circle cx="{H / 2 + 2}" cy="{H / 2}" r="24" fill="none" stroke="#26A5E4" class="ping"/>
<text class="a" x="{H + 12}" y="{H / 2 - 2}">Message me on Telegram</text>
<text class="b" x="{H + 12}" y="{H / 2 + 19}">@fab_butt</text>
</svg>
"""
    write("telegram.svg", svg)


def footer() -> None:
    W, H = 1200, 150

    def wave(amp: float, length: float, base: float) -> str:
        pts = [f"M0,{H}", f"L0,{base}"]
        x = 0.0
        while x < W * 2 + length:
            pts.append(f"Q{x + length / 4:.0f},{base - amp} {x + length / 2:.0f},{base}")
            pts.append(f"Q{x + length * 3 / 4:.0f},{base + amp} {x + length:.0f},{base}")
            x += length
        pts.append(f"L{x:.0f},{H} Z")
        return " ".join(pts)

    layers = [
        (CYAN, 0.18, 18, 400, 70, 16),
        (VIOLET, 0.22, 14, 300, 88, 11),
        (PINK, 0.26, 10, 240, 104, 8),
    ]
    paths = "".join(
        f'<path d="{wave(a, ln, b)}" fill="{col}" fill-opacity="{op}" style="animation:w{i} {dur}s linear infinite"/>'
        for i, (col, op, a, ln, b, dur) in enumerate(layers)
    )
    kf = "".join(
        f"@keyframes w{i}{{to{{transform:translateX(-{ln}px)}}}}" for i, (_, _, _, ln, _, _) in enumerate(layers)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" preserveAspectRatio="none" role="img" aria-label="footer wave">
<title>footer</title>
<style>{kf}{REDUCED_MOTION}</style>
<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff"/><stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>
<g mask="url(#m)">{paths}</g>
</svg>
"""
    write("footer.svg", svg)


def sections() -> None:
    for key, title in [
        ("about", "About"),
        ("projects", "Projects"),
        ("lab", "In the lab"),
        ("achievements", "Achievements"),
        ("stack", "Stack"),
        ("github", "GitHub"),
        ("now", "Now building"),
        ("contact", "Contact"),
    ]:
        header(key, title)
    achievements()
    stack()
    contact_button()
    footer()


if __name__ == "__main__":
    sections()
