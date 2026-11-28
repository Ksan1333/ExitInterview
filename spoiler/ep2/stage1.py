"""Episode 2, stage 1: the warehouse."""
from ep2.look import *  # noqa: F401,F403

# parcels: id, label picture, slot value, weight
PARCELS = [("pa", "cat", 1, "かるい"), ("pb", "fish", 2, "おもい"), ("pc", "flower", 3, "おもい"), ("pd", "book", 4, "かるい")]
PNAME = {"pa": "ネコの荷物", "pb": "魚の荷物", "pc": "花の荷物", "pd": "本の荷物"}
PDESC = {"pa": "ラベルにネコの絵。", "pb": "ラベルに魚の絵。", "pc": "ラベルに花の絵。", "pd": "ラベルに本の絵。"}
ANSWER = {1: 3, 2: 4, 3: 1, 4: 2}  # slot -> parcel value (flower, book, cat, fish)
SLOTS = [(160, 140), (315, 140), (470, 140), (625, 140)]  # x, y of each shelf box (145 x 112)
STAGE1_ITEMS = ["battery", "flash", "flashon", "pa", "pb", "pc", "pd", "skey"]
RULES = ["社訓", "おおきな声で あいさつ", "つかれたら すわって休む", "かたづけは 使った人が", "れいぞうこは すぐしめる"]
DONE_SORT = eq("a_sorted", 1)


def give_back(slot_flag):
    """Gives back whichever parcel is in a slot."""
    ops = [["give", "pd"]]
    for pid, _, val, _ in reversed(PARCELS[:3]):
        ops = [["if", eq(slot_flag, val), [["give", pid]], ops]]
    return ops


CHECK = ["if", all_(*[ne("a_s%d" % i, 0) for i in range(1, 5)]),
         [["if", all_(*[eq("a_s%d" % i, ANSWER[i]) for i in range(1, 5)]),
           [["set", "a_sorted", 1], ["sfx", "ok"], ["msg", "カチッ。棚の上の小箱が開いた。"]],
           [["sfx", "buzz"], ["shake"], ["msg", "ブー。並べ方がちがうみたい。"]]]]]

# ------------------------------------------------------------------ the shutter wall
v = View("a1", 1, "シャッターの壁", l="a4", r="a2")
s = v.s
warehouse(s, 480)


def shutter(s, open_=False):
    s.frect(292, 72, 376, 18, METAL_D, sw=2.4)
    if open_:
        s.frect(300, 90, 360, 320, "#0b0f10")
        s.solid([(300, 410), (660, 410), (600, 200), (360, 200)], LIGHT, 0.10)
        for k in range(5):
            y = 380 - k * 38
            s.line(330 + k * 12, y, 630 - k * 12, y, sw=2, stroke="#6d6a5a", passes=1)
        s.frect(300, 90, 360, 40, METAL, sw=2.4)
        for y in (100, 110, 120):
            s.line(304, y, 656, y, sw=1.4, opacity=0.6, passes=1)
        return
    s.frect(300, 90, 360, 320, METAL)
    for y in range(102, 410, 14):
        s.line(304, y, 656, y, sw=1.6, opacity=0.55, passes=1)
    s.frect(440, 388, 80, 14, METAL_D, sw=2)


shutter(s)
s.paper(352, 126, 256, 96, [("シャッターの開け方", 20), ("鍵とレバーを 同時に", 20), ("（レバーは管理室）", 17)], align="center", pin=False, pad=10)
# the company rules, written backwards
mirror_g(s, 170)
s.paper(72, 110, 196, 214, [(RULES[0], 22)] + [(t, 16) for t in RULES[1:]], align="left", gap=1.7, pad=12)
s.raw("</g>")
s.paper(694, 84, 126, 150, [("本日の", 18), ("採用条件", 21), ("45分以内", 17), ("ヒント3回まで", 15), ("スキップなし", 16)],
        align="center", gap=1.3, pad=8, color=PAPER_L)
s.frect(694, 250, 62, 84, METAL_D, sw=2.4)
s.fell(725, 282, 10, 10, "#0a0d0e", sw=2)
s.frect(722, 288, 6, 16, "#0a0d0e", sw=1.2)
s.vignette()
v.variant("open", (286, 66, 388, 350), eq("a_open", 1), lambda s: shutter(s, True))
v.variant("kturn", (688, 244, 74, 96), ["cool", "a_kt"], lambda s: (
    s.frect(694, 250, 62, 84, METAL_D, sw=2.4), s.glow(725, 290, 30, LIGHT, 0.14),
    key_icon(s, 734, 290, 0.6), s.fell(725, 282, 10, 10, "#0a0d0e", sw=2)))
v.text(725, 362, 26, "a_kt", kind="cool", color=LIGHT, when=all_(["cool", "a_kt"], eq("a_open", 0)))
OPEN = [["set", "a_open", 1], ["take", "skey"], ["sfx", "door"], ["msg", "ガラガラガラ…シャッターが開いた！"]]
v.spot((688, 244, 76, 96), [["cool", "a_kt", 6], ["sfx", "lever"],
                            ["if", ["cool", "a_lt"], OPEN, [["msg", "鍵を回した。レバーは？（6秒）"]]]],
       all_(["sel", "skey"], eq("a_open", 0)))
v.spot((688, 244, 76, 96), [["msg", "大きな鍵穴。"]], eq("a_open", 0))
# the mirror is not needed to get out: it is set to clean on the way out, so that every way through stage 1 ends alike
v.spot((300, 90, 360, 320), [["sfx", "door"], ["set", "a_dust", 4]] + [["takeall", i] for i in STAGE1_ITEMS] + [["stage", 2]],
       eq("a_open", 1))
v.spot((300, 230, 360, 180), [["msg", "シャッターは びくともしない。"]], eq("a_open", 0))
v.spot((72, 110, 196, 214), [["msg", "字が反対向きで、読みにくい…"]])

# ------------------------------------------------------------------ the shelf wall
v = View("a2", 1, "棚の壁", l="a1", r="a3")
s = v.s
warehouse(s, 300)
s.frect(146, 116, 668, 16, STEEL, sw=2.4)
s.frect(146, 254, 668, 14, STEEL, sw=2.4)
s.frect(146, 362, 668, 14, STEEL, sw=2.4)
for x in (146, 304, 459, 614, 800):
    s.frect(x, 100, 14, 300, METAL_D, sw=2.2)
for i, (x, y) in enumerate(SLOTS):
    s.frect(x + 2, y, 141, 112, "#2b3433", outline=False)
    s.frect(x + 52, 270, 40, 26, PAPER_L, sw=1.8)
    s.text(x + 72, 283, str(i + 1), 20)
box(s, 180, 300, 110, 62, CARD_D)
box(s, 498, 312, 90, 50)
box(s, 650, 296, 130, 66, CARD_D)
s.frect(146, 376, 668, 34, "#0c1011", outline=False)
s.line(146, 410, 814, 410, sw=2)
# the little box on top of the shelf
s.frect(432, 74, 96, 42, METAL_D, sw=2.4)
s.fell(480, 95, 6, 6, "#0a0d0e", sw=1.6)
s.fell(560, 92, 9, 9, "#5b2a26", sw=2)
s.paper(574, 76, 118, 36, [("仕分け完了で開く", 13)], align="center", pin=False, pad=6)
# the toolbox
s.frect(70, 440, 120, 56, RED, sw=2.4)
s.frect(70, 430, 120, 16, RED_L, sw=2.2)
s.frect(112, 416, 36, 14, METAL_D, sw=2)
s.vignette()
for pid, kind, val, _ in PARCELS:
    for i, (x, y) in enumerate(SLOTS):
        v.variant("%s%d" % (pid, i + 1), (x - 4, y - 16, 153, 132), eq("a_s%d" % (i + 1), val),
                  lambda s, x=x, y=y, kind=kind: parcel(s, x + 14, y + 30, 118, 82, kind))
v.variant("lit", (540, 76, 40, 34), DONE_SORT, lambda s: (s.glow(560, 92, 22, "#7fe08a", 0.2), s.fell(560, 92, 9, 9, "#7fe08a", sw=2)))
v.variant("boxopen", (424, 50, 112, 70), DONE_SORT, lambda s: (
    s.frect(432, 74, 96, 42, "#0c1011", sw=2.4), s.fpoly([(432, 74), (528, 74), (520, 54), (440, 54)], METAL_D, sw=2.2)))
v.variant("key", (436, 78, 88, 36), all_(DONE_SORT, eq("a_key", 0)), lambda s: (
    s.frect(432, 74, 96, 42, "#0c1011", sw=2.4), key_icon(s, 486, 95, 0.75)), deps=("boxopen",))
v.variant("toolopen", (64, 404, 132, 98), eq("a_tool", 1), lambda s: (
    s.frect(70, 440, 120, 56, RED, sw=2.4), s.frect(74, 444, 112, 20, "#2a1412", sw=1.8),
    s.fpoly([(70, 440), (190, 440), (178, 410), (82, 410)], RED_L, sw=2.2)))
v.spot((432, 60, 96, 56), [["give", "skey"], ["set", "a_key", 1], ["sfx", "get"]], all_(DONE_SORT, eq("a_key", 0)))
v.spot((432, 60, 96, 56), [["msg", "小さな箱。鍵がかかっている。"]], eq("a_sorted", 0))
for i, (x, y) in enumerate(SLOTS):
    flag = "a_s%d" % (i + 1)
    r = (x, y, 145, 112)
    for pid, _, val, _ in PARCELS:
        v.spot(r, [["take", pid], ["set", flag, val], ["sfx", "plop"], ["unsel"], CHECK],
               all_(["sel", pid], eq(flag, 0), eq("a_sorted", 0)))
    v.spot(r, give_back(flag) + [["set", flag, 0], ["sfx", "tick"]], all_(ne(flag, 0), eq("a_sorted", 0)))
    v.spot(r, [["msg", "荷物を選んでからタップすると置ける。"]], all_(eq(flag, 0), eq("a_sorted", 0)))
    v.spot(r, [["msg", "仕分け完了！"]], DONE_SORT)
v.spot((146, 372, 668, 44), [["go", "a2gap"]])
v.spot((66, 406, 130, 96), [["set", "a_tool", 1], ["give", "flash"], ["sfx", "get"], ["msg", "工具箱に懐中電灯が入っていた。"]], eq("a_tool", 0))
v.spot((66, 406, 130, 96), [["msg", "工具箱。もう空っぽ。"]])

# ------------------------------------------------------------------ the workbench wall
v = View("a3", 1, "作業台の壁", l="a2", r="a4")
s = v.s
warehouse(s, 420)
clock(s, 300, 140, 48, 10, 10)
s.frect(100, 300, 470, 20, WOOD_L, sw=2.4)
s.frect(112, 320, 446, 26, WOOD, sw=2.2)
for x in (118, 530):
    s.frect(x, 346, 22, 110, WOOD_D, sw=2)
s.frect(150, 400, 360, 12, WOOD_D, sw=1.8)
# the tall mirror, grey with dust
s.frect(624, 66, 162, 352, WOOD_D, sw=2.8)
s.frect(640, 82, 130, 320, DUST, sw=2)
for k in range(9):
    y = 100 + k * 34
    s.line(650, y, 760, y + 10, sw=1.4, stroke="#a9a69b", opacity=0.7, passes=1)
s.frect(640, 418, 22, 20, WOOD_D, sw=2)
s.frect(748, 418, 22, 20, WOOD_D, sw=2)
s.vignette()
BENCH = {"pa": (126, 216), "pb": (252, 216), "pc": (378, 216)}
for pid, kind, _, _ in PARCELS[:3]:
    x, y = BENCH[pid]
    v.variant(pid, (x - 4, y - 16, 128, 104), eq("a_" + pid, 0), lambda s, x=x, y=y, kind=kind: parcel(s, x, y, 112, 84, kind))
    v.spot((x, y - 10, 112, 94), [["give", pid], ["set", "a_" + pid, 1], ["sfx", "get"]], eq("a_" + pid, 0))
v.variant("clockoff", (246, 86, 108, 108), eq("a_clock", 1), lambda s: (
    clock(s, 300, 140, 48, 10, 10), s.paper(266, 168, 68, 22, [("止まった", 13)], align="center", pin=False, pad=3)))
v.spot((246, 86, 108, 108), [["set", "a_clock", 1], ["give", "battery"], ["sfx", "get"],
                             ["msg", "時計の裏から電池をぬいた。時計が止まった。"]], eq("a_clock", 0))
v.spot((246, 86, 108, 108), [["msg", "止まった時計。"]])
v.spot((624, 66, 162, 352), [["go", "a3mir"]])

# ------------------------------------------------------------------ the manager's window
v = View("a4", 1, "管理室の窓", l="a3", r="a1")
s = v.s
warehouse(s, 700)
s.frect(196, 82, 436, 230, METAL_D, sw=2.6)
s.frect(210, 96, 408, 202, "#1f2a2b", sw=2)
s.frect(240, 220, 140, 64, "#2b2522", sw=1.6, op=0.8)
s.frect(470, 180, 90, 64, "#14191a", sw=1.6, op=0.8)
s.solid([(210, 96), (300, 96), (230, 298), (210, 298)], "#ffffff", 0.05)
s.paper(232, 108, 364, 168, [("仕分けのきまり", 22), ("（左から 1・2・3・4）", 16), "・重い荷物は、両はし", "・ネコは、魚のとなり",
                             "・花は、本より左"], 19, gap=1.32, pad=12)
s.frect(180, 312, 470, 22, STEEL, sw=2.4)
s.frect(196, 334, 438, 76, METAL_D, sw=2.2)
# intercom
s.frect(676, 156, 84, 112, PAPER_L, sw=2.4)
for k in range(4):
    s.line(692, 176 + k * 10, 744, 176 + k * 10, sw=2, passes=1)
s.fell(718, 238, 14, 14, RED_L, sw=2.4)
s.paper(664, 286, 152, 76, [("合言葉は、", 17), ("社訓の頭に", 17), ("ある。", 17)], align="center", gap=1.25, pad=6)
# lever in a glass case
s.frect(74, 318, 100, 130, METAL_D, sw=2.4)
s.frect(118, 344, 12, 80, BLACK, sw=1.8)
s.fell(124, 350, 13, 13, RED_L, sw=2.4)
s.frect(80, 324, 88, 118, "#bfe0e8", sw=2, op=0.25)
s.line(90, 334, 110, 360, stroke="#ffffff", sw=2, opacity=0.5, passes=1)
s.vignette()
v.variant("caseopen", (68, 312, 112, 142), eq("a_word", 1), lambda s: (
    s.frect(74, 318, 100, 130, METAL_D, sw=2.4), s.frect(118, 344, 12, 80, BLACK, sw=1.8), s.fell(124, 350, 13, 13, RED_L, sw=2.4)))
v.variant("leverdown", (68, 312, 112, 142), ["any", ["cool", "a_lt"], eq("a_open", 1)], lambda s: (
    s.frect(74, 318, 100, 130, METAL_D, sw=2.4), s.frect(118, 344, 12, 80, BLACK, sw=1.8), s.fell(124, 418, 13, 13, RED_L, sw=2.4),
    s.glow(124, 418, 24, LIGHT, 0.12)), deps=("caseopen",))
v.text(124, 474, 26, "a_lt", kind="cool", color=LIGHT, when=all_(["cool", "a_lt"], eq("a_open", 0)))
v.spot((664, 150, 104, 124), [["ask", "a_word"]], eq("a_word", 0))
v.spot((664, 150, 104, 124), [["msg", "博士『シャッターは、鍵とレバーを同時に』"]])
v.spot((68, 312, 112, 142), [["msg", "ガラスのカバーがかかっている。"]], eq("a_word", 0))
v.spot((68, 312, 112, 142), [["cool", "a_lt", 6], ["sfx", "lever"],
                             ["if", ["cool", "a_kt"], OPEN, [["msg", "レバーを下ろした。鍵は？（6秒）"]]]], eq("a_open", 0))
v.spot((68, 312, 112, 142), [["msg", "レバーは下りたまま。"]])

ask("a_word", "インターホン『報告の前に、合言葉をどうぞ』",
    ["おつかれ", "お疲れ", "おつかれさま", "お疲れさま", "お疲れ様", "おつかれさまです", "お疲れさまです", "お疲れ様です"],
    [["set", "a_word", 1], ["sfx", "ok"], ["msg", "博士『よろしい。レバーのカバーを開けました』"]], when=eq("a_word", 0))

# ------------------------------------------------------------------ under the shelf
v = View("a2gap", 1, "棚の下", back="a2")
s = v.s
s.frect(0, 0, W, H, "#06090a", outline=False)
s.frect(0, 0, W, 60, STEEL, sw=2.4)
s.frect(0, 470, W, 70, "#1a1c1b", outline=False)
s.text(480, 280, "まっくら", 22, "#8d9a9c")


def gap_lit(s):
    s.frect(0, 60, W, 410, "#151a1a", outline=False)
    s.solid([(0, 470), (W, 470), (W, 160), (0, 300)], "#3a3c36", 0.8)
    s.glow(470, 330, 260, LIGHT, 0.08, 6)
    s.frect(90, 380, 90, 34, BLACK, sw=2)
    s.fpoly([(180, 380), (240, 362), (240, 432), (180, 414)], METAL, sw=2)
    s.solid([(240, 362), (900, 220), (900, 500), (240, 432)], LIGHT, 0.10)
    s.fell(700, 420, 14, 6, BRASS, sw=1.6)
    for x, y in ((320, 440), (560, 452), (780, 430), (640, 380)):
        s.fell(x, y, 10, 4, "#55584f", sw=1, outline=False)


v.variant("lit", (0, 60, W, 410), eq("a_light", 1), gap_lit)
v.variant("pd", (406, 300, 170, 136), all_(eq("a_light", 1), eq("a_p4", 0)), lambda s: parcel(s, 420, 330, 140, 96, "book"), deps=("lit",))
v.spot((410, 310, 160, 124), [["give", "pd"], ["set", "a_p4", 1], ["sfx", "get"]], all_(eq("a_light", 1), eq("a_p4", 0)))
v.spot((90, 70, 780, 390), [["take", "flashon"], ["set", "a_light", 1], ["sfx", "ok"], ["unsel"], ["msg", "懐中電灯を置いて、奥を照らした。"]],
       all_(["sel", "flashon"], eq("a_light", 0)))
v.spot((90, 70, 780, 390), [["msg", "電池が入っていない。"]], all_(["sel", "flash"], eq("a_light", 0)))
v.spot((90, 70, 780, 390), [["msg", "暗くて何も見えない。"]], eq("a_light", 0))
v.spot((680, 406, 40, 30), [["msg", "10円玉。…今は関係なさそう。"]])

# ------------------------------------------------------------------ the dusty mirror
v = View("a3mir", 1, "姿見", back="a3")
s = v.s
s.frect(0, 0, W, H, CONC_D, outline=False)
s.frect(238, 18, 484, 504, WOOD_D, sw=3)
s.frect(256, 36, 448, 468, CONC, sw=2)
s.frect(256, 380, 448, 124, CONC_F, outline=False)
s.line(256, 380, 704, 380, sw=2)
s.frect(600, 60, 104, 320, METAL, sw=2)
for y in range(70, 380, 14):
    s.line(604, y, 704, y, sw=1.4, opacity=0.5, passes=1)
s.paper(300, 70, 270, 290, [(RULES[0], 30)] + [(t, 21) for t in RULES[1:]], align="left", gap=1.75, pad=16)
s.line(260, 40, 330, 110, stroke="#ffffff", sw=3, opacity=0.25, passes=1)


def dust(level):
    def draw(s):
        s.frect(256, 36, 448, 468, DUST, op=level, outline=False)
        r = s.r
        for _ in range(int(30 * level)):
            x, y = r.uniform(270, 690), r.uniform(50, 490)
            s.solid(ell_pts(x, y, r.uniform(20, 60), r.uniform(8, 24), 12), "#b5b2a6", 0.35 * level)
        s.rect(256, 36, 448, 468, sw=2)
    return draw


for k, lv in enumerate((1.0, 0.88, 0.66, 0.4)):
    v.variant("dust%d" % k, (252, 32, 456, 476), eq("a_dust", k), dust(lv))
v.spot((256, 36, 448, 468), [["add", "a_dust", 1], ["sfx", "tick"],
                             ["if", eq("a_dust", 4), [["sfx", "ok"], ["msg", "鏡がきれいになった。"]]]], ["lt", "a_dust", 4], swipe=4)
v.spot((256, 36, 448, 468), [["msg", "ほこりで真っ白。指でこすれば落ちそう。"]], ["lt", "a_dust", 4])
v.spot((256, 36, 448, 468), [["msg", "向かいの壁の張り紙が映っている。"]])

# ------------------------------------------------------------------ things to hold


def battery_icon(s):
    s.frect(18, 38, 58, 22, "#3a3a3a", sw=2.2)
    s.frect(30, 38, 26, 22, ORANGE, sw=1.8)
    s.frect(76, 43, 7, 12, BRASS, sw=1.6)


def flash_icon(s, on=False):
    if on:
        s.solid([(76, 34), (96, 20), (96, 78), (76, 64)], LIGHT, 0.5)
    s.frect(14, 40, 50, 18, METAL, sw=2.2)
    s.fpoly([(62, 36), (78, 28), (78, 70), (62, 62)], METAL_D, sw=2.2)
    s.fell(78, 49, 4, 20, "#f6e7a6" if on else "#55605f", sw=1.6)
    s.frect(30, 36, 10, 6, RED_L, sw=1.4)


def parcel_icon(kind):
    return lambda s: parcel(s, 10, 30, 76, 56, kind)


def parcel_zoom(kind, name):
    def draw(s):
        s.frect(0, 0, 480, 360, "#232b2b", outline=False)
        parcel(s, 60, 90, 360, 240, kind)
        s.text(240, 50, name, 26, TXT)
    return draw


def parcel_back(weight):
    def draw(s):
        s.frect(0, 0, 480, 360, "#232b2b", outline=False)
        s.frect(60, 70, 360, 250, CARD, sw=2.6)
        s.line(60, 195, 420, 195, sw=1.6, opacity=0.5, passes=1)
        s.frect(150, 120, 180, 130, PAPER_L, sw=2.2)
        s.fpoly([(196, 210), (284, 210), (270, 160), (210, 160)], BLACK, sw=2)
        s.fell(240, 150, 12, 9, BLACK, sw=2)
        s.text(240, 232, weight, 30, RED if weight == "おもい" else BLUE)
        s.text(240, 40, "荷物の裏", 24, TXT)
    return draw


item("battery", battery_icon, "電池", ["作業台の壁の時計から ぬいた。"])
item("flash", flash_icon, "懐中電灯", ["電池が入っていない。"])
item("flashon", lambda s: flash_icon(s, True), "懐中電灯（電池入り）", ["明るくつく。"])
for pid, kind, _, weight in PARCELS:
    item(pid, parcel_icon(kind), PNAME[pid], [PDESC[pid], "裏にもシールが貼ってある。"],
         zoom=parcel_zoom(kind, PNAME[pid]), back=parcel_back(weight))
item("skey", lambda s: key_icon(s, 50, 48, 1.05), "シャッターの鍵", ["棚の上の小箱に入っていた。"])

combo("flash", "battery", [["take", "flash"], ["take", "battery"], ["give", "flashon"], ["sfx", "ok"], ["msg", "電池を入れた。つく！"]])

# ------------------------------------------------------------------ puzzles
puzzle("p1", 1, "棚の下の暗がり", None, eq("a_light", 1),
       ["棚の下のすき間が暗い。明かりがほしい。",
        "工具箱の懐中電灯には、電池が入っていない。電池は、この部屋のどこかで使われている。",
        "作業台の壁の時計から電池をぬく。懐中電灯を選んで電池をタップ。棚の下を照らす。"],
       "時計の電池を懐中電灯に入れて、棚の下を照らす",
       [["takeall", "flash"], ["takeall", "battery"], ["takeall", "flashon"], ["set", "a_clock", 1], ["set", "a_tool", 1], ["set", "a_light", 1]])
puzzle("p2", 1, "ほこりの鏡", None, ["ge", "a_dust", 4],
       ["シャッターの壁の張り紙は、字が反対向き。鏡に映せば読みやすい。",
        "作業台の壁の鏡は、ほこりで真っ白。",
        "鏡を指で何回か こする（なぞる）と、きれいになる。"],
       "鏡を指でこすって、ほこりを落とす", [["set", "a_dust", 4]])
puzzle("p3", 1, "荷物の仕分け", None, DONE_SORT,
       ["管理室の窓の『仕分けのきまり』どおりに、棚に荷物を並べる。荷物は4つ。1つは棚の下の暗いところ。",
        "荷物を選んでもう一度タップすると、大きく見られる。裏返すと、重いか軽いかが分かる。",
        "重いのは花と魚で、両はし。花は本より左だから、左はしが花、右はしが魚。ネコは魚のとなり。"],
       "左から 花・本・ネコ・魚",
       [["takeall", p[0]] for p in PARCELS] + [["set", "a_pa", 1], ["set", "a_pb", 1], ["set", "a_pc", 1], ["set", "a_p4", 1]]
       + [["set", "a_s%d" % i, ANSWER[i]] for i in range(1, 5)] + [["set", "a_sorted", 1]])
puzzle("p4", 1, "インターホンの合言葉", None, eq("a_word", 1),
       ["合言葉は社訓の中。社訓はシャッターの壁の張り紙。字が反対向きなので、鏡に映すと読める。",
        "『頭にある』は、それぞれの行の最初の文字のこと。",
        "社訓の行の頭を、上から読むと『おつかれ』。"],
       "おつかれ", [["set", "a_word", 1]])
puzzle("p5", 1, "シャッター", all_(eq("a_word", 1), DONE_SORT), eq("a_open", 1),
       ["シャッターの張り紙：鍵とレバーを同時に。鍵は棚の上の小箱、レバーは管理室の窓。",
        "1人がシャッターで鍵を回し、もう1人が管理室のレバーを下ろす。6秒以内。",
        "『せーの』で、鍵（シャッターの壁）とレバー（管理室の窓）を同時にタップ。"],
       "鍵とレバーを同時に", [["takeall", "skey"], ["set", "a_key", 1], ["set", "a_open", 1]])
