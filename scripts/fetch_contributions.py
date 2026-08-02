#!/usr/bin/env python
"""Fetch a public GitHub contribution calendar and store normalized JSON."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = "navaneeth9908"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"
COUNT_RE = re.compile(r"([\d,]+)\s+contribution", re.IGNORECASE)


def parse_count(text: str) -> int:
    """Extract a contribution count from GitHub's accessible tooltip text."""
    if text.lower().startswith("no contribution"):
        return 0
    match = COUNT_RE.search(text)
    if not match:
        raise ValueError(f"Could not parse contribution tooltip: {text!r}")
    return int(match.group(1).replace(",", ""))


def derive_stats(days: list[dict[str, object]]) -> dict[str, object]:
    counts = [int(day["count"]) for day in days]
    total = sum(counts)
    active_days = sum(count > 0 for count in counts)

    longest = 0
    running = 0
    for count in counts:
        if count > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    current = 0
    index = len(days) - 1
    # A blank current day does not break a streak that was alive yesterday.
    if index >= 0 and int(days[index]["count"]) == 0:
        latest = date.fromisoformat(str(days[index]["date"]))
        if latest == date.today():
            index -= 1
    while index >= 0 and int(days[index]["count"]) > 0:
        current += 1
        index -= 1

    best = max(days, key=lambda day: int(day["count"]), default=None)
    return {
        "total": total,
        "active_days": active_days,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
    }


def fetch(username: str) -> dict[str, object]:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        headers={
            "Accept": "text/html",
            "User-Agent": f"{username}-profile-readme/1.0 (+https://github.com/{username})",
        },
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    tooltips = {
        tip.get("for"): tip.get_text(" ", strip=True)
        for tip in soup.select("tool-tip[for]")
    }

    parsed: dict[str, dict[str, object]] = {}
    for cell in soup.select(".ContributionCalendar-day[data-date]"):
        day_date = str(cell["data-date"])
        tooltip = tooltips.get(cell.get("id"), "")
        if not tooltip:
            raise RuntimeError(f"Missing contribution tooltip for {day_date}")
        parsed[day_date] = {
            "date": day_date,
            "count": parse_count(tooltip),
            "level": int(cell.get("data-level", 0)),
        }

    days = [parsed[key] for key in sorted(parsed)]
    if len(days) < 350:
        raise RuntimeError(f"Expected a full contribution year; parsed only {len(days)} days")

    return {
        "username": username,
        "source": url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "stats": derive_stats(days),
        "days": days,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = fetch(args.username)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {len(payload['days'])} days and "
        f"{payload['stats']['total']} contributions to {args.output}"
    )


if __name__ == "__main__":
    main()
