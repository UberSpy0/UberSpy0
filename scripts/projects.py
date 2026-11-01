"""Project cards for the top public repositories, rebuilt from live GitHub data.

Which repositories show up is decided here (pinned first, then stars, then
recent pushes); profile.json can hide repositories and add notes: a nicer
title, a badge such as "2nd place", a longer description and "my part".
"""

from __future__ import annotations

import datetime as dt

from kit import (
    CONFIG, CYAN, DECOR, DIM, DISPLAY, EFFECTS, FORMATS, INK, MONO, MUTED,
    REDUCED_MOTION, color, esc, font_face, frame, wrap, write,
)

PAD = 32


def select(data: dict) -> list[dict]:
    """Repositories for the Projects section, best first."""
    cfg = CONFIG["projects"]
    exclude = set(cfg.get("exclude", []))
    pool = list(data.get("repos", []))
    if cfg.get("include_contributed", True):
        pool += data.get("contributed", [])
    seen, repos = set(), []
    for r in pool:
        full = r["nameWithOwner"]
        if full in seen or full in exclude or full.split("/")[1] in exclude:
            continue
        seen.add(full)
        repos.append(r)
    pinned = data.get("pinned", [])
    # Two stable sorts: newest push first, then pinned and starred ahead of the rest.
    repos.sort(key=lambda r: r.get("pushedAt") or "", reverse=True)
    repos.sort(key=lambda r: (
        pinned.index(r["nameWithOwner"]) if r["nameWithOwner"] in pinned else len(pinned),
        -r["stargazerCount"],
    ))
    return repos[: int(FORMATS.get("projects_count", 4))]


def ago(stamp: str | None) -> str:
    if not stamp:
        return ""
    then = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    days = (dt.datetime.now(dt.timezone.utc) - then).days
    if days < 1:
        return "updated today"
    if days < 2:
        return "updated yesterday"
    if days < 14:
        return f"updated {days} days ago"
    if days < 60:
        return f"updated {days // 7} weeks ago"
    return f"updated {days // 30} months ago"


def card_file(i: int) -> str:
    return f"project-{i + 1}.svg"


def render(i: int, repo: dict, login: str) -> None:
    note = CONFIG["projects"].get("notes", {}).get(repo["nameWithOwner"], {})
    wide = FORMATS.get("projects", "grid") == "list"
    W = 1200 if wide else 590
    text_w = W - PAD * 2
    owner, name = repo["nameWithOwner"].split("/")
    lang = repo.get("primaryLanguage") or {}

    title = note.get("title") or name
    event = note.get("event") or (repo["nameWithOwner"] if owner != login else (lang.get("name") or "repository"))
    if note.get("badge"):
        badge, badge_color = note["badge"], color(note.get("badge_color", "cyan"))
    else:
        badge, badge_color = f"★ {repo['stargazerCount']}", MUTED
    body = wrap(note.get("body") or repo.get("description") or "No description yet.", 15.5, text_w, em=0.5)
    role = wrap(note["role"], 14, text_w, em=0.5) if note.get("role") else []
    chips = note.get("chips") or [x for x in [lang.get("name")] if x] + [
        t["topic"]["name"] for t in repo.get("repositoryTopics", {}).get("nodes", [])
    ]
    chips_text = "  ·  ".join(chips)
    updated = ago(repo.get("pushedAt"))

    y, rows = 132, []
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
    last = y - (21 if role else 23)  # baseline of the last text line
    H = max(300 if not wide else 220, last + 58)
    if not wide and H > 300:
        raise SystemExit(f"{repo['nameWithOwner']}: card text is too long for the grid (last line at {last}px)")

    title_size = 26 if len(title) < 20 else 23
    live = note.get("badge_color") == "cyan" and EFFECTS.get("live_dot", True)
    dot = ""
    if DECOR.get("status_dots", True):
        cls = ' class="live"' if live else ""
        dot = f'<circle{cls} cx="{W - PAD - len(badge) * 7.8 - 12:.1f}" cy="43.5" r="4" fill="{badge_color}"/>'
    corner = updated + ("  ↗" if DECOR.get("card_arrows", True) else "")
    arrow = f'<text class="m" x="{W - PAD}" y="91" text-anchor="end">{esc(corner)}</text>'
    mono = event + badge + chips_text + updated + "MY PART↗"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}: {esc(badge)}">
<title>{esc(title)}</title>
<style>
{font_face(DISPLAY, 700, title)}
{font_face(DISPLAY, 500, " ".join(body + role))}
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
<text class="m" x="{PAD}" y="48">{esc(event)}</text>
{dot}
<text class="m" x="{W - PAD}" y="48" text-anchor="end" style="fill:{badge_color}">{esc(badge)}</text>
<text class="t" x="{PAD}" y="92">{esc(title)}</text>
{arrow}
{''.join(rows)}
<text class="m" x="{PAD}" y="{H - 32}" style="fill:{MUTED}">{esc(chips_text)}</text>
</svg>
"""
    write(card_file(i), svg)


def projects(data: dict) -> list[dict]:
    """Renders the cards and returns the repositories in README order."""
    repos = select(data)
    for i, repo in enumerate(repos):
        render(i, repo, CONFIG["login"])
    return repos
