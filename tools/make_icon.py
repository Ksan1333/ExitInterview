#!/usr/bin/env python3
"""Draws the app's logo (a door left ajar in the dim room) and writes every picture made from it.

    python3 tools/make_icon.py [--ksanhub DIR] [--preview FILE]

Writes the launcher icon layers under app/src/main/res/mipmap-*/ (the picture and the one-colour shape
that Android uses for themed icons). --ksanhub DIR also writes DIR/exitinterview.png, the 128 px
rounded icon that KsanHub's list shows. --preview FILE writes a sheet for looking at the result.
Needs Pillow and rsvg-convert. The drawing code is the one the stage pictures use.
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "spoiler", "art"))
import hand  # noqa: E402

S = 108  # an adaptive icon layer is 108 x 108 dp; launchers show the middle 72, and only the middle 66 is always safe
DENSITIES = {"xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}


def picture():
    """The whole logo, edge to edge. The door stays inside the middle 66 so that no launcher's mask cuts it."""
    s = hand.Scene(seed=7, sw=1.7, rough=0.45, passes=2)
    # room: wall, a pool of lamp light, floor
    s.solid(hand.rect_pts(-2, -2, S + 4, S + 4), hand.BG)
    for r in (48, 42, 36, 30, 24, 18):
        s.solid(hand.ell_pts(55, 52, r, r, 36), hand.LIGHT, 0.028)
    s.solid(hand.rect_pts(-2, 80, S + 4, 30), hand.FLOOR)
    s.line(-2, 80, S + 2, 80, sw=1.3)
    # the doorway, bright beyond, and the light it throws on the floor
    s.solid([(62, 84.5), (68.5, 80.5), (106, 100), (106, 110), (74, 110)], hand.LIGHT, 0.5)
    s.solid([(63, 84.5), (68.5, 81), (92, 110), (77, 110)], hand.LIGHT, 0.55)
    s.frect(38, 27, 34, 53, hand.WOOD_D)
    s.solid(hand.rect_pts(41.5, 30.5, 27, 49.5), "#fbeeb4")
    # the door itself, swung towards us
    leaf = [(41.5, 30.5), (61, 33.2), (61, 85), (41.5, 80)]
    s.solid(leaf, hand.WOOD)
    s.solid([(56.8, 32.6), (61, 33.2), (61, 85), (56.8, 83.9)], hand.WOOD_L, 0.9)
    s.poly(leaf, True)
    s.poly([(45, 57.2), (55.2, 58.1), (55.2, 78.9), (45, 76.6)], True, sw=0.9, opacity=0.75)
    s.fell(58.6, 58.6, 1.9, 2.1, hand.BRASS, sw=1.0)
    # the notice pinned to it
    s.fpoly([(45.5, 37), (55.4, 38.4), (55.4, 51), (45.5, 50)], hand.PAPER_L, sw=0.9)
    s.line(47.4, 41.6, 53.4, 42.4, sw=0.9)
    s.line(47.4, 44.6, 51.6, 45.2, sw=0.9)
    s.solid(hand.ell_pts(52.3, 47.9, 1.8, 1.8, 14), hand.RED_L)
    s.dot(50.5, 38.6, 0.8, hand.RED)
    return s.out


def shape():
    """The same door as one flat shape: Android tints it for themed icons, so only its outline matters."""
    white = "#ffffff"
    s = hand.Scene(seed=7, stroke=white, sw=2.6, rough=0.35, passes=2, opacity=1.0)
    s.rect(39, 28, 32, 52)
    leaf = [(41.5, 30.5), (61, 33.2), (61, 85), (41.5, 80)]
    s.solid(leaf, white)
    s.poly(leaf, True, sw=1.6)
    s.solid([(66, 83.5), (71, 82), (86, 96), (75, 96)], white, 0.85)
    cut = hand.Scene(seed=7)
    cut.solid(hand.ell_pts(58.4, 58.6, 2.2, 2.4, 16), "#000000")
    cut.solid([(45.5, 37), (55, 38.3), (55, 50.4), (45.5, 49.6)], "#000000")
    return s.out, cut.out


def render(elems, scale):
    return hand.render(elems, 0, 0, S, S, None, scale).convert("RGBA")


def monochrome(scale):
    solid, holes = shape()
    alpha = render(solid, scale).getchannel("A")
    alpha = ImageChops.subtract(alpha, render(holes, scale).getchannel("A"))
    out = Image.new("RGBA", alpha.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def rounded(size):
    """The middle of the picture with KsanHub's rounded corners (a launcher shows the middle 72 of 108; this is a little closer)."""
    k, shown = 8, 68.0
    big = render(picture(), size * k / shown)
    edge = round((S - shown) / 2 * size * k / shown)
    big = big.crop((edge, edge, edge + size * k, edge + size * k)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), radius=round(size * 4 * 0.22), fill=255)
    big.putalpha(mask.resize((size, size), Image.LANCZOS))
    return big


def main():
    args = sys.argv[1:]
    res = os.path.join(ROOT, "app", "src", "main", "res")
    for name, scale in DENSITIES.items():
        folder = os.path.join(res, "mipmap-" + name)
        os.makedirs(folder, exist_ok=True)
        render(picture(), scale).convert("RGB").save(os.path.join(folder, "ic_launcher_foreground.png"), optimize=True)
        monochrome(scale).save(os.path.join(folder, "ic_launcher_monochrome.png"), optimize=True)
    print("wrote launcher layers for " + ", ".join(DENSITIES))
    if "--ksanhub" in args:
        path = os.path.join(args[args.index("--ksanhub") + 1], "exitinterview.png")
        rounded(128).save(path, optimize=True)
        print("wrote " + path)
    if "--preview" in args:
        sheet = Image.new("RGB", (1180, 420), (242, 242, 247))
        sheet.paste(render(picture(), 3).convert("RGB"), (20, 48))
        big = rounded(288)
        sheet.paste(big, (364, 66), big)
        x = 680
        for size in (128, 96, 48):
            im = rounded(size)
            sheet.paste(im, (x, 210 - size // 2), im)
            x += size + 24
        dark = Image.new("RGB", (150, 150), (28, 28, 30))
        mono = monochrome(150 / 108.0)
        dark.paste((208, 228, 255), (0, 0), mono)
        sheet.paste(dark, (1010, 135))
        sheet.save(args[args.index("--preview") + 1])
        print("wrote the preview sheet")


if __name__ == "__main__":
    main()
