"""Shared pieces for every SVG in the profile: config, palette, fonts, helpers.

Everything a person might want to restyle lives in profile.json at the repo
root (the README Editor app edits that file); the scripts only read it.

GitHub renders README images through <img>, so an SVG can't load external
fonts or run scripts. Fonts are fetched from Google Fonts as a subset of the
glyphs the image actually uses and embedded as base64.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CACHE = ROOT / ".cache" / "fonts"
ICONS = Path(__file__).resolve().parent / "icons"

CONFIG = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
COLORS = CONFIG["colors"]
EFFECTS = CONFIG["effects"]
DECOR = CONFIG["decorations"]
WINDOWS = CONFIG["windows"]
FORMATS = CONFIG["formats"]

BG = COLORS["bg"]
INK = COLORS["ink"]
MUTED = COLORS["muted"]
DIM = COLORS["dim"]
LINE = COLORS["line"]  # hairline borders and dividers
EMPTY = COLORS["empty"]  # empty heatmap cells and bar tracks
CYAN = COLORS["cyan"]
VIOLET = COLORS["violet"]
PINK = COLORS["pink"]
GREEN = COLORS["green"]
AMBER = COLORS["amber"]
BLUE = COLORS["blue"]
RUST = COLORS["rust"]
FRONT = COLORS["front"]
ORANGE = COLORS["orange"]

DISPLAY = "Space Grotesk"
MONO = "JetBrains Mono"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def color(name: str) -> str:
    """A palette key from profile.json ("amber") or a literal "#hex"."""
    return COLORS.get(name, name)


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def font_face(family: str, weight: int, text: str) -> str:
    """@font-face rule with a woff2 subset covering `text`, embedded as base64."""
    glyphs = "".join(sorted(set(text + " ")))
    key = hashlib.sha1(f"{family}|{weight}|{glyphs}".encode()).hexdigest()[:16]
    cached = CACHE / f"{key}.woff2"
    if not cached.exists():
        query = urllib.parse.urlencode(
            {"family": f"{family}:wght@{weight}", "text": glyphs, "display": "block"}
        )
        css = _get(f"https://fonts.googleapis.com/css2?{query}").decode()
        url = re.search(r"url\((https://[^)]+)\)", css).group(1)
        CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(_get(url))
    data = base64.b64encode(cached.read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
    )


def icon_path(slug: str) -> str:
    """Path data of a Simple Icons logo, kept in scripts/icons/."""
    path = ICONS / f"{slug}.svg"
    if not path.exists():
        ICONS.mkdir(exist_ok=True)
        path.write_bytes(_get(f"https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{slug}.svg"))
    return re.search(r' d="([^"]+)"', path.read_text()).group(1)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text: str, size: float, width: float, em: float = 0.53) -> list[str]:
    """Greedy word wrap by an average glyph width of `em`."""
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


def radius() -> float:
    return float(WINDOWS.get("radius", 14))


def border_attrs(dashed: bool = False) -> str:
    """Stroke for a window frame, per windows.border: solid, dashed or none."""
    style = "dashed" if dashed else WINDOWS.get("border", "solid")
    if style == "none":
        return 'stroke="none"'
    dash = ' stroke-dasharray="5 5"' if style == "dashed" else ""
    return f'stroke="{LINE}"{dash}'


def frame(w: float, h: float, rx: float | None = None, dashed: bool = False) -> str:
    """The flat card every block sits on: background plus a hairline border."""
    rx = radius() if rx is None else rx
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="{BG}" {border_attrs(dashed)}/>'


REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def write(name: str, svg: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    path.write_text(svg, encoding="utf-8")
    print(f"{name}: {path.stat().st_size // 1024} KB")
