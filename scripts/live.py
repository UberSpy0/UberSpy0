"""Live cards rebuilt by the GitHub Action: activity stats and now building.

    GH_TOKEN=... GH_LOGIN=UberSpy0 python3 scripts/live.py
    python3 scripts/live.py --demo      # synthetic data into .cache/demo, for previews

With the default Actions token private repositories only show up as counts.
A PROFILE_TOKEN secret (read-only PAT) lets "Now building" see private
activity; private repository names are never printed.
"""

import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

from kit import (
    ASSETS, CYAN, DIM, DISPLAY, GREEN, INK, MONO, MUTED, REDUCED_MOTION, ROOT,
    esc, font_face, frame,
)

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!, $recent: DateTime!) {
  user(login: $login) {
    year: contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
      commitContributionsByRepository(maxRepositories: 100) {
        contributions { totalCount }
        repository {
          languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
            totalSize edges { size node { name color } }
          }
        }
      }
    }
    recent: contributionsCollection(from: $recent, to: $to) {
      commitContributionsByRepository(maxRepositories: 6) {
        contributions { totalCount }
        repository {
          name nameWithOwner isPrivate description
          primaryLanguage { name color }
          defaultBranchRef { target { ... on Commit { history(first: 1) { nodes { messageHeadline } } } } }
        }
      }
    }
  }
}
"""

# Coursework and this profile repo never count as "now building".
HIDDEN = {"Python_Labs", "UberSpy0"}
# Sandboxes: their activity counts, but the name shows as "private project".
MASKED = {"ML-Practice-Repo"}

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch(login: str, token: str) -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    variables = {
        "login": login,
        "from": (now - dt.timedelta(days=364)).isoformat(),
        "to": now.isoformat(),
        "recent": (now - dt.timedelta(days=14)).isoformat(),
    }
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def demo() -> dict:
    rnd = random.Random(3)
    start = dt.date.today() - dt.timedelta(days=364)
    weeks, days = [], []
    for i in range(365):
        d = start + dt.timedelta(days=i)
        busy = 0.25 + 0.6 * (i / 365)
        n = rnd.choice([0, 0, 1, 2, 3, 5, 8]) if rnd.random() < busy else 0
        lvl = "NONE" if n == 0 else ["FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"][min(3, n // 2)]
        days.append({"date": d.isoformat(), "contributionCount": n, "contributionLevel": lvl})
        if d.weekday() == 5 or i == 364:
            weeks.append({"contributionDays": days})
            days = []
    lang = lambda n, c, s: {"size": s, "node": {"name": n, "color": c}}
    return {
        "year": {
            "totalCommitContributions": 312,
            "totalPullRequestContributions": 18,
            "restrictedContributionsCount": 140,
            "contributionCalendar": {"totalContributions": 486, "weeks": weeks},
            "commitContributionsByRepository": [
                {"contributions": {"totalCount": 120}, "repository": {"languages": {"totalSize": 100, "edges": [lang("Python", "#3572A5", 80), lang("TypeScript", "#3178c6", 20)]}}},
                {"contributions": {"totalCount": 60}, "repository": {"languages": {"totalSize": 100, "edges": [lang("JavaScript", "#f1e05a", 70), lang("CSS", "#663399", 30)]}}},
                {"contributions": {"totalCount": 20}, "repository": {"languages": {"totalSize": 100, "edges": [lang("Rust", "#dea584", 100)]}}},
            ],
        },
        "recent": {
            "commitContributionsByRepository": [
                {"contributions": {"totalCount": 34}, "repository": {"name": "ML-Practice-Repo", "nameWithOwner": "UberSpy0/ML-Practice-Repo", "isPrivate": False, "description": None, "primaryLanguage": {"name": "Python", "color": "#3572A5"}, "defaultBranchRef": {"target": {"history": {"nodes": [{"messageHeadline": "feat: gradient descent from scratch"}]}}}}},
                {"contributions": {"totalCount": 12}, "repository": {"name": "secret", "nameWithOwner": "UberSpy0/secret", "isPrivate": True, "description": None, "primaryLanguage": {"name": "JavaScript", "color": "#f1e05a"}, "defaultBranchRef": None}},
            ]
        },
    }


def calendar_days(user: dict) -> list[tuple[str, int, int]]:
    out = []
    for w in user["year"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            out.append((d["date"], d["contributionCount"], LEVEL[d["contributionLevel"]]))
    return out


def streaks(days: list[tuple[str, int, int]]) -> tuple[int, int]:
    longest = run = 0
    for _, n, _ in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    tail = days[::-1]
    if tail and tail[0][1] == 0:
        tail = tail[1:]  # today may still be empty
    for _, n, _ in tail:
        if not n:
            break
        current += 1
    return current, longest


def languages(user: dict, top: int = 5) -> list[tuple[str, str, float]]:
    weight: dict[str, float] = {}
    colors: dict[str, str] = {}
    for item in user["year"]["commitContributionsByRepository"]:
        commits = item["contributions"]["totalCount"]
        langs = item["repository"]["languages"]
        total = langs["totalSize"] or 1
        for e in langs["edges"]:
            name = e["node"]["name"]
            weight[name] = weight.get(name, 0) + commits * e["size"] / total
            colors[name] = e["node"]["color"] or MUTED
    s = sum(weight.values()) or 1
    ranked = sorted(weight.items(), key=lambda kv: -kv[1])[:top]
    return [(n, colors[n], w / s) for n, w in ranked]


def stats_card(user: dict) -> str:
    W, H = 1200, 228
    y = user["year"]
    days = calendar_days(user)
    cur, longest = streaks(days)
    numbers = [
        ("contributions", y["contributionCalendar"]["totalContributions"]),
        ("commits", y["totalCommitContributions"] + y["restrictedContributionsCount"]),
        ("pull requests", y["totalPullRequestContributions"]),
        ("day streak", cur),
        ("best streak", longest),
    ]
    metrics = "".join(
        f'<text class="v" x="{40 + i * 150}" y="106">{val}</text>'
        f'<text class="m" x="{40 + i * 150}" y="132">{label}</text>'
        for i, (label, val) in enumerate(numbers)
    )

    # Last 26 weeks as a small one-color heatmap on the right.
    weeks = y["contributionCalendar"]["weeks"][-26:]
    cell, step = 9, 12
    x0 = W - 40 - len(weeks) * step + (step - cell)
    shades = ["#141829", "#1B6496", "#2385C2", "#2FA3DF", CYAN]
    dark, lit = [], []
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            level = LEVEL[d["contributionLevel"]]
            rect = (
                f'<rect x="{x0 + wi * step}" y="{58 + dt.date.fromisoformat(d["date"]).isoweekday() % 7 * step}" '
                f'width="{cell}" height="{cell}" rx="2" fill="{shades[level]}"'
            )
            if not level:
                dark.append(rect + "/>")
                continue
            # Days with activity are neon tubes: each flickers on its own clock.
            # Seeded by date, so a rebuild doesn't reshuffle unchanged days.
            rnd = random.Random(d["date"])
            lit.append(
                rect + f' class="neon" style="animation-duration:{rnd.uniform(3.5, 8):.2f}s;'
                f'animation-delay:-{rnd.uniform(0, 8):.2f}s"/>'
            )
    cells = "".join(dark) + f'<g filter="url(#glow)">{"".join(lit)}</g>'

    langs = languages(user)
    bar, legend, x, lx = [], [], 40.0, 40.0
    for name, color, share in langs:
        w = (W - 80) * share
        bar.append(f'<rect x="{x:.1f}" y="166" width="{max(w - 2, 1):.1f}" height="6" fill="{color}"/>')
        x += w
        label = f"{name} {share * 100:.0f}%"
        legend.append(
            f'<circle cx="{lx + 4:.1f}" cy="{197.5}" r="4" fill="{color}"/>'
            f'<text class="m" x="{lx + 14:.1f}" y="202" style="fill:{MUTED}">{esc(label)}</text>'
        )
        lx += 14 + len(label) * 7.2 + 28
    updated = dt.datetime.now(dt.timezone.utc).strftime("updated %d %b %Y")
    text = "".join(l for l, _ in numbers) + "".join(f"{n} {s * 100:.0f}%" for n, _, s in langs) + "last 12 months" + updated + "0123456789"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub activity for the last 12 months">
<title>GitHub activity</title>
<style>
{font_face(DISPLAY, 700, "0123456789")}
{font_face(MONO, 500, text)}
.v{{font:700 38px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.5px}}
.m{{font:500 12.5px '{MONO}',monospace;fill:{DIM}}}
.neon{{animation:neon linear infinite}}
@keyframes neon{{0%,40%,44%,47%,72%,75%,100%{{opacity:1}}41%{{opacity:.15}}42%{{opacity:.9}}43%{{opacity:.3}}46%{{opacity:.45}}73.5%{{opacity:.55}}}}
{REDUCED_MOTION}
</style>
<defs>
<filter id="glow" x="-20%" y="-30%" width="140%" height="160%">
  <feGaussianBlur in="SourceGraphic" stdDeviation="2.4" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>
{frame(W, H)}
<text class="m" x="40" y="44">last 12 months</text>
<text class="m" x="{W - 40}" y="44" text-anchor="end">{updated}</text>
{metrics}
{cells}
<clipPath id="bar"><rect x="40" y="166" width="{W - 80}" height="6" rx="3"/></clipPath>
<g clip-path="url(#bar)"><rect x="40" y="166" width="{W - 80}" height="6" fill="#141829"/>{''.join(bar)}</g>
{''.join(legend)}
</svg>
"""


def now_card(user: dict) -> str:
    W, H = 1200, 136
    repos = [
        r for r in user["recent"]["commitContributionsByRepository"]
        if r["repository"]["name"] not in HIDDEN
    ]
    days = calendar_days(user)[-14:]
    peak = max([n for _, n, _ in days] + [1])
    pts = [(820 + i * (340 / 13), 112 - n / peak * 44) for i, (_, n, _) in enumerate(days)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    total14 = sum(n for _, n, _ in days)

    def hidden(repo: dict) -> bool:
        return repo["isPrivate"] or repo["name"] in MASKED

    lock = ""
    if repos:
        top = repos[0]["repository"]
        count = repos[0]["contributions"]["totalCount"]
        name = "private project" if hidden(top) else top["name"]
        lang = top["primaryLanguage"] or {"name": "—", "color": MUTED}
        commit = ""
        if not hidden(top) and top.get("defaultBranchRef"):
            nodes = top["defaultBranchRef"]["target"]["history"]["nodes"]
            commit = nodes[0]["messageHeadline"][:56] if nodes else ""
        if hidden(top):
            lock = (
                f'<path d="M0 7h12v9H0z M2.5 7V4.5a3.5 3.5 0 0 1 7 0V7" fill="none" stroke="{MUTED}" '
                f'stroke-width="1.6" transform="translate(40 72)"/>'
            )
        meta = f"{lang['name']}  ·  {count} commits" + (f"  ·  {commit}" if commit else "")
    else:
        name, lang, meta = "taking a breath", {"name": "", "color": DIM}, "no public commits in the last two weeks"

    name_x = 62 if lock else 40
    head = f"{total14} contributions · 14 days"
    text = "now building" + meta + head
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Now building: {esc(name)}">
<title>Now building</title>
<style>
{font_face(DISPLAY, 700, name)}
{font_face(MONO, 500, text)}
.n{{font:700 26px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.3px}}
.m{{font:500 13px '{MONO}',monospace;fill:{DIM};white-space:pre}}
.live{{animation:live 2.4s ease-in-out infinite}}
@keyframes live{{50%{{opacity:.3}}}}
{REDUCED_MOTION}
</style>
{frame(W, H)}
<circle class="live" cx="44" cy="40.5" r="4" fill="{GREEN}"/>
<text class="m" x="58" y="45">now building</text>
<text class="m" x="{W - 40}" y="45" text-anchor="end">{esc(head)}</text>
{lock}
<text class="n" x="{name_x}" y="88">{esc(name)}</text>
<circle cx="44" cy="107.5" r="4" fill="{lang['color']}"/>
<text class="m" x="56" y="112" style="fill:{MUTED}">{esc(meta)}</text>
<path d="{line}" fill="none" stroke="{CYAN}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.5" fill="{CYAN}"/>
</svg>
"""


def main() -> None:
    if "--demo" in sys.argv:
        user, out = demo(), ROOT / ".cache" / "demo"
    else:
        token = os.environ["GH_TOKEN"]
        user, out = fetch(os.environ.get("GH_LOGIN", "UberSpy0"), token), ASSETS
    out.mkdir(parents=True, exist_ok=True)
    for name, svg in [("github.svg", stats_card(user)), ("now.svg", now_card(user))]:
        (out / name).write_text(svg, encoding="utf-8")
        print(f"{out.name}/{name}: {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
