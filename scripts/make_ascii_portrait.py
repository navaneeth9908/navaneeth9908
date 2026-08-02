#!/usr/bin/env python
"""Convert the profile avatar into an animated terminal-style ASCII SVG."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "assets" / "avatar-source.png"
DEFAULT_OUTPUT = ROOT / "assets" / "ascii-portrait.svg"
RAMP = " .,:;irsXA253hMHGS#9B&@"


def ascii_rows(source: Path, columns: int = 78, rows: int = 47) -> list[str]:
    image = Image.open(source).convert("RGB")
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    gray = ImageOps.grayscale(image).resize((columns, rows), Image.Resampling.LANCZOS)
    gray = ImageOps.autocontrast(gray, cutoff=1)

    # Preserve facial and clothing detail while keeping the near-black studio
    # background empty. Edge energy adds definition without background removal.
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageEnhance.Contrast(edges).enhance(1.8)
    signal = ImageChops.lighter(gray, edges)

    output: list[str] = []
    for y in range(rows):
        chars: list[str] = []
        for x in range(columns):
            base = gray.getpixel((x, y))
            value = signal.getpixel((x, y))
            if base < 17 and value < 26:
                chars.append(" ")
                continue
            normalized = max(0.0, min(1.0, (value - 14) / 218))
            index = int(normalized * (len(RAMP) - 1))
            chars.append(RAMP[index])
        output.append("".join(chars).rstrip())
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = ascii_rows(args.input)
    width, height = 380, 410
    text_x = 24
    first_y = 77
    line_height = 6.65
    reveal_width = 334

    defs: list[str] = []
    body: list[str] = []
    for index, row in enumerate(rows):
        y = first_y + index * line_height
        begin = 0.35 + index * 0.055
        defs.append(
            f'<clipPath id="row-{index}"><rect x="{text_x}" y="{y - 6.2:.2f}" width="0" height="7.2">'
            f'<animate attributeName="width" from="0" to="{reveal_width}" begin="{begin:.3f}s" dur="0.20s" fill="freeze"/>'
            '</rect></clipPath>'
        )
        body.append(
            f'<text x="{text_x}" y="{y:.2f}" clip-path="url(#row-{index})" xml:space="preserve" '
            f'font-size="6.4" fill="#c9d1d9">{html.escape(row)}</text>'
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Animated ASCII portrait of Sai Navaneeth Thota</title>',
        '<desc id="desc">A monochrome portrait types itself row by row in a terminal window.</desc>',
        '<defs>',
        *defs,
        '</defs>',
        '<rect width="380" height="410" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '<circle cx="20" cy="20" r="5" fill="#ff5f57"/><circle cx="38" cy="20" r="5" fill="#febc2e"/><circle cx="56" cy="20" r="5" fill="#28c840"/>',
        '<text x="190" y="25" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" fill="#8b949e">portrait.svg</text>',
        '<text x="20" y="51" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" fill="#58a6ff">$ render --mode ascii --subject sai</text>',
        '<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        *body,
        '</g>',
        '<text x="20" y="397" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="9" fill="#3fb950" opacity="0">[ok] portrait rendered',
        '<animate attributeName="opacity" from="0" to="1" begin="3.2s" dur="0.3s" fill="freeze"/></text>',
        '</svg>',
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"Rendered {len(rows)} ASCII rows to {args.output}")


if __name__ == "__main__":
    main()
