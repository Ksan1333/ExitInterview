"""Episode 2: titles, story captions, the stage list and the endings."""
from game.core import META, STAGES, START

START.clear()
START.update({"main2": 1, "test2": 9})
META.update(title="第2話 弁償バイト", tagline="こたつ代は、働いて返す")

CREDITS = ["作った人：けい と AI", "遊んだ人：2人"]
END_CAP = ["面談が終わった。", "ロボット『おつかれさまでした。結果は後日、郵送します』", "1週間後。手紙が届いた。"]
PASS_SECONDS = 45 * 60
MAX_HINTS = 3

STAGES.update({
    "1": dict(start="a1", cap=[
        "面接から1週間。手紙が2通届いた。",
        "1通目：不採用。",
        "2通目：こたつ修理代 98,000円。払えない場合は、1日働いて返すこと。",
        "勤務先：じゃがいも博士の なんでも屋。",
        "追伸：働きぶりによっては、採用もありえます。",
        "採用の条件：45分以内・ヒント3回まで・スキップなし。"]),
    "2": dict(start="b1", cap=[
        "シャッターの先は、台所だった。",
        "張り紙：『昼ごはんにカレーを作り、料理用エレベーターで社長室へ送ること』"]),
    "3": dict(start="c1", cap=[
        "カレーは、料理用エレベーターで上へ。2人は階段で上へ。",
        "社長室。博士はいない。机に『退職面談シート』。",
        "スピーカー『最後の仕事です。シートに博士のハンコを押して、出口のロボットと面談すること』"]),
    "31": dict(end=1, cap=END_CAP, credits=CREDITS,
               letter=["採用。", "理由：仕事が早く、", "ていねいだったため。", "（カレーは むらさきだったが、", "おいしかった）"]),
    "32": dict(end=1, cap=END_CAP, credits=CREDITS, letter=["不採用。", "理由：仕事をとばしたため。"]),
    "33": dict(end=1, cap=END_CAP, credits=CREDITS, letter=["不採用。", "理由：人に聞きすぎたため。"]),
    "34": dict(end=1, cap=END_CAP, credits=CREDITS, letter=["不採用。", "理由：45分で", "終わらなかったため。"]),
    "9": dict(start="t1", cap=[]),
    "90": dict(end=1, cap=["テスト部屋クリア。"], credits=[], letter=[]),
})

# the grade, decided by whoever opens the last door: skips first, then hints, then the time
GRADE = [["if", ["ge", "n_skip", 1], [["stage", 32]],
          [["if", ["gt", "n_hint", MAX_HINTS], [["stage", 33]],
            [["if", ["within", "t0", PASS_SECONDS], [["stage", 31]], [["stage", 34]]]]]]]]
