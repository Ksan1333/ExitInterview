"""Stage 1."""
from game.core import *  # noqa: F401,F403

SYMS = ["o", "tri", "sq", "star", "dia"]
INIT["f"].update(s1_la=4, s1_lb=4)


def wall(s, lamp_x=480):
    s.room()
    for x in range(40, W, 80):
        s.line(x, 315, x, 397, sw=1.5, opacity=0.4, passes=1)
    s.frect(0, 22, W, 12, METAL_D, sw=2)
    s.line(lamp_x, 34, lamp_x, 52, sw=2.5)
    s.fpoly([(lamp_x - 22, 52), (lamp_x + 22, 52), (lamp_x + 36, 74), (lamp_x - 36, 74)], METAL)
    s.fell(lamp_x, 79, 9, 7, "#f6e7a6", sw=2)
    for rr, op in ((70, 0.09), (130, 0.06), (200, 0.04)):
        s.solid(ell_pts(lamp_x, 90, rr, rr * 0.85, 32), LIGHT, op)


def lever_plate(s, x, y, label):
    s.frect(x, y, 120, 250, METAL_D)
    s.text(x + 60, y + 16, label, 20, PAPER_L)
    for k, kind in enumerate(SYMS):
        s.sym(kind, x + 30, y + 46 + k * 45, 11, PAPER_L, 2.6)
        s.line(x + 52, y + 46 + k * 45, x + 70, y + 46 + k * 45, stroke=PAPER_L, sw=2, passes=1)


def lever_column(s, x, y, pos):
    s.solid(rect_pts(x + 68, y + 28, 42, 216), METAL_D)
    s.frect(x + 82, y + 34, 12, 204, BLACK, sw=2)
    cy = y + 46 + pos * 45
    s.frect(x + 74, cy - 6, 28, 12, METAL, sw=2)
    s.fell(x + 88, cy, 14, 14, RED_L, sw=2.6)


def lever_spot(v, rect, flag):
    v.spot(rect, [["cyc", flag, 5], ["sfx", "tick"],
                  ["if", all_(eq("s1_la", 3), eq("s1_lb", 0)), [["set", "s1_hatch", 1], ["sfx", "ok"]]]],
           all_(eq("s1_hatch", 0)) if flag == "s1_la" else all_(eq("s1_shutter", 1), eq("s1_hatch", 0)))


# ------------------------------------------------------------------ front wall
v = View("s1v1", 1, "ドアの壁", l="s1v2", r="s1v3")
s = v.s
wall(s, 250)
s.frect(150, 22, 110, 30, METAL, sw=2.4)
s.line(160, 37, 250, 37, sw=2, passes=1)
s.dot(205, 44, 3.5, BRASS)
s.paper(86, 120, 236, 176, [("博士の手順", 22), "1   ☆ を混ぜる", "2   △ を温める", "3   □ を冷やす", "4   ○ を飲む"], 20)
s.frect(392, 102, 176, 298, BLACK)
s.frect(400, 110, 160, 290, WOOD)
s.frect(418, 130, 124, 104, WOOD_D, sw=2)
s.frect(418, 252, 124, 130, WOOD_D, sw=2)
s.fell(544, 262, 8, 8, BRASS, sw=2.2)
s.paper(430, 62, 100, 32, [("出口", 19)], align="center", pin=False, pad=6)
# portrait of the potato professor
s.frect(646, 54, 116, 124, "#6b5437")
s.frect(657, 65, 94, 102, "#8f9b86", sw=2)
s.fell(704, 120, 30, 36, "#c8a66a", sw=2.5)
s.ellipse(693, 112, 9, 8, sw=2)
s.ellipse(715, 112, 9, 8, sw=2)
s.line(702, 111, 706, 111, sw=2, passes=1)
s.curve([(695, 136), (704, 140), (713, 136)], sw=2, passes=1)
for hx1, hx2, hy in ((699, 694, 76), (704, 705, 72), (709, 716, 77)):
    s.line(hx1, 86, hx2, hy, sw=1.8, passes=1)
s.dot(690, 128, 2, "#8a6a42")
s.dot(720, 104, 2, "#8a6a42")
# symbol panel
PX = [634, 684, 734, 784]


def panel(s, lit):
    s.frect(604, 196, 210, 108, METAL_D)
    for i, kind in enumerate(SYMS[:4]):
        s.frect(PX[i] - 22, 244, 44, 44, PAPER_L if lit else "#5d6a6c", sw=2.4)
        s.sym(kind, PX[i], 266, 12, INK, 2.8)
        s.fell(PX[i], 218, 7, 7, "#3a4648", sw=1.8)


panel(s, False)
s.vignette()

v.variant("hatch", (140, 14, 130, 96), eq("s1_hatch", 1), lambda s: (
    s.frect(150, 22, 110, 30, "#080b0c", sw=2.4),
    s.fpoly([(150, 52), (260, 52), (252, 96), (158, 96)], METAL, sw=2.4),
    s.line(170, 74, 240, 74, sw=2, passes=1)))
FUSE_ON_FLOOR = all_(eq("s1_hatch", 1), eq("s1_fusepick", 0))


def fuse(s, cx, cy, k=1.0):
    s.frect(cx - 22 * k, cy - 9 * k, 44 * k, 18 * k, "#d9d6c8", sw=2.2)
    s.frect(cx - 30 * k, cy - 7 * k, 9 * k, 14 * k, BRASS, sw=2)
    s.frect(cx + 21 * k, cy - 7 * k, 9 * k, 14 * k, BRASS, sw=2)
    s.line(cx - 16 * k, cy, cx + 16 * k, cy, sw=1.6, passes=1)


v.variant("fuse", (166, 436, 90, 56), FUSE_ON_FLOOR, lambda s: fuse(s, 210, 464))
v.spot((160, 426, 104, 76), [["give", "fuse"], ["set", "s1_fusepick", 1], ["sfx", "get"]], FUSE_ON_FLOOR)
v.variant("panel_on", (598, 190, 222, 120), eq("s1_power", 1), lambda s: panel(s, True))
seq_dots(v, "q1", 4, PX, 218, eq("s1_power", 1), deps=("panel_on",))
for i in range(4):
    v.spot((PX[i] - 24, 240, 48, 52),
           [["sfx", "tick"], ["seq", "q1", i, 4, [2, 3, 0, 1], [["set", "s1_door", 1], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]],
           all_(eq("s1_power", 1), eq("s1_door", 0)))
v.variant("door_open", (388, 98, 184, 306), eq("s1_door", 1), lambda s: (
    s.frect(392, 102, 176, 298, BLACK),
    s.frect(400, 110, 160, 290, "#0a0d0e"),
    s.solid([(400, 400), (560, 400), (520, 150), (440, 150)], LIGHT, 0.10),
    s.fpoly([(560, 110), (590, 128), (590, 418), (560, 400)], WOOD, sw=2.4)))
v.spot((400, 110, 160, 290), [["sfx", "door"], ["stage", 2]], eq("s1_door", 1))

# ------------------------------------------------------------------ left wall
v = View("s1v2", 1, "モニターの壁", r="s1v1")
s = v.s
wall(s, 250)
s.paper(84, 96, 226, 168, [("本日の暗号", 20), ("（上）", 17), ("2・6・1・4", 34), ("二つ合わせて一つ", 16)], align="center", gap=1.45)
lever_plate(s, 356, 104, "A")
lever_column(s, 356, 104, 4)
s.frect(532, 92, 256, 166, METAL)
s.frect(546, 104, 228, 140, "#0c1213", sw=2.4)
s.frect(630, 258, 60, 14, METAL_D, sw=2)
s.frect(596, 300, 118, 84, METAL_D)
s.frect(608, 312, 94, 60, "#1b2728", sw=2)
s.frect(622, 330, 10, 24, BRASS, sw=1.8)
s.frect(678, 330, 10, 24, BRASS, sw=1.8)
s.curve([(726, 300), (750, 290), (760, 258)], sw=4, stroke="#1b1f21", passes=1)
s.vignette()
for k in range(4):
    v.variant("la%d" % k, (424, 132, 42, 216), eq("s1_la", k), lambda s, k=k: lever_column(s, 356, 104, k))
lever_spot(v, (356, 104, 120, 250), "s1_la")
v.variant("mon", (540, 98, 240, 152), eq("s1_monitor", 1), lambda s: (
    s.frect(546, 104, 228, 140, "#17382b", sw=2.4),
    s.text(660, 174, "3→1→4→2", 36, "#bfe8c0"),
    s.line(556, 222, 764, 222, stroke="#2f6a4c", sw=1.5, passes=1)))
v.variant("fusein", (592, 296, 126, 92), eq("s1_power", 1), lambda s: (
    fuse(s, 655, 342, 0.9), s.glow(700, 306, 14, "#7fe08a", 0.16), s.dot(700, 306, 4, "#7fe08a")))
v.spot((590, 290, 130, 100), [["take", "fuse"], ["set", "s1_power", 1], ["sfx", "ok"], ["unsel"]], all_(["sel", "fuse"], eq("s1_power", 0)))

# ------------------------------------------------------------------ right wall
v = View("s1v3", 1, "机の壁", l="s1v1")
s = v.s
wall(s, 420)
s.paper(84, 78, 226, 168, [("本日の暗号", 20), ("（下）", 17), ("1・2・7・5", 34), ("二つ合わせて一つ", 16)], align="center", gap=1.45)
s.frect(250, 274, 76, 26, METAL_D, sw=2.4)
s.fell(288, 272, 27, 15, RED, sw=2.6)
s.frect(78, 300, 336, 22, WOOD_L)
s.frect(94, 322, 304, 122, WOOD)
s.frect(108, 334, 276, 74, WOOD_D, sw=2.4)
DX = [150, 198, 246, 294]
for x in DX:
    s.frect(x - 20, 346, 40, 50, PAPER_L, sw=2.2)
s.fell(350, 371, 17, 17, BRASS, sw=2.6)
s.line(343, 371, 357, 371, sw=2, passes=1)
s.frect(110, 444, 14, 60, WOOD_D, sw=2)
s.frect(368, 444, 14, 60, WOOD_D, sw=2)
# shutter
s.frect(470, 92, 296, 300, METAL_D)
for y in range(112, 384, 20):
    s.line(476, y, 760, y, sw=1.8, opacity=0.6, passes=1)
s.frect(776, 212, 38, 56, METAL, sw=2.4)
s.fell(795, 240, 9, 9, "#080b0c", sw=2)
s.vignette()
for i, x in enumerate(DX):
    fl = "s1_d%d" % (i + 1)
    v.text(x, 371, 32, fl, when=eq("s1_drawer", 0))
    v.spot((x - 22, 344, 44, 54), [["cyc", fl, 10], ["sfx", "tick"]], eq("s1_drawer", 0))
v.spot((328, 348, 46, 46), [["if", all_(eq("s1_d1", 3), eq("s1_d2", 8), eq("s1_d3", 8), eq("s1_d4", 9)),
                           [["set", "s1_drawer", 1], ["give", "handle"], ["sfx", "ok"]], [["sfx", "buzz"], ["shake"]]]], eq("s1_drawer", 0))
v.variant("drawer", (90, 326, 312, 150), eq("s1_drawer", 1), lambda s: (
    s.frect(108, 334, 276, 74, "#1b1512", sw=2.4),
    s.fpoly([(96, 392), (396, 392), (408, 466), (84, 466)], WOOD_D, sw=2.6),
    s.frect(100, 380, 292, 16, WOOD_L, sw=2.2),
    s.fell(246, 432, 14, 10, BRASS, sw=2.2)))
v.variant("btn_on", (236, 236, 104, 68), eq("s1_power", 1), lambda s: (
    s.glow(288, 268, 46, RED_L, 0.10), s.frect(250, 274, 76, 26, METAL_D, sw=2.4), s.fell(288, 272, 27, 15, RED_L, sw=2.6),
    s.curve([(274, 266), (284, 261), (296, 262)], stroke="#ffd0c0", sw=2.5, passes=1)))
v.spot((240, 240, 96, 62), [["set", "s1_monitor", 1], ["sfx", "ok"]], all_(eq("s1_power", 1), eq("s1_monitor", 0)))


def shutter_open(s):
    s.frect(470, 92, 296, 300, METAL_D)
    s.frect(480, 126, 276, 258, "#16201f", sw=2.4)
    s.frect(470, 92, 296, 36, METAL, sw=2.4)
    for y in (102, 112, 122):
        s.line(476, y, 760, y, sw=1.6, opacity=0.6, passes=1)
    lever_plate(s, 500, 130, "B")
    lever_column(s, 500, 130, 4)
    s.paper(640, 170, 104, 130, ["Aは", "最初。", "Bは", "最後。"], 18, pad=10)
    s.frect(776, 212, 38, 56, METAL, sw=2.4)
    s.line(795, 240, 822, 222, sw=6, stroke=BRASS)
    s.fell(824, 220, 8, 8, BRASS, sw=2)


v.variant("shut", (464, 86, 376, 312), eq("s1_shutter", 1), shutter_open)
for k in range(4):
    v.variant("lb%d" % k, (568, 158, 42, 216), all_(eq("s1_shutter", 1), eq("s1_lb", k)),
              lambda s, k=k: lever_column(s, 500, 130, k), deps=("shut",))
v.spot((760, 196, 66, 88), [["take", "handle"], ["set", "s1_shutter", 1], ["sfx", "ok"], ["unsel"]], all_(["sel", "handle"], eq("s1_shutter", 0)))
lever_spot(v, (500, 130, 120, 250), "s1_lb")


# ------------------------------------------------------------------ items and hints
def handle_icon(s):
    s.line(30, 66, 62, 34, sw=9, stroke=BRASS)
    s.line(30, 66, 62, 34, sw=2.2, passes=1)
    s.fell(26, 70, 9, 9, METAL, sw=2.4)
    s.fell(68, 28, 12, 12, RED_L, sw=2.6)


item("handle", handle_icon)
item("fuse", lambda s: fuse(s, 48, 48, 1.25))

puzzle("s1a", 1, "机の引き出し", None, eq("s1_drawer", 1),
       ["暗号のポスターは1枚ではない。",
        "左の壁に「上」、右の壁に「下」。どちらにも「二つ合わせて一つ」と書いてある。",
        "同じ順番の数字を足す。2＋1、6＋2、1＋7、4＋5。"],
       "3889", [["set", "s1_drawer", 1], ["give", "handle"]])
puzzle("s1b", 1, "2本のレバー", eq("s1_drawer", 1), eq("s1_hatch", 1),
       ["レバーは2本ある。もう1本は隠れている。引き出しの中身を使おう。",
        "シャッターの奥に「Aは最初。Bは最後。」とある。記号が並んだものを探そう。",
        "「博士の手順」の最初の記号は星、最後は丸。Aを星、Bを丸に合わせる。"],
       "Aを☆、Bを○", [["take", "handle"], ["set", "s1_shutter", 1], ["set", "s1_la", 3], ["set", "s1_lb", 0], ["set", "s1_hatch", 1]])
puzzle("s1c", 1, "ドアのパネル", eq("s1_hatch", 1), eq("s1_door", 1),
       ["落ちてきたヒューズを左の壁の箱に入れて、光った赤いボタンを押そう。",
        "モニターの数字は、「博士の手順」の番号。",
        "3番、1番、4番、2番の記号を順に押す。"],
       "四角 → 星 → 丸 → 三角",
       [["takeall", "fuse"], ["set", "s1_fusepick", 1], ["set", "s1_power", 1], ["set", "s1_monitor", 1], ["set", "s1_door", 1]])
