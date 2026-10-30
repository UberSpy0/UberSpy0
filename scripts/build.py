"""Builds the static SVGs in assets/. Run: python3 scripts/build.py

Live cards (stats, now building) come from the GitHub Action.
"""

from kit import (
    BG, CYAN, DIM, DISPLAY, FRONT, GREEN, INK, LINE, MONO, MUTED, ORANGE, PINK,
    REDUCED_MOTION, RUST, VIOLET, esc, font_face, write,
)

W, H = 1200, 240


def role_line(roles: list[str], accent: dict[str, str]) -> str:
    """Roles on one line, each one's keyword in its accent color."""
    out = []
    for role in roles:
        word = next((w for w in accent if role.startswith(w)), "")
        rest = esc(role[len(word):])
        out.append(f'<tspan fill="{accent[word]}">{esc(word)}</tspan>{rest}' if word else esc(role))
    return f'<tspan fill="{DIM}">  ·  </tspan>'.join(out)


def hero() -> None:
    name = "Artem Krupa"
    path, nick = "~/uberspy0", "TomaToma0"
    roles = ["ML Engineer", "Rust Developer", "Frontend Designer", "Marketing Analyst", "Competitive Programmer"]
    accent = {"ML": GREEN, "Rust": RUST, "Frontend": FRONT, "Competitive": ORANGE}
    place = "NUST MISIS  ·  Moscow  ·  from Krasnodar"
    mono_text = path + nick + "".join(roles) + place + "·"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{name} — {', '.join(roles)}">
<title>{name}</title>
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
<clipPath id="f"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#f)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect class="hl" y="{H - 2}" width="{W * 2}" height="2" fill="url(#hl)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{LINE}"/>
<text class="m" x="56" y="60" style="fill:{DIM}">{path}  <tspan fill="{MUTED}">{nick}</tspan></text>
<text class="n" x="52" y="128">{name}</text>
<text class="r" x="56" y="168">{role_line(roles, accent)}</text>
<text class="m" x="56" y="202">{esc(place)}</text>
</svg>
"""
    write("hero.svg", svg)


if __name__ == "__main__":
    from cards import cards
    from sections import sections

    hero()
    cards()
    sections()
