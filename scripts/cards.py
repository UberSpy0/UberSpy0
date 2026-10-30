"""Project cards: one SVG per project so each can be its own link in the README."""

from dataclasses import dataclass, field

from kit import (
    AMBER, CYAN, DIM, DISPLAY, GREEN, INK, MONO, MUTED, REDUCED_MOTION, VIOLET,
    esc, font_face, frame, wrap, write,
)

W, H = 590, 300
PAD = 32

STATUS = {"medal": AMBER, "shipped": GREEN, "building": CYAN, "progress": VIOLET}


@dataclass
class Card:
    file: str
    title: str
    event: str
    status: tuple[str, str]  # (kind, label), kind is a key of STATUS
    body: str
    role: str = ""
    chips: list[str] = field(default_factory=list)
    linked: bool = False  # the README wraps it in a link; draws an arrow


CARDS = [
    Card(
        file="card-mlpath.svg",
        title="ML Path",
        event="Learning platform · 2026",
        status=("building", "Building"),
        body=(
            "An interactive course that takes a first-year student to an ML internship: "
            "a phased roadmap, lessons with quizzes, real Python in the browser and an "
            "algorithms track where every step is animated next to the code."
        ),
        chips=["Python", "Pyodide", "JavaScript", "C++"],
    ),
    Card(
        file="card-saluteagent.svg",
        title="SaluteAgent",
        event="ShortHack × SberTech · Sep 2026",
        status=("medal", "2nd place"),
        body=(
            "AI support assistant: drafts an answer from the knowledge base, then "
            "fact-checks every claim against its sources."
        ),
        role="Frontend, UI design and a ticket classifier fine-tuned on YandexGPT-5-Pro. Team of 4.",
        chips=["YandexGPT-5-Pro", "React", "FastAPI", "Claude Code"],
        linked=True,
    ),
    Card(
        file="card-hotel.svg",
        title="One Step to the Perfect Hotel",
        event="Ostrovok Hackathon · Oct 2026",
        status=("shipped", "Shipped"),
        body=(
            "Finds what hotel listings never mention: sea view, real quiet, beach "
            "access, mountain sun. Every fact keeps its source."
        ),
        role="Street-noise model per facade, floor and hour, checked against guest reviews. Team of 5.",
        chips=["Python", "GeoPandas", "OpenStreetMap", "Claude Code"],
    ),
    Card(
        file="card-vst.svg",
        title="Rust VST Plugin",
        event="Audio DSP · Ableton Live & FL Studio",
        status=("progress", "In progress"),
        body=(
            "A music plugin for Ableton Live and FL Studio: real-time sound processing "
            "on the audio thread, packaged as VST3 and CLAP."
        ),
        chips=["Rust", "DSP", "VST3", "CLAP"],
        linked=True,
    ),
]


def render(c: Card) -> None:
    color = STATUS[c.status[0]]
    text_w = W - PAD * 2
    body = wrap(c.body, 15.5, text_w, em=0.5)
    role = wrap(c.role, 14, text_w, em=0.5) if c.role else []
    chips = "  ·  ".join(c.chips)
    title_size = 26 if len(c.title) < 20 else 23

    y = 132
    rows = []
    for line in body:
        rows.append(f'<text class="b" x="{PAD}" y="{y}">{esc(line)}</text>')
        y += 23
    if role:
        y += 14
        rows.append(f'<text class="k" x="{PAD}" y="{y}">MY PART</text>')
        y += 24
        for line in role:
            rows.append(f'<text class="r" x="{PAD}" y="{y}">{esc(line)}</text>')
            y += 21
    last = int(rows[-1].split('y="')[1].split('"')[0])
    if last > H - 58:
        raise SystemExit(f"{c.file}: text runs into the chips (last line at {last}px)")

    # Building pulses gently; everything else is still.
    dot_cls = ' class="live"' if c.status[0] == "building" else ""
    arrow = f'<text class="m" x="{W - PAD}" y="{92 if title_size == 26 else 90}" text-anchor="end">↗</text>' if c.linked else ""
    mono = c.event + c.status[1] + chips + "MY PART↗"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(c.title)}: {esc(c.status[1])}">
<title>{esc(c.title)}</title>
<style>
{font_face(DISPLAY, 700, c.title)}
{font_face(DISPLAY, 500, c.body + c.role)}
{font_face(MONO, 500, mono)}
.t{{font:700 {title_size}px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.3px}}
.b{{font:500 15.5px '{DISPLAY}',sans-serif;fill:{MUTED}}}
.r{{font:500 14px '{DISPLAY}',sans-serif;fill:#A3A9C7}}
.m{{font:500 13px '{MONO}',monospace;fill:{DIM};white-space:pre}}
.k{{font:500 11px '{MONO}',monospace;fill:{DIM};letter-spacing:1.5px}}
.live{{animation:live 2.4s ease-in-out infinite}}
@keyframes live{{50%{{opacity:.3}}}}
{REDUCED_MOTION}
</style>
{frame(W, H)}
<text class="m" x="{PAD}" y="48">{esc(c.event)}</text>
<circle{dot_cls} cx="{W - PAD - len(c.status[1]) * 7.8 - 12:.1f}" cy="43.5" r="4" fill="{color}"/>
<text class="m" x="{W - PAD}" y="48" text-anchor="end" style="fill:{color}">{esc(c.status[1])}</text>
<text class="t" x="{PAD}" y="92">{esc(c.title)}</text>
{arrow}
{''.join(rows)}
<text class="m" x="{PAD}" y="{H - 32}" style="fill:{MUTED}">{esc(chips)}</text>
</svg>
"""
    write(c.file, svg)


def cards() -> None:
    for c in CARDS:
        render(c)


if __name__ == "__main__":
    cards()
