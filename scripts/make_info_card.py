#!/usr/bin/env python
"""Generate an animated neofetch-inspired professional information card."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "assets" / "info-card.svg"

ROWS = [
    ("Name", "Sai Navaneeth Thota"),
    ("Handle", "@navaneeth9908"),
    ("Location", "Atlanta, GA"),
    ("Role", "Data Engineer / Analytics"),
    ("Focus", "Agentic BI + AI-enabled data"),
    ("Languages", "Python · SQL"),
    ("Data", "PySpark · pandas · DuckDB"),
    ("Build", "FastAPI · Docker · GitHub Actions"),
    ("Quality", "pytest · evals · reproducibility"),
    ("Status", "Open to U.S. data + AI roles"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    lines: list[str] = []
    start_y = 86
    for index, (key, value) in enumerate(ROWS):
        y = start_y + index * 27
        begin = 0.35 + index * 0.17
        lines.extend(
            [
                f'<g opacity="0" transform="translate(0 7)">',
                f'<text x="27" y="{y}" font-size="12" fill="#58a6ff">{html.escape(key)}</text>',
                f'<text x="128" y="{y}" font-size="12" fill="#e6edf3">{html.escape(value)}</text>',
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.32s" fill="freeze"/>',
                f'<animateTransform attributeName="transform" type="translate" from="0 7" to="0 0" begin="{begin:.2f}s" dur="0.32s" fill="freeze"/>',
                '</g>',
            ]
        )

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="410" viewBox="0 0 500 410" role="img" aria-labelledby="title desc">',
        '<title id="title">Sai Navaneeth Thota professional information card</title>',
        '<desc id="desc">An animated neofetch-style card describing a data engineer and analytics professional.</desc>',
        '<rect width="500" height="410" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '<circle cx="20" cy="20" r="5" fill="#ff5f57"/><circle cx="38" cy="20" r="5" fill="#febc2e"/><circle cx="56" cy="20" r="5" fill="#28c840"/>',
        '<text x="250" y="25" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" fill="#8b949e">sai@github: ~</text>',
        '<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        '<text x="25" y="55" font-size="12" fill="#3fb950">$ neofetch --profile</text>',
        '<line x1="25" y1="66" x2="475" y2="66" stroke="#21262d"/>',
        *lines,
        '<g opacity="0">',
        '<text x="27" y="377" font-size="11" fill="#8b949e">Evidence-first systems. Tested, cited, reproducible.</text>',
        '<animate attributeName="opacity" from="0" to="1" begin="2.2s" dur="0.4s" fill="freeze"/>',
        '</g>',
        '<rect x="27" y="390" width="9" height="3" fill="#3fb950" opacity="0">',
        '<animate attributeName="opacity" values="0;1;0;1" begin="2.35s" dur="1.2s" repeatCount="indefinite"/></rect>',
        '</g>',
        '</svg>',
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"Rendered {len(ROWS)} profile rows to {args.output}")


if __name__ == "__main__":
    main()
