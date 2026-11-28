package com.ksan.exitinterview.engine

/** Shared room state: integer flags and shared item counts. Zero values are never stored. */
class GameState(val flags: Map<String, Int>, val items: Map<String, Int>) {
    fun f(k: String): Int = flags[k] ?: 0
    fun n(item: String): Int = items[item] ?: 0

    override fun equals(other: Any?): Boolean = other is GameState && other.flags == flags && other.items == items
    override fun hashCode(): Int = flags.hashCode() * 31 + items.hashCode()

    fun toJson(): String = Json.str(mapOf("f" to flags.toSortedMap(), "i" to items.toSortedMap()))

    companion object {
        val EMPTY = GameState(emptyMap(), emptyMap())

        fun fromJson(s: String): GameState = if (s.isEmpty()) EMPTY else fromAny(Json.parse(s))

        fun fromAny(v: Any?): GameState {
            val m = v.asMap()
            val f = HashMap<String, Int>()
            for ((k, x) in m["f"].asMap()) if (x.asInt() != 0) f[k] = x.asInt()
            val i = HashMap<String, Int>()
            for ((k, x) in m["i"].asMap()) if (x.asInt() > 0) i[k] = x.asInt()
            return GameState(f, i)
        }
    }
}

/** Things the acting device should do right away; they are not part of the shared state. */
class Fx {
    val sfx = ArrayList<String>()
    var shake = false
    var go: String? = null
    var unsel = false

    /** A short line shown on the acting device only ("It is locked." and the like). */
    var msg: String? = null

    /** A question to answer by typing ([Pack.asks]); the acting device opens it. */
    var ask: String? = null
}

/**
 * Result of one action. [reads] names every flag ("f:name") and item ("i:name") the action looked
 * at; the server uses it to tell whether the partner changed something this action depended on.
 */
class Outcome(val state: GameState, val fx: Fx, val changed: Boolean, val reads: Set<String>)

private class Work(private val base: GameState, val sel: String?, val now: Int, val pack: Pack) {
    val flags = HashMap(base.flags)
    val items = HashMap(base.items)
    val fx = Fx()
    val reads = HashSet<String>()

    fun f(k: String): Int {
        reads.add("f:$k")
        return flags[k] ?: 0
    }

    fun setF(k: String, v: Int) {
        if (v == 0) flags.remove(k) else flags[k] = v
    }

    fun n(k: String): Int {
        reads.add("i:$k")
        return items[k] ?: 0
    }

    fun setN(k: String, v: Int) {
        if (v <= 0) items.remove(k) else items[k] = v
    }

    fun test(cond: Any?): Boolean = Rules.testWith(cond, { f(it) }, { n(it) }, sel, now)

    fun outcome(): Outcome {
        val next = GameState(HashMap(flags), HashMap(items))
        return Outcome(next, fx, next != base, reads)
    }
}

object Rules {
    const val STAGE = "stage"
    const val T0 = "t0"
    const val T1 = "t1"
    const val N_HINT = "n_hint"
    const val N_SKIP = "n_skip"
    const val MAX_HINT = 4

    /** Evaluates a condition from the pack. [sel] is the item the acting player has selected. */
    fun test(cond: Any?, st: GameState, sel: String?, now: Int): Boolean =
        testWith(cond, { st.f(it) }, { st.n(it) }, sel, now)

    internal fun testWith(cond: Any?, f: (String) -> Int, n: (String) -> Int, sel: String?, now: Int): Boolean {
        if (cond == null) return true
        if (cond is Boolean) return cond
        val c = cond.asList()
        if (c.isEmpty()) return true
        val a = c.getOrNull(1)
        val b = c.getOrNull(2)
        return when (c[0].asStr()) {
            "eq" -> f(a.asStr() ?: "") == b.asInt()
            "ne" -> f(a.asStr() ?: "") != b.asInt()
            "ge" -> f(a.asStr() ?: "") >= b.asInt()
            "le" -> f(a.asStr() ?: "") <= b.asInt()
            "gt" -> f(a.asStr() ?: "") > b.asInt()
            "lt" -> f(a.asStr() ?: "") < b.asInt()
            "has" -> n(a.asStr() ?: "") >= (if (b == null) 1 else b.asInt())
            "sel" -> sel != null && sel == a.asStr()
            "cool" -> now < f(a.asStr() ?: "")
            // ["within", flag, seconds]: the time in flag (such as t0, when the game began) is less than seconds ago
            "within" -> f(a.asStr() ?: "").let { it != 0 && now - it < b.asInt() }
            "all" -> c.drop(1).all { testWith(it, f, n, sel, now) }
            "any" -> c.drop(1).any { testWith(it, f, n, sel, now) }
            "not" -> !testWith(a, f, n, sel, now)
            else -> false
        }
    }

    private fun run(ops: List<Any?>, w: Work) {
        for (raw in ops) {
            val o = raw.asList()
            if (o.isEmpty()) continue
            val a = o.getOrNull(1)
            val b = o.getOrNull(2)
            when (o[0].asStr()) {
                "set" -> w.setF(a.asStr() ?: "", b.asInt())
                "add" -> w.setF(a.asStr() ?: "", w.f(a.asStr() ?: "") + b.asInt())
                "cyc" -> w.setF(a.asStr() ?: "", (w.f(a.asStr() ?: "") + 1) % b.asInt().coerceAtLeast(1))
                "give" -> w.setN(a.asStr() ?: "", w.n(a.asStr() ?: "") + (if (b == null) 1 else b.asInt()))
                "take" -> w.setN(a.asStr() ?: "", w.n(a.asStr() ?: "") - (if (b == null) 1 else b.asInt()))
                "takeall" -> w.setN(a.asStr() ?: "", 0)
                "givef" -> w.setN(a.asStr() ?: "", w.n(a.asStr() ?: "") + w.f(b.asStr() ?: ""))
                "go" -> w.fx.go = a.asStr()
                "sfx" -> a.asStr()?.let { w.fx.sfx.add(it) }
                "shake" -> w.fx.shake = true
                "unsel" -> w.fx.unsel = true
                "msg" -> w.fx.msg = a.asStr()
                "ask" -> w.fx.ask = a.asStr()
                "cool" -> w.setF(a.asStr() ?: "", w.now + b.asInt())
                "if" -> {
                    val yes = w.test(a)
                    run((if (yes) b else o.getOrNull(3)).asList(), w)
                }
                "seq" -> seq(o, w)
                "maze" -> maze(a.asStr() ?: "", b.asInt(), w)
                "stage" -> {
                    w.setF(STAGE, a.asInt())
                    if (w.f(T0) == 0) w.setF(T0, w.now)
                    if (w.pack.stages[a.asInt()]?.end == true && w.f(T1) == 0) w.setF(T1, w.now)
                }
            }
        }
    }

    /** ["seq", buffer, symbol, length, [answer...], [ok ops], [ng ops]] */
    private fun seq(o: List<Any?>, w: Work) {
        val buf = o.getOrNull(1).asStr() ?: return
        val sym = o.getOrNull(2).asInt()
        val len = o.getOrNull(3).asInt()
        val ans = o.getOrNull(4).asList().map { it.asInt() }
        val count = w.f(buf + "_n") + 1
        val value = w.f(buf) * 8 + sym + 1
        if (count < len) {
            w.setF(buf, value)
            w.setF(buf + "_n", count)
            return
        }
        var want = 0
        for (s in ans) want = want * 8 + s + 1
        w.setF(buf, 0)
        w.setF(buf + "_n", 0)
        run((if (value == want) o.getOrNull(5) else o.getOrNull(6)).asList(), w)
    }

    /** Button directions: 0 up, 1 right, 2 down, 3 left. Row 0 is the near side. */
    private fun maze(id: String, button: Int, w: Work) {
        val m = w.pack.mazes[id] ?: return
        val dir = m.remap.getOrElse(button) { button }
        val pos = w.f(m.pos)
        if (pos == m.goal) return
        var col = pos % m.w
        var row = pos / m.w
        when (dir) {
            0 -> row += 1
            1 -> col += 1
            2 -> row -= 1
            3 -> col -= 1
        }
        if (col < 0 || col >= m.w || row < 0 || row >= m.h) {
            w.fx.sfx.add("tick")
            return
        }
        val next = row * m.w + col
        if (next in m.blocked) {
            w.setF(m.pos, m.start)
            w.fx.sfx.add("buzz")
            w.fx.shake = true
            return
        }
        w.setF(m.pos, next)
        w.fx.sfx.add("move")
        if (next == m.goal) run(m.ok, w)
    }

    /** A tap at (x, y) in the 960x540 space of [viewId]. Null when nothing is there or the view is closed. */
    fun tap(pack: Pack, st: GameState, viewId: String, x: Float, y: Float, sel: String?, now: Int): Outcome? {
        val view = pack.views[viewId] ?: return null
        val w = Work(st, sel, now, pack)
        if (w.f(STAGE) != view.stage || !w.test(view.cond)) return null
        val spot = view.spots.firstOrNull { it.swipe == null && it.hit(x, y) && w.test(it.cond) } ?: return null
        run(spot.ops, w)
        if (w.f(T0) == 0) w.setF(T0, now)
        return w.outcome()
    }

    /** A finger drawn across [viewId] from (x, y) in direction [dir] (0 up, 1 right, 2 down, 3 left). */
    fun swipe(pack: Pack, st: GameState, viewId: String, x: Float, y: Float, dir: Int, sel: String?, now: Int): Outcome? {
        val view = pack.views[viewId] ?: return null
        val w = Work(st, sel, now, pack)
        if (w.f(STAGE) != view.stage || !w.test(view.cond)) return null
        val spot = view.spots.firstOrNull { (it.swipe == dir || it.swipe == Spot.ANY) && it.hit(x, y) && w.test(it.cond) } ?: return null
        run(spot.ops, w)
        if (w.f(T0) == 0) w.setF(T0, now)
        return w.outcome()
    }

    /** A typed answer to the question [askId]. Null when the question is closed (the partner answered it already). */
    fun answer(pack: Pack, st: GameState, askId: String, text: String, now: Int): Outcome? {
        val q = pack.asks[askId] ?: return null
        val w = Work(st, null, now, pack)
        if (!w.test(q.cond)) return null
        val said = normalize(text)
        if (said.isEmpty()) return null
        run(if (q.answers.any { normalize(it) == said }) q.ok else q.ng, w)
        if (w.f(T0) == 0) w.setF(T0, now)
        return w.outcome()
    }

    /** The held thing [a] used on the held thing [b]. Null when the two do not go together. */
    fun combine(pack: Pack, st: GameState, a: String, b: String, now: Int): Outcome? {
        if (a == b) return null
        val w = Work(st, null, now, pack)
        val c = pack.combos.firstOrNull { ((it.a == a && it.b == b) || (it.a == b && it.b == a)) } ?: return null
        if (w.n(a) <= 0 || w.n(b) <= 0 || !w.test(c.cond)) return null
        run(c.ops, w)
        if (w.f(T0) == 0) w.setF(T0, now)
        return w.outcome()
    }

    /**
     * How typed answers are compared: full-width and half-width forms, upper and lower case, katakana and hiragana
     * count as the same, and spaces and punctuation are left out.
     */
    fun normalize(text: String): String {
        // after NFKC, full-width punctuation is already half-width; the long vowel mark ー is kept (it is part of words)
        val t = java.text.Normalizer.normalize(text, java.text.Normalizer.Form.NFKC).lowercase()
        val out = StringBuilder()
        for (ch in t) {
            when {
                ch.isWhitespace() || ch in DROP -> Unit
                ch in 'ァ'..'ヶ' -> out.append(ch - 0x60)
                else -> out.append(ch)
            }
        }
        return out.toString()
    }

    private const val DROP = "。、,.・!?「」『』()〜~-"

    /** Puzzles of the current stage that can be worked on now and are not finished. */
    fun openPuzzles(pack: Pack, st: GameState, now: Int): List<Puzzle> {
        val stage = st.f(STAGE)
        return pack.puzzles.filter { it.stage == stage && test(it.avail, st, null, now) && !test(it.done, st, null, now) }
    }

    fun hintLevel(st: GameState, puzzleId: String): Int = st.f("h_$puzzleId")

    /** Opens the next hint level (1..3 are hints, 4 is the answer) for both players. */
    fun revealHint(pack: Pack, st: GameState, puzzleId: String, now: Int): Outcome {
        val w = Work(st, null, now, pack)
        val level = w.f("h_$puzzleId")
        if (level < MAX_HINT) {
            w.setF("h_$puzzleId", level + 1)
            w.setF(N_HINT, w.f(N_HINT) + 1)
        }
        return w.outcome()
    }

    /** Solves a puzzle for the players. */
    fun skip(pack: Pack, st: GameState, puzzleId: String, now: Int): Outcome {
        val w = Work(st, null, now, pack)
        val p = pack.puzzles.firstOrNull { it.id == puzzleId }
        if (p != null && w.f(STAGE) == p.stage && w.test(p.avail) && !w.test(p.done)) {
            run(p.skip, w)
            w.setF(N_SKIP, w.f(N_SKIP) + 1)
        }
        return w.outcome()
    }

    /** First state of a room. */
    fun initialState(pack: Pack, mode: String): GameState {
        val f = HashMap(pack.initial.flags)
        f[STAGE] = pack.startStage[mode] ?: 1
        return GameState(f, HashMap(pack.initial.items))
    }

    /** Where a player should be: the wanted view if it is still open, else its parent, else the stage start. */
    fun resolve(pack: Pack, st: GameState, wanted: String?, now: Int): String? {
        val stage = st.f(STAGE)
        val start = pack.stages[stage]?.start
        var v = pack.views[wanted ?: ""] ?: return start
        if (v.stage != stage) return start
        var guard = 0
        while (!test(v.cond, st, null, now)) {
            v = pack.views[v.back ?: ""] ?: return start
            if (++guard > 8) return start
        }
        return v.id
    }

    /** Seconds played so far (or in total once the game has ended). */
    fun playSeconds(st: GameState, now: Int): Int {
        val t0 = st.f(T0)
        if (t0 == 0) return 0
        val t1 = st.f(T1)
        return ((if (t1 != 0) t1 else now) - t0).coerceAtLeast(0)
    }
}
