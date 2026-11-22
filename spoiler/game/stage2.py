"""Stage 2."""
from game.core import *  # noqa: F401,F403

TILE, TFLOOR = "#35585a", "#3f4f52"
TBLUE, TRED = "#3f78b0", "#d0503f"
CAT = "#e2d2b0"
INIT["f"].update(s2_tv=30)


def bath_wall(s, floor_y=400):
    s.room(wall=TILE, floor_y=floor_y, floor=TFLOOR, wain=None, planks=False)
    for x in range(24, W, 48):
        s.line(x, 0, x, floor_y, sw=1.2, opacity=0.22, passes=1)
    for y in range(40, floor_y, 48):
        s.line(0, y, W, y, sw=1.2, opacity=0.22, passes=1)
    for x in range(0, W + 1, 96):
        s.line(x, floor_y + 2, W / 2 + (x - W / 2) * 1.5, H, sw=1.4, opacity=0.35, passes=1)


def cat(s, cx, cy, k=1.0, happy=False):
    s.fell(cx, cy + 34 * k, 62 * k, 44 * k, CAT)
    s.curve([(cx + 56 * k, cy + 50 * k), (cx + 92 * k, cy + 44 * k), (cx + 98 * k, cy + 10 * k)], sw=7 * k, stroke=CAT, passes=1)
    s.fpoly([(cx - 34 * k, cy - 34 * k), (cx - 26 * k, cy - 66 * k), (cx - 8 * k, cy - 44 * k)], CAT, sw=2.4)
    s.fpoly([(cx + 34 * k, cy - 34 * k), (cx + 26 * k, cy - 66 * k), (cx + 8 * k, cy - 44 * k)], CAT, sw=2.4)
    s.fell(cx, cy - 22 * k, 42 * k, 34 * k, CAT)
    for sx in (-1, 1):
        if happy:
            s.curve([(cx + sx * 24 * k, cy - 24 * k), (cx + sx * 16 * k, cy - 32 * k), (cx + sx * 8 * k, cy - 24 * k)], sw=2.4, passes=1)
        else:
            s.line(cx + sx * 24 * k, cy - 26 * k, cx + sx * 8 * k, cy - 26 * k, sw=2.6, passes=1)
        for dy in (-4, 4):
            s.line(cx + sx * 26 * k, cy - 12 * k + dy * k * 0.5, cx + sx * 56 * k, cy - 14 * k + dy * k * 1.6, sw=1.4, passes=1)
    s.dot(cx, cy - 16 * k, 3.5 * k, "#b0736a")
    s.curve([(cx - 8 * k, cy - 8 * k), (cx, cy - 4 * k), (cx + 8 * k, cy - 8 * k)], sw=2, passes=1)
    for dx in (-12, 0, 12):
        s.line(cx + dx * k, cy - 54 * k, cx + dx * k, cy - 44 * k, stroke="#a88a5a", sw=3 * k, passes=1)


def bottle(s, x, y, color, k=1.0):
    s.frect(x + 16 * k, y, 18 * k, 12 * k, METAL, sw=2)
    s.frect(x + 13 * k, y + 12 * k, 24 * k, 22 * k, color, sw=2.2)
    s.frect(x, y + 34 * k, 50 * k, 116 * k, color, sw=2.6)
    s.frect(x + 7 * k, y + 70 * k, 36 * k, 34 * k, PAPER_L, sw=1.6)


def duck(s, cx, cy, k=1.0, key=False):
    s.fell(cx, cy, 28 * k, 17 * k, "#f0c63a")
    s.fell(cx + 20 * k, cy - 18 * k, 13 * k, 12 * k, "#f0c63a")
    s.fpoly([(cx + 31 * k, cy - 20 * k), (cx + 44 * k, cy - 16 * k), (cx + 31 * k, cy - 12 * k)], ORANGE, sw=2)
    s.dot(cx + 23 * k, cy - 21 * k, 2.2 * k)
    s.curve([(cx - 14 * k, cy - 2 * k), (cx - 2 * k, cy + 6 * k), (cx + 8 * k, cy - 2 * k)], sw=2, passes=1)
    if key:
        key_shape(s, cx - 8 * k, cy - 22 * k, 0.8 * k)


def key_shape(s, cx, cy, k=1.0, color=BRASS):
    s.fell(cx - 14 * k, cy, 10 * k, 10 * k, color, sw=2.4)
    s.dot(cx - 14 * k, cy, 3.5 * k, "#1b1f21")
    s.frect(cx - 5 * k, cy - 3 * k, 30 * k, 6 * k, color, sw=2)
    s.frect(cx + 13 * k, cy + 3 * k, 5 * k, 8 * k, color, sw=1.8)
    s.frect(cx + 21 * k, cy + 3 * k, 4 * k, 6 * k, color, sw=1.8)


def faucet(s, x, color=None):
    s.frect(x - 6, 286, 12, 46, METAL, sw=2)
    s.fpoly([(x - 6, 292), (x + 28, 292), (x + 28, 312), (x + 17, 312), (x + 17, 303), (x - 6, 303)], METAL, sw=2)
    s.frect(x - 5, 270, 10, 16, METAL_D, sw=2)
    if color:
        faucet_handle(s, x, 266, color)


def faucet_handle(s, cx, cy, color, k=1.0):
    s.frect(cx - 24 * k, cy - 5 * k, 48 * k, 10 * k, color, sw=2.2)
    s.frect(cx - 5 * k, cy - 18 * k, 10 * k, 36 * k, color, sw=2.2)
    s.fell(cx, cy, 7 * k, 7 * k, PAPER_L, sw=2)


# ------------------------------------------------------------------ front: the bath
v = View("s2v1", 2, "湯船の壁", l="s2v2", r="s2v3")
s = v.s
bath_wall(s)
s.frect(230, 40, 440, 204, "#6f96b8")
s.fell(596, 84, 24, 24, "#e8b04a", sw=2.4)
s.fpoly([(280, 244), (450, 80), (620, 244)], "#3f5f86")
s.fpoly([(418, 112), (450, 80), (482, 112), (466, 104), (450, 118), (434, 104)], WHITE, sw=2)
s.solid(rect_pts(232, 220, 436, 22), "#4f8a5a")
s.rect(230, 40, 440, 204, sw=3.6)
s.paper(64, 70, 152, 60, ["当たりは", "2段目ではない"], 15, pad=9)
s.paper(686, 66, 130, 98, [("いい湯加減", 17), ("＝", 16), ("タマの年 × 3", 17)], align="center", pad=9)
faucet(s, 250)
faucet(s, 650, TBLUE)
s.frect(150, 332, 580, 96, "#8fa3a8")
s.solid(rect_pts(166, 344, 548, 60), "#5f9fb5")
s.rect(166, 344, 548, 60, sw=2.2)
for x0 in (200, 330, 470, 600):
    s.curve([(x0, 372), (x0 + 22, 366), (x0 + 44, 372), (x0 + 66, 366)], stroke="#9fd0e0", sw=2, passes=1)
for x0 in (300, 430, 560):
    s.curve([(x0, 320), (x0 - 10, 296), (x0 + 8, 280), (x0 - 4, 258)], stroke=WHITE, sw=2.5, opacity=0.25, passes=1)
s.vignette()

v.variant("hot", (218, 240, 64, 46), eq("s2_hot", 1), lambda s: faucet_handle(s, 250, 266, TRED))
CHECK = [["sfx", "water"],
         ["if", ["any", ["gt", "s2_tv", 50], ["lt", "s2_tv", 20]],
          [["set", "s2_tv", 30], ["cool", "s2_fx", 2], ["sfx", "buzz"]],
          [["if", eq("s2_tv", 42), [["set", "s2_temp", 1], ["sfx", "ok"]]]]]]
v.spot((208, 236, 92, 100), [["take", "fhandle"], ["set", "s2_hot", 1], ["sfx", "ok"], ["unsel"]], all_(["sel", "fhandle"], eq("s2_hot", 0)))
v.spot((208, 236, 92, 100), [["add", "s2_tv", 5]] + CHECK, all_(eq("s2_hot", 1), eq("s2_temp", 0)))
v.spot((608, 236, 92, 100), [["add", "s2_tv", -3]] + CHECK, eq("s2_temp", 0))
v.variant("plug", (386, 296, 200, 112), ["cool", "s2_fx"], lambda s: (
    s.fell(470, 376, 46, 14, "#3f7f95", sw=2), s.curve([(450, 376), (470, 382), (492, 374), (476, 368)], stroke="#9fd0e0", sw=2, passes=1),
    s.line(470, 372, 520, 326, stroke=METAL, sw=3), s.fell(534, 318, 24, 17, CAT, sw=2.4),
    s.line(524, 312, 524, 322, sw=1.6, passes=1), s.line(534, 310, 534, 322, sw=1.6, passes=1), s.line(544, 312, 544, 322, sw=1.6, passes=1)))
v.variant("duck_far", (556, 326, 72, 46), eq("s2_temp", 0), lambda s: duck(s, 590, 356, 0.5))
NEAR = all_(eq("s2_temp", 1), eq("s2_duck", 0))
v.variant("duck_near", (396, 338, 130, 78), NEAR, lambda s: duck(s, 452, 384, 1.0, key=True))
v.spot((392, 332, 138, 88), [["give", "key"], ["set", "s2_duck", 1], ["sfx", "get"]], NEAR)


def mural_up(s):
    s.solid(rect_pts(222, 32, 456, 220), TILE)
    for x in range(264, 678, 48):
        s.line(x, 32, x, 252, sw=1.2, opacity=0.22, passes=1)
    for y in range(40, 252, 48):
        s.line(222, y, 678, y, sw=1.2, opacity=0.22, passes=1)
    s.frect(230, 34, 440, 26, "#6f96b8", sw=3)
    s.line(236, 52, 664, 52, sw=1.6, opacity=0.6, passes=1)
    s.frect(372, 70, 156, 176, BLACK)
    s.frect(380, 78, 140, 168, WOOD)
    s.paper(410, 86, 80, 28, [("出口", 16)], align="center", pin=False, pad=5)
    s.frect(404, 150, 92, 40, METAL, sw=2.2)
    for i in range(4):
        s.frect(410 + i * 21, 158, 17, 24, PAPER_L, sw=1.6)


v.variant("mural_up", (222, 32, 456, 220), eq("s2_chair", 1), mural_up)
v.spot((372, 70, 156, 176), [["go", "s2exit"], ["sfx", "tick"]], eq("s2_chair", 1))

# ------------------------------------------------------------------ exit door close-up
v = View("s2exit", 2, "出口", back="s2v1", when=eq("s2_chair", 1))
s = v.s
bath_wall(s, 510)
s.frect(240, 30, 480, 480, BLACK)
s.frect(250, 40, 460, 470, WOOD)
s.frect(296, 58, 368, 176, PAPER, sw=2.4)
s.frect(336, 100, 130, 26, WHITE, sw=2.2)
s.frect(346, 107, 76, 12, RED_L, outline=False)
s.fell(334, 113, 17, 17, RED_L, sw=2.4)
for x in range(360, 460, 20):
    s.line(x, 100, x, 108, sw=1.6, passes=1)
s.frect(496, 82, 52, 66, METAL_D, sw=2.4)
s.frect(502, 88, 40, 54, "#0a0d0e", sw=1.8)
s.solid(star_pts(522, 115, 13), LIGHT)
s.fpoly([(548, 82), (562, 90), (562, 152), (548, 148)], METAL, sw=2)
s.line(574, 84, 632, 84, sw=2.2)
s.frect(580, 88, 46, 60, "#7fb0d0", sw=2.4)
s.line(580, 104, 626, 104, stroke=WHITE, sw=3, passes=1)
s.line(580, 132, 626, 132, stroke=WHITE, sw=3, passes=1)
s.text(480, 204, "この銭湯で見つけた数字", 19)
EX = [362, 442, 522, 602]
for x in EX:
    s.frect(x - 30, 262, 60, 82, PAPER_L, sw=2.6)
s.fell(672, 303, 23, 23, BRASS, sw=2.8)
s.line(662, 303, 682, 303, sw=2.2, passes=1)
s.vignette()
for i, x in enumerate(EX):
    fl = "s2_e%d" % (i + 1)
    v.text(x, 303, 52, fl, when=eq("s2_exit", 0))
    v.spot((x - 34, 258, 68, 90), [["cyc", fl, 10], ["sfx", "tick"]], eq("s2_exit", 0))
v.spot((644, 275, 56, 56), [["if", all_(eq("s2_e1", 4), eq("s2_e2", 2), eq("s2_e3", 7), eq("s2_e4", 6)),
                            [["set", "s2_exit", 1], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]], eq("s2_exit", 0))
v.variant("open", (236, 26, 488, 490), eq("s2_exit", 1), lambda s: (
    s.frect(240, 30, 480, 480, BLACK), s.frect(250, 40, 460, 470, "#0a0d0e"),
    [s.fpoly([(290 + i * 22, 470 - i * 56), (670 - i * 22, 470 - i * 56), (670 - i * 22, 510 - i * 56), (290 + i * 22, 510 - i * 56)],
             "#2a2422", sw=2) for i in range(6)],
    s.solid(ell_pts(480, 150, 90, 60, 24), LIGHT, 0.10)))
v.spot((250, 40, 460, 470), [["sfx", "door"], ["stage", 3]], eq("s2_exit", 1))

# ------------------------------------------------------------------ left: lockers and laundry
v = View("s2v2", 2, "ロッカーの壁", r="s2v1")
s = v.s
bath_wall(s)
LX, LY, LW, LH = [110, 180, 250], [92, 160, 228], 64, 62


def lpos(n):
    return LX[(n - 1) % 3], LY[(n - 1) // 3]


s.paper(110, 44, 204, 38, [("当たりは一つ", 19)], align="center", pad=6, pin=False)
for n in range(1, 10):
    x, y = lpos(n)
    s.frect(x, y, LW, LH, METAL_D)
    s.text(x + 26, y + 26, str(n), 26, PAPER_L)
    s.fell(x + LW - 11, y + LH / 2 + 10, 4, 4, BRASS, sw=1.6)
    s.line(x + 10, y + LH - 12, x + 34, y + LH - 12, sw=1.5, opacity=0.6, passes=1)
s.curve([(372, 106), (590, 118), (812, 104)], sw=2.6)
TOWELS = [TBLUE, TRED, TRED, TBLUE, TRED, TBLUE]
PINS = [4, 1, 6, 2, 5, 3]
for i in range(6):
    tx = 384 + i * 70
    s.frect(tx, 120, 56, 98, TOWELS[i])
    s.line(tx + 2, 140, tx + 54, 140, stroke=WHITE, sw=3, passes=1)
    s.line(tx + 2, 198, tx + 54, 198, stroke=WHITE, sw=3, passes=1)
    s.frect(tx + 15, 98, 26, 28, PAPER_L, sw=2)
    s.text(tx + 28, 112, str(PINS[i]), 19)
s.frect(420, 436, 130, 44, "#8c979a")
s.fell(485, 432, 24, 14, PAPER_L, sw=2.2)
s.line(485, 432, 496, 424, stroke=RED_L, sw=2, passes=1)
s.vignette()

LOCK_OK = all_(eq("s2_locker", 0), ["not", ["cool", "s2_cool"]])
for n in range(1, 10):
    x, y = lpos(n)
    if n == 7:
        v.spot((x, y, LW, LH), [["set", "s2_locker", 1], ["give", "coin"], ["sfx", "ok"]], LOCK_OK)
    else:
        v.spot((x, y, LW, LH), [["cool", "s2_cool", 10], ["sfx", "buzz"], ["shake"]], LOCK_OK)
v.variant("l7", (104, 222, 96, 76), eq("s2_locker", 1), lambda s: (
    s.frect(110, 228, LW, LH, "#0a0d0e"), s.glow(142, 259, 26, LIGHT, 0.10), s.solid(star_pts(142, 259, 15), LIGHT),
    s.fpoly([(174, 228), (196, 238), (196, 298), (174, 290)], METAL, sw=2.2), s.text(185, 262, "7", 17, PAPER_L)))


def crosses(s):
    for n in range(1, 10):
        x, y = lpos(n)
        s.sym("x", x + LW / 2, y + LH / 2, 20, RED_L, 5)


v.variant("cool", (100, 84, 224, 214), ["cool", "s2_cool"], crosses)
v.text(212, 322, 34, "s2_cool", kind="cool", color=RED_L, when=["cool", "s2_cool"])


def scale_up(s):
    s.fpoly([(400, 488), (580, 488), (570, 336), (410, 336)], "#6f7a7d", sw=2.8)
    s.paper(414, 362, 152, 62, ["当たりの番号は", "3で割れない"], 15, pin=False, pad=8)
    s.fell(430, 470, 8, 8, BLACK, sw=2)
    s.fell(550, 470, 8, 8, BLACK, sw=2)


v.variant("scale", (392, 326, 198, 170), eq("s2_scale", 1), scale_up)
v.spot((392, 326, 198, 170), [["set", "s2_scale", 0], ["sfx", "tick"]], eq("s2_scale", 1))
v.spot((408, 410, 154, 80), [["set", "s2_scale", 1], ["sfx", "tick"]], eq("s2_scale", 0))

# ------------------------------------------------------------------ right: fridge, counter, chair
v = View("s2v3", 2, "番台の壁", l="s2v1")
s = v.s
bath_wall(s)
s.frect(90, 130, 180, 270, "#aebbbb")
s.frect(104, 146, 152, 112, "#16201f", sw=2.4)
for i, c in enumerate([BROWN, PINK, WHITE, BROWN, WHITE]):
    bottle(s, 112 + i * 28, 170, c, 0.44)
s.text(180, 284, "牛乳", 19)
for i, c in enumerate([WHITE, BROWN, PINK]):
    s.fell(140 + i * 40, 320, 10, 10, c, sw=2)
s.frect(120, 356, 120, 26, "#16201f", sw=2)
s.paper(284, 150, 130, 62, ["当たりは", "左か右の列"], 15, pad=9)
s.frect(420, 258, 230, 16, WOOD_L)
s.frect(430, 274, 210, 126, WOOD)
s.frect(446, 290, 178, 30, PAPER, sw=2)
cat(s, 520, 214, 0.55)
s.frect(596, 196, 40, 62, PAPER_L, sw=2)
s.line(616, 206, 616, 246, stroke=RED_L, sw=3, passes=1)
s.fpoly([(690, 168), (792, 168), (804, 332), (678, 332)], "#3a2f3f")
s.frect(668, 332, 146, 40, "#4a3d50")
s.frect(660, 300, 22, 80, "#2b2330", sw=2.4)
s.frect(800, 300, 22, 80, "#2b2330", sw=2.4)
s.frect(684, 372, 20, 30, "#1b1f21", sw=2)
s.frect(778, 372, 20, 30, "#1b1f21", sw=2)
for y in (200, 236, 272):
    s.fell(741, y, 26, 12, "#4a3d50", sw=2)
s.vignette()
v.spot((90, 130, 180, 270), [["go", "s2fridge"], ["sfx", "tick"]])
v.spot((420, 150, 230, 250), [["go", "s2bandai"], ["sfx", "tick"]])
v.spot((660, 168, 162, 234), [["go", "s2chair"], ["sfx", "tick"]])

# ------------------------------------------------------------------ fridge close-up
v = View("s2fridge", 2, "冷蔵庫", back="s2v3")
s = v.s
bath_wall(s, 520)
s.frect(70, 40, 500, 480, "#aebbbb")
s.frect(90, 62, 430, 250, "#16201f", sw=2.6)
for i, c in enumerate([BROWN, PINK, WHITE, BROWN, WHITE]):
    bottle(s, 118 + i * 80, 100, c)
s.line(96, 258, 514, 258, stroke=METAL, sw=3, passes=1)
BX = [170, 300, 430]
BC = [WHITE, BROWN, PINK]
BT = ["白＝牛乳", "茶＝コーヒー", "ピンク＝フルーツ"]


def buttons(s, lit):
    for i in range(3):
        if lit:
            s.glow(BX[i], 384, 44, LIGHT, 0.08)
        s.fell(BX[i], 384, 30, 30, BC[i], sw=3, op=1.0 if lit else 0.45)
        s.text(BX[i], 432, BT[i], 15)
    for x in (260, 300, 340):
        s.fell(x, 334, 6, 6, "#3a4648", sw=1.6)


buttons(s, False)
s.frect(516, 336, 40, 72, METAL, sw=2.4)
s.frect(532, 350, 8, 30, BLACK, sw=1.6)
s.frect(190, 456, 220, 50, "#16201f", sw=2.4)
s.paper(580, 46, 300, 330, [("牛乳の買い方", 21), "1 左端のビンと", "   同じ味のボタンを押す。", "2 右から2番目のビンと",
                            "   同じ味のボタンを押す。", "3 残ったボタンを押す。", "", ("※ 左・右は、ビンから見た向きです。", 15)], 18, gap=1.55)
s.vignette()
v.spot((70, 40, 500, 480), [["take", "coin"], ["set", "s2_coin", 1], ["sfx", "coin"], ["unsel"]], all_(["sel", "coin"], eq("s2_coin", 0)))
v.variant("lit", (120, 322, 370, 124), eq("s2_coin", 1), lambda s: (s.solid(rect_pts(120, 322, 370, 124), "#aebbbb"), buttons(s, True)))
seq_dots(v, "q2", 3, [260, 300, 340], 334, eq("s2_coin", 1), deps=("lit",), r=6)
for i in range(3):
    v.spot((BX[i] - 36, 348, 72, 72),
           [["sfx", "tick"], ["seq", "q2", i, 3, [0, 2, 1], [["set", "s2_milk", 1], ["give", "milk"], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]],
           all_(eq("s2_coin", 1), eq("s2_milk", 0)))

# ------------------------------------------------------------------ counter close-up
v = View("s2bandai", 2, "番台", back="s2v3")
s = v.s
bath_wall(s, 530)
s.frect(100, 288, 720, 18, WOOD_L)
s.frect(110, 306, 700, 234, WOOD)
cat(s, 440, 190, 1.35)
s.frect(196, 268, 28, 20, METAL, sw=2)
s.frect(146, 112, 128, 158, PAPER_L)
s.text(210, 134, "温度", 18)
s.frect(160, 152, 100, 78, WHITE, sw=2)
s.text(246, 250, "度", 20)
s.paper(330, 334, 236, 48, [("番台：タマ（14歳）", 19)], align="center", pin=False, pad=10)
s.paper(612, 104, 204, 100, ["風呂上がりは", "フルーツ牛乳に限る", "　　　　　　タマ"], 16, pad=10)
s.paper(604, 440, 200, 40, [("当たりは3より大きい", 16)], pin=False, pad=9)
s.vignette()
v.text(210, 191, 46, "s2_tv")
v.spot((330, 90, 220, 200), [["take", "milk"], ["set", "s2_cat", 1], ["give", "fhandle"], ["sfx", "meow"], ["unsel"]], all_(["sel", "milk"], eq("s2_cat", 0)))
v.variant("cat_happy", (318, 80, 290, 212), eq("s2_cat", 1), lambda s: (
    s.solid(rect_pts(318, 80, 290, 206), TILE), cat(s, 440, 190, 1.35, happy=True), bottle(s, 548, 206, PINK, 0.52)))

# ------------------------------------------------------------------ massage chair close-up
v = View("s2chair", 2, "マッサージ椅子", back="s2v3")
s = v.s
bath_wall(s, 520)
s.fpoly([(150, 60), (810, 60), (850, 540), (110, 540)], "#3a2f3f")
for y in (120, 470):
    s.fell(480, y, 240, 26, "#4a3d50", sw=2.4)
s.frect(316, 186, 328, 228, METAL_D)
s.frect(332, 202, 296, 196, "#1b2a2c", sw=2.4)
s.frect(380, 240, 200, 120, "#22282b", sw=2)
s.fell(480, 300, 18, 18, BRASS, sw=2.6)
s.frect(476, 296, 8, 14, BLACK, outline=False)
s.vignette()
RX = [380, 420, 460, 500, 540, 580]


def remote(s):
    s.frect(316, 186, 328, 228, METAL_D)
    s.frect(330, 168, 300, 256, "#2b2f33")
    s.paper(370, 182, 220, 40, [("干した順にもむ", 19)], align="center", pin=False, pad=8)
    s.fell(420, 300, 42, 42, TRED, sw=3)
    s.fell(540, 300, 42, 42, TBLUE, sw=3)
    for x in RX:
        s.fell(x, 388, 7, 7, "#3a4648", sw=1.8)


v.spot((316, 186, 328, 228), [["take", "key"], ["set", "s2_remote", 1], ["sfx", "ok"], ["unsel"]], all_(["sel", "key"], eq("s2_remote", 0)))
v.variant("remote", (308, 160, 344, 272), eq("s2_remote", 1), remote)
seq_dots(v, "q3", 6, RX, 388, eq("s2_remote", 1), deps=("remote",))
for i, x in enumerate((420, 540)):
    v.spot((x - 46, 254, 92, 92),
           [["sfx", "tick"], ["seq", "q3", i, 6, [0, 1, 1, 1, 0, 0], [["set", "s2_chair", 1], ["sfx", "ok"], ["shake"]], [["sfx", "buzz"], ["shake"]]]],
           all_(eq("s2_remote", 1), eq("s2_chair", 0)))


# ------------------------------------------------------------------ items and hints
def coin_icon(s):
    s.fell(48, 48, 32, 32, "#c9cdd0", sw=3)
    s.ellipse(48, 48, 25, 25, sw=1.6, passes=1)
    s.text(48, 48, "100", 24)


item("coin", coin_icon)
item("milk", lambda s: bottle(s, 30, 8, PINK, 0.55))
item("fhandle", lambda s: faucet_handle(s, 48, 48, TRED, 1.5))
item("key", lambda s: key_shape(s, 44, 48, 1.7))

puzzle("s2a", 2, "ロッカー", None, eq("s2_locker", 1),
       ["ロッカーのヒントの貼り紙は、部屋のあちこちに4枚ある。1枚はめくらないと見えない。",
        "4枚をすべて満たす番号は1つだけ。1から9まで1つずつ確かめる。",
        "2段目（4・5・6）と、3で割れる数（3・6・9）は違う。残りのうち、左か右の列で、3より大きいものは？"],
       "7番", [["set", "s2_locker", 1], ["give", "coin"]])
puzzle("s2b", 2, "冷蔵庫", eq("s2_locker", 1), eq("s2_milk", 1),
       ["ロッカーの中身を冷蔵庫に入れよう。説明書は最後の行まで読もう。素直にやると3つ目が決まらないはず。",
        "「ビンから見た向き」。ビンはこちらを向いている。ビンにとっての左は、こちらから見ると右。",
        "こちらから見て右端は白。左から2番目はフルーツ。残りはコーヒー。"],
       "白 → ピンク → 茶", [["takeall", "coin"], ["set", "s2_coin", 1], ["set", "s2_milk", 1], ["give", "milk"]])
puzzle("s2c", 2, "湯船", eq("s2_milk", 1), eq("s2_temp", 1),
       ["番台のタマは何か欲しがっている。温度計は番台の上、蛇口は湯船の壁。",
        "目指す温度は、看板とタマの名札から。蛇口は1回で何度変わるか、試して数える。",
        "目指すのは42度。左の蛇口は＋5、右は−3。30度から左を3回、右を1回。"],
       "42度（左3回、右1回）",
       [["takeall", "milk"], ["takeall", "fhandle"], ["set", "s2_cat", 1], ["set", "s2_hot", 1], ["set", "s2_tv", 42], ["set", "s2_temp", 1]])
puzzle("s2d", 2, "マッサージ椅子", eq("s2_temp", 1), eq("s2_chair", 1),
       ["アヒルの鍵は椅子のリモコンに使う。「干した順」は左からとは限らない。",
        "ロッカーの壁の洗濯ばさみに数字がある。1から6の順にタオルの色を読む。",
        "1番は左から2枚目（赤）。2番は4枚目（青）。3番は6枚目（青）。4番は1枚目（青）。5番は5枚目（赤）。6番は3枚目（赤）。"],
       "赤 → 青 → 青 → 青 → 赤 → 赤",
       [["takeall", "key"], ["set", "s2_duck", 1], ["set", "s2_remote", 1], ["set", "s2_chair", 1]])
puzzle("s2e", 2, "出口", eq("s2_chair", 1), eq("s2_exit", 1),
       ["貼り紙の絵は、この銭湯で使ったもの。絵の並びがダイヤルの並び。",
        "温度計はいい湯加減。ロッカーは当たりの番号。タオルは枚数。",
        "42、7、6をつなげる。"],
       "4276", [["set", "s2_exit", 1]])
