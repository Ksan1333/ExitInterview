"""Episode 2, stage 2: the kitchen."""
from ep2.look import *  # noqa: F401,F403

STAGE2_ITEMS = ["mizu", "imo", "ninjin", "tamanegi", "roux", "juice", "curry"]
EYES = [(-0.45, -0.05), (0.45, 0.12), (-0.02, 0.45), (0.08, -0.38)]
CODE = [(2, 1), (3, 2), (1, 3)]  # (sprouts, eyes) of the three potatoes on the recipe
TABLE = [["あ", "ぶ", "か", "さ"], ["た", "な", "ど", "は"], ["う", "ま", "や", "ら"], ["わ", "ん", "し", "お"]]  # rows: eyes, cols: sprouts
CURRY_BROWN = "#8a5a2e"


def potato(s, cx, cy, rx, ry, sprouts=0, eyes=0, color=POTATO):
    s.fell(cx, cy, rx, ry, color, sw=max(1.6, rx * 0.09))
    for i in range(sprouts):
        x = cx + (i - (sprouts - 1) / 2.0) * rx * 0.5
        y = cy - ry * 0.82
        s.line(x, y, x, y - ry * 0.62, stroke=GREEN, sw=max(2.0, rx * 0.13), passes=1)
        s.fell(x + rx * 0.14, y - ry * 0.64, rx * 0.18, ry * 0.14, GREEN, sw=1.2)
    for ox, oy in EYES[:eyes]:
        s.dot(cx + ox * rx, cy + oy * ry, max(2.2, rx * 0.13), POTATO_D)


def apple(s, cx, cy, color):
    s.fell(cx, cy, 22, 20, color, sw=2)
    s.line(cx, cy - 18, cx + 3, cy - 30, sw=2.4, passes=1)
    s.fell(cx + 11, cy - 27, 8, 4, "#3d6b2e", sw=1.4)


def door_content(s, photo):
    """The fridge door, in a 560 x 480 box. photo: as it was before the cleaning (three things differ)."""
    s.paper(24, 30, 262, 300, [("博士のカレー", 24), "水 ……… 4カップ", "じゃがいも・にんじん", "たまねぎ", "ルー（入れ方は 箱のうら）",
                               "かくし味："], 18, color=PAPER_L, gap=1.4, pad=14, pin=False)
    s.fell(155, 34, 12, 12, RED_L, sw=2)
    for i, (sp, ey) in enumerate(CODE):
        potato(s, 82 + i * 72, 262, 26, 19, sp, ey)
    apple(s, 340, 64, RED_L if photo else GREEN)
    if photo:
        s.sym("star", 460, 94, 22, fill=LIGHT)
    label_pic(s, "fish", 370, 192, 1.25)
    label_pic(s, "cat", 492, 222, 1.15)
    potato(s, 92, 418, 24, 17, 0, 2)
    s.paper(320, 280, 200, 92, [("かいもの", 18), ("・たまねぎ" if photo else "・たまご", 17), ("・ぎゅうにゅう", 17)], 17,
            gap=1.35, pad=10, pin=False)
    s.fell(420, 282, 9, 9, BLUE_L, sw=1.6)
    s.frect(340, 392, 200, 80, "#2a3133", sw=2.2)
    s.text(440, 410, "写真とちがうところを", 15, TXT)
    s.text(440, 432, "3つタッチで開く", 15, TXT)
    for i in range(3):
        s.fell(400 + i * 40, 456, 7, 7, "#3b4447", sw=1.6)


def kitchen_wall(s, lamp_x=480):
    kitchen(s, lamp_x, counter=False)


def counter(s, x0, x1, top=300):
    s.frect(x0, top, x1 - x0, 22, "#b9a27a", sw=2.4)
    s.frect(x0, top + 22, x1 - x0, 420 - top - 22, WOOD, sw=2.4)


# ------------------------------------------------------------------ the dumbwaiter wall
v = View("b1", 2, "エレベーターの壁", l="b4", r="b2")
s = v.s
kitchen_wall(s, 480)
s.frect(70, 120, 150, 300, METAL_D, sw=2.6)
s.frect(84, 136, 122, 120, METAL, sw=2)
s.fell(196, 290, 7, 7, BRASS, sw=2)
s.paper(92, 270, 92, 30, [("倉庫", 17)], align="center", pin=False, pad=4)
s.frect(360, 150, 240, 190, STEEL, sw=2.6)
s.frect(390, 180, 180, 140, "#c3cbcc", sw=2.4)
s.line(480, 180, 480, 320, sw=2)
s.fell(470, 250, 4, 10, METAL_D, sw=1.4)
s.fell(490, 250, 4, 10, METAL_D, sw=1.4)
s.paper(372, 104, 216, 38, [("料理用エレベーター", 19)], align="center", pin=False, pad=6)
s.frect(612, 206, 42, 92, METAL_D, sw=2.2)
s.fell(633, 236, 12, 12, PAPER_L, sw=2)
s.fpoly([(633, 228), (641, 242), (625, 242)], INK, outline=False)
s.text(633, 274, "社長室", 13, TXT)
s.frect(690, 80, 132, 210, "#a77b4f", sw=2.6)
s.frect(706, 96, 100, 112, WHITE, sw=2)
s.frect(714, 104, 84, 80, FRIDGE, sw=1.4)
s.frect(732, 110, 50, 70, "#f3f2ea", sw=1.2)
s.text(756, 196, "そうじの前", 13)
s.dot(756, 100, 3.5, RED)
s.paper(708, 218, 96, 60, [("今日の仕事", 13), ("昼ごはん", 13), ("を作る", 13)], align="center", gap=1.25, pin=False, pad=5)
s.vignette()
v.variant("open", (384, 174, 192, 152), ["ge", "b_dw", 1], lambda s: (
    s.frect(390, 180, 180, 140, "#0b0d0e", sw=2.4), s.frect(398, 296, 164, 16, METAL_D, sw=1.6)))
v.variant("pot", (384, 174, 192, 152), eq("b_dw", 2), lambda s: (
    s.fpoly([(420, 250), (540, 250), (534, 300), (426, 300)], METAL, sw=2.2), s.fell(480, 250, 60, 14, METAL_D, sw=2),
    s.fell(480, 251, 54, 10, PURPLE, outline=False)), deps=("open",))
v.spot((390, 180, 180, 140), [["set", "b_dw", 1], ["sfx", "door"]], eq("b_dw", 0))
v.spot((390, 180, 180, 140), [["take", "curry"], ["set", "b_dw", 2], ["sfx", "plop"], ["unsel"], ["msg", "なべを入れた。"]],
       all_(["sel", "curry"], eq("b_dw", 1)))
v.spot((390, 180, 180, 140), [["msg", "中は からっぽ。"]], eq("b_dw", 1))
v.spot((390, 180, 180, 140), [["msg", "カレーのなべが入っている。"]])
v.spot((606, 200, 54, 104), [["sfx", "launch"]] + [["takeall", i] for i in STAGE2_ITEMS] + [["stage", 3]],
       eq("b_dw", 2))
v.spot((606, 200, 54, 104), [["sfx", "tick"], ["msg", "ボタンを押した。…送るものが入っていない。"]])
v.spot((690, 80, 132, 210), [["go", "b1photo"]])
v.spot((70, 120, 150, 300), [["msg", "倉庫へのドア。シャッターが下りて、もどれない。"]])

# ------------------------------------------------------------------ the old photo
v = View("b1photo", 2, "掲示板の写真", back="b1")
s = v.s
s.frect(0, 0, W, H, "#7a5634", outline=False)
for k in range(30):
    s.dot(s.r.uniform(0, W), s.r.uniform(0, H), s.r.uniform(1, 2.4), "#5f4127")
s.frect(232, 16, 496, 508, WHITE, sw=2.6)
s.frect(250, 34, 460, 400, "#e3dccb", sw=2)
s.frect(250, 34, 14, 400, "#c9c1ad", outline=False)
s.raw('<g transform="translate(262 48) scale(0.78)">')
door_content(s, True)
s.raw("</g>")
s.text(480, 474, "そうじの前の冷蔵庫（博士）", 20)
s.dot(480, 26, 5, RED)
s.vignette(0.12)
v.spot((250, 34, 460, 400), [["msg", "冷蔵庫のとびらの写真。そうじの前に とったらしい。"]])

# ------------------------------------------------------------------ the stove wall
v = View("b2", 2, "コンロの壁", l="b1", r="b3")
s = v.s
kitchen_wall(s, None)
counter(s, 0, 290)
counter(s, 570, W)
# range hood
s.fpoly([(300, 20), (560, 20), (580, 110), (280, 110)], STEEL, sw=2.6)
s.frect(276, 104, 308, 14, METAL_D, sw=2)
s.paper(372, 50, 116, 32, [("火の元注意", 16)], align="center", pin=False, pad=4)
# range
s.frect(290, 252, 280, 168, "#d9d6cc", sw=2.6)
s.frect(290, 252, 280, 12, "#3a3f41", sw=2.2)
s.frect(300, 270, 260, 44, "#c4c0b4", sw=1.8)
for x in (370, 490):
    s.fell(x, 291, 15, 15, METAL_D, sw=2)
    s.line(x, 291, x, 279, sw=3, passes=1)
s.frect(316, 322, 228, 88, "#bdb9ad", sw=2)
s.frect(340, 338, 180, 44, "#2c3133", sw=1.8)
s.frect(430, 248, 120, 8, "#2a2f31", sw=1.4)
# the pot (on the left burner)
s.frect(316, 186, 20, 12, METAL_D, sw=1.8)
s.frect(484, 186, 20, 12, METAL_D, sw=1.8)
s.fpoly([(330, 168), (490, 168), (484, 250), (336, 250)], METAL, sw=2.6)
s.fell(410, 168, 80, 22, METAL_D, sw=2.4)
s.fell(410, 170, 72, 17, "#2b3436", sw=1.6)
# spice rack
s.frect(612, 84, 196, 152, WOOD_D, sw=2.4)
for y in (150, 226):
    s.frect(612, y, 196, 10, WOOD_L, sw=1.8)
for row, y in enumerate((106, 182)):
    for i in range(4):
        x = 634 + i * 46
        col = ["#6b6b6b", "#f0f0ea", "#ebe6d6", "#d9a33b", PURPLE, "#d0503f", "#5a3a22", "#3a2618"][row * 4 + i]
        s.frect(x - 13, y, 26, 42, col, sw=1.6)
        s.frect(x - 9, y - 8, 18, 9, METAL_D, sw=1.2)
s.vignette()


def pot_content(k):
    def draw(s):
        base = {1: WATER, 2: WATER, 3: WATER, 4: WATER, 5: "#9cc3d6", 6: CURRY_BROWN, 7: PURPLE}[k]
        s.fell(410, 172, 70, 15, base, outline=False)
        n = {1: 0, 2: 3, 3: 6, 4: 9, 5: 9, 6: 9, 7: 9}[k]
        cols = [POTATO, ORANGE, "#efe6cf"]
        for i in range(n):
            x = 360 + (i * 37) % 100
            y = 166 + (i * 13) % 12
            s.fpoly([(x, y), (x + 12, y - 4), (x + 16, y + 6), (x + 3, y + 8)], cols[i % 3], sw=1.4)
        if k == 5:
            for x, y in ((372, 170), (430, 166), (458, 174)):
                s.ellipse(x, y, 5, 3, sw=1.4)
        if k in (6, 7):
            s.fell(410, 172, 70, 15, base, op=0.55, outline=False)
        s.ellipse(410, 170, 72, 17, sw=1.6)
    return draw


for k in range(1, 8):
    v.variant("pot%d" % k, (326, 140, 168, 52), eq("b_pot", k), pot_content(k))
v.variant("steam", (326, 56, 168, 84), all_(eq("b_fire", 1), ["ge", "b_pot", 1], ["le", "b_pot", 7]), lambda s: [
    s.curve([(x, 136), (x - 10, 116), (x + 8, 96), (x - 6, 72)], sw=2.4, stroke="#e8eef0", opacity=0.7) for x in (370, 410, 450)])


def flames(s):
    for i in range(9):
        x = 342 + i * 17
        s.fpoly([(x - 6, 252), (x, 236 + (i % 3) * 3), (x + 6, 252)], "#4f8fe0", sw=1.2)
        s.fpoly([(x - 3, 252), (x, 244), (x + 3, 252)], "#ffd27a", outline=False)


v.variant("flame", (322, 230, 176, 30), eq("b_fire", 1), flames)
v.variant("knob", (346, 266, 48, 50), eq("b_fire", 1), lambda s: (
    s.fell(370, 291, 15, 15, METAL_D, sw=2), s.line(370, 291, 381, 282, sw=3, passes=1), s.dot(392, 304, 4, RED_L)))
v.variant("gone", (306, 112, 208, 152), eq("b_pot", 8), lambda s: (
    tiles_in(s, 306, 112, 208, 140), s.frect(290, 252, 224, 12, "#3a3f41", outline=False), s.line(306, 252, 514, 252, sw=2.2),
    s.frect(350, 246, 120, 8, "#2a2f31", sw=1.4)))
POT = (326, 120, 168, 136)
VEG = {"imo": "じゃがいも", "ninjin": "にんじん", "tamanegi": "たまねぎ"}
BOIL = [["set", "b_pot", 5], ["msg", "ぐつぐつ…具がやわらかく煮えた。"]]
v.spot(POT, [["take", "mizu"], ["set", "b_pot", 1], ["sfx", "water"], ["unsel"], ["msg", "水を4カップ入れた。"]],
       all_(["sel", "mizu"], eq("b_pot", 0)))
for vid, vname in VEG.items():
    v.spot(POT, [["take", vid], ["add", "b_pot", 1], ["sfx", "plop"], ["unsel"],
                 ["if", all_(eq("b_pot", 4), eq("b_fire", 1)), BOIL, [["msg", vname + "を入れた。"]]]],
           all_(["sel", vid], ["ge", "b_pot", 1], ["le", "b_pot", 3]))
    v.spot(POT, [["msg", "先に水を入れよう。"]], all_(["sel", vid], eq("b_pot", 0)))
v.spot(POT, [["msg", "具が まだかたい。"]], all_(["sel", "roux"], ["le", "b_pot", 4]))
v.spot(POT, [["sfx", "buzz"], ["shake"], ["msg", "ジュッ！…ルーが こげつきそう。あわてて取り出した。"]],
       all_(["sel", "roux"], eq("b_pot", 5), eq("b_fire", 1)))
v.spot(POT, [["take", "roux"], ["set", "b_pot", 6], ["sfx", "ok"], ["unsel"], ["msg", "ルーをとかした。いいにおい！"]],
       all_(["sel", "roux"], eq("b_pot", 5)))
v.spot(POT, [["msg", "かくし味は、最後に入れよう。"]], all_(["sel", "juice"], ["le", "b_pot", 5]))
v.spot(POT, [["take", "juice"], ["set", "b_pot", 7], ["sfx", "water"], ["unsel"], ["msg", "…カレーが むらさき色になった！ レシピどおり、のはず。"]],
       all_(["sel", "juice"], eq("b_pot", 6)))
v.spot(POT, [["msg", "火を止めてから持とう。"]], all_(eq("b_pot", 7), eq("b_fire", 1)))
v.spot(POT, [["give", "curry"], ["set", "b_pot", 8], ["sfx", "get"], ["msg", "カレーのなべを持った。社長室へ送ろう。"]], eq("b_pot", 7))
v.spot(POT, [["msg", "空のなべ。"]], eq("b_pot", 0))
v.spot(POT, [["msg", "水が入っている。"]], eq("b_pot", 1))
v.spot(POT, [["msg", "水と具が入っている。"]], ["le", "b_pot", 4])
v.spot(POT, [["msg", "具が やわらかく煮えた。"]], eq("b_pot", 5))
v.spot(POT, [["msg", "カレーができた。…何か足りない気がする。"]], eq("b_pot", 6))
KNOB = (346, 266, 48, 50)
v.spot(KNOB, [["set", "b_fire", 0], ["sfx", "tick"], ["msg", "火を止めた。"]], eq("b_fire", 1))
v.spot(KNOB, [["msg", "空のなべを火にかけるのは あぶない。"]], eq("b_pot", 0))
v.spot(KNOB, [["msg", "なべがない。"]], eq("b_pot", 8))
v.spot(KNOB, [["set", "b_fire", 1], ["sfx", "tick"], ["if", eq("b_pot", 4), BOIL, [["msg", "火をつけた。"]]]])
v.spot((462, 266, 56, 50), [["msg", "右のコンロは使わない。"]])
v.spot((606, 78, 208, 164), [["go", "b2rack"]])

# ------------------------------------------------------------------ the spice rack
BOTTLES = [("こしょう", "#6b6b6b", "jar"), ("しお", "#f0f0ea", "jar"), ("さとう", "#ebe6d6", "jar"), ("はちみつ", "#d9a33b", "jar"),
           ("ぶどう", PURPLE, "bottle"), ("りんご", "#d0503f", "bottle"), ("チョコ", "#5a3a22", "jar"), ("コーヒー", "#3a2618", "jar")]
RIGHT = 4


def bottle_xy(i):
    return 200 + (i % 4) * 160, (232 if i < 4 else 432)


def bottle(s, i):
    name, col, kind = BOTTLES[i]
    cx, base = bottle_xy(i)
    if kind == "jar":
        s.frect(cx - 40, base - 118, 80, 118, "#dfe9ec", sw=2.2, op=0.6)
        s.frect(cx - 36, base - 92, 72, 88, col, sw=1.4)
        s.frect(cx - 44, base - 132, 88, 18, METAL_D, sw=2)
    else:
        s.fpoly([(cx - 32, base), (cx + 32, base), (cx + 32, base - 86), (cx + 12, base - 110), (cx + 12, base - 140),
                 (cx - 12, base - 140), (cx - 12, base - 110), (cx - 32, base - 86)], "#dfe9ec", sw=2.2, op=0.6)
        s.frect(cx - 28, base - 82, 56, 78, col, sw=1.4)
        s.frect(cx - 13, base - 150, 26, 14, METAL_D, sw=1.8)
    s.frect(cx - 38, base - 66, 76, 30, PAPER_L, sw=1.8)
    s.text(cx, base - 51, name, 17 if len(name) < 4 else 15)


v = View("b2rack", 2, "スパイス棚", back="b2")
s = v.s
s.frect(0, 0, W, H, TILE_D, outline=False)
s.frect(90, 30, 740, 470, WOOD_D, sw=3)
s.frect(110, 70, 700, 166, "#3a2a1c", sw=2)
s.frect(110, 270, 700, 166, "#3a2a1c", sw=2)
for y in (232, 432):
    s.frect(100, y, 720, 18, WOOD_L, sw=2.2)
for i in range(8):
    bottle(s, i)
s.paper(330, 20, 300, 42, [("まちがえたら 30秒ロック", 20)], align="center", pin=False, pad=6)
s.vignette()
v.variant("taken", (146, 270, 108, 166), eq("b_juice", 1), lambda s: (
    s.frect(110, 270, 160, 162, "#3a2a1c", outline=False), s.frect(100, 432, 170, 18, WOOD_L, sw=2.2)))
v.variant("locked", (330, 456, 160, 48), ["cool", "b_lock"], lambda s: (
    s.frect(330, 458, 160, 44, "#2a1210", sw=2), s.text(400, 480, "ロック中", 20, RED_L)))
v.text(520, 482, 26, "b_lock", kind="cool", color=RED_L, when=["cool", "b_lock"])
ALL_BOTTLES = (110, 70, 700, 380)
v.spot(ALL_BOTTLES, [["msg", "ロック中。少し待とう。"]], ["cool", "b_lock"])
for i in range(8):
    cx, base = bottle_xy(i)
    r = (cx - 50, base - 156, 100, 156)
    if i == RIGHT:
        v.spot(r, [["give", "juice"], ["set", "b_juice", 1], ["sfx", "get"], ["msg", "ぶどうジュースを取った。"]], eq("b_juice", 0))
        v.spot(r, [["msg", "もう取った。"]])
    else:
        v.spot(r, [["cool", "b_lock", 30], ["sfx", "buzz"], ["shake"], ["msg", "ブーッ！ちがうみたい。30秒ロック。"]], eq("b_juice", 0))
        v.spot(r, [["msg", "今日は使わない。"]])

# ------------------------------------------------------------------ the sink wall
v = View("b3", 2, "流しの壁", l="b2", r="b4")
s = v.s
kitchen_wall(s, None)
s.frect(350, 60, 220, 150, "#cfe6ef", sw=2.6)
s.frect(350, 60, 220, 150, "#9fc7d8", op=0.4, outline=False)
s.line(460, 60, 460, 210, sw=2.4)
s.line(350, 135, 570, 135, sw=2)
counter(s, 0, W)
s.frect(330, 300, 240, 16, "#5d6a6c", sw=2)
s.frect(440, 262, 20, 40, STEEL, sw=2)
s.frect(404, 226, 56, 14, STEEL, sw=2)
s.frect(446, 226, 14, 40, STEEL, sw=2)
s.fell(452, 256, 9, 5, METAL_D, sw=1.4)
for x in (330, 450):
    s.frect(x, 330, 120, 82, "#6a5138", sw=2.2)
    s.fell(x + (106 if x == 330 else 14), 370, 4, 9, BRASS, sw=1.4)
for x in (20, 180, 600, 740):
    s.frect(x, 330, 130 if x < 600 else 120, 82, WOOD_D, sw=2)
# measuring jugs on the counter
s.frect(612, 254, 40, 46, "#dfe9ec", sw=2, op=0.6)
s.frect(664, 228, 52, 72, "#dfe9ec", sw=2, op=0.6)
s.text(632, 278, "3", 16)
s.text(690, 268, "5", 16)
# wall cupboard
s.frect(90, 70, 210, 150, WOOD_L, sw=2.6)
s.line(195, 70, 195, 220, sw=2.2)
s.fell(184, 150, 4, 8, BRASS, sw=1.4)
s.fell(206, 150, 4, 8, BRASS, sw=1.4)
s.vignette()


def cupboard_open(s):
    s.frect(90, 70, 210, 150, "#3a2a1c", sw=2.6)
    s.frect(96, 142, 198, 8, WOOD_L, sw=1.6)
    for x in (116, 146):
        s.fpoly([(x - 10, 134), (x + 10, 134), (x + 8, 112), (x - 8, 112)], WHITE, sw=1.4)
    for x in (230, 262):
        s.fpoly([(x - 10, 210), (x + 10, 210), (x + 8, 188), (x - 8, 188)], WHITE, sw=1.4)


def roux_box(s, x, y, w, h):
    s.frect(x, y, w, h, ORANGE, sw=2.2)
    s.frect(x + 4, y + h * 0.18, w - 8, h * 0.3, "#fff1c9", sw=1.4)
    s.text(x + w / 2, y + h * 0.33, "カレー", max(10, h * 0.2), RED)
    s.fell(x + w / 2, y + h * 0.72, w * 0.3, h * 0.13, CURRY_BROWN, sw=1.4)


v.variant("cup", (84, 64, 222, 162), ["ge", "b_cup", 1], cupboard_open)
v.variant("roux", (84, 64, 222, 162), all_(["ge", "b_cup", 1], eq("b_rx", 0)), lambda s: roux_box(s, 210, 92, 64, 46), deps=("cup",))
v.spot((410, 220, 70, 90), [["msg", "水が出ない。流しの下から、ゴボゴボ音がする。"]], eq("b_pipe", 0))
v.spot((410, 220, 70, 90), [["sfx", "water"], ["msg", "水が出る。はかるなら計量カップで。"]])
v.spot((330, 326, 240, 90), [["go", "b3pipe"]])
v.spot((600, 220, 130, 86), [["go", "b3jug"]])
v.spot((90, 70, 210, 150), [["set", "b_cup", 1], ["sfx", "door"]], eq("b_cup", 0))
v.spot((90, 70, 210, 150), [["give", "roux"], ["set", "b_rx", 1], ["sfx", "get"], ["msg", "カレールーの箱を取った。"]], eq("b_rx", 0))
v.spot((90, 70, 210, 150), [["msg", "コップしかない。"]])

# ------------------------------------------------------------------ the measuring jugs
SJ = (270, 220, 120, 180)  # small jug body: 3 cups of 60
BJ = (560, 100, 160, 300)  # big jug body: 5 cups of 60
SR = (258, 210, 144, 200)  # tap and swipe areas
BR = (548, 90, 184, 320)


def jug(s, box, cups, level, label, handle_left):
    x, y, w, h = box
    hx = x - 20 if handle_left else x + w
    s.frect(hx, y + 30, 20, 90, "#dfe9ec", sw=2, op=0.7)
    s.frect(x, y, w, h, "#dfe9ec", sw=2.6, op=0.45)
    if level:
        s.frect(x + 4, y + h - level * 60, w - 8, level * 60 - 3, WATER, op=0.85, outline=False)
        s.line(x + 4, y + h - level * 60, x + w - 4, y + h - level * 60, stroke=WATER_D, sw=2, passes=1)
    for k in range(1, cups):
        yy = y + h - k * 60
        s.line(x + (w - 34 if handle_left else 6), yy, x + (w - 6 if handle_left else 34), yy, sw=2, passes=1)
    s.rect(x, y, w, h, sw=2.6)
    s.paper(x + w / 2 - 44, y - 34, 88, 30, [(label, 16)], align="center", pin=False, pad=4)


v = View("b3jug", 2, "計量カップ", back="b3")
s = v.s
s.frect(0, 0, W, H, TILE, outline=False)
for y in range(40, 420, 40):
    s.line(0, y, W, y, sw=1.2, stroke=TILE_D, opacity=0.6, passes=1)
s.frect(180, 404, 640, 70, "#7d898b", sw=2.6)
s.frect(196, 404, 608, 20, "#5d6a6c", sw=1.6)
s.frect(0, 474, W, 66, "#b9a27a", sw=2.4)
s.frect(466, 0, 28, 120, STEEL, sw=2.2)
s.frect(456, 112, 48, 20, STEEL, sw=2)
s.fell(480, 136, 10, 5, METAL_D, sw=1.4)
jug(s, SJ, 3, 0, "3カップ", True)
jug(s, BJ, 5, 0, "5カップ", False)
s.paper(26, 40, 214, 118, [("タップ：水を入れる", 17), ("となりへなぞる：注ぐ", 17), ("下へなぞる：すてる", 17)], 17, gap=1.5, pad=10, pin=False)
s.vignette(0.12)
for k in range(1, 4):
    v.variant("s%d" % k, (SR[0], SR[1] - 30, SR[2], SR[3] + 30), eq("b_j3", k), lambda s, k=k: jug(s, SJ, 3, k, "3カップ", True))
for k in range(1, 6):
    v.variant("b%d" % k, (BR[0], BR[1] - 30, BR[2], BR[3] + 30), eq("b_j5", k), lambda s, k=k: jug(s, BJ, 5, k, "5カップ", False))
NOWATER = [["msg", "水が出ない。"]]
v.spot(BR, [["give", "mizu"], ["set", "b_mizu", 1], ["set", "b_j5", 0], ["sfx", "get"], ["msg", "ちょうど4カップ！ボウルに移した。"]],
       all_(eq("b_j5", 4), eq("b_mizu", 0)))
v.spot(SR, NOWATER, eq("b_pipe", 0))
v.spot(BR, NOWATER, eq("b_pipe", 0))
v.spot(SR, [["set", "b_j3", 3], ["sfx", "water"]])
v.spot(BR, [["set", "b_j5", 5], ["sfx", "water"]])
v.spot(SR, [["set", "b_j3", 0], ["sfx", "water"]], ["ge", "b_j3", 1], swipe=2)
v.spot(BR, [["set", "b_j5", 0], ["sfx", "water"]], ["ge", "b_j5", 1], swipe=2)
for a in range(1, 4):
    for b in range(0, 5):
        m = min(a, 5 - b)
        v.spot(SR, [["set", "b_j3", a - m], ["set", "b_j5", b + m], ["sfx", "water"]], all_(eq("b_j3", a), eq("b_j5", b)), swipe=1)
for b in range(1, 6):
    for a in range(0, 3):
        m = min(b, 3 - a)
        v.spot(BR, [["set", "b_j5", b - m], ["set", "b_j3", a + m], ["sfx", "water"]], all_(eq("b_j3", a), eq("b_j5", b)), swipe=3)
v.spot(SR, [["msg", "注げない。"]], swipe=1)
v.spot(BR, [["msg", "注げない。"]], swipe=3)

# ------------------------------------------------------------------ the pipes under the sink
TILE0, TS = (380, 120), 96
GRID = [["L", "I", "I"], ["I", "L", "L"], ["I", "L", "L"]]
ROT0 = {(0, 0): 2, (0, 1): 1, (0, 2): 0, (1, 0): 0, (1, 1): 2, (1, 2): 1, (2, 0): 1, (2, 1): 0, (2, 2): 0}
GOOD = {(2, 0): (0, 2), (2, 1): (3,), (1, 1): (1,), (1, 2): (3,), (0, 2): (1, 3)}
SOLVED = {(2, 0): 0, (2, 1): 3, (1, 1): 1, (1, 2): 3, (0, 2): 1}
DIRS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
CONN = {"L": [("N", "E"), ("E", "S"), ("S", "W"), ("W", "N")], "I": [("W", "E"), ("N", "S"), ("W", "E"), ("N", "S")]}


def tflag(r, c):
    return "b_t%d%d" % (r, c)


for (r, c), k in ROT0.items():
    INIT["f"][tflag(r, c)] = k


def pipe_tile(s, r, c, rot, water=False):
    x0, y0 = TILE0[0] + c * TS, TILE0[1] + r * TS
    cx, cy = x0 + TS / 2, y0 + TS / 2
    s.frect(x0 + 3, y0 + 3, TS - 6, TS - 6, "#3d2e22", sw=1.6)
    for band, col in ((15, "#9aa6a8"), (7, WATER if water else "#5b6668")):
        for d in CONN[GRID[r][c]][rot]:
            dx, dy = DIRS[d]
            if dx:
                s.frect(min(cx, cx + dx * TS / 2), cy - band, TS / 2, band * 2, col, sw=2.2 if band > 10 else 1, outline=band > 10)
            else:
                s.frect(cx - band, min(cy, cy + dy * TS / 2), band * 2, TS / 2, col, sw=2.2 if band > 10 else 1, outline=band > 10)
        s.fell(cx, cy, band + 3, band + 3, col, sw=2.2 if band > 10 else 1, outline=band > 10)


v = View("b3pipe", 2, "流しの下", back="b3")
s = v.s
s.frect(0, 0, W, H, "#2b2119", outline=False)
s.fpoly([(0, 0), (330, 40), (330, 500), (0, 540)], "#4a3726", outline=False)
s.line(330, 40, 330, 500, sw=2.4)
s.line(330, 500, W, 500, sw=2.4)
# the cipher table on the side wall
s.frect(36, 66, 280, 300, PAPER_L, sw=2.2)
s.text(176, 88, "芽と目のひょう", 20)
for i in range(6):
    s.line(52, 118 + i * 48, 292, 118 + i * 48, sw=1.6, passes=1)
    s.line(52 + i * 48, 118, 52 + i * 48, 358, sw=1.6, passes=1)
for k in range(1, 5):
    potato(s, 76 + k * 48, 146, 14, 10, k, 0)
    potato(s, 76, 142 + k * 48, 14, 10, 0, k)
for r in range(4):
    for c in range(4):
        s.text(124 + c * 48, 190 + r * 48, TABLE[r][c], 24)
s.text(176, 380, "（博士の らくがき）", 15, TXT)
# pipes coming in and going out
s.frect(330, 345, 56, 30, "#9aa6a8", sw=2.2)
s.fell(352, 360, 18, 18, RED, sw=2)
s.frect(605, 0, 30, 126, "#9aa6a8", sw=2.2)
s.frect(374, 114, 300, 300, "#1f1812", sw=2.4)
s.paper(700, 150, 150, 92, [("マスをタップ", 16), ("すると回る", 16)], align="center", gap=1.4, pin=False, pad=12)
s.vignette()
for (r, c) in ROT0:
    for k in range(4):
        x0, y0 = TILE0[0] + c * TS, TILE0[1] + r * TS
        v.variant("t%d%d_%d" % (r, c, k), (x0, y0, TS, TS), eq(tflag(r, c), k), lambda s, r=r, c=c, k=k: pipe_tile(s, r, c, k))
for (r, c), k in SOLVED.items():
    x0, y0 = TILE0[0] + c * TS, TILE0[1] + r * TS
    v.variant("w%d%d" % (r, c), (x0, y0, TS, TS), eq("b_pipe", 1), lambda s, r=r, c=c, k=k: pipe_tile(s, r, c, k, True))
PIPE_OK = all_(*[any_(*[eq(tflag(r, c), k) for k in ks]) for (r, c), ks in GOOD.items()])
for (r, c) in ROT0:
    x0, y0 = TILE0[0] + c * TS, TILE0[1] + r * TS
    v.spot((x0, y0, TS, TS), [["cyc", tflag(r, c), 4], ["sfx", "tick"],
                              ["if", PIPE_OK, [["set", "b_pipe", 1], ["sfx", "water"], ["msg", "ゴボゴボ…水が流れた！"]]]], eq("b_pipe", 0))
v.spot((374, 114, 300, 300), [["msg", "水が流れている。"]])

# ------------------------------------------------------------------ the fridge wall
v = View("b4", 2, "冷蔵庫の壁", l="b3", r="b1")
s = v.s
kitchen_wall(s, 560)
counter(s, 380, W)
s.frect(110, 40, 220, 380, FRIDGE, sw=2.8)
s.line(110, 150, 330, 150, sw=2.4)
s.frect(126, 80, 12, 50, FRIDGE_D, sw=1.6)
s.frect(126, 170, 12, 120, FRIDGE_D, sw=1.6)
s.frect(160, 176, 70, 80, PAPER_L, sw=1.4)
for x, y, col in ((260, 180, GREEN), (290, 214, BLUE_L), (296, 252, "#8a8a8a"), (250, 236, LIGHT)):
    s.fell(x, y, 8, 8, col, sw=1.2)
s.frect(250, 330, 60, 30, "#2a3133", sw=1.6)
s.frect(420, 80, 100, 120, PAPER_L, sw=2.2)
s.text(470, 100, "11月", 18)
for i in range(12):
    s.rect(430 + (i % 4) * 21, 118 + (i // 4) * 24, 18, 20, sw=1, passes=1)
s.ellipse(491, 166, 9, 9, stroke=RED_L, sw=2.4)
s.frect(620, 70, 190, 150, "#cfe6ef", sw=2.6)
for y in range(84, 220, 14):
    s.line(624, y, 806, y, sw=1.6, passes=1)
# potato basket
s.fpoly([(560, 300), (700, 300), (684, 250), (576, 250)], "#a77b4f", sw=2.4)
for x, y in ((600, 244), (630, 240), (660, 246), (614, 232), (646, 230)):
    potato(s, x, y, 16, 12, 0, 2)
s.fpoly([(560, 300), (700, 300), (690, 268), (570, 268)], "#a77b4f", sw=2.4)
s.vignette()
v.variant("unlocked", (244, 324, 72, 42), eq("b_fridge", 1), lambda s: (
    s.frect(250, 330, 60, 30, "#2a3133", sw=1.6), s.fell(280, 345, 7, 7, "#7fe08a", sw=1.6)))
v.spot((110, 150, 220, 270), [["go", "b4door"]], eq("b_fridge", 0))
v.spot((110, 150, 220, 270), [["go", "b4in"]])
v.spot((110, 40, 220, 110), [["msg", "冷凍庫。アイスしか入っていない。"]])
v.spot((556, 220, 150, 84), [["give", "imo"], ["set", "b_imo", 1], ["sfx", "get"], ["msg", "じゃがいもを1つ取った。"]], eq("b_imo", 0))
v.spot((556, 220, 150, 84), [["msg", "じゃがいもは 1つで足りる。"]])
v.spot((420, 80, 100, 120), [["msg", "カレンダー。今日のところに『カレーの日』。"]])

# ------------------------------------------------------------------ the fridge door
v = View("b4door", 2, "冷蔵庫のとびら", back="b4")
s = v.s
s.frect(0, 0, W, H, TILE_D, outline=False)
s.frect(180, 14, 600, 512, FRIDGE, sw=3)
s.frect(188, 120, 14, 280, FRIDGE_D, sw=1.8)
s.raw('<g transform="translate(200 30)">')
door_content(s, False)
s.raw("</g>")
s.vignette(0.12)
DIFFS = [((508, 62, 64, 64), (540, 94, 36, 36)), ((628, 92, 64, 64), (660, 124, 36, 36)), ((524, 342, 120, 26), (584, 355, 72, 22))]
DF_ALL = all_(*[eq("b_df%d" % (i + 1), 1) for i in range(3)])
for i, (spot, (cx, cy, rx, ry)) in enumerate(DIFFS):
    flag = "b_df%d" % (i + 1)
    v.variant("ring%d" % i, (cx - rx - 8, cy - ry - 8, rx * 2 + 16, ry * 2 + 16), eq(flag, 1),
              lambda s, cx=cx, cy=cy, rx=rx, ry=ry: s.ellipse(cx, cy, rx, ry, stroke=RED_L, sw=4))
    v.variant("lamp%d" % i, (588 + i * 40, 474, 24, 24), eq(flag, 1), lambda s, i=i: (
        s.glow(600 + i * 40, 486, 14, "#7fe08a", 0.2), s.fell(600 + i * 40, 486, 7, 7, "#7fe08a", sw=1.6)))
    v.spot(spot, [["set", flag, 1], ["sfx", "ok"],
                  ["if", DF_ALL, [["set", "b_fridge", 1], ["msg", "カチャ。冷蔵庫のロックが外れた！"]], [["msg", "ここがちがう！"]]]],
           all_(eq(flag, 0), eq("b_fridge", 0)))
v.spot((180, 14, 600, 512), [["msg", "写真と同じに見える。"]], eq("b_fridge", 0))
v.spot((180, 14, 600, 512), [["go", "b4in"]])

# ------------------------------------------------------------------ inside the fridge
v = View("b4in", 2, "冷蔵庫の中", back="b4")
s = v.s
s.frect(0, 0, W, H, "#3c4a4d", outline=False)
s.frect(170, 10, 620, 520, "#eef3f3", sw=3)
for y in (180, 350):
    s.frect(178, y, 604, 10, "#c9dadd", sw=1.6, op=0.9)
s.glow(480, 30, 120, "#ffffff", 0.08, 4)
# milk and eggs (not needed)
s.frect(640, 230, 70, 120, WHITE, sw=2.2)
s.fpoly([(640, 230), (710, 230), (690, 200), (660, 200)], "#d9e6f0", sw=2)
s.text(675, 290, "牛乳", 18)
for i in range(4):
    s.fell(250 + i * 44, 495, 18, 22, "#f3ead7", sw=1.8)
s.vignette(0.1)


def carrot(s, cx, cy, k=1.0):
    s.fpoly([(cx - 46 * k, cy - 10 * k), (cx + 40 * k, cy - 4 * k), (cx + 40 * k, cy + 6 * k), (cx - 46 * k, cy + 12 * k)], ORANGE, sw=2)
    s.fpoly([(cx - 46 * k, cy - 10 * k), (cx - 64 * k, cy - 26 * k), (cx - 58 * k, cy), (cx - 66 * k, cy + 22 * k), (cx - 46 * k, cy + 12 * k)],
            GREEN, sw=1.6)


def onion(s, cx, cy, k=1.0):
    s.fell(cx, cy, 30 * k, 28 * k, "#d9b878", sw=2.2)
    s.fpoly([(cx - 6 * k, cy - 26 * k), (cx, cy - 46 * k), (cx + 6 * k, cy - 26 * k)], "#b98f4c", sw=1.6)
    s.curve([(cx - 14 * k, cy - 20 * k), (cx - 20 * k, cy), (cx - 12 * k, cy + 22 * k)], sw=1.2, passes=1)


v.variant("ninjin", (200, 100, 200, 90), eq("b_nin", 0), lambda s: carrot(s, 300, 150, 1.4))
v.variant("tamanegi", (430, 80, 140, 110), eq("b_tam", 0), lambda s: onion(s, 500, 146, 1.3))
v.spot((200, 100, 200, 90), [["give", "ninjin"], ["set", "b_nin", 1], ["sfx", "get"]], eq("b_nin", 0))
v.spot((430, 80, 140, 110), [["give", "tamanegi"], ["set", "b_tam", 1], ["sfx", "get"]], eq("b_tam", 0))
v.spot((620, 190, 110, 170), [["msg", "牛乳。今日は使わない。"]])
v.spot((220, 460, 200, 70), [["msg", "たまご。今日は使わない。"]])

# ------------------------------------------------------------------ things to hold


def bowl_icon(s):
    s.fpoly([(14, 46), (82, 46), (70, 76), (26, 76)], "#e8e2d2", sw=2.2)
    s.fell(48, 46, 34, 9, WATER, sw=2)


def jar_icon(s, col, label=None):
    s.fpoly([(32, 86), (64, 86), (64, 46), (56, 34), (56, 14), (40, 14), (40, 34), (32, 46)], "#dfe9ec", sw=2, op=0.7)
    s.frect(35, 50, 26, 34, col, sw=1.4)


def roux_zoom(s):
    s.frect(0, 0, 480, 360, "#3a2a1c", outline=False)
    roux_box(s, 110, 50, 260, 260)
    s.text(240, 30, "カレールー（表）", 20, TXT)


def roux_back(s):
    s.frect(0, 0, 480, 360, "#3a2a1c", outline=False)
    s.frect(110, 50, 260, 260, ORANGE, sw=2.4)
    s.paper(126, 66, 228, 228, [("作り方", 22), "1 具を やわらかく", "　煮る", "2 火を止めてから", "　ルーを入れる", "3 よくまぜる"], 18,
            color="#fff1c9", gap=1.35, pin=False, pad=10)
    s.text(240, 30, "カレールー（うら）", 20, TXT)


def pot_icon(s):
    s.fpoly([(18, 44), (78, 44), (74, 82), (22, 82)], METAL, sw=2.2)
    s.fell(48, 44, 32, 9, PURPLE, sw=2)
    s.frect(8, 52, 10, 8, METAL_D, sw=1.4)
    s.frect(78, 52, 10, 8, METAL_D, sw=1.4)


item("mizu", bowl_icon, "水（4カップ）", ["計量カップで、ちょうど4カップ。"])
item("imo", lambda s: potato(s, 48, 50, 30, 22, 0, 3), "じゃがいも", ["カゴに入っていた。"])
item("ninjin", lambda s: carrot(s, 54, 50, 0.7), "にんじん", ["冷蔵庫に入っていた。"])
item("tamanegi", lambda s: onion(s, 48, 56, 0.9), "たまねぎ", ["冷蔵庫に入っていた。"])
item("roux", lambda s: roux_box(s, 20, 20, 56, 56), "カレールー", ["箱のうらにも 何か書いてある。"], zoom=roux_zoom, back=roux_back)
item("juice", lambda s: jar_icon(s, PURPLE), "ぶどうジュース", ["スパイス棚にあった。"])
item("curry", pot_icon, "カレーのなべ", ["むらさき色のカレー。"])

# ------------------------------------------------------------------ puzzles
puzzle("q1", 2, "流しの下の水道管", None, eq("b_pipe", 1),
       ["流しの水が出ない。流しの下の戸棚を見てみよう。",
        "管のマスをタップすると回る。左下から入る水を、右上の出口までつなぐ。",
        "左下は横まっすぐ。その右は左と上、真ん中は下と右、右の真ん中は左と上、右上は たてまっすぐ。"],
       "左下から 右・上・右・上 とつなぐ", [["set", tflag(r, c), k] for (r, c), k in SOLVED.items()] + [["set", "b_pipe", 1]])
puzzle("q2", 2, "4カップの水", eq("b_pipe", 1), any_(eq("b_mizu", 1), ["ge", "b_pot", 1]),
       ["冷蔵庫の壁のレシピには『水 4カップ』。計量カップは 3カップと5カップ。",
        "カップは、タップで満タン、となりへなぞると注ぐ、下へなぞると すてる。",
        "5を満タン→3へ注ぐ→3をすてる→5の残り2を3へ→5を満タン→3がいっぱいになるまで注ぐと、5に4残る。"],
       "5カップのほうに 4カップ残す", [["set", "b_j3", 0], ["set", "b_j5", 0], ["set", "b_mizu", 1], ["give", "mizu"]])
puzzle("q3", 2, "冷蔵庫のロック", None, eq("b_fridge", 1),
       ["冷蔵庫のロック：写真とちがうところを3つタッチ。写真は、エレベーターの壁の掲示板。",
        "マグネットとメモを、写真と見くらべよう。",
        "リンゴの色、星のマグネット（写真にはある）、メモの『たまご』。"],
       "リンゴ・星のあった場所・メモのたまご", [["set", "b_df1", 1], ["set", "b_df2", 1], ["set", "b_df3", 1], ["set", "b_fridge", 1]])
puzzle("q5", 2, "カレーを煮る", all_(eq("b_fridge", 1), eq("b_mizu", 1)), ["ge", "b_pot", 6],
       ["なべに水と、じゃがいも・にんじん・たまねぎを入れて、つまみで火をつける。",
        "ルーの箱を選んで、もう一度タップ。大きくして裏返すと、入れ方が書いてある。",
        "具が煮えたら、火を止めてからルーを入れる。"],
       "火を止めてから ルー",
       [["takeall", i] for i in ("mizu", "imo", "ninjin", "tamanegi", "roux")]
       + [["set", f_, 1] for f_ in ("b_imo", "b_nin", "b_tam", "b_cup", "b_rx")] + [["set", "b_pot", 6], ["set", "b_fire", 0]])
puzzle("q4", 2, "かくし味", None, ["ge", "b_pot", 7],
       ["レシピのかくし味は、芽と目のある いもの絵。読み方の表が どこかにある。",
        "流しの下の『芽と目のひょう』。芽の数で たて、目の数で 横を見る。",
        "芽2・目1＝ぶ、芽3・目2＝ど、芽1・目3＝う。スパイス棚の『ぶどう』を、ルーのあとに入れる。"],
       "ぶどう", [["set", "b_juice", 1], ["takeall", "juice"],
                  ["if", eq("b_pot", 6), [["set", "b_pot", 7]], [["give", "juice"]]]])
