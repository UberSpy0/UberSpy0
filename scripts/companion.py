"""Capri: an optional tiny digital companion that wanders across the README.

A stylized chibi inspired by the chaotic personality construct from
Cyberpunk: Edgerunners 2: black silhouette, huge shard-like pink hair with
green tips, a green visor with blue eyes.

GitHub shows each README block as a separate <img>, so she can't really walk
from one picture to another. Instead every block gets the same companion
layer with one shared animation cycle, and each block owns a slice of that
cycle: she glitches in, drifts or teleports between a few spots, pulls a face
or says something short, and glitches out, then turns up in the next block.

Everything is driven by the "companion" object in profile.json.
"""

from __future__ import annotations

import random
import re

from kit import ASSETS, BG, CONFIG, INK, MONO, ROOT, color, esc, font_face

DEFAULTS = {
    "enabled": False,
    "size": 34,
    "opacity": 0.85,
    "cycle": 120,
    "order": "random",
    "faces": True,
    "phrases_on": True,
    "phrases": ["hi, choom", "boo!"],
    "skip": [],
    "seed": 1,
    "colors": {"hair": "#FF3E7F", "tips": "#4BFF6E", "visor": "#4BFF6E",
               "eyes": "#3DA9FF", "body": "#07070C", "outline": "#FF3E7F"},
}

SETTINGS = {**DEFAULTS, **CONFIG.get("companion", {})}
SETTINGS["colors"] = {**DEFAULTS["colors"], **SETTINGS.get("colors", {})}

# Which README section each generated picture belongs to.
SECTION_OF = {"hero.svg": "hero", "achievements.svg": "achievements", "stack.svg": "stack",
              "github.svg": "activity", "now.svg": "activity", "telegram.svg": "contact"}

FACES = ("wink", "happy", "angry", "hearts", "tongue", "glitch")

# Her drawing lives in a 32 x 40 box; hair sticks out of it on every side.
LEFT, RIGHT, TOP, BOTTOM = -9, 41, -4, 40

SHARDS = (
    "8,9 12,-2 15,6 19,-4 24,8",   # crest
    "9,8 -6,1 -1,8 -9,13 8,16",    # left sweep
    "23,8 38,0 33,8 41,13 24,16",  # right sweep
    "9,14 1,25 10,19",             # left lock
    "23,14 31,25 22,19",           # right lock
)
TIPS = ("-6,1 -2.5,2.6 -3.4,4.6", "-9,13 -5,11.6 -4.6,13.8", "38,0 34.6,1.8 35.6,3.8",
        "41,13 37,11.6 36.6,13.8", "1,25 3,21 4.6,22.6", "31,25 29,21 27.4,22.6", "19,-4 18.6,-.4 20.6,0")


def section_of(asset: str) -> str:
    if asset.startswith("h-"):
        return asset[2:-4]
    if asset.startswith("project-"):
        return "projects"
    return SECTION_OF.get(asset, "")


# ---------------------------------------------------------------- drawing --

def _eye(cx: float, cy: float, c: dict) -> str:
    return (f'<circle cx="{cx}" cy="{cy}" r="2" fill="#000"/>'
            f'<circle cx="{cx}" cy="{cy}" r="1.3" fill="{c["eyes"]}"/>'
            f'<circle cx="{cx + .2}" cy="{cy - .2}" r=".5" fill="#fff"/>')


def _heart(cx: float, cy: float, fill: str) -> str:
    return (f'<path d="M{cx} {cy + 1.5}L{cx - 1.7} {cy - .1}A.9 .9 0 0 1 {cx} {cy - 1.1}'
            f'A.9 .9 0 0 1 {cx + 1.7} {cy - .1}Z" fill="{fill}"/>')


def _limb(d: str, c: dict) -> str:
    return (f'<path d="{d}" stroke="{c["outline"]}" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
            f'<path d="{d}" stroke="{c["body"]}" stroke-width="1.5" stroke-linecap="round" fill="none"/>')


def body(c: dict) -> str:
    """Everything that doesn't change with her expression."""
    hair, tips, out = c["hair"], c["tips"], c["outline"]
    shards = "".join(f'<polygon points="{p}" fill="{hair}"/>' for p in SHARDS)
    tip_svg = "".join(f'<polygon points="{p}" fill="{tips}"/>' for p in TIPS)
    return "".join([
        shards,
        f'<g class="gl">{tip_svg}</g>',
        '<circle class="sp" cx="2" cy="7" r=".6" fill="#fff"/><circle class="sp s2" cx="33" cy="6" r=".5" fill="#fff"/>',
        _limb("M11.5 23L7 28.5", c), _limb("M20.5 23L25 28.5", c),
        _limb("M14 31L13.2 38.6", c), _limb("M18 31L18.8 38.6", c),
        f'<polygon points="11,21.5 21,21.5 19.5,31.5 12.5,31.5" fill="{c["body"]}" stroke="{out}" stroke-width=".8" stroke-linejoin="round"/>',
        f'<path d="M12.6 24.2L19.4 26" stroke="{hair}" stroke-width="1.2"/>',
        f'<path d="M13.6 28.2L16 29.6L18.4 28.2" stroke="{tips}" stroke-width="1" fill="none"/>',
        f'<circle cx="16" cy="14" r="7.6" fill="{c["body"]}" stroke="{out}" stroke-width=".8"/>',
        f'<rect x="9.4" y="10.4" width="13.2" height="6.2" rx="1.3" fill="{c["visor"]}"/>',
    ])


def normal_face(c: dict) -> str:
    return (_eye(13, 13.5, c) + _eye(19, 13.5, c)
            + f'<path d="M14 19Q16 20.6 18 19" stroke="{c["outline"]}" stroke-width=".8" fill="none" stroke-linecap="round"/>'
            # eyelids for blinking
            + f'<g class="bl"><rect x="10.4" y="11.2" width="11.2" height="4.6" fill="{c["visor"]}"/>'
              '<path d="M11.4 13.6h3.2M17.4 13.6h3.2" stroke="#000" stroke-width=".9"/></g>')


def face(kind: str, c: dict) -> str:
    pink = c["outline"]
    line = 'stroke="#000" stroke-width="1.1" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    smile = f'<path d="M14 19Q16 20.6 18 19" stroke="{pink}" stroke-width=".8" fill="none" stroke-linecap="round"/>'
    wink = f'<path d="M17.4 14.2L19 12.6L20.6 14.2" {line}/>'
    if kind == "wink":
        return _eye(13, 13.5, c) + wink + smile
    if kind == "happy":
        return (f'<path d="M11.4 14.4L13 12.7L14.6 14.4M17.4 14.4L19 12.7L20.6 14.4" {line}/>'
                f'<path d="M13.4 18.4Q16 22.4 18.6 18.4Z" fill="{pink}"/>')
    if kind == "angry":
        return (f'<path d="M11.8 12.3L14.3 13.6L11.8 14.9M20.2 12.3L17.7 13.6L20.2 14.9" {line}/>'
                f'<path d="M13.6 20L14.8 19L16 20L17.2 19L18.4 20" stroke="{pink}" stroke-width=".8" fill="none"/>')
    if kind == "hearts":
        return _heart(13, 13.6, pink) + _heart(19, 13.6, pink) + f'<circle cx="16" cy="19.6" r=".9" fill="{pink}"/>'
    if kind == "tongue":
        return _eye(13, 13.5, c) + wink + smile + '<ellipse cx="17.1" cy="20.4" rx="1.1" ry="1.3" fill="#FF9EC4"/>'
    # glitch: the visor fills with static
    return (f'<rect x="9.4" y="10.4" width="13.2" height="6.2" rx="1.3" fill="{c["hair"]}"/>'
            '<path d="M10.4 12h4M16 12h5.4M11 14h7M19.4 14h2.2M10.4 15.6h3" stroke="#fff" stroke-width=".7"/>'
            f'<path d="M14 19.4h4" stroke="{pink}" stroke-width=".8"/>')


# ---------------------------------------------------------------- motion --

def _pct(t: float, cycle: float) -> str:
    return f"{max(0.0, min(100.0, 100 * t / cycle)):.3f}%"


def _keyframes(name: str, frames: list, cycle: float) -> str:
    """frames: (seconds, css body). Equal percentages keep the last body."""
    seen: dict = {}
    for t, css in sorted(frames, key=lambda f: f[0]):
        seen[_pct(t, cycle)] = css
    return f"@keyframes {name}{{" + "".join(f"{p}{{{css}}}" for p, css in seen.items()) + "}"


def layer(asset: str, w: float, h: float, slot: tuple) -> str:
    s = SETTINGS
    c = {k: color(v) for k, v in s["colors"].items()}
    cycle = float(s["cycle"])
    size = max(16.0, min(float(s["size"]), h - 10))
    k = size / BOTTOM
    op = max(0.2, min(1.0, float(s["opacity"])))
    rng = random.Random(f"{s['seed']}:{asset}")

    # where she may stand: the whole drawing stays inside the block
    x_lo, x_hi = -LEFT * k + 6, w - RIGHT * k - 6
    y_lo, y_hi = -TOP * k + 4, h - BOTTOM * k - 4
    if x_hi < x_lo or y_hi < y_lo:
        return ""

    def spot() -> tuple:
        return round(rng.uniform(x_lo, x_hi), 1), round(rng.uniform(y_lo, y_hi), 1)

    start, length = slot
    a = start + length * 0.08
    b = start + min(length * 0.9, length * 0.08 + 16)
    # as many stops as fit while every pause stays long enough to read a phrase
    fit = [n for n in (2, 3, 3, 4) if (b - a - 0.9 - 1.3 * (n - 1)) / n >= 2.0] or [1]
    stops = rng.choice(fit)
    points = [spot() for _ in range(stops)]
    kinds = ["teleport" if rng.random() < 0.35 else "walk" for _ in range(stops - 1)]
    move_time = sum(0.18 if kd == "teleport" else 1.3 for kd in kinds)
    pause = max(0.6, (b - a - 0.9 - move_time) / stops)

    moves, pauses = [(0.0, points[0]), (a, points[0])], []
    fade = [(0.0, "opacity:0"), (a, f"opacity:{op}"), (a + .1, "opacity:.15"), (a + .2, f"opacity:{op}"),
            (a + .28, "opacity:.4"), (a + .36, f"opacity:{op}")]
    t = a + 0.4
    for i, kd in enumerate(kinds):
        pauses.append((t, t + pause, points[i]))
        t += pause
        dt = 0.18 if kd == "teleport" else 1.3
        if kd == "teleport":
            fade += [(t, "opacity:0"), (t + dt + .04, f"opacity:{op}")]
        moves += [(t, points[i]), (t + dt, points[i + 1])]
        t += dt
    pauses.append((t, b - 0.4, points[-1]))
    moves.append((cycle, points[-1]))
    fade += [(b - .4, "opacity:.3"), (b - .3, f"opacity:{op}"), (b - .15, "opacity:.2"), (b, "opacity:0")]

    rng.shuffle(pauses)
    style, extra, face_svg = [], "", ""
    if s.get("faces", True) and rng.random() < 0.8:
        p0, p1, _ = pauses[0]
        f0, f1 = p0 + 0.25, min(p1, p0 + 0.25 + 1.8)
        face_svg = f'<g class="fx">{face(rng.choice(FACES), c)}</g>'
        style += [_keyframes("cpn", [(0, "opacity:1"), (f0, "opacity:0"), (f1, "opacity:1")], cycle),
                  _keyframes("cpf", [(0, "opacity:0"), (f0, "opacity:1"), (f1, "opacity:0")], cycle),
                  f".fn{{animation:cpn {cycle}s step-end infinite}}.fx{{opacity:0;animation:cpf {cycle}s step-end infinite}}"]
    phrases = [p.strip()[:30] for p in s.get("phrases", []) if p.strip()]
    if s.get("phrases_on", True) and phrases and rng.random() < 0.7:
        p0, p1, (px, py) = pauses[-1]
        if len(pauses) == 1 and face_svg:  # same pause as the face: talk right after it
            p0 = max(p0, min(p1 - 1.0, p0 + 1.2))
        phrase = rng.choice(phrases)
        b0, b1 = p0 + 0.2, min(p1, p0 + 0.2 + 1.4 + 0.06 * len(phrase))
        bw, bh = len(phrase) * 6.6 + 14, 20
        if py + TOP * k - bh - 4 >= 2:  # room above her head
            bx = min(max(px + 16 * k - bw / 2, 4), w - bw - 4)
            by = py + TOP * k - bh - 4
        else:  # beside her
            by = min(max(py + 6 * k, 2), h - bh - 2)
            bx = px + RIGHT * k + 4 if px + RIGHT * k + 4 + bw <= w - 4 else px + LEFT * k - 4 - bw
            bx = min(max(bx, 4), w - bw - 4)
        extra = (f'<g class="bub" transform="translate({bx - px:.1f} {by - py:.1f})">'
                 f'<rect width="{bw:.1f}" height="{bh}" rx="7" fill="{BG}" stroke="{c["hair"]}" stroke-width="1"/>'
                 f'<text x="7" y="14" class="cpt">{esc(phrase)}</text></g>')
        style += [_keyframes("cpp", [(0, "opacity:0"), (b0, "opacity:1"), (b1, "opacity:0")], cycle),
                  f".bub{{opacity:0;animation:cpp {cycle}s step-end infinite}}",
                  font_face(MONO, 600, phrase).replace(f"'{MONO}'", "'CpMono'"),
                  f".cpt{{font:600 11px 'CpMono',monospace;fill:{INK};white-space:pre}}"]

    style += [
        _keyframes("cpm", [(tt, f"transform:translate({x}px,{y}px)") for tt, (x, y) in moves], cycle),
        _keyframes("cpo", fade, cycle),
        f".cpm{{animation:cpm {cycle}s ease-in-out infinite}}",
        f".cpo{{opacity:0;animation:cpo {cycle}s step-end infinite}}",
        ".cpb{animation:cpb 1.7s ease-in-out infinite alternate}@keyframes cpb{to{transform:translateY(-1.6px)}}",
        ".bl{opacity:0;animation:cpbl 4.3s step-end infinite}@keyframes cpbl{0%{opacity:0}93%{opacity:1}96%{opacity:0}}",
        ".gl{animation:cpg 2.9s step-end infinite}@keyframes cpg{0%{opacity:1}88%{opacity:.25}91%{opacity:1}95%{opacity:0}97%{opacity:1}}",
        ".sp{opacity:0;animation:cpsp 2.2s step-end infinite}.s2{animation-delay:-1.1s}@keyframes cpsp{0%{opacity:0}60%{opacity:1}75%{opacity:0}}",
        "@media (prefers-reduced-motion: reduce){.cpw{display:none}}",
    ]
    x0, y0 = points[0]
    return (f'<g class="cpw" aria-hidden="true"><style>{"".join(style)}</style>'
            f'<g class="cpm" style="transform:translate({x0}px,{y0}px)"><g class="cpo"><g class="cpb">'
            f'<g transform="scale({k:.4f})">{body(c)}<g class="fn">{normal_face(c)}</g>{face_svg}</g>'
            f'</g>{extra}</g></g></g>')


def stations(readme: str) -> list:
    assets = re.findall(r'src="assets/([^"]+\.svg)"', readme)
    skip = set(SETTINGS.get("skip", []))
    out = [a for a in dict.fromkeys(assets) if section_of(a) not in skip]
    if SETTINGS.get("order") == "random":
        random.Random(f"order:{SETTINGS['seed']}").shuffle(out)
    return out


def apply() -> None:
    """Adds her to the pictures the README shows. Run after everything is written."""
    preview()
    if not SETTINGS.get("enabled"):
        return
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    route = stations(readme)
    if not route:
        return
    length = float(SETTINGS["cycle"]) / len(route)
    for i, asset in enumerate(route):
        path = ASSETS / asset
        svg = path.read_text(encoding="utf-8")
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
        if not m:
            continue
        piece = layer(asset, float(m.group(1)), float(m.group(2)), (i * length, length))
        cut = svg.rfind("</svg>")
        path.write_text(svg[:cut] + piece + "\n" + svg[cut:], encoding="utf-8")
    print(f"companion: {len(route)} blocks, {SETTINGS['cycle']}s cycle")


def preview() -> None:
    """A sheet with every expression, for the editor. Not committed (.cache/)."""
    c = {k: color(v) for k, v in SETTINGS["colors"].items()}
    cell = 60
    kinds = ("normal",) + FACES
    parts = []
    for i, kd in enumerate(kinds):
        face_svg = normal_face(c) if kd == "normal" else face(kd, c)
        parts.append(f'<g transform="translate({i * cell + 15} 6) scale(.9)">{body(c)}{face_svg}</g>')
    w = cell * len(kinds)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 50" width="{w * 2}" height="100">'
           '<style>.bl{opacity:0;animation:b 4.3s step-end infinite}@keyframes b{0%{opacity:0}93%{opacity:1}96%{opacity:0}}'
           '.gl{animation:g 2.9s step-end infinite}@keyframes g{0%{opacity:1}88%{opacity:.25}91%{opacity:1}95%{opacity:0}97%{opacity:1}}'
           '.sp{opacity:0}</style>'
           f'<rect width="{w}" height="50" rx="8" fill="{BG}"/>{"".join(parts)}</svg>')
    out = ROOT / ".cache" / "companion.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
