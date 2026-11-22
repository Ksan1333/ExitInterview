"""Stage 3."""
import math

from game.core import *  # noqa: F401,F403
from game.stage2 import key_shape

WALL3, TATAMI, TATAMI_L = "#4f5a48", "#6b6a3e", "#8a8650"
SPACE = "#0b1020"
ALIEN = "#7fd07a"
PANEL = "#2b2f33"


def washitsu(s, floor_y=400):
    s.room(wall=WALL3, floor_y=floor_y, floor=TATAMI, wain=None, planks=False)
    s.frect(0, 40, W, 12, WOOD_D, sw=2)
    if floor_y < H - 20:
        s.line(0, floor_y + 70, W, floor_y + 70, sw=2, opacity=0.45, passes=1)
        for x in (120, 480, 840):
            s.line(x, floor_y + 2, W / 2 + (x - W / 2) * 1.5, H, sw=2, opacity=0.45, passes=1)


def alien(s, cx, cy, pose, k=1.0):
    """pose: 0 holds a start sign, 1 both arms up, 2 one arm up, 3 bows, 4 stands on one leg."""
    lw = 5.5 * k

    def limb(pts):
        s.curve(pts, stroke=INK, sw=lw + 3, passes=1, rough=0.4)
        s.curve(pts, stroke=ALIEN, sw=lw, passes=1, rough=0.4)

    hip_y = cy + 24 * k
    if pose == 4:
        limb([(cx - 6 * k, hip_y), (cx - 6 * k, hip_y + 30 * k)])
        limb([(cx + 8 * k, hip_y), (cx + 26 * k, hip_y + 8 * k), (cx + 12 * k, hip_y + 20 * k)])
    else:
        limb([(cx - 8 * k, hip_y), (cx - 10 * k, hip_y + 30 * k)])
        limb([(cx + 8 * k, hip_y), (cx + 10 * k, hip_y + 30 * k)])
    if pose == 3:
        s.raw('<g transform="rotate(62 %s %s)">' % (f(cx), f(hip_y)))
    sh_y = cy - 2 * k
    if pose == 1:
        limb([(cx - 18 * k, sh_y), (cx - 30 * k, cy - 34 * k)])
        limb([(cx + 18 * k, sh_y), (cx + 30 * k, cy - 34 * k)])
    elif pose == 2:
        limb([(cx - 18 * k, sh_y), (cx - 28 * k, cy + 22 * k)])
        limb([(cx + 18 * k, sh_y), (cx + 30 * k, cy - 34 * k)])
    elif pose == 4:
        limb([(cx - 18 * k, sh_y), (cx - 40 * k, sh_y - 2 * k)])
        limb([(cx + 18 * k, sh_y), (cx + 40 * k, sh_y - 2 * k)])
    else:
        limb([(cx - 18 * k, sh_y), (cx - 26 * k, cy + 20 * k)])
        limb([(cx + 18 * k, sh_y), (cx + 26 * k, cy + 20 * k)])
    s.fell(cx, cy, 20 * k, 27 * k, ALIEN, sw=2.6)
    s.line(cx, cy - 26 * k, cx, cy - 38 * k, sw=2.2, passes=1)
    s.dot(cx, cy - 40 * k, 3.5 * k, ALIEN)
    for sx in (-1, 1):
        s.fell(cx + sx * 8 * k, cy - 8 * k, 6.5 * k, 8 * k, WHITE, sw=1.8)
        s.dot(cx + sx * 8 * k, cy - 7 * k, 2.6 * k)
    s.curve([(cx - 5 * k, cy + 8 * k), (cx, cy + 11 * k), (cx + 5 * k, cy + 8 * k)], sw=1.8, passes=1)
    if pose == 3:
        s.raw("</g>")
    if pose == 0:
        s.frect(cx - 38 * k, cy + 2 * k, 76 * k, 30 * k, PAPER_L, sw=2.2)
        s.text(cx, cy + 17 * k, "はじめ", 19 * k)


def fish(s, cx, cy, k=1.0):
    s.fpoly([(cx - 20 * k, cy), (cx - 36 * k, cy - 13 * k), (cx - 32 * k, cy), (cx - 36 * k, cy + 13 * k)], "#e8693a", sw=2.2)
    s.fell(cx, cy, 22 * k, 14 * k, "#f0803a", sw=2.6)
    s.fpoly([(cx - 4 * k, cy - 13 * k), (cx + 6 * k, cy - 24 * k), (cx + 10 * k, cy - 12 * k)], "#e8693a", sw=2)
    s.fell(cx + 11 * k, cy - 3 * k, 4.5 * k, 4.5 * k, WHITE, sw=1.6)
    s.dot(cx + 12 * k, cy - 3 * k, 2 * k)


def mikan(s, cx, cy, r=16):
    s.fell(cx, cy, r, r * 0.92, ORANGE, sw=2.4)
    s.fpoly([(cx - 1, cy - r * 0.9), (cx + r * 0.55, cy - r * 1.35), (cx + r * 0.25, cy - r * 0.8)], GREEN, sw=1.8)
    s.dot(cx - r * 0.35, cy - r * 0.25, 1.6, "#f4c07a")


def daruma(s, cx, cy, k=1.0):
    s.fell(cx, cy, 38 * k, 42 * k, RED_L, sw=3)
    s.fell(cx, cy - 8 * k, 24 * k, 19 * k, PAPER_L, sw=2.2)
    for sx in (-1, 1):
        s.fell(cx + sx * 10 * k, cy - 9 * k, 6 * k, 6 * k, WHITE, sw=1.8)
        s.dot(cx + sx * 10 * k, cy - 9 * k, 2.4 * k)
        s.line(cx + sx * 4 * k, cy - 20 * k, cx + sx * 18 * k, cy - 22 * k, sw=2.6, passes=1)
    s.curve([(cx - 9 * k, cy + 4 * k), (cx, cy + 1 * k), (cx + 9 * k, cy + 4 * k)], sw=2.2, passes=1)
    s.curve([(cx - 14 * k, cy + 24 * k), (cx, cy + 30 * k), (cx + 14 * k, cy + 24 * k)], stroke=BRASS, sw=3, passes=1)


def neko(s, cx, cy, k=1.0):
    s.fell(cx, cy + 14 * k, 30 * k, 30 * k, WHITE, sw=2.8)
    s.fpoly([(cx - 22 * k, cy - 30 * k), (cx - 16 * k, cy - 50 * k), (cx - 4 * k, cy - 36 * k)], WHITE, sw=2.2)
    s.fpoly([(cx + 22 * k, cy - 30 * k), (cx + 16 * k, cy - 50 * k), (cx + 4 * k, cy - 36 * k)], WHITE, sw=2.2)
    s.fell(cx, cy - 20 * k, 26 * k, 22 * k, WHITE, sw=2.8)
    s.fell(cx + 28 * k, cy - 34 * k, 9 * k, 11 * k, WHITE, sw=2.4)
    s.line(cx + 26 * k, cy - 24 * k, cx + 24 * k, cy - 6 * k, sw=2.4, passes=1)
    for sx in (-1, 1):
        s.dot(cx + sx * 9 * k, cy - 22 * k, 2.6 * k)
    s.curve([(cx - 5 * k, cy - 13 * k), (cx, cy - 10 * k), (cx + 5 * k, cy - 13 * k)], sw=1.8, passes=1)
    s.line(cx - 16 * k, cy - 2 * k, cx + 16 * k, cy - 2 * k, stroke=RED_L, sw=4 * k, passes=1)
    s.fell(cx - 4 * k, cy + 20 * k, 11 * k, 15 * k, BRASS, sw=2.2)


def kyusu(s, cx, cy, k=1.0):
    s.fpoly([(cx + 30 * k, cy + 2 * k), (cx + 58 * k, cy - 14 * k), (cx + 60 * k, cy - 6 * k), (cx + 34 * k, cy + 14 * k)], GREEN, sw=2.4)
    s.curve([(cx - 34 * k, cy - 2 * k), (cx - 62 * k, cy - 8 * k), (cx - 58 * k, cy + 18 * k), (cx - 30 * k, cy + 20 * k)], sw=5 * k, stroke="#3f6a3a", passes=1)
    s.fell(cx, cy + 8 * k, 38 * k, 28 * k, GREEN, sw=3)
    s.fell(cx, cy - 18 * k, 20 * k, 6 * k, "#4f7a40", sw=2.2)
    s.fell(cx, cy - 26 * k, 5 * k, 5 * k, "#3f6a3a", sw=2)


def kokeshi(s, cx, cy, k=1.0):
    s.frect(cx - 17 * k, cy - 8 * k, 34 * k, 50 * k, "#d9b98a", sw=2.8)
    for dy in (6, 20):
        s.line(cx - 16 * k, cy + dy * k, cx + 16 * k, cy + dy * k, stroke=RED_L, sw=4 * k, passes=1)
    s.fell(cx, cy - 28 * k, 23 * k, 21 * k, "#f0dcc0", sw=2.8)
    s.curve([(cx - 22 * k, cy - 34 * k), (cx, cy - 52 * k), (cx + 22 * k, cy - 34 * k)], stroke=BLACK, sw=7 * k, passes=1)
    for sx in (-1, 1):
        s.line(cx + sx * 12 * k, cy - 26 * k, cx + sx * 5 * k, cy - 26 * k, sw=2, passes=1)
    s.dot(cx, cy - 18 * k, 2 * k, RED_L)


def grip_shape(s, cx, cy, k=1.0):
    s.frect(cx - 5 * k, cy, 10 * k, 22 * k, METAL, sw=2.2)
    s.fell(cx, cy - 6 * k, 13 * k, 13 * k, RED_L, sw=2.8)


# ------------------------------------------------------------------ front: windows and cabinet
v = View("s3v1", 3, "まどの かべ", l="s3v2", r="s3v3")
s = v.s
washitsu(s)
s.fell(220, 190, 132, 132, WOOD_D)
s.fell(220, 190, 122, 122, SPACE, sw=2.6)
half = math.sqrt(122 ** 2 - 40 ** 2)
for x in (180, 260):
    s.line(x, 190 - half, x, 190 + half, stroke=WOOD_D, sw=7, rough=0.5)
for y in (150, 230):
    s.line(220 - half, y, 220 + half, y, stroke=WOOD_D, sw=7, rough=0.5)
CELL = {n: (140 + ((n - 1) % 3) * 80, 110 + ((n - 1) // 3) * 80) for n in range(1, 10)}
for n in (1, 2, 4, 6, 9):
    cx, cy = CELL[n]
    s.glow(cx, cy, 24, LIGHT, 0.07)
    s.solid(star_pts(cx, cy, 13), LIGHT)
s.frect(372, 64, 142, 164, WOOD_D)
s.frect(382, 74, 122, 144, SPACE, sw=2.4)
# hanging scroll
s.frect(532, 52, 136, 12, WOOD_D, sw=2)
s.frect(540, 64, 120, 180, PAPER, sw=2.4)
s.frect(532, 244, 136, 12, WOOD_D, sw=2)
for i in range(4):
    alien(s, 566, 90 + i * 42, i + 1, 0.34)
    s.line(588, 90 + i * 42, 648, 90 + i * 42, sw=1.6, opacity=0.6, passes=1)
# cabinet
s.frect(364, 270, 452, 12, WOOD_L)
s.frect(372, 282, 440, 118, WOOD)
LAMP = {n: (396 + ((n - 1) % 3) * 38, 304 + ((n - 1) // 3) * 38) for n in range(1, 10)}
s.frect(374, 284, 120, 116, PANEL, sw=2.4)
for n in range(1, 10):
    s.fell(LAMP[n][0], LAMP[n][1], 13, 13, "#454d50", sw=2)
s.paper(506, 290, 124, 46, ["そとから 見た", "ほしを うつせ"], 13.5, pad=8, pin=False)
s.fell(540, 372, 15, 15, BRASS, sw=2.6)
s.line(532, 372, 548, 372, sw=2, passes=1)
s.frect(650, 312, 112, 62, WOOD_D, sw=2.4)
s.fell(706, 343, 7, 7, BRASS, sw=2)


def bowl(s, with_fish=False, with_grip=False):
    s.fell(750, 246, 40, 28, "#5f93aa", sw=2.8, op=0.9)
    s.fell(750, 226, 26, 7, "#8fc0d0", sw=2.2)
    if with_fish:
        fish(s, 744, 252, 0.62)
    if with_grip:
        grip_shape(s, 768, 224, 0.9)


bowl(s)
s.vignette()

for n in range(1, 10):
    cx, cy = LAMP[n]
    v.variant("lamp%d" % n, (cx - 18, cy - 18, 36, 36), eq("s3_l%d" % n, 1),
              lambda s, cx=cx, cy=cy: (s.glow(cx, cy, 20, LIGHT, 0.12), s.fell(cx, cy, 13, 13, LIGHT, sw=2)))
    v.spot((cx - 19, cy - 19, 38, 38), [["cyc", "s3_l%d" % n, 2], ["sfx", "tick"]], eq("s3_stars", 0))
RIGHT = all_(*[eq("s3_l%d" % n, 1 if n in (2, 3, 4, 6, 7) else 0) for n in range(1, 10)])
v.spot((516, 348, 48, 48), [["if", RIGHT, [["set", "s3_stars", 1], ["give", "food"], ["sfx", "ok"]],
                            [["set", "s3_l%d" % n, 0] for n in range(1, 10)] + [["sfx", "buzz"], ["shake"]]]], eq("s3_stars", 0))
v.variant("drawer3", (638, 304, 138, 96), eq("s3_stars", 1), lambda s: (
    s.frect(650, 312, 112, 62, "#1b1512", sw=2.4), s.fpoly([(644, 358), (768, 358), (774, 396), (638, 396)], WOOD_D, sw=2.4),
    s.fell(706, 378, 7, 6, BRASS, sw=2)))
for i in range(5):
    v.variant("al%d" % i, (378, 70, 130, 152), None, lambda s, i=i: (s.frect(382, 74, 122, 144, SPACE, sw=2.4), alien(s, 443, 142, i, 1.05)), layer=False)
v.anim(["al%d" % i for i in range(5)], (378, 70, 130, 152), eq("s3_stars", 1), 2000)
GRIP_IN = all_(eq("s3_fish", 1), eq("s3_grip", 0))
v.variant("bowl_grip", (704, 196, 92, 82), GRIP_IN, lambda s: bowl(s, True, True))
v.variant("bowl_fish", (704, 196, 92, 82), all_(eq("s3_fish", 1), eq("s3_grip", 1)), lambda s: bowl(s, True, False))
v.spot((700, 192, 100, 88), [["give", "grip"], ["set", "s3_grip", 1], ["sfx", "get"]], GRIP_IN)
v.spot((532, 52, 136, 204), [["go", "s3scroll"], ["sfx", "tick"]])

# ------------------------------------------------------------------ scroll close-up
v = View("s3scroll", 3, "かけじく", back="s3v1")
s = v.s
washitsu(s, 530)
s.frect(176, 22, 608, 16, WOOD_D)
s.frect(190, 38, 580, 464, PAPER)
s.frect(176, 502, 608, 16, WOOD_D)
LEGEND = ["いちばん たかい もの", "いちばん やすい もの", "2ばんめに たかい もの", "のこり"]
for i, t in enumerate(LEGEND):
    y = 96 + i * 112
    alien(s, 286, y - 4, i + 1, 1.0)
    s.text(366, y, "＝", 28)
    s.text(400, y, t, 26, anchor="start")
s.vignette()

# ------------------------------------------------------------------ left: shelf, lever, mikan box
v = View("s3v2", 3, "たなの かべ", r="s3v1")
s = v.s
washitsu(s)
s.frect(110, 176, 320, 12, WOOD_L)
s.frect(290, 256, 320, 12, WOOD_L)
s.frect(110, 100, 12, 168, WOOD_D, sw=2)
s.frect(598, 100, 12, 168, WOOD_D, sw=2)
daruma(s, 180, 140, 0.7)
neko(s, 340, 144, 0.7)
kyusu(s, 400, 232, 0.6)
kokeshi(s, 530, 228, 0.7)
for x, y in ((180, 172), (340, 172), (400, 252), (530, 252)):
    s.frect(x + 24, y - 16, 22, 14, PAPER_L, sw=1.6)
s.frect(660, 52, 50, 348, WOOD_D)
s.frect(668, 206, 34, 34, METAL, sw=2.4)
s.fell(685, 223, 6, 6, BLACK, sw=1.8)
s.paper(718, 146, 98, 58, ["じゅうりょく", "オン／オフ"], 13, pad=8)
s.frect(150, 420, 230, 86, "#a8834a")
s.text(265, 468, "みかん", 24)
s.vignette()


def lever(s, on):
    s.frect(668, 206, 34, 34, METAL, sw=2.4)
    ey = 182 if on else 264
    s.line(685, 223, 706, ey, stroke=INK, sw=10, passes=1, rough=0.4)
    s.line(685, 223, 706, ey, stroke=METAL, sw=6, passes=1, rough=0.4)
    s.fell(708, ey + (-4 if on else 4), 11, 11, RED_L, sw=2.6)
    s.fell(685, 223, 6, 6, BLACK, sw=1.8)


v.variant("lever_on", (660, 164, 64, 118), all_(eq("s3_lever", 1), eq("s3_goff", 0)), lambda s: lever(s, True))
v.variant("lever_off", (660, 164, 64, 118), all_(eq("s3_lever", 1), eq("s3_goff", 1)), lambda s: lever(s, False))
v.spot((648, 160, 80, 126), [["take", "grip"], ["set", "s3_lever", 1], ["sfx", "ok"], ["unsel"]], all_(["sel", "grip"], eq("s3_lever", 0)))
v.spot((648, 160, 80, 126), [["cyc", "s3_goff", 2], ["sfx", "lever"]], all_(eq("s3_lever", 1), eq("s3_fuel", 0)))
v.spot((104, 76, 512, 196), [["go", "s3shelf"], ["sfx", "tick"]])


def mikan_spots(v, n, gx, gy, fx, fy):
    """One mikan: on the ground while gravity is on, floating out of reach while it is off."""
    here = eq("s3_m%d" % n, 0)
    v.variant("mk%d" % n, (gx - 20, gy - 24, 40, 44), all_(here, eq("s3_goff", 0)), lambda s: mikan(s, gx, gy))
    v.variant("mf%d" % n, (fx - 20, fy - 24, 40, 44), all_(here, eq("s3_goff", 1)), lambda s: mikan(s, fx, fy))
    v.spot((gx - 22, gy - 24, 44, 46), [["give", "mikan"], ["set", "s3_m%d" % n, 1], ["sfx", "get"]], all_(here, eq("s3_goff", 0)))
    v.spot((fx - 22, fy - 24, 44, 46), [["sfx", "boing"]], all_(here, eq("s3_goff", 1)))


for i in range(4):
    mikan_spots(v, i + 1, 190 + i * 50, 412, 200 + i * 52, 330 - (i % 2) * 30)

# ------------------------------------------------------------------ shelf close-up
v = View("s3shelf", 3, "ちがいだな", back="s3v2")
s = v.s
washitsu(s, 530)
s.frect(70, 292, 790, 16, WOOD_L)
OX = [170, 360, 550, 740]
daruma(s, OX[0], 226, 1.45)
neko(s, OX[1], 232, 1.45)
kyusu(s, OX[2], 238, 1.3)
kokeshi(s, OX[3], 228, 1.45)
TAGS = [["800えん"], ["だるまの 2ばい", "より 100えん", "やすい"], ["300えん"], ["きゅうすの", "4ばい"]]
for x, lines in zip(OX, TAGS):
    s.paper(x - 76, 330, 152, 30 + 22 * len(lines), lines, 15.5, pad=9)
QX = [400, 440, 480, 520]
for x in QX:
    s.fell(x, 76, 7, 7, "#3a4034", sw=1.8)
s.vignette()
seq_dots(v, "q4", 4, QX, 76)
for i, x in enumerate(OX):
    v.spot((x - 82, 130, 164, 170),
           [["sfx", "tick"], ["seq", "q4", i, 4, [1, 2, 3, 0], [["set", "s3_daruma", 1], ["give", "ekey"], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]],
           all_(eq("s3_stars", 1), eq("s3_daruma", 0)))


def daruma_open(s):
    s.solid(rect_pts(96, 140, 150, 150), WALL3)
    s.fpoly([(112, 286), (118, 226), (150, 206), (160, 232), (150, 286)], RED_L, sw=3)
    s.fpoly([(196, 286), (184, 236), (196, 208), (230, 226), (236, 286)], RED_L, sw=3)
    s.fpoly([(150, 206), (160, 232), (152, 250)], PAPER_L, sw=2)
    for a, b in ((170, 176), (160, 186), (182, 188)):
        s.line(172, 220, a, b, sw=2, passes=1)


v.variant("daruma_open", (92, 136, 158, 156), eq("s3_daruma", 1), daruma_open)

# ------------------------------------------------------------------ right: kotatsu
v = View("s3v3", 3, "こたつの かべ", l="s3v1")
s = v.s
washitsu(s)
s.fpoly([(230, 0), (790, 0), (740, 38), (280, 38)], "#6a5a40", sw=2.4)
for i in range(1, 6):
    s.line(230 + i * 93, 2, 280 + i * 77, 36, sw=1.4, opacity=0.6, passes=1)
s.line(256, 19, 765, 19, sw=1.4, opacity=0.6, passes=1)
s.paper(84, 70, 204, 40, [("この きんぎょ、へそまがり", 14.5)], pad=9)
s.fpoly([(140, 470), (250, 462), (268, 500), (132, 508)], "#5a4a78")
s.fpoly([(650, 462), (760, 470), (772, 508), (636, 500)], "#5a4a78")


def kotatsu(s, dy=0, full=False):
    s.fpoly([(310, 324 + dy), (590, 324 + dy), (612, 424 + dy), (288, 424 + dy)], "#7a3b3b")
    for x in (360, 420, 480, 540):
        s.line(x, 330 + dy, x + (x - 450) * 0.12, 420 + dy, stroke="#a85a4a", sw=3, passes=1)
    s.frect(298, 300 + dy, 304, 24, WOOD_L)
    s.frect(410, 292 + dy, 80, 10, BRASS, sw=2.2)
    s.dot(450, 297 + dy, 2.4)
    s.frect(536, 304 + dy, 48, 16, PAPER_L, sw=1.8)
    s.line(560, 318 + dy, 574 if full else 546, 307 + dy, stroke=RED_L, sw=2.4, passes=1)
    if dy:
        s.fpoly([(288, 424 + dy), (612, 424 + dy), (596, 446 + dy), (304, 446 + dy)], "#0a0d0e", sw=2.4)


kotatsu(s)
s.vignette()


def float_up(s):
    s.solid(rect_pts(270, 170, 360, 230), WALL3)
    s.solid(rect_pts(270, 400, 360, 44), TATAMI)
    s.line(270, 400, 630, 400)
    s.solid(ell_pts(450, 424, 150, 12), "#000000", 0.28)
    kotatsu(s, -112)


v.variant("float", (270, 170, 360, 274), eq("s3_goff", 1), float_up)
v.variant("gauge", (530, 298, 60, 28), eq("s3_fuel", 1), lambda s: (
    s.frect(536, 304, 48, 16, PAPER_L, sw=1.8), s.line(560, 318, 574, 307, stroke=RED_L, sw=2.4, passes=1), s.dot(580, 301, 3, "#7fe08a")))
for i, (gx, fx, fy) in enumerate(((332, 330, 150), (364, 380, 120), (512, 540, 140))):
    mikan_spots(v, i + 5, gx, 286, fx, fy)
FISH_AIR = eq("s3_fish_ready", 0)
FISH_DOWN = all_(eq("s3_fish_ready", 1), eq("s3_fish", 0))
v.variant("fish_air", (150, 126, 124, 104), FISH_AIR, lambda s: (
    fish(s, 214, 182, 1.25), s.ellipse(252, 150, 5, 5, stroke=WHITE, sw=1.6, passes=1), s.ellipse(262, 134, 3.5, 3.5, stroke=WHITE, sw=1.4, passes=1)))
v.variant("fish_down", (300, 440, 130, 76), FISH_DOWN, lambda s: (
    [s.line(308 + i * 28, 446, 308 + i * 28, 510, sw=1.4, opacity=0.6, passes=1) for i in range(5)],
    [s.line(304, 452 + i * 20, 424, 452 + i * 20, sw=1.4, opacity=0.6, passes=1) for i in range(4)],
    fish(s, 350, 484, 0.8)))
v.spot((146, 120, 132, 114), [["take", "food"], ["set", "s3_fish_ready", 1], ["sfx", "ok"], ["unsel"]], all_(["sel", "food"], FISH_AIR))
v.spot((296, 436, 138, 84), [["go", "s3maze"], ["sfx", "tick"]], eq("s3_fish_ready", 1))
v.spot((230, 0, 560, 40), [["go", "s3ceil"], ["sfx", "tick"]])
v.spot((288, 318, 324, 110), [["go", "s3under"], ["sfx", "tick"]], eq("s3_goff", 1))
v.spot((394, 270, 112, 44), [["take", "ekey"], ["set", "s3_panel", 1], ["sfx", "ok"], ["unsel"]],
       all_(["sel", "ekey"], eq("s3_panel", 0), eq("s3_fuel", 1)))
v.spot((394, 270, 112, 44), [["go", "s3panel"], ["sfx", "tick"]], eq("s3_panel", 1))

# ------------------------------------------------------------------ maze on the tatami
GX0, GY0, GC = 140, 64, 64


def cell_xy(col, row):
    """Centre of a cell; col and row count from 1, row 1 is the near side."""
    return GX0 + (col - 0.5) * GC, GY0 + (6 - row + 0.5) * GC


def grid(s, color):
    s.frect(GX0, GY0, GC * 6, GC * 6, color)
    for i in range(1, 6):
        s.line(GX0 + i * GC, GY0, GX0 + i * GC, GY0 + GC * 6, sw=2, opacity=0.7, passes=1)
        s.line(GX0, GY0 + i * GC, GX0 + GC * 6, GY0 + i * GC, sw=2, opacity=0.7, passes=1)


BLOCKED = [(1, 2), (2, 2), (3, 2), (5, 2), (6, 3), (4, 4), (5, 4), (1, 5), (5, 5), (1, 6), (3, 6)]
MAZES["m1"] = dict(pos="mz", w=6, h=6, blocked=[(r - 1) * 6 + (c - 1) for c, r in BLOCKED], start=0, goal=35,
                   remap=[1, 2, 3, 0], ok=[["set", "s3_fish", 1], ["sfx", "ok"]])

v = View("s3maze", 3, "たたみ", back="s3v3", when=eq("s3_fish_ready", 1))
s = v.s
washitsu(s, 530)
grid(s, TATAMI_L)
gx, gy = cell_xy(6, 6)
s.fell(gx, gy + 4, 24, 18, "#5f93aa", sw=2.4)
s.fell(gx, gy - 9, 16, 5, "#8fc0d0", sw=2)
s.frect(580, 120, 250, 300, PANEL)
fish(s, 705, 158, 0.7)
ARROWS = [(705, 226, 0), (771, 292, 1), (705, 358, 2), (639, 292, 3)]
for ax, ay, d in ARROWS:
    s.frect(ax - 29, ay - 29, 58, 58, PAPER_L, sw=2.6)
    a = [-90, 0, 90, 180][d]
    pts = [(ax + math.cos(math.radians(a + t)) * 17, ay + math.sin(math.radians(a + t)) * 17) for t in (0, 130, 230)]
    s.fpoly(pts, INK, sw=1.5)
s.vignette()
sprite("fish", 52, 44, lambda s: fish(s, 30, 23, 0.72))
v.sprite("fish", 52, 44, "mz", [(cell_xy(c, r)[0] - 26, cell_xy(c, r)[1] - 22) for r in range(1, 7) for c in range(1, 7)], eq("s3_fish", 0))
for ax, ay, d in ARROWS:
    v.spot((ax - 31, ay - 31, 62, 62), [["maze", "m1", d]], eq("s3_fish", 0))
v.variant("done", (gx - 30, gy - 30, 60, 60), eq("s3_fish", 1), lambda s: fish(s, gx, gy + 2, 0.5))

# ------------------------------------------------------------------ ceiling
v = View("s3ceil", 3, "てんじょう", back="s3v3")
s = v.s
s.solid(rect_pts(0, 0, W, H), "#5a4c36")
for y in range(0, H, 54):
    s.line(0, y, W, y, sw=1.6, opacity=0.4, passes=1)
grid(s, "#75643f")
for c, r in BLOCKED:
    x, y = cell_xy(c, r)
    s.sym("x", x, y, 17, RED, 5.5)
s.paper(584, 216, 250, 50, [("たたみと おなじ むき", 20)], align="center", pad=11)
s.vignette()

# ------------------------------------------------------------------ under the kotatsu
v = View("s3under", 3, "こたつの した", back="s3v3", when=eq("s3_goff", 1))
s = v.s
s.solid(rect_pts(0, 0, W, H), "#1c1614")
s.frect(60, 30, 800, 480, "#3a2d25")
s.frect(170, 60, 560, 96, PAPER, sw=2.4)
s.text(450, 92, "ねんりょうは まどの ほしの かず だけ。", 22)
s.text(450, 128, "いれすぎ ちゅうい", 22)
s.fell(350, 320, 82, 70, BRASS, sw=3)
s.fell(350, 320, 62, 52, "#080b0c", sw=2.6)
s.frect(470, 280, 80, 76, PAPER_L, sw=2.6)
s.frect(600, 282, 170, 72, RED, sw=3)
s.text(685, 318, "しめる", 28, PAPER_L)
s.vignette()
v.text(510, 318, 44, "s3_fc")
v.spot((262, 244, 180, 156), [["take", "mikan"], ["add", "s3_fc", 1], ["sfx", "plop"]], all_(["sel", "mikan"], eq("s3_fuel", 0)))
v.spot((600, 282, 170, 72), [["if", eq("s3_fc", 5),
                             [["set", "s3_fuel", 1], ["set", "s3_fc", 0], ["set", "s3_goff", 0], ["sfx", "ok"]],
                             [["givef", "mikan", "s3_fc"], ["set", "s3_fc", 0], ["cool", "s3_fxb", 2], ["sfx", "buzz"], ["shake"]]]], eq("s3_fuel", 0))
v.variant("gep", (250, 176, 220, 64), ["cool", "s3_fxb"], lambda s: s.text(360, 208, "ゲップ", 40, PAPER_L, rot=-6))

# ------------------------------------------------------------------ launch panel
v = View("s3panel", 3, "そうさばん", back="s3v3", when=eq("s3_panel", 1))
s = v.s
s.solid(rect_pts(0, 0, W, H), "#3a2d25")
s.frect(110, 40, 760, 470, PANEL)
s.paper(140, 66, 330, 176, ["ほしは だるまより まえ", "みかんは さいご では ない", "きんぎょは さいしょ では ない", "みかんは きんぎょの すぐ あと"], 19, pad=14, gap=1.5)
KX = [200, 340, 480, 620]
for x in KX:
    s.frect(x - 56, 300, 112, 112, PAPER_L, sw=3)
s.solid(star_pts(KX[0], 356, 36), LIGHT)
s.poly(star_pts(KX[0], 356, 36), True, 1.0, sw=2.6)
fish(s, KX[1] + 4, 356, 1.5)
daruma(s, KX[2], 356, 1.0)
mikan(s, KX[3], 360, 34)
PQ = [530, 570, 610, 650]
for x in PQ:
    s.fell(x, 268, 7, 7, "#3a4648", sw=1.8)
s.vignette()
seq_dots(v, "q5", 4, PQ, 268)
for i, x in enumerate(KX):
    v.spot((x - 58, 298, 116, 116),
           [["sfx", "tick"], ["seq", "q5", i, 4, [0, 1, 3, 2], [["set", "s3_code", 1], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]],
           eq("s3_code", 0))
v.variant("launch", (560, 70, 270, 170), eq("s3_code", 1), lambda s: (
    s.glow(694, 152, 110, RED_L, 0.07), s.fell(694, 152, 100, 64, RED_L, sw=4), s.text(694, 152, "はっしゃ", 40, PAPER_L)))
v.spot((580, 80, 230, 150), [["sfx", "launch"], ["stage", 4]], eq("s3_code", 1))


# ------------------------------------------------------------------ items and hints
def food_icon(s):
    s.fpoly([(22, 26), (74, 26), (80, 84), (16, 84)], "#b99a6b", sw=2.8)
    s.line(22, 36, 74, 36, sw=2, passes=1)
    fish(s, 50, 60, 0.6)


item("food", food_icon)
item("grip", lambda s: grip_shape(s, 48, 46, 2.0))
item("ekey", lambda s: (key_shape(s, 46, 40, 1.8, "#c9cdd0"), s.frect(26, 58, 44, 24, RED_L, sw=2.2), s.solid(star_pts(48, 70, 8), LIGHT)))
item("mikan", lambda s: mikan(s, 48, 52, 28))

puzzle("s3a", 3, "ちゃだんす", None, eq("s3_stars", 1),
       ["まどの 星は 5つ。ランプで おなじ 場所を つけても だめ。",
        "はりがみは「そとから 見た」と 言っている。",
        "そとから 見ると 左右が ぎゃく。上のだんは まんなかと 右。まんなかのだんは 左と 右。下のだんは 左。"],
       "上：まんなか・右／中：左・右／下：左", [["set", "s3_stars", 1], ["give", "food"]])
puzzle("s3b", 3, "きんぎょ", eq("s3_stars", 1), eq("s3_fish", 1),
       ["ひきだしの エサを きんぎょに あげよう。入っては いけない マスは たたみには かいて いない。へやの べつの 場所を 見よう。",
        "てんじょうに ×が ある。1人が てんじょうを 見て 道を つたえ、もう1人が たたみで リモコンを おす。きんぎょは おした むきに うごかないが、でたらめ では ない。",
        "↑で 右、→で 下、↓で 左、←で 上。うごかす じゅんは、右3、上2、左1、上2、右1、上1、右2。"],
       "ボタン：↑↑↑ ←← ↓ ←← ↑ ← ↑↑",
       [["takeall", "food"], ["set", "s3_fish_ready", 1], ["set", "mz", 35], ["set", "s3_fish", 1]])
puzzle("s3c", 3, "ちがいだな", eq("s3_stars", 1), eq("s3_daruma", 1),
       ["小さい まどの 外に だれか きた。おなじ うごきを くりかえしている。",
        "かけじくが ポーズの いみ。「たかい・やすい」は 左の かべの ねふだ。ねだんは じぶんで もとめる。",
        "ねだんは まねきねこ 1500、こけし 1200、だるま 800、きゅうす 300。いちばん たかい → いちばん やすい → 2ばんめ → のこり の じゅんに タップ。"],
       "まねきねこ → きゅうす → こけし → だるま", [["set", "s3_daruma", 1], ["give", "ekey"]])
puzzle("s3d", 3, "こたつの した", eq("s3_fish", 1), eq("s3_fuel", 1),
       ["金魚ばちから 出てきたものを 左の かべの はしらに つけよう。レバーで へやの ものが うく。",
        "こたつの下は、ういている ときしか 見られない。みかんは ういている ときは とれない。なんこ 入れるかは こたつの うらに かいてある。",
        "まどの 星は 5つ。じゅうりょくを オンに して みかんを 5こ ひろい、オフに して こたつの下に 5こ 入れて しめる。"],
       "みかん 5こ",
       [["takeall", "grip"], ["set", "s3_grip", 1], ["set", "s3_lever", 1], ["set", "s3_goff", 0], ["takeall", "mikan"], ["set", "s3_fc", 0], ["set", "s3_fuel", 1]])
puzzle("s3e", 3, "そうさばん", all_(eq("s3_fuel", 1), eq("s3_daruma", 1)), eq("s3_code", 1),
       ["だるまから 出てきた カギを こたつの ふたに つかおう。メモが 4ぎょう ある。",
        "4ぎょうを ぜんぶ みたす ならびは 1つだけ。「すぐ あと」から かんがえる。",
        "きんぎょ・みかんは つづき。さいしょは きんぎょ では ないので ほし。のこりの だるまが さいご。"],
       "ほし → きんぎょ → みかん → だるま", [["takeall", "ekey"], ["set", "s3_panel", 1], ["set", "s3_code", 1]])
