"""Section headers, achievements grid, tech stack, contact button."""

import re

from kit import (
    AMBER, CYAN, DIM, DISPLAY, GREEN, INK, LINE, MONO, MUTED, ROOT, esc,
    font_face, frame, wrap, write,
)

ICONS = ROOT / ".cache" / "icons"


def icon_path(slug: str) -> str:
    return re.search(r' d="([^"]+)"', (ICONS / f"{slug}.svg").read_text()).group(1)


SECTIONS = [
    ("about", "About"),
    ("projects", "Projects"),
    ("achievements", "Achievements"),
    ("stack", "Stack"),
    ("activity", "Activity"),
    ("contact", "Contact"),
]


def header(n: int, key: str, title: str) -> None:
    W, H = 1200, 56
    x_line = 44 + len(title) * 12.8 + 20
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
{font_face(DISPLAY, 700, title)}
{font_face(MONO, 500, "0123456789")}
.t{{font:700 22px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.2px}}
.n{{font:500 13px '{MONO}',monospace;fill:{DIM}}}
</style>
<text class="n" x="2" y="34">{n:02d}</text>
<text class="t" x="40" y="35">{esc(title)}</text>
<rect x="{x_line:.0f}" y="28" width="{W - x_line:.0f}" height="1" fill="{LINE}"/>
</svg>
"""
    write(f"h-{key}.svg", svg)


# Newest first. New results go at the top; the last tile says more are coming.
ACHIEVEMENTS = [
    ("2026 · Hackathon", "ShortHack × SberTech", "2nd place", AMBER,
     "SaluteAgent, an AI support assistant. My part: frontend, design and the YandexGPT-5-Pro classifier."),
    ("2026 · Hackathon", "Ostrovok Hackathon", "Shipped", GREEN,
     "Hotel facts search for the Sochi coast and Krasnaya Polyana. My part: noise and geo models."),
    ("2026 · Olympiad", "ICPC", "1/8 stage", CYAN,
     "International Collegiate Programming Contest: algorithmic problems against the clock."),
    ("2024 · Robotics", "RoboFinist", "3rd place", AMBER,
     "Habitat: Exploring the Red Planet. Robot assembly and Arduino / C++ modules."),
    ("2023 · Robotics", "RoboFinist", "3rd place ×2", AMBER,
     "Underwater robotics and MGBot × R:ED Habitat. Robot assembly and Arduino / C++ modules."),
]
NEXT = ("next", "More on the way", "New hackathons and olympiads land here.")


def achievements() -> None:
    cols, gap = 3, 20
    tw, th = (1200 - gap * (cols - 1)) / cols, 170
    tiles = ACHIEVEMENTS + [NEXT]
    rows = -(-len(tiles) // cols)
    W, H = 1200, rows * th + (rows - 1) * gap + 34
    out, mono, body = [], "", ""
    for i, tile in enumerate(tiles):
        x, y = (i % cols) * (tw + gap), (i // cols) * (th + gap)
        if tile is NEXT:
            meta, name, desc = tile
            result, color = "", DIM
            name_style = f' style="fill:{MUTED}"'
        else:
            name_style = ""
            meta, name, result, color, desc = tile
        lines = wrap(desc, 14, tw - 56, em=0.5)
        if len(lines) > 3:
            raise SystemExit(f"achievement {name!r}: description wraps to {len(lines)} lines")
        mono += meta + result
        body += desc
        out.append(
            f'<g transform="translate({x:.1f} {y})">'
            f'<rect x=".5" y=".5" width="{tw - 1:.1f}" height="{th - 1}" rx="14" fill="none" stroke="{LINE}"'
            + (' stroke-dasharray="5 5"' if tile is NEXT else "") + "/>"
            f'<text class="m" x="28" y="42">{esc(meta)}</text>'
            + (
                f'<circle cx="{tw - 28 - len(result) * 7.8 - 12:.1f}" cy="37.5" r="4" fill="{color}"/>'
                f'<text class="m" x="{tw - 28:.1f}" y="42" text-anchor="end" style="fill:{color}">{esc(result)}</text>'
                if result else ""
            )
            + f'<text class="t" x="28" y="80"{name_style}>{esc(name)}</text>'
            + "".join(f'<text class="b" x="28" y="{108 + k * 20}">{esc(l)}</text>' for k, l in enumerate(lines))
            + "</g>"
        )
    note = "RoboFinist is on Russia's official list of school olympiads."
    names = "".join(t[1] for t in tiles)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Achievements">
<title>Achievements</title>
<style>
{font_face(DISPLAY, 700, names)}
{font_face(DISPLAY, 500, body)}
{font_face(MONO, 500, mono + note)}
.t{{font:700 20px '{DISPLAY}',sans-serif;fill:{INK}}}
.b{{font:500 14px '{DISPLAY}',sans-serif;fill:{MUTED}}}
.m{{font:500 13px '{MONO}',monospace;fill:{DIM}}}
</style>
{''.join(out)}
<text class="m" x="2" y="{H - 6}">{esc(note)}</text>
</svg>
"""
    write("achievements.svg", svg)


STACK = [
    ("ML", [("python", "Python"), ("pytorch", "PyTorch"), ("scikitlearn", "scikit-learn"),
            ("numpy", "NumPy"), ("pandas", "pandas"), ("jupyter", "Jupyter")]),
    ("Systems", [("rust", "Rust"), ("cplusplus", "C++"), ("arduino", "Arduino")]),
    ("Web", [("typescript", "TypeScript"), ("javascript", "JavaScript"), ("react", "React"),
             ("vite", "Vite"), ("tailwindcss", "Tailwind"), ("html5", "HTML"), ("css", "CSS"),
             ("figma", "Figma")]),
    ("Backend", [("fastapi", "FastAPI"), ("sqlite", "SQLite"), ("postgresql", "PostgreSQL"),
                 ("docker", "Docker")]),
    ("Tools", [("git", "Git"), ("linux", "Linux"), ("claude", "Claude Code")]),
]


def stack() -> None:
    W, row = 1200, 52
    H = row * len(STACK) + 16
    out, names = [], ""
    for r, (group, items) in enumerate(STACK):
        y = 8 + r * row
        if r:
            out.append(f'<rect x="28" y="{y}" width="{W - 56}" height="1" fill="{LINE}"/>')
        out.append(f'<text class="g" x="32" y="{y + 31}">{group.upper()}</text>')
        x = 170
        for slug, name in items:
            names += name
            out.append(
                f'<g transform="translate({x} {y + 17}) scale(.75)"><path d="{icon_path(slug)}" fill="{MUTED}"/></g>'
                f'<text class="i" x="{x + 26}" y="{y + 31}">{esc(name)}</text>'
            )
            x += 26 + len(name) * 8.4 + 30
        if x > W - 20:
            raise SystemExit(f"stack row {group!r} is too wide ({x:.0f}px)")
    groups = "".join(g.upper() for g, _ in STACK)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Stack">
<title>Stack</title>
<style>
{font_face(DISPLAY, 500, names)}
{font_face(MONO, 500, groups)}
.i{{font:500 15px '{DISPLAY}',sans-serif;fill:{INK}}}
.g{{font:500 11px '{MONO}',monospace;fill:{DIM};letter-spacing:1.5px}}
</style>
{frame(W, H)}
{''.join(out)}
</svg>
"""
    write("stack.svg", svg)


def contact_button() -> None:
    W, H = 360, 64
    a, b = "Telegram", "@fab_butt"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Message me on Telegram: @fab_butt">
<title>Telegram @fab_butt</title>
<style>
{font_face(DISPLAY, 700, a)}
{font_face(MONO, 500, b + "↗")}
.a{{font:700 18px '{DISPLAY}',sans-serif;fill:{INK}}}
.b{{font:500 14px '{MONO}',monospace;fill:{MUTED}}}
</style>
{frame(W, H, rx=32)}
<g transform="translate(24 20)"><path d="{icon_path("telegram")}" fill="#26A5E4"/></g>
<text class="a" x="60" y="38">{a}</text>
<text class="b" x="146" y="38">{b}</text>
<text class="b" x="{W - 28}" y="38" text-anchor="end">↗</text>
</svg>
"""
    write("telegram.svg", svg)


def sections() -> None:
    for n, (key, title) in enumerate(SECTIONS, 1):
        header(n, key, title)
    achievements()
    stack()
    contact_button()


if __name__ == "__main__":
    sections()
