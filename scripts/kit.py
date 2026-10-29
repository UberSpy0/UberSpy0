"""Shared pieces for every SVG in the profile: palette, fonts, helpers.

GitHub renders README images through <img>, so an SVG can't load external
fonts or run scripts. Fonts are fetched from Google Fonts as a subset of the
glyphs the image actually uses and embedded as base64.
"""

import base64
import hashlib
import random
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CACHE = ROOT / ".cache" / "fonts"

# Taken from the avatar: sky-blue background and the pink-violet flag.
BG = "#0A0C16"
BG2 = "#11142A"
INK = "#E6EAF5"
MUTED = "#8A90AD"
DIM = "#4A5072"
CYAN = "#38BDF8"
AQUA = "#22D3EE"
PINK = "#F472B6"
VIOLET = "#A78BFA"
GREEN = "#4ADE80"
AMBER = "#FBBF24"

DISPLAY = "Space Grotesk"
MONO = "JetBrains Mono"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"


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


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def stars(w: int, h: int, n: int, seed: int, cls: str = "star") -> str:
    """Twinkling dots with fixed positions so rebuilds don't churn the diff."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([0.6, 0.8, 1.0, 1.0, 1.3, 1.7])
        dur = rnd.uniform(2.5, 6.5)
        delay = rnd.uniform(0, 6)
        out.append(
            f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:-{delay:.2f}s"/>'
        )
    return "\n".join(out)


REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def write(name: str, svg: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    path.write_text(svg, encoding="utf-8")
    print(f"{name}: {path.stat().st_size // 1024} KB")
