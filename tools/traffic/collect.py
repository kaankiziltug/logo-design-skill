#!/usr/bin/env python3
"""Archive the repo's GitHub traffic, which GitHub keeps for only 14 days.

Each run merges the current 14-day window into CSV files under --out, so the
history keeps growing for as long as the job runs. Star history is rebuilt in
full every time from the stargazers API, which has no 14-day limit.

Needs a token that can read the repo's traffic (a fine-grained token with
"Administration: Read-only"), in TRAFFIC_TOKEN or GITHUB_TOKEN.

Usage:
    python tools/traffic/collect.py --repo owner/name --out traffic-data
"""

import argparse
import csv
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

API = "https://api.github.com"

DAILY_FIELDS = ["date", "count", "uniques"]
REFERRER_FIELDS = ["snapshot", "referrer", "count", "uniques"]
PATH_FIELDS = ["snapshot", "path", "title", "count", "uniques"]
REPO_FIELDS = ["date", "stars", "forks", "watchers", "open_issues"]
STAR_FIELDS = ["date", "new", "total"]


def get(path, token, accept="application/vnd.github+json"):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "logo-design-skill-traffic",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"GET {path} -> HTTP {err.code}: {detail}") from None


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def stringify(rows):
    return [{k: str(v) for k, v in row.items()} for row in rows]


def merge_daily(path, new_rows):
    """Upsert rows by date. The newest fetch wins, so a partial day is
    overwritten with its final count on the next run."""
    by_date = {r["date"]: r for r in read_rows(path)}
    for row in stringify(new_rows):
        by_date[row["date"]] = row
    write_rows(path, DAILY_FIELDS, [by_date[d] for d in sorted(by_date)])


def replace_snapshot(path, fields, snapshot, new_rows, sort_key):
    """Keep one 14-day snapshot per day: drop any earlier run from today."""
    kept = [r for r in read_rows(path) if r["snapshot"] != snapshot]
    rows = kept + stringify({"snapshot": snapshot, **r} for r in new_rows)
    rows.sort(key=lambda r: (r["snapshot"], -int(r["count"]), sort_key(r)))
    write_rows(path, fields, rows)


def daily(entries):
    return [{"date": e["timestamp"][:10], "count": e["count"], "uniques": e["uniques"]}
            for e in entries]


def star_history(repo, token):
    """Every stargazer with the date they starred, grouped per day."""
    per_day = Counter()
    page = 1
    while True:
        batch = get(f"/repos/{repo}/stargazers?per_page=100&page={page}", token,
                    accept="application/vnd.github.star+json")
        if not batch:
            break
        per_day.update(s["starred_at"][:10] for s in batch)
        page += 1
    rows, total = [], 0
    for day in sorted(per_day):
        total += per_day[day]
        rows.append({"date": day, "new": per_day[day], "total": total})
    return rows


def collect(repo, token, out, today):
    views = get(f"/repos/{repo}/traffic/views", token)
    clones = get(f"/repos/{repo}/traffic/clones", token)
    referrers = get(f"/repos/{repo}/traffic/popular/referrers", token)
    paths = get(f"/repos/{repo}/traffic/popular/paths", token)
    info = get(f"/repos/{repo}", token)

    merge_daily(out / "views.csv", daily(views["views"]))
    merge_daily(out / "clones.csv", daily(clones["clones"]))
    replace_snapshot(out / "referrers.csv", REFERRER_FIELDS, today, referrers,
                     sort_key=lambda r: r["referrer"])
    replace_snapshot(out / "paths.csv", PATH_FIELDS, today, paths,
                     sort_key=lambda r: r["path"])

    repo_rows = {r["date"]: r for r in read_rows(out / "repo.csv")}
    repo_rows[today] = stringify([{
        "date": today,
        "stars": info["stargazers_count"],
        "forks": info["forks_count"],
        "watchers": info["subscribers_count"],
        "open_issues": info["open_issues_count"],
    }])[0]
    write_rows(out / "repo.csv", REPO_FIELDS, [repo_rows[d] for d in sorted(repo_rows)])

    # Traffic is the data that expires, so a failing star fetch must not lose
    # it: keep the previous stars.csv and carry on.
    try:
        stars = star_history(repo, token)
    except RuntimeError as err:
        print(f"::warning::Star history not updated: {err}", file=sys.stderr)
    else:
        write_rows(out / "stars.csv", STAR_FIELDS, stringify(stars))
    return views, clones


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--out", required=True, type=Path, help="data directory")
    args = parser.parse_args()

    token = os.environ.get("TRAFFIC_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Set TRAFFIC_TOKEN (or GITHUB_TOKEN) to a token that can read traffic.")

    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    views, clones = collect(args.repo, token, args.out, today)
    print(f"{args.repo}: 14-day window has {views['count']} views, "
          f"{clones['count']} clones; archived to {args.out}")


if __name__ == "__main__":
    main()
