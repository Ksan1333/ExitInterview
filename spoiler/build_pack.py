#!/usr/bin/env python3
"""Builds app/src/main/assets/stage.pack from the stage sources in this folder.

    python3 spoiler/build_pack.py [--preview DIR] [--only stage1,testroom]
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
ap.add_argument("--out", default=os.path.join(HERE, "..", "app", "src", "main", "assets", "stage.pack"))
args = ap.parse_args()

from game import core  # noqa: E402
import game.story  # noqa: E402,F401

for mod in (args.only.split(",") if args.only else ["stage1", "stage2", "stage3", "testroom"]):
    importlib.import_module("game." + mod)
if args.preview:
    os.makedirs(args.preview, exist_ok=True)
if args.only:
    for vid in [s.get("start") for s in core.STAGES.values()]:
        if vid and vid not in core.VIEWS:
            core.View(vid, 0, "-")
core.build(os.path.abspath(args.out), args.preview)
