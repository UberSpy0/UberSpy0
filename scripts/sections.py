"""Section headers, achievements grid, tech stack, contact button."""

from __future__ import annotations

from kit import (
    CONFIG, DECOR, DIM, DISPLAY, FORMATS, INK, LINE, MONO, MUTED, border_attrs,
    color, esc, font_face, frame, icon_path, radius, wrap, write,
)


def visible_sections() -> list[dict]:
    return [s for s in CONFIG["sections"] if s.get("show", True)]


def header(n: int, key: str, title: str) -> None:
    W, H = 1200, 56
    numbered = DECOR.get("section_numbers", True)
    tx = 40 if numbered else 2
    x_line = tx + len(title) * 12.8 + 20
    number = f'<text class="n" x="2" y="34">{n:02d}</text>' if numbered else ""
    rule = (
        f'<rect x="{x_line:.0f}" y="28" width="{W - x_line:.0f}" height="1" fill="{LINE}"/>'
        if DECOR.get("section_rule", True) else ""
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
{font_face(DISPLAY, 700, title)}
{font_face(MONO, 500, "0123456789")}
.t{{font:700 22px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.2px}}
.n{{font:500 13px '{MONO}',monospace;fill:{DIM}}}
</style>
{number}
<text class="t" x="{tx}" y="35">{esc(title)}</text>
{rule}
</svg>
"""
    write(f"h-{key}.svg", svg)


def achievements() -> None:
    """Grid of results, newest first; the last, dashed tile says more are coming."""
    cols, gap = int(FORMATS.get("achievements_columns", 3)), 20
    tw, th = (1200 - gap * (cols - 1)) / cols, 170
    nxt = CONFIG["achievements_next"]
    tiles = [dict(a) for a in CONFIG["achievements"]] + [{"meta": "next", "name": nxt["name"], "desc": nxt["desc"], "next": True}]
    rows = -(-len(tiles) // cols)
    note = CONFIG.get("achievements_note", "")
    W, H = 1200, rows * th + (rows - 1) * gap + (34 if note else 4)
    dots = DECOR.get("status_dots", True)
    out, mono, body = [], "", ""
    for i, t in enumerate(tiles):
        x, y = (i % cols) * (tw + gap), (i // cols) * (th + gap)
        result = t.get("result", "")
        c = color(t.get("color", "dim"))
        lines = wrap(t["desc"], 14, tw - 56, em=0.5)
        if len(lines) > 3:
            raise SystemExit(f"achievement {t['name']!r}: description wraps to {len(lines)} lines")
        mono += t["meta"] + result
        body += t["desc"]
        name_style = f' style="fill:{MUTED}"' if t.get("next") else ""
        badge = ""
        if result:
            dot = f'<circle cx="{tw - 28 - len(result) * 7.8 - 12:.1f}" cy="37.5" r="4" fill="{c}"/>' if dots else ""
            badge = dot + f'<text class="m" x="{tw - 28:.1f}" y="42" text-anchor="end" style="fill:{c}">{esc(result)}</text>'
        out.append(
            f'<g transform="translate({x:.1f} {y})">'
            f'<rect x=".5" y=".5" width="{tw - 1:.1f}" height="{th - 1}" rx="{radius()}" fill="none" {border_attrs(bool(t.get("next")))}/>'
            f'<text class="m" x="28" y="42">{esc(t["meta"])}</text>{badge}'
            f'<text class="t" x="28" y="80"{name_style}>{esc(t["name"])}</text>'
            + "".join(f'<text class="b" x="28" y="{108 + k * 20}">{esc(l)}</text>' for k, l in enumerate(lines))
            + "</g>"
        )
    names = "".join(t["name"] for t in tiles)
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
{f'<text class="m" x="2" y="{H - 6}">{esc(note)}</text>' if note else ''}
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
    a, b = "Telegram", "@" + CONFIG["contact"]["telegram"]
    arrow = f'<text class="b" x="{W - 28}" y="38" text-anchor="end">↗</text>' if DECOR.get("card_arrows", True) else ""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Message me on Telegram: {esc(b)}">
<title>Telegram {esc(b)}</title>
<style>
{font_face(DISPLAY, 700, a)}
{font_face(MONO, 500, b + "↗")}
.a{{font:700 18px '{DISPLAY}',sans-serif;fill:{INK}}}
.b{{font:500 14px '{MONO}',monospace;fill:{MUTED}}}
</style>
{frame(W, H, rx=min(32, radius() * 2.3))}
<g transform="translate(24 20)"><path d="{icon_path("telegram")}" fill="{color("telegram")}"/></g>
<text class="a" x="60" y="38">{a}</text>
<text class="b" x="146" y="38">{esc(b)}</text>
{arrow}
</svg>
"""
    write("telegram.svg", svg)


def sections() -> None:
    for n, s in enumerate(visible_sections(), 1):
        header(n, s["id"], s["title"])
    achievements()
    stack()
    contact_button()


if __name__ == "__main__":
    sections()
