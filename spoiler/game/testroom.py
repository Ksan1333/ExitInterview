"""Test room: the sample puzzle that may be shown openly, plus a shared-item check."""
from game.core import *  # noqa: F401,F403
from game.stage1 import wall
from game.stage2 import key_shape

TAN = "#c9a26a"

# ------------------------------------------------------------------ shelf with five bags
v = View("t1", 9, "たなの まえ", r="t2")
s = v.s
wall(s, 790)
s.frect(210, 286, 540, 12, WOOD, sw=2.4)
s.fpoly([(240, 298), (262, 298), (240, 326)], WOOD_D, sw=2)
s.fpoly([(698, 298), (720, 298), (720, 326)], WOOD_D, sw=2)
BX = [222 + 104 * i for i in range(5)]
for bx in BX:
    s.frect(bx, 190, 84, 96, "#b99a6b", sw=2.6)
    s.line(bx, 208, bx + 84, 208, sw=1.8, passes=1)
    s.line(bx + 18, 216, bx + 13, 278, sw=1.3, opacity=0.5, passes=1)
    s.line(bx + 66, 216, bx + 71, 278, sw=1.3, opacity=0.5, passes=1)
s.paper(282, 40, 440, 138, ["なかみ：しんぶん・ほね・スリッパ・ちくわ・ボール", "ほねは はしっこ", "しんぶんは スリッパの すぐ右",
                            "スリッパと ボールは となりあわない", "ちくわは まんなか では ない", "ボールは しんぶんより 左"], 15, rot=-1, pin=False, pad=10, gap=1.32)
QT = [440, 480, 520]
for x in QT:
    s.fell(x, 330, 7, 7, "#3a4648", sw=1.8)
s.vignette()
seq_dots(v, "qt", 3, QT, 330)
for i, bx in enumerate(BX):
    v.spot((bx - 6, 184, 96, 108),
           [["sfx", "tick"], ["seq", "qt", i, 3, [1, 0, 2], [["set", "t_done", 1], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]], eq("t_done", 0))

# ------------------------------------------------------------------ dog in front of the door
v = View("t2", 9, "いぬの まえ", l="t1")
s = v.s
wall(s, 250)
s.frect(390, 70, 180, 330, "#1b2728")
s.frect(404, 84, 152, 316, WOOD)
s.frect(424, 104, 112, 100, WOOD_D, sw=2)
s.frect(424, 224, 112, 150, WOOD_D, sw=2)
s.fell(540, 236, 8, 8, BRASS, sw=2.2)
s.paper(436, 34, 88, 30, [("でぐち", 18)], align="center", pin=False, pad=5)
s.curve([(524, 420), (548, 410), (556, 390)], sw=6, stroke="#8a6a42", passes=1)
s.fell(480, 388, 46, 58, TAN)
s.fell(460, 438, 12, 8, TAN, sw=2.4)
s.fell(500, 438, 12, 8, TAN, sw=2.4)
s.fpoly([(448, 292), (436, 328), (456, 324)], "#8a6a42", sw=2.4)
s.fpoly([(512, 292), (524, 328), (504, 324)], "#8a6a42", sw=2.4)
s.fell(480, 308, 36, 30, TAN)
s.line(454, 337, 506, 337, stroke=RED, sw=5, passes=1)
s.fell(480, 318, 16, 11, "#e6d3ae", sw=2)
s.dot(480, 312, 4, INK)
s.dot(468, 301, 3, INK)
s.dot(492, 301, 3, INK)
s.curve([(473, 324), (480, 328), (487, 324)], sw=2, passes=1)
# thought bubble: chikuwa, ball, slipper
s.fell(548, 264, 8, 6, PAPER_L, sw=2)
s.fell(566, 240, 12, 9, PAPER_L, sw=2.2)
s.fell(690, 158, 128, 64, PAPER_L, sw=3)
s.frect(594, 134, 48, 24, "#e8d7b0", sw=2.4)
s.line(606, 137, 606, 155, stroke="#9a6a3a", sw=3, passes=1)
s.line(617, 137, 617, 155, stroke="#9a6a3a", sw=3, passes=1)
s.fell(642, 146, 6, 12, "#f4ecd6", sw=2)
s.fell(690, 146, 20, 20, "#d8e06a", sw=2.4)
s.curve([(676, 134), (682, 146), (676, 158)], stroke="#f6f6ea", sw=2.2, passes=1)
s.curve([(704, 134), (698, 146), (704, 158)], stroke="#f6f6ea", sw=2.2, passes=1)
s.fpoly([(760, 158), (764, 142), (778, 138), (788, 158)], "#c96f8a", sw=2.2)
s.fpoly([(734, 158), (788, 158), (790, 166), (732, 166)], "#8a6a42", sw=2)
for n_, cx in (("1", 618), ("2", 690), ("3", 760)):
    s.text(cx, 186, n_, 18)
s.vignette()
KEY_OUT = all_(eq("t_done", 1), eq("t_key", 0))
v.variant("tkey", (590, 430, 90, 56), KEY_OUT, lambda s: key_shape(s, 634, 458, 1.3))
v.spot((584, 424, 102, 68), [["give", "tkey"], ["set", "t_key", 1], ["sfx", "get"]], KEY_OUT)
v.spot((404, 84, 152, 200), [["take", "tkey"], ["sfx", "door"], ["unsel"], ["stage", 90]], ["sel", "tkey"])

item("tkey", lambda s: key_shape(s, 44, 48, 1.7))
puzzle("t1", 9, "ふくろ", None, eq("t_done", 1),
       ["いぬが ほしい ものは 3つ。ふくろの 中身は メモから かんがえる。",
        "ほねは はしっこ。しんぶんは スリッパの すぐ右。じゅんに あてはめる。",
        "左から ボール・ちくわ・スリッパ・しんぶん・ほね。いぬの じゅんに タップ。"],
       "2ばんめ → 1ばんめ → 3ばんめ", [["set", "t_done", 1]])
