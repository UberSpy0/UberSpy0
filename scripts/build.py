"""Builds every SVG in assets/ and README.md from profile.json.

    python3 scripts/build.py            # from the saved data/github.json (no token needed)
    GH_TOKEN=... python3 scripts/build.py --fetch   # refresh GitHub data first (the Action)
"""

from __future__ import annotations

import os
import sys

from kit import (
    ASSETS, BG, CONFIG, CYAN, DECOR, DIM, DISPLAY, EFFECTS, INK, MONO, MUTED,
    PINK, REDUCED_MOTION, VIOLET, border_attrs, color, esc, font_face, radius,
    write,
)

W, H = 1200, 240


def role_line(roles: list[dict]) -> str:
    """Roles on one line, each one's keyword in its accent color."""
    out = []
    for role in roles:
        text, word = role["text"], role.get("keyword", "")
        if word and text.startswith(word):
            out.append(f'<tspan fill="{color(role["color"])}">{esc(word)}</tspan>{esc(text[len(word):])}')
        else:
            out.append(esc(text))
    return f'<tspan fill="{DIM}">  ·  </tspan>'.join(out)


def hero() -> None:
    name, nick, path, place = CONFIG["name"], CONFIG["nick"], CONFIG["path"], CONFIG["place"]
    roles = CONFIG["roles"]
    mono_text = path + nick + "".join(r["text"] for r in roles) + place + "·"
    rx = radius() + 2
    line = (
        f'<rect class="hl" y="{H - 2}" width="{W * 2}" height="2" fill="url(#hl)"/>'
        if EFFECTS.get("hero_line", True) else ""
    )
    path_line = (
        f'<text class="m" x="56" y="60" style="fill:{DIM}">{esc(path)}  <tspan fill="{MUTED}">{esc(nick)}</tspan></text>'
        if DECOR.get("hero_path", True) else ""
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(name)} — {esc(', '.join(r['text'] for r in roles))}">
<title>{esc(name)}</title>
<style>
{font_face(DISPLAY, 700, name)}
{font_face(MONO, 500, mono_text)}
.n{{font:700 60px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-1.5px}}
.m{{font:500 15px '{MONO}',monospace;fill:{MUTED};white-space:pre}}
.r{{font:500 17px '{MONO}',monospace;fill:{INK};white-space:pre}}
.hl{{animation:slide 12s linear infinite}}
@keyframes slide{{to{{transform:translateX(-{W}px)}}}}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="hl" gradientUnits="userSpaceOnUse" x1="0" x2="{W * 2}" y1="0" y2="0">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".25" stop-color="{VIOLET}"/><stop offset=".5" stop-color="{PINK}"/>
  <stop offset=".75" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/>
</linearGradient>
<clipPath id="f"><rect width="{W}" height="{H}" rx="{rx}"/></clipPath>
</defs>
<g clip-path="url(#f)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  {line}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{rx - .5}" fill="none" {border_attrs()}/>
{path_line}
<text class="n" x="52" y="128">{esc(name)}</text>
<text class="r" x="56" y="168">{role_line(roles)}</text>
<text class="m" x="56" y="202">{esc(place)}</text>
</svg>
"""
    write("hero.svg", svg)


def main() -> None:
    import live
    from projects import projects
    from readme import readme
    from sections import sections

    if "--fetch" in sys.argv:
        data = live.fetch(CONFIG["login"], os.environ["GH_TOKEN"])
        live.save(data)
    else:
        data = live.load()

    for old in ASSETS.glob("project-*.svg"):
        old.unlink()
    hero()
    sections()
    write("github.svg", live.stats_card(data))
    write("now.svg", live.now_card(data))
    repos = projects(data)
    readme(repos)


if __name__ == "__main__":
    main()
