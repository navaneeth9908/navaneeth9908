#!/usr/bin/env python
"""Render normalized contribution data as a self-contained animated SVG."""

from __future__ import annotations

import argparse
import html
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "contributions.json"
DEFAULT_OUTPUT = ROOT / "assets" / "contribution-heatmap.svg"
PALETTE = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    days = payload["days"]
    stats = payload["stats"]
    username = payload["username"]

    dates = [date.fromisoformat(item["date"]) for item in days]
    first = min(dates)
    first_sunday = first - timedelta(days=(first.weekday() + 1) % 7)

    cell = 11
    gap = 3
    step = cell + gap
    left = 54
    top = 62
    width = 860
    height = 226

    month_positions: list[tuple[int, str]] = []
    seen_months: set[tuple[int, int]] = set()
    for day in dates:
        key = (day.year, day.month)
        week = (day - first_sunday).days // 7
        if key not in seen_months and day.day <= 7:
            month_positions.append((week, day.strftime("%b")))
            seen_months.add(key)

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(username)} GitHub contribution activity</title>',
        '<desc id="desc">An animated 53-week contribution heatmap generated from public GitHub activity.</desc>',
        '<style>',
        'text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}',
        '.muted{fill:#8b949e}.primary{fill:#e6edf3}.accent{fill:#58a6ff}',
        '</style>',
        '<rect width="860" height="226" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '<circle cx="21" cy="20" r="5" fill="#ff5f57"/><circle cx="39" cy="20" r="5" fill="#febc2e"/><circle cx="57" cy="20" r="5" fill="#28c840"/>',
        f'<text x="430" y="25" text-anchor="middle" font-size="12" class="muted">{esc(username)}@github: ~/activity</text>',
        '<text x="20" y="49" font-size="12" class="accent">$ ./contributions.sh --last-year</text>',
    ]

    for week, label in month_positions:
        x = left + week * step
        if x < width - 45:
            svg.append(f'<text x="{x}" y="58" font-size="10" class="muted">{label}</text>')

    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        svg.append(
            f'<text x="18" y="{top + row * step + 9}" font-size="9" class="muted">{label}</text>'
        )

    for item in days:
        day = date.fromisoformat(item["date"])
        week = (day - first_sunday).days // 7
        weekday = (day.weekday() + 1) % 7
        x = left + week * step
        y = top + weekday * step
        level = max(0, min(int(item["level"]), len(PALETTE) - 1))
        delay = 0.18 + week * 0.025 + weekday * 0.012
        title = f'{item["count"]} contributions on {item["date"]}'
        svg.extend(
            [
                f'<rect x="{x}" y="{y - 9}" width="{cell}" height="{cell}" rx="2" fill="{PALETTE[level]}" opacity="0">',
                f'<title>{esc(title)}</title>',
                f'<animate attributeName="y" from="{y - 9}" to="{y}" begin="{delay:.3f}s" dur="0.32s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>',
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.28s" fill="freeze"/>',
                '</rect>',
            ]
        )

    total = int(stats["total"])
    active = int(stats["active_days"])
    current = int(stats["current_streak"])
    longest = int(stats["longest_streak"])
    footer = (
        f"{total:,} contributions  ·  {active} active days  ·  "
        f"current streak {current}d  ·  longest {longest}d"
    )
    svg.extend(
        [
            f'<text x="20" y="192" font-size="11" class="primary">{esc(footer)}</text>',
            '<text x="681" y="213" font-size="9" class="muted">Less</text>',
        ]
    )
    for index, color in enumerate(PALETTE):
        svg.append(
            f'<rect x="{710 + index * 16}" y="203" width="11" height="11" rx="2" fill="{color}"/>'
        )
    svg.extend(
        [
            '<text x="797" y="213" font-size="9" class="muted">More</text>',
            f'<text x="20" y="213" font-size="9" class="muted">Public data through {esc(payload["range"]["end"])}</text>',
            '</svg>',
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"Rendered {len(days)} contribution cells to {args.output}")


if __name__ == "__main__":
    main()
