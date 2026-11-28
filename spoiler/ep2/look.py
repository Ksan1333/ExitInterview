"""Drawing helpers shared by the episode 2 stages."""
from game.core import *  # noqa: F401,F403

# warehouse
CONC, CONC_D, CONC_F = "#3f4b49", "#323d3b", "#4a4744"
CARD, CARD_D, TAPE = "#b08a5a", "#8e6c43", "#d8c08a"
# kitchen
TILE, TILE_D, TILE_L = "#4f6b63", "#3f5852", "#6d8a80"
FRIDGE, FRIDGE_D = "#d9d8cf", "#b9b8ae"
# office
OFFICE, OFFICE_D, OFFICE_L = "#5a3433", "#472a29", "#6e4544"
STEEL = "#8f9a9b"
WATER, WATER_D = "#6fb3d9", "#3f7ea3"
PURPLE, PURPLE_L = "#7b4a9a", "#a77cc4"
DUST = "#c9c6bb"
POTATO, POTATO_D = "#c8a66a", "#8a6a42"


def lamp(s, x, y0=0, y1=46, glow=True):
    """A hanging lamp with a warm glow."""
    s.line(x, y0, x, y1, sw=2.5)
    s.fpoly([(x - 24, y1), (x + 24, y1), (x + 38, y1 + 24), (x - 38, y1 + 24)], METAL)
    s.fell(x, y1 + 29, 9, 7, "#f6e7a6", sw=2)
    if glow:
        for rr, op in ((70, 0.09), (130, 0.06), (200, 0.04)):
            s.solid(ell_pts(x, y1 + 40, rr, rr * 0.85, 32), LIGHT, op)


def warehouse(s, lamp_x=480):
    """Concrete walls and floor."""
    s.room(wall=CONC, floor_y=410, floor=CONC_F, wain=CONC_D, wain_h=60, planks=False)
    for x in range(0, W + 1, 160):
        s.line(x, 0, x, 348, sw=1.2, opacity=0.3, passes=1)
    for y in (116, 232):
        s.line(0, y, W, y, sw=1.2, opacity=0.25, passes=1)
    for x in range(80, W, 200):
        s.line(x, 413, W / 2 + (x - W / 2) * 1.5, H, sw=1.5, opacity=0.3, passes=1)
    s.line(0, 470, W, 470, sw=1.4, opacity=0.25, passes=1)
    if lamp_x is not None:
        lamp(s, lamp_x)


def kitchen(s, lamp_x=480, counter=True):
    """Tiled kitchen wall with a counter top along it."""
    s.room(wall=TILE, floor_y=420, floor="#6b5a48", wain=None, planks=False)
    for y in range(40, 420, 40):
        s.line(0, y, W, y, sw=1.2, stroke=TILE_D, opacity=0.6, passes=1)
    for row, y in enumerate(range(0, 420, 40)):
        off = 0 if row % 2 == 0 else 30
        for x in range(off, W, 60):
            s.line(x, y, x, y + 40, sw=1.0, stroke=TILE_D, opacity=0.5, passes=1)
    for x in range(0, W, 120):
        s.line(x, 422, x + 60, H, sw=1.4, opacity=0.25, passes=1)
    if counter:
        s.frect(0, 300, W, 22, "#b9a27a", sw=2.4)
        s.frect(0, 322, W, 98, WOOD, sw=2.4)
        for x in range(0, W, 160):
            s.frect(x + 10, 332, 140, 80, WOOD_D, sw=2)
            s.fell(x + 80, 344, 12, 4, BRASS, sw=1.6)
    if lamp_x is not None:
        lamp(s, lamp_x)


def office(s, lamp_x=480):
    """Striped wallpaper, wainscot and a carpet."""
    s.room(wall=OFFICE, floor_y=410, floor="#3a2e2a", wain=OFFICE_D, wain_h=90, planks=False)
    for x in range(20, W, 40):
        s.line(x, 0, x, 318, sw=6, stroke=OFFICE_L, opacity=0.25, passes=1)
    s.line(0, 322, W, 322, sw=2.2)
    s.solid([(120, 430), (840, 430), (900, 540), (60, 540)], "#5b2f2c", 0.9)
    s.poly([(120, 430), (840, 430), (900, 540), (60, 540)], True)
    if lamp_x is not None:
        lamp(s, lamp_x)


def box(s, x, y, w, h, color=CARD, tape=True):
    """A cardboard box seen from the front."""
    s.frect(x, y, w, h, color, sw=2.4)
    s.fpoly([(x, y), (x + w, y), (x + w - 8, y - 10), (x + 8, y - 10)], CARD_D, sw=2)
    if tape:
        s.frect(x + w / 2 - 8, y - 10, 16, h * 0.45 + 10, TAPE, sw=1.4, op=0.95)


def clock(s, cx, cy, r, hh, mm, face=PAPER_L, rim=METAL_D):
    """A wall clock showing hh:mm."""
    s.fell(cx, cy, r + 6, r + 6, rim, sw=2.6)
    s.fell(cx, cy, r, r, face, sw=2.2)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r1 = r * (0.78 if k % 3 else 0.68)
        s.line(cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9,
               sw=2.2 if k % 3 == 0 else 1.4, passes=1)
    am = math.radians(mm * 6 - 90)
    ah = math.radians((hh % 12) * 30 + mm * 0.5 - 90)
    s.line(cx, cy, cx + math.cos(ah) * r * 0.5, cy + math.sin(ah) * r * 0.5, sw=4.5)
    s.line(cx, cy, cx + math.cos(am) * r * 0.78, cy + math.sin(am) * r * 0.78, sw=3)
    s.dot(cx, cy, 4)


def label_pic(s, kind, cx, cy, k=1.0):
    """The pictures on the parcel labels: cat, fish, flower, book."""
    if kind == "cat":
        s.fpoly([(cx - 15 * k, cy - 6 * k), (cx - 12 * k, cy - 22 * k), (cx - 3 * k, cy - 11 * k)], "#8a8a8a", sw=1.8)
        s.fpoly([(cx + 15 * k, cy - 6 * k), (cx + 12 * k, cy - 22 * k), (cx + 3 * k, cy - 11 * k)], "#8a8a8a", sw=1.8)
        s.fell(cx, cy, 16 * k, 13 * k, "#8a8a8a", sw=2)
        s.dot(cx - 6 * k, cy - 2 * k, 2.2 * k)
        s.dot(cx + 6 * k, cy - 2 * k, 2.2 * k)
        s.dot(cx, cy + 4 * k, 1.8 * k, PINK)
        for d in (-1, 1):
            s.line(cx + d * 8 * k, cy + 5 * k, cx + d * 22 * k, cy + 2 * k, sw=1.2, passes=1)
            s.line(cx + d * 8 * k, cy + 7 * k, cx + d * 22 * k, cy + 9 * k, sw=1.2, passes=1)
    elif kind == "fish":
        s.fpoly([(cx + 10 * k, cy), (cx + 24 * k, cy - 11 * k), (cx + 24 * k, cy + 11 * k)], BLUE_L, sw=1.8)
        s.fell(cx - 4 * k, cy, 18 * k, 10 * k, BLUE_L, sw=2)
        s.dot(cx - 13 * k, cy - 2 * k, 2.2 * k)
        s.curve([(cx - 2 * k, cy - 7 * k), (cx + 2 * k, cy), (cx - 2 * k, cy + 7 * k)], sw=1.4, passes=1)
    elif kind == "flower":
        for i in range(5):
            a = math.radians(i * 72 - 90)
            s.fell(cx + math.cos(a) * 10 * k, cy + math.sin(a) * 10 * k, 8 * k, 8 * k, PINK, sw=1.6)
        s.fell(cx, cy, 6 * k, 6 * k, LIGHT, sw=1.6)
        s.line(cx, cy + 14 * k, cx, cy + 26 * k, stroke=GREEN, sw=2.4, passes=1)
    else:  # book
        s.fpoly([(cx - 20 * k, cy - 14 * k), (cx, cy - 10 * k), (cx, cy + 16 * k), (cx - 20 * k, cy + 12 * k)], RED_L, sw=1.8)
        s.fpoly([(cx + 20 * k, cy - 14 * k), (cx, cy - 10 * k), (cx, cy + 16 * k), (cx + 20 * k, cy + 12 * k)], RED_L, sw=1.8)
        for d in (-1, 1):
            for j in range(3):
                s.line(cx + d * 4 * k, cy - 4 * k + j * 6 * k, cx + d * 15 * k, cy - 6 * k + j * 6 * k, sw=1.0, passes=1)


def parcel(s, x, y, w, h, kind):
    """A parcel with a picture label (bottom edge at y + h)."""
    box(s, x, y, w, h)
    lw, lh = w * 0.46, h * 0.52
    s.frect(x + w * 0.27 - lw / 2 + w * 0.02, y + h * 0.42 - lh / 2, lw, lh, PAPER_L, sw=1.8)
    label_pic(s, kind, x + w * 0.29, y + h * 0.42, min(lw / 50.0, lh / 44.0))


def key_icon(s, cx, cy, k=1.0, color=BRASS):
    s.fell(cx - 22 * k, cy, 13 * k, 13 * k, color, sw=2.4)
    s.fell(cx - 22 * k, cy, 5 * k, 5 * k, "#2a2a2a", sw=1.6)
    s.frect(cx - 10 * k, cy - 4 * k, 40 * k, 8 * k, color, sw=2)
    s.frect(cx + 18 * k, cy + 4 * k, 6 * k, 9 * k, color, sw=1.6)
    s.frect(cx + 26 * k, cy + 4 * k, 5 * k, 6 * k, color, sw=1.6)


def button_label(s, x, y, w, h, text, size=20, color=PAPER_L):
    """A flat button with a word on it."""
    s.frect(x, y, w, h, color, sw=2.4)
    s.text(x + w / 2, y + h / 2, text, size)


def mirror_g(s, cx):
    """Starts a group drawn mirrored around x = cx; close it with s.raw('</g>')."""
    s.raw('<g transform="translate(%s 0) scale(-1 1)">' % f(2 * cx))


def ne(flag, v):
    return ["ne", flag, v]


def any_(*c):
    return ["any"] + list(c)


def tiles_in(s, x, y, w, h):
    """Kitchen wall tiles inside one box (to paint over something that has gone)."""
    s.frect(x, y, w, h, TILE, outline=False)
    for ty in range(40, 420, 40):
        if y < ty < y + h:
            s.line(x, ty, x + w, ty, sw=1.2, stroke=TILE_D, opacity=0.6, passes=1)
    for row, ty in enumerate(range(0, 420, 40)):
        off = 0 if row % 2 == 0 else 30
        for tx in range(off, W, 60):
            if x < tx < x + w and ty + 40 > y and ty < y + h:
                s.line(tx, max(ty, y), tx, min(ty + 40, y + h), sw=1.0, stroke=TILE_D, opacity=0.5, passes=1)


def darkness(s, alpha=0.88):
    s.frect(0, 0, W, H, "#04060a", op=alpha, outline=False)


def glow_mark(s, cx, cy, k=1.0):
    """A glow-in-the-dark sticker shaped like a potato."""
    s.glow(cx, cy, 26 * k, "#a8ffb8", 0.16, 4)
    s.fell(cx, cy, 9 * k, 7 * k, "#c8ffd2", outline=False)
    s.dot(cx - 3 * k, cy - 1 * k, 1.4 * k, "#5fbf74")
    s.dot(cx + 3 * k, cy + 2 * k, 1.4 * k, "#5fbf74")


def key_part(s, cx, cy, k=1.0, part="all", color=METAL):
    """A key, or only its bow (top) or its blade (bottom)."""
    if part in ("all", "top"):
        s.fell(cx - 22 * k, cy, 13 * k, 13 * k, color, sw=2.4)
        s.fell(cx - 22 * k, cy, 5 * k, 5 * k, "#2a2a2a", sw=1.6)
        s.frect(cx - 10 * k, cy - 4 * k, 12 * k if part == "top" else 40 * k, 8 * k, color, sw=2)
    if part == "bottom":
        s.frect(cx - 10 * k, cy - 4 * k, 40 * k, 8 * k, color, sw=2)
    if part in ("all", "bottom"):
        s.frect(cx + 18 * k, cy + 4 * k, 6 * k, 9 * k, color, sw=1.6)
        s.frect(cx + 26 * k, cy + 4 * k, 5 * k, 6 * k, color, sw=1.6)
