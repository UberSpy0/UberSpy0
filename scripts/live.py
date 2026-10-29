"""Live cards rebuilt by the GitHub Action: stats, now building, contribution tetris.

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
    AMBER, ASSETS, CYAN, DISPLAY, GREEN, INK, MONO, MUTED, PINK, REDUCED_MOTION,
    ROOT, VIOLET, esc, font_face,
)

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!, $recent: DateTime!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) { nodes { stargazerCount } }
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

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
BLOCK = ["#161B2E", "#1D4E6B", CYAN, VIOLET, PINK]


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
        "repositories": {"nodes": [{"stargazerCount": 2}, {"stargazerCount": 1}]},
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


def odometer(value: int, x: float, y: float, size: int, color: str, delay: float, clip: str) -> str:
    """Number whose digits roll up from 0 into place; `clip` shows one digit row."""
    out = []
    for i, ch in enumerate(str(value)):
        dx = x + i * size * 0.6
        col = "".join(f'<text x="{dx:.1f}" y="{y + k * size * 1.1:.1f}">{k}</text>' for k in range(10))
        out.append(
            f'<g clip-path="url(#{clip})"><g class="roll d{size}" style="--to:-{int(ch) * size * 1.1:.1f}px;'
            f'animation-duration:{1.2 + i * 0.25:.2f}s;animation-delay:{delay:.2f}s" fill="{color}">{col}</g></g>'
        )
    return "".join(out)


def digit_clip(cid: str, y: float, size: int) -> str:
    return f'<clipPath id="{cid}"><rect x="0" y="{y - size:.1f}" width="1200" height="{size * 1.3:.1f}"/></clipPath>'


def stats_card(user: dict) -> str:
    W, H = 1200, 330
    y = user["year"]
    days = calendar_days(user)
    cur, longest = streaks(days)
    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])
    repos = len(y["commitContributionsByRepository"])
    numbers = [
        ("contributions", y["contributionCalendar"]["totalContributions"], CYAN),
        ("commits", y["totalCommitContributions"] + y["restrictedContributionsCount"], VIOLET),
        ("pull requests", y["totalPullRequestContributions"], PINK),
        ("repos touched", repos, "#22D3EE"),
        ("stars earned", stars, AMBER),
    ]
    langs = languages(user)

    rows = []
    for i, (label, val, color) in enumerate(numbers):
        cx = 56 + (i % 3) * 140
        r = i // 3
        cy = 128 + r * 104
        rows.append(
            f'{odometer(val, cx, cy, 36, color, 0.3 + i * 0.12, f"row{r}")}'
            f'<text x="{cx}" y="{cy + 26}" class="lab">{esc(label)}</text>'
        )
    clips = digit_clip("row0", 128, 36) + digit_clip("row1", 232, 36) + digit_clip("streakd", 143, 44)
    rows_svg = "".join(rows)

    # streak block
    sx = 520
    last7 = days[-7:]
    peak = max([n for _, n, _ in last7] + [1])
    bars = "".join(
        f'<rect x="{sx + 40 + k * 26}" y="{262 - max(4, n / peak * 46):.1f}" width="16" height="{max(4, n / peak * 46):.1f}" rx="4" '
        f'fill="{BLOCK[max(1, lvl)] if n else "#1F2440"}" class="bar" style="animation-delay:{0.8 + k * 0.08:.2f}s"/>'
        for k, (_, n, lvl) in enumerate(last7)
    )
    streak_digits = str(cur)
    streak_svg = (
        f'<circle cx="{sx + 130}" cy="128" r="58" fill="none" stroke="#fff" stroke-opacity=".07" stroke-width="8"/>'
        f'<circle cx="{sx + 130}" cy="128" r="58" fill="none" stroke="url(#streak)" stroke-width="8" stroke-linecap="round" '
        f'pathLength="1" class="ringdraw" style="--to:{1 - min(1, cur / max(longest, 1)):.3f}" transform="rotate(-90 {sx + 130} 128)"/>'
        + odometer(cur, sx + 130 - len(streak_digits) * 44 * 0.6 / 2, 143, 44, INK, 0.5, "streakd")
        + f'<text x="{sx + 130}" y="166" text-anchor="middle" class="lab">day streak</text>'
        f'<text x="{sx + 130}" y="214" text-anchor="middle" class="lab">longest <tspan fill="{INK}">{longest}</tspan> days</text>'
        f'{bars}<text x="{sx + 130}" y="290" text-anchor="middle" class="lab">last 7 days</text>'
    )

    # languages
    lx, lw = 800, 340
    lang_svg = [f'<text x="{lx}" y="76" class="cap">languages I commit in</text>']
    for i, (name, color, share) in enumerate(langs):
        ly = 112 + i * 40
        lang_svg.append(
            f'<circle cx="{lx + 6}" cy="{ly - 5}" r="5" fill="{color}"/>'
            f'<text x="{lx + 20}" y="{ly}" class="lname">{esc(name)}</text>'
            f'<text x="{lx + lw}" y="{ly}" text-anchor="end" class="lab">{share * 100:.1f}%</text>'
            f'<rect x="{lx}" y="{ly + 9}" width="{lw}" height="5" rx="2.5" fill="#fff" fill-opacity=".07"/>'
            f'<rect x="{lx}" y="{ly + 9}" width="{max(4, lw * share):.1f}" height="5" rx="2.5" fill="{color}" class="grow" '
            f'style="transform-origin:{lx}px 0;animation-delay:{0.6 + i * 0.12:.2f}s"/>'
        )

    text = "".join(n[0] for n in numbers) + "0123456789daystreaklongestdayslast7languagesIcommitin%." + "".join(l[0] for l in langs) + "GitHub · last 12 months"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub stats for the last 12 months">
<title>GitHub stats</title>
<style>
{font_face(MONO, 500, text)}
{font_face(MONO, 700, "0123456789")}
.lab{{font:500 13px '{MONO}',monospace;fill:{MUTED}}}
.cap{{font:500 13px '{MONO}',monospace;fill:{INK};letter-spacing:.5px}}
.lname{{font:500 15px '{MONO}',monospace;fill:{INK}}}
.d36 text{{font:700 36px '{MONO}',monospace}}
.d44 text{{font:700 44px '{MONO}',monospace}}
.roll{{animation:roll cubic-bezier(.2,.9,.25,1) both}}
@keyframes roll{{from{{transform:translateY(0)}}to{{transform:translateY(var(--to))}}}}
.ringdraw{{stroke-dasharray:1;stroke-dashoffset:1;animation:ring 1.8s cubic-bezier(.3,.8,.3,1) .4s forwards}}
@keyframes ring{{to{{stroke-dashoffset:var(--to)}}}}
.grow{{animation:grow 1.2s cubic-bezier(.3,.8,.3,1) both}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.bar{{transform-box:fill-box;transform-origin:bottom;animation:up .7s cubic-bezier(.3,.8,.3,1) both}}
@keyframes up{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
{clips}
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="#0C0F1E" stroke="#fff" stroke-opacity=".08"/>
<text x="56" y="62" class="cap">GitHub · last 12 months</text>
<line x1="480" x2="480" y1="40" y2="{H - 40}" stroke="#fff" stroke-opacity=".07"/>
<line x1="770" x2="770" y1="40" y2="{H - 40}" stroke="#fff" stroke-opacity=".07"/>
{rows_svg}
{streak_svg}
{''.join(lang_svg)}
</svg>
"""


def now_card(user: dict) -> str:
    W, H = 1200, 190
    repos = [
        r for r in user["recent"]["commitContributionsByRepository"]
        if r["repository"]["name"] not in HIDDEN
    ]
    days = calendar_days(user)[-14:]
    peak = max([n for _, n, _ in days] + [1])
    pts = [(640 + i * (500 / 13), 150 - n / peak * 80) for i, (_, n, _) in enumerate(days)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = line + f" L{pts[-1][0]:.1f},150 L{pts[0][0]:.1f},150 Z"
    total14 = sum(n for _, n, _ in days)

    if repos:
        top = repos[0]["repository"]
        count = repos[0]["contributions"]["totalCount"]
        name = "private project" if top["isPrivate"] else top["name"]
        lang = top["primaryLanguage"] or {"name": "—", "color": MUTED}
        commit = ""
        if not top["isPrivate"] and top.get("defaultBranchRef"):
            nodes = top["defaultBranchRef"]["target"]["history"]["nodes"]
            commit = nodes[0]["messageHeadline"][:58] if nodes else ""
        lock = (
            f'<path d="M0 6h10v8H0z M2 6V4a3 3 0 0 1 6 0v2" fill="none" stroke="{MUTED}" stroke-width="1.6" '
            f'transform="translate(58 84)"/>' if top["isPrivate"] else ""
        )
        others = [
            ("private" if r["repository"]["isPrivate"] else r["repository"]["name"], r["contributions"]["totalCount"])
            for r in repos[1:3]
        ]
    else:
        name, count, lang, commit, lock, others = "taking a breath", 0, {"name": "—", "color": MUTED}, "", "", []

    name_x = 82 if lock else 56
    also = "  ·  ".join(f"{n} {c}" for n, c in others)
    text = f"NOW BUILDING{name}{lang['name']}{commit}{count} commits · last 14 daysalso:{also}{total14} contributions"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Now building: {esc(name)}">
<title>Now building</title>
<style>
{font_face(DISPLAY, 700, name)}
{font_face(MONO, 500, text)}
.k{{font:500 12px '{MONO}',monospace;letter-spacing:2px;fill:{GREEN}}}
.n{{font:700 34px '{DISPLAY}',sans-serif;fill:{INK};letter-spacing:-.5px}}
.m{{font:500 13.5px '{MONO}',monospace;fill:{MUTED}}}
.live{{animation:live 1.6s ease-in-out infinite}}
@keyframes live{{50%{{opacity:.35}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 1.6s ease-out infinite}}
@keyframes ring{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3);opacity:0}}}}
.spark{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2s ease-out .3s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.area{{opacity:0;animation:in 1s ease 1.6s forwards}}
@keyframes in{{to{{opacity:1}}}}
.dot{{animation:in .4s ease 2.2s both}}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="sl" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="sa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".3"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="#0C0F1E" stroke="#fff" stroke-opacity=".08"/>
<circle class="ring" cx="62" cy="50" r="4.5" fill="none" stroke="{GREEN}"/>
<circle class="live" cx="62" cy="50" r="4.5" fill="{GREEN}"/>
<text x="76" y="54" class="k">NOW BUILDING</text>
{lock}
<text x="{name_x}" y="98" class="n">{esc(name)}</text>
<circle cx="62" cy="126" r="5" fill="{lang['color']}"/>
<text x="74" y="131" class="m"><tspan fill="{INK}">{esc(lang['name'])}</tspan>  ·  {count} commits · last 14 days</text>
<text x="56" y="160" class="m">{esc(commit) if commit else (f"also: {esc(also)}" if also else "")}</text>
<path class="area" d="{area}" fill="url(#sa)"/>
<path class="spark" d="{line}" pathLength="1" fill="none" stroke="url(#sl)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
<circle class="dot" cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="4.5" fill="{PINK}"/>
<text x="1140" y="54" text-anchor="end" class="m">{total14} contributions</text>
</svg>
"""


def tetris_card(user: dict) -> str:
    """Last year's contribution graph assembled by falling columns, then cleared."""
    weeks = user["year"]["contributionCalendar"]["weeks"]
    cell, gap = 16, 4
    ox, oy = 60, 70
    W = ox * 2 + len(weeks) * (cell + gap) - gap
    H = oy + 7 * (cell + gap) + 46
    step, fall = 0.16, 0.55
    land = len(weeks) * step + fall
    period = land + 5.5
    pct = lambda t: f"{t / period * 100:.3f}%"
    rules, cols, grid = [], [], []
    for w, week in enumerate(weeks):
        x = ox + w * (cell + gap)
        blocks = []
        for d in week["contributionDays"]:
            row = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            y = oy + row * (cell + gap)
            grid.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="#fff" fill-opacity=".035"/>')
            lvl = LEVEL[d["contributionLevel"]]
            if lvl:
                blocks.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{BLOCK[lvl]}"/>')
        if not blocks:
            continue
        t0 = w * step
        out = land + 3.6 + (len(weeks) - w) * 0.012
        rules.append(
            f"@keyframes c{w}{{0%,{pct(t0)}{{transform:translateY(-{H}px);opacity:0;animation-timing-function:cubic-bezier(.55,0,1,.45)}}"
            f"{pct(t0 + 0.02)}{{opacity:1}}"
            f"{pct(t0 + fall)}{{transform:translateY(0);animation-timing-function:ease-out}}"
            f"{pct(t0 + fall + 0.12)}{{transform:translateY(-3px)}}"
            f"{pct(t0 + fall + 0.24)},{pct(out)}{{transform:translateY(0);opacity:1;animation-timing-function:cubic-bezier(.55,0,1,.45)}}"
            f"{pct(out + 0.9)},100%{{transform:translateY({H}px);opacity:0}}}}"
        )
        cols.append(f'<g style="animation:c{w} {period:.2f}s infinite">{"".join(blocks)}</g>')
    total = user["year"]["contributionCalendar"]["totalContributions"]
    label = f"contribution tetris · {total} contributions in the last year"
    flash_at = land + 0.4
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}">
<title>contribution tetris</title>
<style>
{font_face(MONO, 500, label + "LINE CLEAR!")}
.lab{{font:500 13px '{MONO}',monospace;fill:{MUTED}}}
.clear{{font:500 13px '{MONO}',monospace;fill:{PINK};letter-spacing:3px}}
{''.join(rules)}
@keyframes sweep{{0%,{pct(flash_at)}{{transform:translateX(-300px);opacity:0}}{pct(flash_at + 0.1)}{{opacity:1}}{pct(flash_at + 1.4)}{{transform:translateX({W + 100}px);opacity:1}}{pct(flash_at + 1.5)},100%{{opacity:0}}}}
@keyframes msg{{0%,{pct(flash_at + 0.5)}{{opacity:0}}{pct(flash_at + 0.8)},{pct(flash_at + 2.8)}{{opacity:1}}{pct(flash_at + 3.2)},100%{{opacity:0}}}}
{REDUCED_MOTION}
</style>
<defs>
<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="fr"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="#0C0F1E" stroke="#fff" stroke-opacity=".08"/>
<text x="{ox}" y="42" class="lab">{esc(label)}</text>
<text x="{W - ox}" y="42" text-anchor="end" class="clear" style="animation:msg {period:.2f}s infinite">LINE CLEAR!</text>
<g clip-path="url(#fr)">
{''.join(grid)}
{''.join(cols)}
<rect x="0" y="{oy - 10}" width="240" height="{7 * (cell + gap) + 12}" fill="url(#beam)" style="animation:sweep {period:.2f}s infinite"/>
</g>
</svg>
"""


def main() -> None:
    if "--demo" in sys.argv:
        user, out = demo(), ROOT / ".cache" / "demo"
    else:
        token = os.environ["GH_TOKEN"]
        user, out = fetch(os.environ.get("GH_LOGIN", "UberSpy0"), token), ASSETS
    out.mkdir(parents=True, exist_ok=True)
    for name, svg in [("github.svg", stats_card(user)), ("now.svg", now_card(user)), ("tetris.svg", tetris_card(user))]:
        (out / name).write_text(svg, encoding="utf-8")
        print(f"{out.name}/{name}: {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
