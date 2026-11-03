#!/usr/bin/env python3
"""Turn the archived traffic CSVs into a README dashboard with SVG charts.

Reads what collect.py wrote and writes README.md and charts/*.svg into the
same directory, so the data repo renders as a dashboard on GitHub.

Usage:
    python tools/traffic/report.py --data traffic-data --repo owner/name
"""

import argparse
import csv
import datetime
import math
from collections import defaultdict
from pathlib import Path

VIEWS_COLOR = "#2563eb"
UNIQUES_COLOR = "#93c5fd"
CLONES_COLOR = "#059669"
CLONERS_COLOR = "#6ee7b7"
STARS_COLOR = "#d97706"


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(n):
    return f"{n:,}"


def nice_max(value):
    if value <= 0:
        return 1
    magnitude = 10 ** math.floor(math.log10(value))
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * magnitude:
            return step * magnitude
    return 10 * magnitude


def short_num(n):
    if n >= 1000:
        text = f"{n / 1000:.1f}".rstrip("0").rstrip(".")
        return f"{text}k"
    return f"{n:g}"


def line_chart(dates, series, width=800, height=240):
    """series: [(label, values, color)]. Returns a self-contained SVG string
    that follows the viewer's light or dark theme."""
    left, right, top, bottom = 52, 16, 28, 30
    plot_w, plot_h = width - left - right, height - top - bottom
    peak = nice_max(max((max(v) for _, v, _ in series if v), default=0))
    n = len(dates)

    def x(i):
        return left + (plot_w * i / (n - 1) if n > 1 else plot_w / 2)

    def y(v):
        return top + plot_h - plot_h * v / peak

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" font-size="11">',
        "<style>.t{fill:#57606a}.g{stroke:#d0d7de}"
        "@media (prefers-color-scheme:dark){.t{fill:#8b949e}.g{stroke:#30363d}}</style>",
    ]
    for k in range(5):
        value = peak * k / 4
        gy = y(value)
        parts.append(f'<line class="g" x1="{left}" x2="{width - right}" y1="{gy:.1f}" y2="{gy:.1f}" stroke-width="1"/>')
        parts.append(f'<text class="t" x="{left - 8}" y="{gy + 4:.1f}" text-anchor="end">{short_num(value)}</text>')

    ticks = sorted({0, n - 1, *(round((n - 1) * k / 5) for k in range(1, 5))}) if n else []
    for i in ticks:
        anchor = "start" if i == 0 else "end" if i == n - 1 else "middle"
        parts.append(f'<text class="t" x="{x(i):.1f}" y="{height - 10}" text-anchor="{anchor}">{dates[i][5:]}</text>')

    legend_x = left
    for label, values, color in series:
        if not values:
            continue
        points = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values))
        if n > 1:
            area = f"{x(0):.1f},{y(0):.1f} {points} {x(n - 1):.1f},{y(0):.1f}"
            parts.append(f'<polygon points="{area}" fill="{color}" fill-opacity="0.08"/>')
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>')
        parts.append(f'<rect x="{legend_x}" y="8" width="10" height="10" rx="2" fill="{color}"/>')
        parts.append(f'<text class="t" x="{legend_x + 14}" y="17">{label}</text>')
        legend_x += 14 + 7 * len(label) + 18
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def daily_series(rows):
    return {r["date"]: (int(r["count"]), int(r["uniques"])) for r in rows}


def fill_days(start, end):
    day = datetime.date.fromisoformat(start)
    last = datetime.date.fromisoformat(end)
    days = []
    while day <= last:
        days.append(day.isoformat())
        day += datetime.timedelta(days=1)
    return days


def window_sum(by_date, days, index):
    return sum(by_date.get(d, (0, 0))[index] for d in days)


def change(current, previous):
    if previous == 0:
        return "—"
    pct = (current - previous) / previous * 100
    return f"{pct:+.0f}%"


def latest_snapshot(rows):
    if not rows:
        return None, []
    snap = max(r["snapshot"] for r in rows)
    return snap, [r for r in rows if r["snapshot"] == snap]


def build(data, repo, today):
    views = daily_series(read_rows(data / "views.csv"))
    clones = daily_series(read_rows(data / "clones.csv"))
    stars = read_rows(data / "stars.csv")
    repo_rows = read_rows(data / "repo.csv")
    ref_snap, referrers = latest_snapshot(read_rows(data / "referrers.csv"))
    _, paths = latest_snapshot(read_rows(data / "paths.csv"))
    new_stars = {r["date"]: int(r["new"]) for r in stars}

    if not views:
        raise SystemExit(f"No views.csv in {data}; run collect.py first.")

    first = min(min(views), min(clones) if clones else min(views))
    days = fill_days(first, max(max(views), max(clones) if clones else max(views)))

    # Compare whole days only: the newest day is usually still filling up.
    complete = [d for d in days if d < today]
    last7, prev7 = complete[-7:], complete[-14:-7]

    charts = data / "charts"
    charts.mkdir(exist_ok=True)
    (charts / "views.svg").write_text(line_chart(days, [
        ("Views", [views.get(d, (0, 0))[0] for d in days], VIEWS_COLOR),
        ("Unique visitors", [views.get(d, (0, 0))[1] for d in days], UNIQUES_COLOR),
    ]), encoding="utf-8")
    (charts / "clones.svg").write_text(line_chart(days, [
        ("Clones", [clones.get(d, (0, 0))[0] for d in days], CLONES_COLOR),
        ("Unique cloners", [clones.get(d, (0, 0))[1] for d in days], CLONERS_COLOR),
    ]), encoding="utf-8")
    if stars:
        star_days = fill_days(stars[0]["date"], max(stars[-1]["date"], today))
        totals, running = [], 0
        for d in star_days:
            running += new_stars.get(d, 0)
            totals.append(running)
        (charts / "stars.svg").write_text(
            line_chart(star_days, [("Total stars", totals, STARS_COLOR)]), encoding="utf-8")

    def row(label, by_date, index):
        cur, prev = window_sum(by_date, last7, index), window_sum(by_date, prev7, index)
        total = window_sum(by_date, days, index)
        return f"| {label} | {num(cur)} | {num(prev)} | {change(cur, prev)} | {num(total)} |"

    star_cur = sum(new_stars.get(d, 0) for d in last7)
    star_prev = sum(new_stars.get(d, 0) for d in prev7)
    best_day = max(days, key=lambda d: views.get(d, (0, 0))[0])
    latest = repo_rows[-1] if repo_rows else {}
    clone_rate = window_sum(clones, last7, 1) / max(window_sum(views, last7, 1), 1) * 100

    lines = [
        f"# Traffic · {repo}",
        "",
        f"Updated {today} (UTC). Archived daily since {first}. "
        f"Generated by `tools/traffic/report.py` in {repo}; don't edit by hand.",
        "",
        "## At a glance",
        "",
        "| | Last 7 days | Previous 7 days | Change | All archived |",
        "|---|---:|---:|---:|---:|",
        row("Views", views, 0),
        row("Unique visitors\\*", views, 1),
        row("Clones", clones, 0),
        row("Unique cloners\\*", clones, 1),
        f"| New stars | {num(star_cur)} | {num(star_prev)} | {change(star_cur, star_prev)} "
        f"| {num(int(stars[-1]['total'])) if stars else '—'} |",
        "",
    ]
    if latest:
        lines += [
            f"**{num(int(latest['stars']))}** stars · **{num(int(latest['forks']))}** forks · "
            f"**{num(int(latest['watchers']))}** watchers · "
            f"best day so far: **{num(views[best_day][0])}** views on {best_day} · "
            f"unique cloners per unique visitor (7 days): **{clone_rate:.0f}%**",
            "",
        ]
    lines += [
        "\\* GitHub only reports uniques per day, so multi-day figures are sums of daily uniques "
        "and count a returning visitor once per day.",
        "",
        "## Views",
        "",
        "![Daily views](charts/views.svg)",
        "",
        "## Clones",
        "",
        "Clones are the closest signal to installs: GitHub doesn't count plugin marketplace installs separately.",
        "",
        "![Daily clones](charts/clones.svg)",
        "",
    ]
    if stars:
        lines += ["## Stars", "", "![Total stars](charts/stars.svg)", ""]

    if referrers:
        total_ref = sum(int(r["count"]) for r in referrers) or 1
        lines += [
            f"## Top referrers (14 days to {ref_snap})", "",
            "| Source | Views | Unique | Share |", "|---|---:|---:|---:|",
        ]
        lines += [f"| {r['referrer']} | {num(int(r['count']))} | {num(int(r['uniques']))} "
                  f"| {int(r['count']) / total_ref * 100:.0f}% |" for r in referrers]
        lines.append("")
    if paths:
        prefix = f"/{repo}"
        lines += [f"## Popular pages (14 days to {ref_snap})", "",
                  "| Page | Views | Unique |", "|---|---:|---:|"]
        for r in paths:
            page = r["path"][len(prefix):] if r["path"].startswith(prefix) else r["path"]
            lines.append(f"| `{page or '/'}` | {num(int(r['count']))} | {num(int(r['uniques']))} |")
        lines.append("")

    months = defaultdict(lambda: [0, 0, 0, 0])
    for d in days:
        m = months[d[:7]]
        m[0] += views.get(d, (0, 0))[0]
        m[1] += views.get(d, (0, 0))[1]
        m[2] += clones.get(d, (0, 0))[0]
    for d, n in new_stars.items():
        months[d[:7]][3] += n
    lines += ["## By month", "", "| Month | Views | Unique visitors\\* | Clones | New stars |",
              "|---|---:|---:|---:|---:|"]
    for key in sorted(months, reverse=True):
        v, u, c, s = months[key]
        tracked = "" if key >= first[:7] else " (stars only)"
        lines.append(f"| {key}{tracked} | {num(v)} | {num(u)} | {num(c)} | {num(s)} |")
    lines += [
        "",
        "## Raw data",
        "",
        "`views.csv` and `clones.csv` (daily), `referrers.csv` and `paths.csv` (one 14-day snapshot per day), "
        "`repo.csv` (daily stars, forks, watchers), `stars.csv` (stars per day since the repo was created).",
        "",
    ]
    (data / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", required=True, type=Path, help="data directory")
    parser.add_argument("--repo", required=True, help="owner/name, for the title")
    args = parser.parse_args()
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    build(args.data, args.repo, today)
    print(f"Wrote {args.data / 'README.md'}")


if __name__ == "__main__":
    main()
