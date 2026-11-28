#!/usr/bin/env python3
"""Builds app/src/main/assets/stage2.pack (episode 2) from spoiler/ep2.

    python spoiler/build_pack2.py [--preview DIR] [--only stage1,testroom] [--out FILE]

Pictures are drawn with rsvg-convert where it is installed, else resvg (set EI_RESVG to its path). Episode 2 was made
with resvg, so only resvg rebuilds it byte for byte.
"""
import argparse
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ap = argparse.ArgumentParser()
ap.add_argument("--preview", help="also write plain PNG previews into this folder")
ap.add_argument("--only", help="comma separated stage modules (for quick drafts)")
ap.add_argument("--out", default=os.path.join(HERE, "..", "app", "src", "main", "assets", "stage2.pack"))
args = ap.parse_args()

from game import core  # noqa: E402
import ep2.story  # noqa: E402,F401

for mod in (args.only.split(",") if args.only else ["stage1", "stage2", "stage3", "testroom"]):
    importlib.import_module("ep2." + mod)
if args.preview:
    os.makedirs(args.preview, exist_ok=True)
if args.only:
    for vid in [s.get("start") for s in core.STAGES.values()]:
        if vid and vid not in core.VIEWS:
            core.View(vid, 0, "-")
core.build(os.path.abspath(args.out), args.preview)
