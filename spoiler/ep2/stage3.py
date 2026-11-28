"""Episode 2, stage 3: the boss's office."""
from ep2.look import *  # noqa: F401,F403
from ep2.story import GRADE

STAGE3_ITEMS = ["card", "hanko", "sheet2"]
LAND, SEA = "#86ad5c", "#4f86a8"
DARK = eq("c_dark", 1)
DARK_MSG = [["msg", "暗くて よく見えない。"]]

# continents, roughly, in a -1..1 box
CONT = {
    "EU": [(-0.85, 0.45), (-0.55, 0.35), (-0.6, 0.0), (-0.3, -0.2), (-0.35, -0.6), (-0.05, -0.95), (0.25, -0.8), (0.15, -0.45),
           (0.45, -0.55), (0.9, -0.2), (0.75, 0.25), (0.45, 0.3), (0.35, 0.8), (0.15, 0.5), (-0.05, 0.45), (-0.3, 0.75), (-0.6, 0.7)],
    "AF": [(-0.55, -0.9), (0.05, -0.95), (0.35, -0.75), (0.55, -0.5), (0.9, -0.35), (0.65, 0.0), (0.55, 0.35), (0.3, 0.7), (0.1, 0.95),
           (-0.05, 0.75), (-0.05, 0.35), (-0.2, 0.05), (-0.6, -0.05), (-0.9, -0.3), (-0.85, -0.65)],
    "AS": [(-0.95, -0.35), (-0.55, -0.75), (0.0, -0.9), (0.6, -0.85), (0.95, -0.55), (0.85, -0.15), (0.65, 0.15), (0.75, 0.4), (0.45, 0.5),
           (0.35, 0.85), (0.15, 0.5), (-0.05, 0.45), (-0.2, 0.85), (-0.35, 0.45), (-0.65, 0.35), (-0.8, 0.05)],
    "AU": [(-0.9, -0.15), (-0.55, -0.5), (-0.2, -0.55), (-0.05, -0.3), (0.15, -0.75), (0.45, -0.55), (0.75, -0.2), (0.9, 0.2), (0.7, 0.55),
           (0.3, 0.7), (-0.1, 0.5), (-0.45, 0.6), (-0.85, 0.4)],
    "NA": [(-0.95, -0.55), (-0.7, -0.85), (-0.2, -0.8), (0.2, -0.95), (0.7, -0.9), (0.95, -0.55), (0.6, -0.3), (0.55, 0.0), (0.3, 0.25),
           (0.35, 0.55), (0.2, 0.5), (0.0, 0.75), (-0.15, 0.95), (-0.3, 0.7), (-0.5, 0.3), (-0.7, -0.1), (-0.9, -0.25)],
    "SA": [(-0.55, -0.85), (-0.1, -0.95), (0.3, -0.75), (0.75, -0.45), (0.85, -0.2), (0.55, 0.15), (0.3, 0.35), (0.1, 0.65), (-0.05, 0.95),
           (-0.2, 0.8), (-0.25, 0.45), (-0.35, 0.05), (-0.65, -0.3), (-0.75, -0.6)],
}
FACES = ["EU", "AF", "AS", "AU", "NA", "SA"]  # globe faces in order of a swipe to the left
HOME = FACES.index("SA")
SIZE = {"EU": (88, 80), "AF": (100, 120), "AS": (130, 100), "AU": (100, 80), "NA": (120, 110), "SA": (72, 124)}
ON_MAP = {"NA": (528, 128, 46, 40), "SA": (566, 206, 24, 38), "EU": (640, 112, 20, 18), "AF": (648, 186, 28, 34),
          "AS": (716, 122, 44, 34), "AU": (734, 214, 20, 16)}
# books: 2 rows of 6; three carry a sticker that glows in the dark
BOOK_X = [166 + i * 74 for i in range(6)]
BOOK_ROW = [(92, 206), (232, 346)]
BOOK_H = [104, 92, 110, 86, 100, 96, 98, 108, 90, 104, 88, 100]
BOOK_C = [RED, BLUE, GREEN, "#7b4a9a", ORANGE, WOOD_L, BLUE_L, "#5a3a22", RED_L, "#3f6f5f", "#a77b4f", PURPLE]
MARKED = (1, 8, 10)
# the word search in the newspaper, and the holes of the card
GR, GC, CELL, G0 = 6, 8, 44, (488, 212)
MESSAGE = "いものふるさとをおせ"
HOLES = [(0, 1), (0, 5), (1, 2), (1, 6), (2, 0), (2, 4), (3, 3), (3, 7), (4, 1), (5, 5)]
FILL = "けまちへくよねりむあえゆぬほてれかひこみなろつすやうしきわはそにたんめらねく"


def bflag(i):
    return "c_bk%d" % i


def book_rect(i):
    x = BOOK_X[i % 6]
    y0, y1 = BOOK_ROW[i // 6]
    return x + 6, y1 - BOOK_H[i], 60, BOOK_H[i]


def book(s, i, pulled=False):
    x, y, w, h = book_rect(i)
    if pulled:
        s.frect(x, y, w, 8, "#140d08", outline=False)
        y += 8
        s.frect(x - 3, y, w + 6, h, BOOK_C[i], sw=2.4)
        s.frect(x - 3, y + h - 6, w + 6, 6, "#1a120c", outline=False)
    else:
        s.frect(x, y, w, h, BOOK_C[i], sw=2)
    for yy in (y + 14, y + h - 18):
        s.line(x + 4, yy, x + w - 4, yy, sw=1.6, stroke=PAPER_L, opacity=0.7, passes=1)


def grid_letter(r, c):
    if (r, c) in HOLES:
        return MESSAGE[HOLES.index((r, c))]
    k = sum(1 for rr in range(GR) for cc in range(GC) if (rr, cc) not in HOLES and (rr, cc) < (r, c))
    return FILL[k]


def continent(s, key, cx, cy, rx, ry, color=LAND, sw=2):
    s.fpoly([(cx + x * rx, cy + y * ry) for x, y in CONT[key]], color, sw=sw)


def robot(s, x, y, eyes="#7fe0ff"):
    s.frect(x + 4, y - 110, 16, 50, METAL, sw=2)
    s.frect(x + 120, y - 110, 16, 50, METAL, sw=2)
    s.frect(x + 20, y - 124, 100, 96, "#c9cfd1", sw=2.6)
    s.paper(x + 36, y - 100, 68, 28, [("面談係", 15)], align="center", pin=False, pad=3)
    s.frect(x + 30, y - 206, 80, 74, "#c9cfd1", sw=2.6)
    s.frect(x + 40, y - 196, 60, 46, "#1d2a2e", sw=2)
    s.fell(x + 58, y - 176, 6, 6, eyes, outline=False)
    s.fell(x + 82, y - 176, 6, 6, eyes, outline=False)
    s.line(x + 60, y - 160, x + 80, y - 160, stroke=eyes, sw=2, passes=1)
    s.line(x + 70, y - 206, x + 70, y - 226, sw=2.4)
    s.dot(x + 70, y - 228, 5, RED_L)
    for wx in (x + 42, x + 98):
        s.fell(wx, y - 18, 15, 15, METAL_D, sw=2.2)


# ------------------------------------------------------------------ the exit wall
v = View("c1", 3, "出口の壁", l="c4", r="c2")
s = v.s
office(s, 480)
s.frect(380, 90, 200, 320, WOOD_D, sw=2.8)
s.frect(398, 110, 164, 130, WOOD, sw=2)
s.frect(398, 256, 164, 130, WOOD, sw=2)
s.fell(552, 260, 8, 8, BRASS, sw=2)
s.paper(430, 52, 100, 32, [("出口", 19)], align="center", pin=False, pad=4)
robot(s, 240, 410)
s.frect(640, 216, 44, 70, PAPER_L, sw=2.2)
s.frect(655, 232, 14, 38, "#d9d6cc", sw=1.6)
s.fell(662, 240, 6, 6, WHITE, sw=1.4)
s.frect(66, 64, 170, 236, WOOD_L, sw=2.6)
s.paper(76, 74, 150, 216, [("社訓", 19), "1 おおきな声で", "　あいさつ", "2 つかれたら", "　すわって休む", "3 かたづけは", "　使った人が",
                           "4 れいぞうこは", "　すぐしめる"], 14, color=PAPER_L, gap=1.22, pad=8, pin=False)
s.line(760, 100, 760, 410, sw=4)
s.line(730, 410, 790, 410, sw=4)
s.fpoly([(740, 120), (780, 120), (800, 300), (722, 300)], WHITE, sw=2.2)
s.vignette()


def c1_dark(s):
    darkness(s)
    s.glow(662, 250, 46, "#a8ffb8", 0.12, 4)
    s.frect(640, 216, 44, 70, "#5f8a6a", sw=1.6)
    s.frect(655, 232, 14, 38, "#a8ffb8", outline=False)
    s.fell(298, 234, 6, 6, "#7fe0ff", outline=False)
    s.fell(322, 234, 6, 6, "#7fe0ff", outline=False)


v.variant("dark", (0, 0, W, H), DARK, c1_dark)
TIDY = all_(*[eq(bflag(i), 0) for i in range(12)], ne("c_drawer", 1), ne("c_globe", 1))
ROBOT = (246, 176, 132, 236)
v.spot((630, 206, 64, 90), [["if", eq("c_dark", 0), [["set", "c_dark", 1], ["msg", "明かりを消した。"]], [["set", "c_dark", 0], ["msg", "明かりをつけた。"]]],
                            ["sfx", "tick"]])
v.spot(ROBOT, [["msg", "ロボット『暗いですね。明かりを つけてください』"]], DARK)
v.spot(ROBOT, [["takeall", i] for i in STAGE3_ITEMS] + [["set", "c_end", 1], ["sfx", "ok"]] + GRADE, all_(["sel", "sheet2"], TIDY))
v.spot(ROBOT, [["sfx", "buzz"], ["msg", "ロボット『社訓の3つめを 守っていない人とは、面談できません』"]], ["sel", "sheet2"])
v.spot(ROBOT, [["msg", "ロボット『ハンコを押したシートを、わたしてください』"]], eq("c_stamp", 1))
v.spot(ROBOT, [["msg", "ロボット『退職面談シートに 博士のハンコを押して、持ってきてください』"]])
v.spot((0, 0, W, H), DARK_MSG, DARK)
v.spot((380, 90, 200, 320), [["msg", "出口。ロボットが前に立っている。"]])
v.spot((66, 64, 170, 236), [["msg", "社訓の額。"]])
v.spot((720, 100, 84, 210), [["msg", "博士の白衣。ポケットは空っぽ。"]])

# ------------------------------------------------------------------ the desk wall
v = View("c2", 3, "机の壁", l="c1", r="c3")
s = v.s
office(s, 480)
s.paper(110, 84, 190, 116, [("博士メモ", 19), ("夜に読む本には、", 16), ("光るシールを はった", 16)], 16, color=PAPER_L, gap=1.45, pad=10)
s.frect(420, 80, 120, 130, WOOD_L, sw=2.4)
s.frect(432, 92, 96, 106, "#d9e6f0", sw=1.6)
s.fell(480, 150, 30, 24, POTATO, sw=2)
s.ellipse(468, 146, 9, 7, sw=1.8)
s.ellipse(492, 146, 9, 7, sw=1.8)
s.line(477, 146, 483, 146, sw=1.6, passes=1)
s.frect(180, 270, 540, 20, WOOD_L, sw=2.6)
s.frect(196, 290, 508, 120, WOOD, sw=2.4)
for x in (210, 510):
    s.frect(x, 304, 180, 40, WOOD_D, sw=1.8)
    s.fell(x + 90, 324, 10, 4, BRASS, sw=1.4)
s.fpoly([(250, 270), (370, 270), (366, 262), (254, 262)], PAPER_L, sw=1.6)
s.fpoly([(470, 270), (640, 270), (632, 258), (478, 258)], "#d8d4c6", sw=1.6)
s.frect(660, 196, 10, 66, METAL_D, sw=1.6)
s.fpoly([(640, 196), (700, 196), (690, 176), (650, 176)], GREEN, sw=2)
s.vignette()
v.variant("dark", (0, 0, W, H), DARK, darkness)
v.spot((0, 0, W, H), DARK_MSG, DARK)
v.spot((180, 236, 540, 60), [["go", "c2desk"]])
v.spot((110, 84, 190, 116), [["msg", "博士のメモ。"]])
v.spot((420, 80, 120, 130), [["msg", "博士の写真。…じゃがいもにしか見えない。"]])

# ------------------------------------------------------------------ the desk top
v = View("c2desk", 3, "机の上", back="c2")
s = v.s
s.frect(0, 0, W, H, WOOD, outline=False)
for y in range(30, H, 60):
    s.line(0, y, W, y + 6, sw=1.4, stroke=WOOD_D, opacity=0.6, passes=1)
s.paper(70, 40, 340, 450, [("退職面談シート", 26), "氏名：＿＿＿＿＿＿", "　　　＿＿＿＿＿＿", "働いた場所：", "　倉庫・台所・社長室", "今日の仕事：",
                           "　仕分け・昼ごはん"], 19, color=PAPER_L, gap=1.6, pad=18, pin=False)
s.text(250, 440, "社長印 →", 18)
s.rect(300, 400, 80, 80, sw=2, stroke=RED)
s.frect(466, 40, 396, 454, "#e6e2d4", sw=2.4)
s.text(664, 74, "博士新聞", 30)
s.line(480, 100, 848, 100, sw=2)
for k in range(5):
    s.frect(484, 114 + k * 14, 360 - (k % 2) * 60, 6, "#b9b4a4", outline=False)
s.text(664, 194, "もじさがし", 18)
for r in range(GR):
    for c in range(GC):
        s.text(G0[0] + c * CELL + CELL / 2, G0[1] + r * CELL + CELL / 2, grid_letter(r, c), 24)
s.rect(G0[0], G0[1], GC * CELL, GR * CELL, sw=1.6)
s.vignette(0.12)


def stamp_mark(s, cx, cy, r=30):
    s.ellipse(cx, cy, r, r, stroke=RED_L, sw=3.2)
    s.text(cx, cy, "博士", r * 0.7, RED_L)


def card_over(s):
    x0, y0, w, h = G0[0] - 10, G0[1] - 10, GC * CELL + 20, GR * CELL + 20
    d = "M%s %sH%sV%sH%sZ" % (f(x0), f(y0), f(x0 + w), f(y0 + h), f(x0))
    for r, c in HOLES:
        hx, hy = G0[0] + c * CELL + 4, G0[1] + r * CELL + 4
        d += "M%s %sH%sV%sH%sZ" % (f(hx), f(hy), f(hx + CELL - 8), f(hy + CELL - 8), f(hx))
    s.raw('<path d="%s" fill="#4d4740" fill-rule="evenodd"/>' % d)
    s.rect(x0, y0, w, h, sw=2.4)
    for r, c in HOLES:
        s.rect(G0[0] + c * CELL + 4, G0[1] + r * CELL + 4, CELL - 8, CELL - 8, sw=1.6)


v.variant("stamp", (300, 400, 80, 80), eq("c_stamp", 1), lambda s: stamp_mark(s, 340, 440))
v.variant("taken", (60, 30, 360, 470), eq("c_sheet", 1), lambda s: (
    s.frect(60, 30, 360, 470, WOOD, outline=False), [s.line(60, y, 420, y + 3, sw=1.4, stroke=WOOD_D, opacity=0.6, passes=1) for y in range(30, 500, 60)]))
v.variant("card", (G0[0] - 16, G0[1] - 16, GC * CELL + 32, GR * CELL + 32), eq("c_ov", 1), card_over)
v.variant("dark", (0, 0, W, H), DARK, darkness)
v.spot((0, 0, W, H), [["msg", "暗くて読めない。"]], DARK)
v.spot((300, 400, 80, 80), [["takeall", "hanko"], ["set", "c_stamp", 1], ["sfx", "plop"], ["unsel"], ["msg", "ポン！ハンコを押した。"]],
       all_(["sel", "hanko"], eq("c_stamp", 0)))
v.spot((70, 40, 340, 450), [["give", "sheet2"], ["set", "c_sheet", 1], ["sfx", "get"], ["msg", "シートを持った。"]], all_(eq("c_stamp", 1), eq("c_sheet", 0)))
v.spot((70, 40, 340, 450), [["msg", "退職面談シート。『社長印』のらんが空いている。"]], eq("c_stamp", 0))
v.spot((466, 40, 396, 454), [["take", "card"], ["set", "c_ov", 1], ["set", "c_seen", 1], ["sfx", "tick"], ["unsel"], ["msg", "カードを重ねた。穴から文字が見える。"]],
       all_(["sel", "card"], eq("c_ov", 0)))
v.spot((466, 40, 396, 454), [["give", "card"], ["set", "c_ov", 0], ["sfx", "tick"], ["msg", "カードを取った。"]], eq("c_ov", 1))
v.spot((466, 40, 396, 454), [["msg", "新聞のすみに『もじさがし』。ひらがなが びっしり。"]])

# ------------------------------------------------------------------ the bookshelf wall
v = View("c3", 3, "本棚の壁", l="c2", r="c4")
s = v.s
office(s, 420)
s.frect(150, 64, 472, 346, WOOD_D, sw=2.8)
for y0, y1 in BOOK_ROW:
    s.frect(160, y0 - 10, 452, y1 - y0 + 10, "#2a1d14", outline=False)
    s.frect(156, y1, 460, 10, WOOD_L, sw=2)
s.frect(160, 356, 452, 50, WOOD, sw=2)
s.frect(290, 362, 192, 40, WOOD_L, sw=2.2)
s.fell(386, 382, 12, 5, BRASS, sw=1.6)
for i in range(12):
    book(s, i)
s.frect(722, 300, 46, 110, WOOD_D, sw=2.2)
s.fpoly([(700, 410), (790, 410), (770, 396), (720, 396)], WOOD_D, sw=2)
s.fell(745, 230, 58, 58, SEA, sw=2.6)
continent(s, "EU", 745, 222, 28, 26)
s.ellipse(745, 230, 66, 66, sw=2.2)
s.vignette()
for i in range(12):
    x, y, w, h = book_rect(i)
    v.variant("pull%d" % i, (x - 6, y - 4, w + 12, h + 14), eq(bflag(i), 1), lambda s, i=i: book(s, i, True))
v.variant("drawer", (284, 356, 204, 54), ["ge", "c_drawer", 1], lambda s: (
    s.frect(284, 362, 204, 46, WOOD_L, sw=2.2), s.frect(294, 364, 184, 18, "#1a120c", sw=1.4), s.fell(386, 396, 12, 5, BRASS, sw=1.6)))
v.variant("card", (284, 356, 204, 54), all_(eq("c_drawer", 1), eq("c_card", 0)), lambda s: s.frect(330, 366, 70, 14, "#4d4740", sw=1.4),
          deps=("drawer",))
v.variant("shut", (284, 356, 204, 54), eq("c_drawer", 2), lambda s: (
    s.frect(290, 362, 192, 40, WOOD_L, sw=2.2), s.fell(386, 382, 12, 5, BRASS, sw=1.6)))
v.variant("globe", (676, 160, 140, 140), eq("c_globe", 1), lambda s: (
    s.fell(745, 230, 66, 66, WOOD, outline=False), s.fell(718, 232, 40, 56, SEA, sw=2.2), s.fell(772, 232, 40, 56, SEA, sw=2.2),
    s.fell(745, 232, 14, 50, "#1a120c", outline=False)))


def c3_dark(s):
    darkness(s)
    for i in MARKED:
        x, y, w, h = book_rect(i)
        glow_mark(s, x + w / 2, y + h / 2)


v.variant("dark", (0, 0, W, H), DARK, c3_dark)
DRAWER_OPENS = ["if", all_(eq("c_drawer", 0), *[eq(bflag(i), 1 if i in MARKED else 0) for i in range(12)]),
                [["set", "c_drawer", 1], ["sfx", "door"], ["msg", "カタン。本棚の引き出しが開いた。"]]]
for i in range(12):
    x = BOOK_X[i % 6]
    y0, y1 = BOOK_ROW[i // 6]
    v.spot((x, y0, 74, y1 - y0), [["if", eq(bflag(i), 0), [["set", bflag(i), 1], ["msg", "本を引き出した。"]], [["set", bflag(i), 0], ["msg", "本をもどした。"]]],
                                  ["sfx", "tick"], DRAWER_OPENS])
v.spot((0, 0, W, H), DARK_MSG, DARK)
DRAWER = (284, 356, 204, 54)
v.spot(DRAWER, [["msg", "引き出し。開かない。"]], eq("c_drawer", 0))
v.spot(DRAWER, [["give", "card"], ["set", "c_card", 1], ["sfx", "get"], ["msg", "穴のあいたカードが入っていた。"]], all_(eq("c_drawer", 1), eq("c_card", 0)))
v.spot(DRAWER, [["set", "c_drawer", 2], ["sfx", "door"], ["msg", "引き出しを閉めた。"]], eq("c_drawer", 1))
v.spot(DRAWER, [["msg", "空っぽの引き出し。"]])
v.spot((676, 160, 140, 250), [["go", "c3globe"]])

# ------------------------------------------------------------------ the globe
GLOBE = (480, 250, 180)
v = View("c3globe", 3, "地球儀", back="c3")
s = v.s
office(s, None)
s.frect(440, 420, 80, 30, WOOD_D, sw=2.2)
s.fpoly([(380, 470), (580, 470), (556, 448), (404, 448)], WOOD_D, sw=2.4)
s.curve([(270, 250), (300, 90), (480, 46), (660, 90), (690, 250)], sw=4, stroke=BRASS)
s.fell(480, 250, 180, 180, SEA, sw=3)
s.paper(330, 482, 300, 40, [("← なぞって回す →", 19)], align="center", pin=False, pad=6)
s.vignette()


def globe_face(key):
    def draw(s):
        cx, cy, r = GLOBE
        s.fell(cx, cy, r, r, SEA, sw=3)
        for k in (-2, -1, 0, 1, 2):
            s.curve([(cx + k * 60 - 10, cy - r + 20), (cx + k * 70, cy), (cx + k * 60 - 10, cy + r - 20)], sw=1.2, stroke="#9fc4da", opacity=0.6)
        for yy in (-110, -50, 10, 70, 130):
            w = math.sqrt(max(0, r * r - yy * yy))
            s.line(cx - w + 6, cy + yy, cx + w - 6, cy + yy, sw=1.2, stroke="#9fc4da", opacity=0.6, passes=1)
        rx, ry = SIZE[key]
        continent(s, key, cx, cy, rx, ry, LAND, 2.6)
        s.ellipse(cx, cy, r, r, sw=3)
    return draw


def globe_open(s):
    cx, cy, r = GLOBE
    s.fell(cx - 70, cy, 110, 176, SEA, sw=3)
    s.fell(cx + 70, cy, 110, 176, SEA, sw=3)
    s.fell(cx, cy, 60, 150, "#1a120c", sw=2)


def hanko_side(s, cx, cy, k=1.0):
    s.fell(cx, cy - 40 * k, 22 * k, 16 * k, WOOD_L, sw=2)
    s.frect(cx - 12 * k, cy - 36 * k, 24 * k, 50 * k, WOOD, sw=2)
    s.frect(cx - 20 * k, cy + 14 * k, 40 * k, 18 * k, BLACK, sw=2)
    s.frect(cx - 20 * k, cy + 30 * k, 40 * k, 6 * k, RED_L, sw=1.4)


for k, key in enumerate(FACES):
    v.variant("face%d" % k, (290, 60, 380, 380), all_(eq("c_gf", k), ne("c_globe", 1)), globe_face(key))
v.variant("open", (290, 60, 380, 380), eq("c_globe", 1), globe_open)
v.variant("hanko", (420, 160, 120, 180), all_(eq("c_globe", 1), eq("c_st_t", 0)), lambda s: hanko_side(s, 480, 250, 1.4), deps=("open",))
v.variant("locked", (700, 466, 160, 48), ["cool", "c_glock"], lambda s: (
    s.frect(700, 468, 160, 44, "#2a1210", sw=2), s.text(760, 490, "ロック中", 18, RED_L)))
v.text(836, 492, 24, "c_glock", kind="cool", color=RED_L, when=["cool", "c_glock"])
v.variant("dark", (0, 0, W, H), DARK, darkness)
GL = (300, 70, 360, 360)
v.spot(GL, [["cyc", "c_gf", 6], ["sfx", "tick"]], ne("c_globe", 1), swipe=3)
v.spot(GL, [["if", eq("c_gf", 0), [["set", "c_gf", 5]], [["add", "c_gf", -1]]], ["sfx", "tick"]], ne("c_globe", 1), swipe=1)
v.spot((0, 0, W, H), DARK_MSG, DARK)
v.spot(GL, [["give", "hanko"], ["set", "c_st_t", 1], ["sfx", "get"], ["msg", "博士のハンコを手に入れた！"]], all_(eq("c_globe", 1), eq("c_st_t", 0)))
v.spot(GL, [["set", "c_globe", 2], ["sfx", "door"], ["msg", "地球儀を閉じた。"]], eq("c_globe", 1))
v.spot(GL, [["msg", "空っぽの地球儀。"]], eq("c_globe", 2))
v.spot(GL, [["msg", "ロック中。少し待とう。"]], ["cool", "c_glock"])
v.spot(GL, [["set", "c_globe", 1], ["sfx", "door"], ["msg", "パカッ！地球儀が2つに割れた。"]], eq("c_gf", HOME))
v.spot(GL, [["cool", "c_glock", 20], ["sfx", "buzz"], ["shake"], ["msg", "ブーッ！ちがうみたい。20秒ロック。"]])

# ------------------------------------------------------------------ the window wall
v = View("c4", 3, "窓の壁", l="c3", r="c1")
s = v.s
office(s, 300)
s.frect(100, 70, 280, 230, "#f3eac2", sw=2.8)
for y in range(80, 300, 12):
    s.line(104, y, 376, y, sw=2, stroke="#c9b98a", passes=1)
s.frect(440, 60, 340, 230, WOOD_L, sw=2.8)
s.frect(456, 76, 308, 180, SEA, sw=2)
for key, (cx, cy, rx, ry) in ON_MAP.items():
    continent(s, key, cx, cy, rx, ry, LAND, 1.6)
potato_x, potato_y = ON_MAP["SA"][0], ON_MAP["SA"][1]
s.fell(potato_x, potato_y - 4, 14, 10, POTATO, sw=1.8)
s.dot(potato_x - 4, potato_y - 6, 1.6, POTATO_D)
s.dot(potato_x + 5, potato_y - 2, 1.6, POTATO_D)
s.paper(540, 262, 140, 26, [("いもの ふるさと", 15)], align="center", pin=False, pad=2)
s.frect(520, 330, 160, 80, STEEL, sw=2.4)
s.frect(536, 340, 128, 60, "#c3cbcc", sw=2)
s.paper(530, 300, 140, 26, [("料理用エレベーター", 13)], align="center", pin=False, pad=3)
s.fpoly([(160, 410), (260, 410), (250, 350), (170, 350)], "#a0522d", sw=2.4)
for k in range(5):
    s.line(210, 350, 160 + k * 25, 290 + (k % 2) * 16, stroke=GREEN, sw=3, passes=1)
for x, y in ((170, 288), (230, 300), (196, 278)):
    s.fell(x, y, 8, 8, WHITE, sw=1.4)
    s.dot(x, y, 2.4, LIGHT)
s.vignette()


def c4_dark(s):
    darkness(s)
    for y in range(80, 300, 12):
        s.line(104, y, 376, y, sw=1.4, stroke="#f3eac2", opacity=0.25, passes=1)


v.variant("dark", (0, 0, W, H), DARK, c4_dark)
v.spot((0, 0, W, H), DARK_MSG, DARK)
v.spot((440, 60, 340, 230), [["msg", "絵の題は『いもの ふるさと』。地図に いもが かいてある。"]])
v.spot((100, 70, 280, 230), [["msg", "ブラインドのすき間から、昼の光。"]])
v.spot((520, 300, 160, 110), [["msg", "料理用エレベーター。むらさきのカレーが とどいている。"]])
v.spot((150, 270, 120, 140), [["msg", "じゃがいもの花が さいている。"]])

# ------------------------------------------------------------------ things to hold


def card_icon(s):
    s.frect(14, 24, 68, 50, "#4d4740", sw=2)
    for r, c in HOLES[:6]:
        s.frect(18 + c * 8, 28 + r * 8, 5, 5, PAPER_L, outline=False)


def card_zoom(back):
    def draw(s):
        s.frect(0, 0, 480, 360, "#2b2a28", outline=False)
        s.frect(40, 30, 400, 300, "#4d4740", sw=2.6)
        if back:
            s.text(240, 180, "博士のしおり", 30, PAPER_L)
            return
        for r, c in HOLES:
            s.frect(56 + c * 46 + 4, 42 + r * 46 + 4, 38, 38, PAPER_L, sw=1.6)
    return draw


def hanko_face(s):
    s.frect(0, 0, 480, 360, "#2b2a28", outline=False)
    s.fell(240, 180, 130, 130, BLACK, sw=2.6)
    s.fell(240, 180, 110, 110, RED_L, sw=2)
    mirror_g(s, 240)
    s.text(240, 180, "博士", 90, "#5a1410")
    s.raw("</g>")


item("card", card_icon, "穴のあいたカード", ["本棚の引き出しに入っていた。"], zoom=card_zoom(False), back=card_zoom(True))
item("hanko", lambda s: hanko_side(s, 48, 54, 0.9), "博士のハンコ", ["地球儀の中に入っていた。"],
     zoom=lambda s: (s.frect(0, 0, 480, 360, "#2b2a28", outline=False), hanko_side(s, 240, 190, 3.2)), back=hanko_face)
item("sheet2", lambda s: (s.frect(24, 12, 48, 70, PAPER_L, sw=2), s.ellipse(58, 66, 8, 8, stroke=RED_L, sw=2)), "退職面談シート",
     ["博士のハンコを押した。"])

# ------------------------------------------------------------------ puzzles
ALL_IN = [["set", bflag(i), 0] for i in range(12)]
puzzle("r1", 3, "光るしるし", None, ["ge", "c_drawer", 1],
       ["机の壁の博士メモ：『夜に読む本には、光るシールを はった』。",
        "出口の壁のスイッチで明かりを消すと、本棚に光るしるしが3つ見える。",
        "光る3冊（上の段の左から2番目、下の段の左から3番目と5番目）だけを引き出す。ほかの本は もどす。"],
       "光る3冊だけを引き出す", ALL_IN + [["set", bflag(i), 1] for i in MARKED] + [["set", "c_drawer", 1], ["set", "c_dark", 0]])
puzzle("r2", 3, "穴のあいたカード", ["ge", "c_drawer", 1], eq("c_seen", 1),
       ["本棚の引き出しのカード。選んで もう一度タップすると、大きく見られる。",
        "カードを選んで、机の上の新聞の『もじさがし』に重ねる。",
        "穴から読むと『いものふるさとをおせ』。"],
       "いものふるさとをおせ", [["takeall", "card"], ["set", "c_card", 1], ["set", "c_seen", 1], ["set", "c_ov", 0]])
puzzle("r3", 3, "地球儀", None, ["ge", "c_globe", 1],
       ["窓の壁の絵『いもの ふるさと』。地図の いもは、どの大陸の上？",
        "地球儀を指で左右になぞって回し、その大陸を正面にして タップ。まちがえると20秒ロック。",
        "いもの大陸は 南アメリカ（下のほうが細い形）。正面にしてタップ。"],
       "南アメリカを正面にして押す", [["set", "c_gf", HOME], ["set", "c_globe", 1]])
puzzle("r4", 3, "社長印", ["ge", "c_globe", 1], eq("c_stamp", 1),
       ["地球儀の中のハンコを取ろう。",
        "ハンコを選んで、机の上の面談シートの『社長印』のらんを タップ。",
        "地球儀をタップしてハンコを取り、机の上のシートの右下へ。"],
       "シートの社長印のらんに押す", [["takeall", "hanko"], ["set", "c_st_t", 1], ["set", "c_stamp", 1]])
puzzle("r5", 3, "退職面談", eq("c_stamp", 1), eq("c_end", 1),
       ["ハンコを押したシートを持って、出口のロボットに わたす。",
        "ロボット『社訓の3つめ』。社訓は、出口の壁の額にある。",
        "社訓の3つめは『かたづけは 使った人が』。本をもどし、引き出しと地球儀を閉じ、明かりをつけてから わたす。"],
       "かたづけてから シートをわたす",
       ALL_IN + [["set", "c_drawer", 2], ["set", "c_globe", 2], ["set", "c_dark", 0], ["set", "c_sheet", 1], ["set", "c_end", 1]]
       + [["takeall", i] for i in STAGE3_ITEMS] + [["stage", 32]])
