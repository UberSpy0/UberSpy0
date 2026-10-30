"""Builds the static animated SVGs in assets/. Run: python3 scripts/build.py

Live cards (stats, now building, tetris, snake) come from the GitHub Action.
"""

from kit import (
    AQUA, BG, CYAN, DIM, DISPLAY, GREEN, INK, MONO, MUTED, PINK, REDUCED_MOTION,
    VIOLET, esc, font_face, stars, write,
)

W, H = 1200, 400
CW = 0.6  # JetBrains Mono advance width, in em


def role_colors(role: str, accent: dict[str, str]) -> list[str | None]:
    """Per-character fill: the role's keyword in its accent color, the rest default."""
    for word, color in accent.items():
        if role.startswith(word):
            return [color] * len(word) + [None] * (len(role) - len(word))
    return [None] * len(role)


def typing_roles(roles: list[str], accent: dict[str, str], y: int, size: int, period: float) -> tuple[str, str]:
    """Roles typed and backspaced one after another, centered; returns (css, svg).

    Every character is its own <text> with an opacity window. Safari doesn't
    repaint CSS animations inside a <clipPath>, so a clip-based reveal left all
    roles visible on top of each other there.
    """
    cw = CW * size
    share = 100 / len(roles)
    css, svg = [], []
    for i, role in enumerate(roles):
        n = len(role)
        full = n * cw
        x0 = W / 2 - (full + cw * 2.2) / 2 + cw * 2.2
        a = i * share
        typed, hold, gone = a + share * 0.25, a + share * 0.8, a + share * 0.93
        chars = []
        for j, (ch, color) in enumerate(zip(role, role_colors(role, accent))):
            if ch == " ":
                continue
            on = a + (typed - a) * j / n
            off = hold + (gone - hold) * (n - j - 1) / n
            css.append(
                f"@keyframes r{i}_{j}{{0%,{on:.2f}%{{opacity:0}}{on + 0.01:.2f}%,{off:.2f}%{{opacity:1}}"
                f"{off + 0.01:.2f}%,100%{{opacity:0}}}}"
            )
            fill = f"fill:{color};" if color else ""
            chars.append(
                f'<text class="role" x="{x0 + j * cw:.1f}" y="{y}" '
                f'style="{fill}animation:r{i}_{j} {period}s step-end infinite">{esc(ch)}</text>'
            )
        css.append(
            f"@keyframes c{i}{{0%,{a:.2f}%{{transform:translateX({x0:.1f}px);opacity:0;animation-timing-function:steps(1,end)}}"
            f"{a + 0.01:.2f}%{{transform:translateX({x0:.1f}px);opacity:1;animation-timing-function:steps({n},end)}}"
            f"{typed:.2f}%,{hold:.2f}%{{transform:translateX({x0 + full:.1f}px);opacity:1;animation-timing-function:steps({n},end)}}"
            f"{gone:.2f}%{{transform:translateX({x0:.1f}px);opacity:1;animation-timing-function:steps(1,end)}}"
            f"{min(gone + 0.01, 100):.2f}%,100%{{opacity:0}}}}"
            f"@keyframes p{i}{{0%,{a:.2f}%{{opacity:0}}{a + 0.01:.2f}%,{gone:.2f}%{{opacity:1}}{min(gone + 0.01, 100):.2f}%,100%{{opacity:0}}}}"
        )
        svg.append(
            f'<text class="prompt" x="{x0 - cw * 2.2:.1f}" y="{y}" style="animation:p{i} {period}s infinite">&gt;</text>'
            + "".join(chars)
            + f'<g style="animation:c{i} {period}s infinite"><rect class="caret" x="2" y="{y - size * 0.78:.1f}" '
            f'width="{size * 0.55:.1f}" height="{size * 0.95:.1f}" rx="1.5"/></g>'
        )
    return "".join(css), "".join(svg)


def hero() -> None:
    name = "Artem Krupa"
    chip = "TomaToma0  ·  @UberSpy0"
    roles = [
        "ML Engineer",
        "Rust Developer",
        "Frontend Designer",
        "Marketing Analyst",
        "Competitive Programmer",
    ]
    place = ["NUST MISIS", "Moscow", "from Krasnodar"]
    mono_text = chip + "".join(roles) + "".join(place) + ">◆"

    accent = {
        "ML": GREEN,
        "Rust": "#FF5F57",
        "Frontend": "#C084FC",
        "Competitive": "#FB923C",
    }
    role_css, role_svg = typing_roles(roles, accent, y=292, size=26, period=20)

    blobs = [
        # cx, cy, rx, ry, color, opacity, duration, delay
        (260, 120, 420, 210, CYAN, 0.62, 19, 0),
        (930, 90, 380, 200, PINK, 0.58, 23, -6),
        (640, 330, 460, 170, VIOLET, 0.52, 27, -12),
        (1080, 360, 300, 160, AQUA, 0.35, 21, -3),
        (90, 380, 280, 150, PINK, 0.30, 25, -9),
    ]
    grads, ells = [], []
    for i, (cx, cy, rx, ry, col, op, dur, delay) in enumerate(blobs):
        grads.append(
            f'<radialGradient id="b{i}"><stop offset="0" stop-color="{col}" stop-opacity="{op}"/>'
            f'<stop offset=".55" stop-color="{col}" stop-opacity="{op * 0.35:.2f}"/>'
            f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>'
        )
        ells.append(
            f'<ellipse class="aur" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#b{i})" '
            f'style="animation-duration:{dur}s;animation-delay:{delay}s"/>'
        )

    sep = f'<tspan fill="{VIOLET}" fill-opacity=".8">   ◆   </tspan>'
    place_line = sep.join(esc(p) for p in place)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{name} — {', '.join(roles)}">
<title>{name}</title>
<style>
{font_face(DISPLAY, 700, name)}
{font_face(MONO, 500, mono_text)}
.aur{{mix-blend-mode:screen;transform-box:fill-box;transform-origin:center;animation:drift ease-in-out infinite alternate}}
@keyframes drift{{0%{{transform:translate(0,0) scale(1) rotate(0deg)}}50%{{transform:translate(60px,-25px) scale(1.18) rotate(8deg)}}100%{{transform:translate(-50px,20px) scale(.9) rotate(-6deg)}}}}
.star{{fill:#fff;animation:tw ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.name{{font:700 112px '{DISPLAY}',sans-serif;letter-spacing:-3px}}
.outline{{fill:none;stroke:url(#line);stroke-width:1.3;stroke-dasharray:620;stroke-dashoffset:620;animation:draw 2.6s cubic-bezier(.6,.1,.2,1) .3s forwards,dim 1.2s ease 2.6s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes dim{{to{{opacity:.25}}}}
.fill{{fill:url(#ink);opacity:0;animation:in 1.4s ease 1.9s forwards}}
.sheen{{fill:url(#sheen);opacity:0;animation:in 1s ease 3.2s forwards}}
.glow{{fill:url(#ink);filter:url(#blur);opacity:0;animation:glow 1.6s ease 2.1s forwards}}
@keyframes in{{to{{opacity:1}}}}
@keyframes glow{{to{{opacity:.5}}}}
.chip,.place{{opacity:0;animation:rise .9s cubic-bezier(.2,.8,.2,1) forwards}}
.chip{{animation-delay:.6s}} .place{{animation-delay:3.4s}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.mono{{font:500 15px '{MONO}',monospace;fill:{MUTED};letter-spacing:.4px}}
.prompt{{font:500 26px '{MONO}',monospace;fill:{CYAN};opacity:0}}
.role{{font:500 26px '{MONO}',monospace;fill:{INK};opacity:0}}
.caret{{fill:{PINK};animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.dot{{fill:{GREEN};animation:pulse 2.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.ring{{fill:none;stroke:{GREEN};animation:ring 2.2s ease-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes ring{{from{{transform:scale(.6);opacity:.8}}to{{transform:scale(2.4);opacity:0}}}}
{role_css}
{REDUCED_MOTION}
</style>
<defs>
{''.join(grads)}
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="250" y1="0" x2="950" y2="0" spreadMethod="reflect">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;700 0;0 0" dur="10s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="0" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1800 0;1800 0" keyTimes="0;.35;1" dur="7s" begin="3.2s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
  <stop offset="0" stop-color="{CYAN}" stop-opacity=".7"/><stop offset=".35" stop-color="{CYAN}" stop-opacity="0"/>
  <stop offset=".65" stop-color="{PINK}" stop-opacity="0"/><stop offset="1" stop-color="{PINK}" stop-opacity=".7"/>
  <animateTransform attributeName="gradientTransform" type="rotate" values="0 600 200;360 600 200" dur="14s" repeatCount="indefinite"/>
</linearGradient>
<radialGradient id="vign" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".85"/></radialGradient>
<filter id="blur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .05 0"/></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="26"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  {''.join(ells)}
  <g>{stars(W, H, 90, seed=11)}</g>
  <rect width="{W}" height="{H}" fill="url(#vign)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="25.5" fill="none" stroke="url(#edge)" stroke-width="1.5"/>

<g class="chip">
  <rect x="{W / 2 - 168}" y="62" width="336" height="36" rx="18" fill="#ffffff" fill-opacity=".05" stroke="#ffffff" stroke-opacity=".12"/>
  <circle class="ring" cx="{W / 2 - 140}" cy="80" r="4.5"/>
  <circle class="dot" cx="{W / 2 - 140}" cy="80" r="4.5"/>
  <text class="mono" x="{W / 2 + 10}" y="85" text-anchor="middle" style="fill:{INK}">{esc(chip)}</text>
</g>

<g text-anchor="middle">
  <text class="name glow" x="{W / 2}" y="210">{name}</text>
  <text class="name outline" x="{W / 2}" y="210">{name}</text>
  <text class="name fill" x="{W / 2}" y="210">{name}</text>
  <text class="name sheen" x="{W / 2}" y="210">{name}</text>
</g>

{role_svg}

<text class="mono place" style="fill:#A3A9C7" x="{W / 2}" y="352" text-anchor="middle">{place_line}</text>
</svg>
"""
    write("hero.svg", svg)


if __name__ == "__main__":
    from cards import cards
    from sections import sections
    from terminal import terminal

    hero()
    terminal()
    cards()
    sections()
