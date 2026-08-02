#!/usr/bin/env python
"""Fast local checks for generated profile artifacts."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_FILES = [
    ROOT / "assets" / "ascii-portrait.svg",
    ROOT / "assets" / "info-card.svg",
    ROOT / "assets" / "contribution-heatmap.svg",
]


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for svg in SVG_FILES:
        ET.parse(svg)
        relative = svg.relative_to(ROOT).as_posix()
        if relative not in readme:
            raise AssertionError(f"README does not reference {relative}")
        text = svg.read_text(encoding="utf-8")
        check_text = text.lower().replace("http://www.w3.org/2000/svg", "")
        if "<script" in check_text or "http://" in check_text or "https://" in check_text:
            raise AssertionError(f"Generated SVG is not self-contained: {svg}")

    payload = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    if payload["username"] != "navaneeth9908":
        raise AssertionError("Contribution data belongs to the wrong account")
    if len(payload["days"]) < 350:
        raise AssertionError("Contribution data is incomplete")
    if int(payload["stats"]["total"]) != sum(int(day["count"]) for day in payload["days"]):
        raise AssertionError("Contribution total does not match daily counts")

    workflow = ROOT / ".github" / "workflows" / "update-contributions.yml"
    if not workflow.exists():
        raise AssertionError("Daily refresh workflow is missing")
    print(f"Validated {len(SVG_FILES)} SVGs, {len(payload['days'])} contribution days, README references, and workflow")


if __name__ == "__main__":
    main()
