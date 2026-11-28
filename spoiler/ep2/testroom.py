"""Episode 2 test room: one of each new way to play (rub, type, put two things together, turn a thing over)."""
from ep2.look import *  # noqa: F401,F403

v = View("t1", 9, "テスト部屋")
s = v.s
warehouse(s, 480)
# the dusty sign
s.frect(110, 96, 220, 120, PAPER_L, sw=2.4)
s.text(220, 156, "ねこ", 48)
s.paper(118, 226, 204, 40, [("こすってみる", 17)], align="center", pin=False, pad=6)
# the box with a question
s.frect(400, 260, 160, 120, WOOD, sw=2.4)
s.frect(400, 246, 160, 20, WOOD_L, sw=2.2)
s.paper(430, 290, 100, 56, [("？", 34)], align="center", pin=False, pad=4)
# two dials (for checking two players at once)
for i, x in enumerate((640, 740)):
    s.frect(x - 36, 110, 72, 84, METAL_D, sw=2.4)
    s.frect(x - 26, 122, 52, 56, PAPER_L, sw=2)
s.paper(612, 206, 166, 32, [("テスト用ダイヤル", 15)], align="center", pin=False, pad=5)
# the door
s.frect(640, 270, 120, 140, WOOD_D, sw=2.6)
s.fell(744, 342, 7, 7, BRASS, sw=2)
s.paper(652, 248, 96, 28, [("出口", 17)], align="center", pin=False, pad=4)
s.vignette()


def sign_dust(level):
    return lambda s: s.frect(110, 96, 220, 120, DUST, op=level)


for k, lv in enumerate((0.97, 0.75, 0.45)):
    v.variant("dust%d" % k, (104, 90, 232, 132), eq("t_dust", k), sign_dust(lv))
v.variant("boxopen", (394, 236, 172, 150), eq("t_box", 1), lambda s: (
    s.frect(400, 260, 160, 120, WOOD, sw=2.4), s.frect(410, 270, 140, 50, "#1d1612", sw=2)))
v.variant("half2", (150, 430, 100, 60), eq("t_half", 0), lambda s: key_part(s, 200, 460, 0.9, "bottom"))
v.variant("card", (300, 436, 110, 60), eq("t_card", 0), lambda s: s.frect(316, 448, 80, 40, PAPER_L, sw=2))
v.variant("dooropen", (634, 264, 132, 152), eq("t_door", 1), lambda s: s.frect(640, 270, 120, 140, "#0a0d0e", sw=2.6))
for i, x in enumerate((640, 740)):
    v.text(x, 150, 34, "t_d%d" % (i + 1))
    v.spot((x - 36, 110, 72, 84), [["cyc", "t_d%d" % (i + 1), 10], ["sfx", "tick"]])
v.spot((110, 96, 220, 120), [["add", "t_dust", 1], ["sfx", "tick"]], ["lt", "t_dust", 3], swipe=4)
v.spot((110, 96, 220, 120), [["msg", "ほこりで読めない。指でこすってみよう。"]], ["lt", "t_dust", 3])
v.spot((400, 246, 160, 134), [["ask", "t_word"]], eq("t_box", 0))
v.spot((150, 430, 100, 60), [["give", "kh2"], ["set", "t_half", 1], ["sfx", "get"]], eq("t_half", 0))
v.spot((300, 436, 110, 60), [["give", "tcard"], ["set", "t_card", 1], ["sfx", "get"]], eq("t_card", 0))
v.spot((640, 270, 120, 140), [["take", "tkey"], ["set", "t_door", 1], ["sfx", "door"], ["unsel"]], all_(["sel", "tkey"], eq("t_door", 0)))
v.spot((640, 270, 120, 140), [["msg", "鍵がかかっている。"]], eq("t_door", 0))
v.spot((640, 270, 120, 140), [["takeall", "tcard"], ["stage", 90]], eq("t_door", 1))

ask("t_word", "箱『看板の字は？』", ["ねこ", "猫", "neko"],
    [["set", "t_box", 1], ["give", "kh1"], ["sfx", "ok"], ["msg", "箱が開いた。鍵の上半分が入っていた。"]], when=eq("t_box", 0))


item("kh1", lambda s: key_part(s, 54, 48, 1.1, "top"), "鍵の上半分", ["下半分と合わせられそう。"])
item("kh2", lambda s: key_part(s, 40, 48, 1.1, "bottom"), "鍵の下半分", ["上半分と合わせられそう。"])
item("tkey", lambda s: key_icon(s, 50, 48, 1.05), "出口の鍵", ["2つを合わせた。"])
item("tcard", lambda s: s.paper(16, 22, 64, 52, [("表", 22)], align="center", pin=False, pad=4), "テスト用カード", ["裏返して見られる。"],
     zoom=lambda s: (s.frect(0, 0, 480, 360, "#232b2b", outline=False), s.paper(90, 60, 300, 240, [("おもて", 48)], align="center", pin=False, pad=70)),
     back=lambda s: (s.frect(0, 0, 480, 360, "#232b2b", outline=False), s.paper(90, 60, 300, 240, [("うら", 48)], align="center", pin=False, pad=70)))
combo("kh1", "kh2", [["take", "kh1"], ["take", "kh2"], ["give", "tkey"], ["sfx", "ok"], ["msg", "鍵ができた！"]])

puzzle("t1", 9, "テスト部屋", None, eq("t_door", 1),
       ["看板を指でこすって、字を読む。", "箱をタップして、看板の字を入れる。床の半分と合わせる。",
        "鍵の上半分を選んで、下半分をタップ。できた鍵で出口を開ける。"],
       "ねこ → 鍵を合わせる → 出口",
       [["set", "t_dust", 3], ["set", "t_box", 1], ["set", "t_half", 1], ["takeall", "kh1"], ["takeall", "kh2"], ["takeall", "tkey"],
        ["set", "t_door", 1]])
