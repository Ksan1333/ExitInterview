// Checks episode 2 (stage2.pack) with the real engine: a full walkthrough, every skip, the grades, wrong answers,
// a search for dead ends, and two players acting at the same time. Contains the answers. Do not open.
import com.ksan.exitinterview.engine.*
import java.io.File
import kotlin.system.exitProcess

sealed class Step
class Tap(val view: String, val x: Float, val y: Float, val times: Int = 1) : Step()
class Swipe(val view: String, val x: Float, val y: Float, val dir: Int, val times: Int = 1) : Step()
class Sel(val item: String?) : Step()
class Ask(val id: String, val text: String) : Step()
class Combine(val a: String, val b: String) : Step()

fun tap(view: String, x: Int, y: Int, times: Int = 1) = Tap(view, x.toFloat(), y.toFloat(), times)
fun swipe(view: String, x: Int, y: Int, dir: Int, times: Int = 1) = Swipe(view, x.toFloat(), y.toFloat(), dir, times)

const val PASS_SECONDS = 45 * 60
val ENDS = setOf(31, 32, 33, 34)

/** One action of a step on a state; null when it cannot be done there. */
fun act(pack: Pack, st: GameState, step: Step, sel: String?, now: Int): Outcome? = when (step) {
    is Tap -> if (Rules.resolve(pack, st, step.view, now) != step.view) null else Rules.tap(pack, st, step.view, step.x, step.y, sel, now)
    is Swipe -> if (Rules.resolve(pack, st, step.view, now) != step.view) null else Rules.swipe(pack, st, step.view, step.x, step.y, step.dir, sel, now)
    is Ask -> Rules.answer(pack, st, step.id, step.text, now)
    is Combine -> Rules.combine(pack, st, step.a, step.b, now)
    is Sel -> null
}

fun timesOf(step: Step) = when (step) {
    is Tap -> step.times
    is Swipe -> step.times
    else -> 1
}

class Sim(val pack: Pack, mode: String) {
    var st = Rules.initialState(pack, mode)
    var sel: String? = null
    var now = 1_800_000_000
    var maxHeld = 0

    /** Returns false when the step could not be done (view closed, nothing there, item missing). */
    fun run(step: Step): Boolean {
        if (step is Sel) {
            if (step.item != null && st.n(step.item) <= 0) return false
            sel = step.item
            return true
        }
        repeat(timesOf(step)) {
            val o = act(pack, st, step, sel, now) ?: return false
            st = o.state
            maxHeld = maxOf(maxHeld, st.items.size)
            if (o.fx.unsel || (step is Combine && o.changed) || (sel != null && st.n(sel!!) <= 0)) sel = null
            now += 1
        }
        return true
    }
}

const val POT_X = 410
const val POT_Y = 188
val BOOKS_ON = listOf(tap("c3", 277, 149), tap("c3", 351, 289), tap("c3", 499, 289))

val MAIN: LinkedHashMap<String, List<Step>> = linkedMapOf(
    "p1" to listOf(tap("a2", 131, 454), tap("a3", 300, 140), Combine("flash", "battery"), Sel("flashon"), tap("a2gap", 480, 260)),
    "p2" to listOf(swipe("a3mir", 480, 270, 1, 4)),
    "p4" to listOf(tap("a4", 716, 212), Ask("a_word", "おつかれ")),
    "p3" to listOf(tap("a3", 182, 253), tap("a3", 308, 253), tap("a3", 434, 253), tap("a2gap", 490, 372),
        Sel("pc"), tap("a2", 232, 196), Sel("pd"), tap("a2", 387, 196), Sel("pa"), tap("a2", 542, 196), Sel("pb"), tap("a2", 697, 196)),
    "p5" to listOf(tap("a2", 480, 88), Sel("skey"), tap("a1", 726, 292), tap("a4", 124, 383)),
    "x1" to listOf(tap("a1", 480, 250)),
    "q1" to listOf(tap("b3pipe", 428, 360), tap("b3pipe", 524, 360, 3), tap("b3pipe", 524, 264, 3), tap("b3pipe", 620, 264, 2), tap("b3pipe", 620, 168)),
    "q2" to listOf(tap("b3jug", 640, 250), swipe("b3jug", 640, 250, 3), swipe("b3jug", 330, 310, 2), swipe("b3jug", 640, 250, 3),
        tap("b3jug", 640, 250), swipe("b3jug", 640, 250, 3), tap("b3jug", 640, 250)),
    "q3" to listOf(tap("b4door", 540, 94), tap("b4door", 660, 124), tap("b4door", 584, 355)),
    "q5" to listOf(tap("b4", 631, 262), tap("b4in", 300, 145), tap("b4in", 500, 135), tap("b3", 195, 145, 2),
        Sel("mizu"), tap("b2", POT_X, POT_Y), Sel("imo"), tap("b2", POT_X, POT_Y), Sel("ninjin"), tap("b2", POT_X, POT_Y),
        Sel("tamanegi"), tap("b2", POT_X, POT_Y), tap("b2", 370, 291), tap("b2", 370, 291), Sel("roux"), tap("b2", POT_X, POT_Y)),
    "q4" to listOf(tap("b2rack", 200, 354), Sel("juice"), tap("b2", POT_X, POT_Y)),
    "x2" to listOf(tap("b2", POT_X, POT_Y), tap("b1", 480, 250), Sel("curry"), tap("b1", 480, 250), tap("b1", 633, 252)),
    "r1" to listOf(tap("c1", 662, 251)) + BOOKS_ON + listOf(tap("c1", 662, 251)),
    "r2" to listOf(tap("c3", 386, 383), Sel("card"), tap("c2desk", 664, 267)),
    "r3" to listOf(swipe("c3globe", 480, 250, 1), tap("c3globe", 480, 250)),
    "r4" to listOf(tap("c3globe", 480, 250), Sel("hanko"), tap("c2desk", 340, 440)),
    "r5" to listOf(tap("c2desk", 240, 265), tap("c3globe", 480, 250), tap("c3", 386, 383)) + BOOKS_ON + listOf(Sel("sheet2"), tap("c1", 312, 294)),
)

val TEST: LinkedHashMap<String, List<Step>> = linkedMapOf(
    "t1" to listOf(swipe("t1", 220, 156, 1, 3), tap("t1", 480, 313), Ask("t_word", "ねこ"), tap("t1", 200, 460), tap("t1", 355, 466),
        Combine("kh1", "kh2"), Sel("tkey"), tap("t1", 700, 340)),
    "x" to listOf(tap("t1", 700, 340)),
)

var failures = 0
fun check(ok: Boolean, what: String) {
    println((if (ok) "ok    " else "FAIL  ") + what)
    if (!ok) failures++
}

fun runAll(pack: Pack, mode: String, script: Map<String, List<Step>>, skip: String? = null, upTo: String? = null, sim: Sim = Sim(pack, mode)): Sim {
    for ((name, steps) in script) {
        if (name == upTo) break
        if (name == skip) {
            sim.st = Rules.skip(pack, sim.st, name, sim.now).state
            sim.sel = null
            continue
        }
        for ((i, s) in steps.withIndex()) if (!sim.run(s)) throw IllegalStateException("step $name#$i failed")
    }
    return sim
}

fun reorder(keys: List<String>): LinkedHashMap<String, List<Step>> {
    val m = LinkedHashMap<String, List<Step>>()
    for (k in keys) m[k] = MAIN[k]!!
    check(m.keys == MAIN.keys, "reordered walkthrough has every part")
    return m
}

fun walkthroughs(pack: Pack) {
    val a = runAll(pack, "main2", MAIN)
    check(a.st.f("stage") == 31 && a.st.f("t1") != 0, "walkthrough reaches the passing ending (${a.st.f("stage")})")
    check(a.st.items.isEmpty(), "no item is left over at the end (${a.st.items})")
    check(a.maxHeld <= 6, "never more than 6 things held at once (${a.maxHeld})")
    val swapped = reorder(listOf("p2", "p4", "p1", "p3", "p5", "x1", "q3", "q1", "q2", "q5", "q4", "x2", "r3", "r1", "r2", "r4", "r5"))
    check(runAll(pack, "main2", swapped).st.f("stage") == 31, "walkthrough with free puzzles in another order")
    val t = runAll(pack, "test2", TEST)
    check(t.st.f("stage") == 90 && t.st.items.isEmpty(), "test room walkthrough")
    for (p in pack.puzzles) {
        val test = p.stage == 9
        val ok = try {
            val s = runAll(pack, if (test) "test2" else "main2", if (test) TEST else MAIN, skip = p.id)
            (if (test) s.st.f("stage") == 90 else s.st.f("stage") == 32) && s.st.f(Rules.N_SKIP) == 1 && s.st.items.isEmpty()
        } catch (e: IllegalStateException) {
            println("      " + e.message)
            false
        }
        check(ok, "skip ${p.id} then finish (a skip fails the interview)")
    }
    for (p in pack.puzzles.filter { it.stage != 9 }) {
        val before = runAll(pack, "main2", MAIN, upTo = p.id)
        check(Rules.openPuzzles(pack, before.st, before.now).any { it.id == p.id }, "hint for ${p.id} is offered when needed")
        check(p.hints.size == 3 && p.hints.all { it.isNotBlank() } && p.answer.isNotBlank(), "${p.id} has 3 hints and an answer")
    }
}

/** The walkthrough with something done to the state just before the last tap. */
fun finishWith(pack: Pack, before: (Sim) -> Unit, last: (Sim) -> Unit = {}): Sim {
    val s = Sim(pack, "main2")
    before(s)
    val steps = MAIN.values.flatten()
    for ((i, st) in steps.withIndex()) {
        if (i == steps.size - 1) last(s)
        if (!s.run(st)) throw IllegalStateException("step $i failed")
    }
    return s
}

fun grades(pack: Pack) {
    fun hints(n: Int): (Sim) -> Unit = { s ->
        repeat(n) { s.st = Rules.revealHint(pack, s.st, "p1", s.now).state }
    }
    check(finishWith(pack, hints(3)).st.f("stage") == 31, "3 hints still pass")
    check(finishWith(pack, hints(4)).st.f("stage") == 33, "a 4th hint fails (too many questions)")
    val late = finishWith(pack, {}, { s -> s.now = s.st.f("t0") + PASS_SECONDS })
    check(late.st.f("stage") == 34, "45 minutes or more fails (too slow)")
    val justIn = finishWith(pack, {}, { s -> s.now = s.st.f("t0") + PASS_SECONDS - 1 })
    check(justIn.st.f("stage") == 31, "a second under 45 minutes passes")
    val both = runAll(pack, "main2", MAIN, skip = "q3", sim = Sim(pack, "main2").also { hints(4)(it) })
    check(both.st.f("stage") == 32, "a skip decides before hints")
    val ending = pack.stages[31]!!
    check(ending.end && ending.letter.firstOrNull() == "採用。", "the passing letter says so")
    for (id in 32..34) check(pack.stages[id]!!.end && pack.stages[id]!!.letter.firstOrNull() == "不採用。", "ending $id is a failing letter")
}

fun wrongAnswers(pack: Pack) {
    // parcels in the wrong order buzz and can be taken down again
    val a = runAll(pack, "main2", MAIN, upTo = "p3")
    for (st in listOf(tap("a3", 182, 253), tap("a3", 308, 253), tap("a3", 434, 253), tap("a2gap", 490, 372), Sel("pa"), tap("a2", 232, 196), Sel("pb"),
        tap("a2", 387, 196), Sel("pc"), tap("a2", 542, 196), Sel("pd"), tap("a2", 697, 196))) a.run(st)
    check(a.st.f("a_sorted") == 0 && (1..4).all { a.st.f("a_s$it") != 0 }, "parcels in the wrong order do not open the box")
    a.run(tap("a2", 232, 196))
    check(a.st.f("a_s1") == 0 && a.st.n("pa") == 1, "a parcel can be taken back down")
    // the password
    val b = Sim(pack, "main2")
    b.run(Ask("a_word", "こんにちは"))
    check(b.st.f("a_word") == 0, "a wrong password does nothing")
    check(b.run(Ask("a_word", " オツカレ ")) && b.st.f("a_word") == 1, "the password in katakana with spaces is accepted")
    check(Rules.answer(pack, b.st, "a_word", "おつかれ", b.now) == null, "the password question closes once answered")
    // the shutter needs the key and the lever within 6 seconds of each other, in either order
    val c = runAll(pack, "main2", MAIN, upTo = "p5")
    c.run(tap("a2", 480, 88)); c.run(Sel("skey")); c.run(tap("a1", 726, 292))
    c.now += 7
    c.run(tap("a4", 124, 383))
    check(c.st.f("a_open") == 0, "key and lever 7 seconds apart do not open the shutter")
    c.now += 7
    c.run(tap("a4", 124, 383)); c.run(Sel("skey")); c.now += 4; c.run(tap("a1", 726, 292))
    check(c.st.f("a_open") == 1 && c.st.n("skey") == 0, "lever first, then the key 5 seconds later, opens it")
    // the mirror needs four rubs
    val d = Sim(pack, "main2")
    d.run(swipe("a3mir", 480, 270, -1, 3))
    check(d.st.f("a_dust") == 3, "three rubs leave dust on the mirror")
    d.run(swipe("a3mir", 480, 270, 2))
    check(d.st.f("a_dust") == 4, "the fourth stroke cleans it")
    // the kitchen
    val e = runAll(pack, "main2", MAIN, upTo = "q1")
    e.run(tap("b3jug", 330, 310))
    check(e.st.f("b_j3") == 0, "no water before the pipes are joined")
    e.run(tap("b3pipe", 428, 360, 4))
    check(e.st.f("b_t20") == pack.initial.f("b_t20") && e.st.f("b_pipe") == 0, "four turns bring a pipe back, no water")
    val f = runAll(pack, "main2", MAIN, upTo = "q2")
    f.run(tap("b3jug", 640, 250)); f.run(tap("b3jug", 640, 250))
    check(f.st.f("b_j5") == 5 && f.st.n("mizu") == 0, "a full big jug is not 4 cups")
    f.run(swipe("b3jug", 330, 310, 1))
    check(f.st.f("b_j3") == 0 && f.st.f("b_j5") == 5, "pouring from an empty jug does nothing")
    val g = runAll(pack, "main2", MAIN, upTo = "q3")
    g.run(tap("b4door", 350, 200))
    check((1..3).all { g.st.f("b_df$it") == 0 }, "tapping a part that is the same as the photo does not count")
    val h = runAll(pack, "main2", MAIN, upTo = "q4")
    h.run(tap("b2rack", 360, 154))
    check(h.st.n("juice") == 0 && h.st.f("b_lock") > h.now, "a wrong bottle locks the rack")
    h.run(tap("b2rack", 200, 354))
    check(h.st.n("juice") == 0, "the right bottle does not come out while locked")
    h.now += 31
    h.run(tap("b2rack", 200, 354))
    check(h.st.n("juice") == 1, "after 30 seconds the right bottle comes out")
    val k = runAll(pack, "main2", MAIN, upTo = "q5")
    for (st in MAIN["q5"]!!.dropLast(3)) k.run(st)
    check(k.st.f("b_pot") == 5 && k.st.f("b_fire") == 1, "the pot boils once everything is in and the fire is on")
    k.run(Sel("roux")); k.run(tap("b2", POT_X, POT_Y))
    check(k.st.n("roux") == 1 && k.st.f("b_pot") == 5, "roux into a pot on the fire is refused")
    k.run(tap("b2", 370, 291)); k.run(Sel("roux")); k.run(tap("b2", POT_X, POT_Y))
    check(k.st.f("b_pot") == 6, "roux goes in once the fire is off")
    // the office
    val m = runAll(pack, "main2", MAIN, upTo = "r1")
    for (st in listOf(tap("c1", 662, 251), tap("c3", 203, 149)) + BOOKS_ON) m.run(st)
    check(m.st.f("c_drawer") == 0, "a fourth book pulled keeps the drawer shut")
    m.run(tap("c3", 203, 149))
    check(m.st.f("c_drawer") == 1, "pushing it back opens the drawer")
    val n = runAll(pack, "main2", MAIN, upTo = "r3")
    n.run(tap("c3globe", 480, 250))
    check(n.st.f("c_globe") == 0 && n.st.f("c_glock") > n.now, "pressing the wrong continent locks the globe")
    n.run(swipe("c3globe", 480, 250, 1)); n.run(tap("c3globe", 480, 250))
    check(n.st.f("c_globe") == 0, "the right continent does not open while locked")
    n.now += 21
    n.run(tap("c3globe", 480, 250))
    check(n.st.f("c_globe") == 1, "after 20 seconds the right continent opens it")
    n.run(tap("c3globe", 480, 250)); n.run(swipe("c3globe", 480, 250, 3))
    check(n.st.f("c_gf") == 5, "the open globe does not turn")
    val r5 = MAIN["r5"]!!
    val o = runAll(pack, "main2", MAIN, upTo = "r5")
    o.run(r5[0])
    o.run(Sel("sheet2")); o.run(tap("c1", 312, 294))
    check(o.st.f("c_end") == 0 && o.st.n("sheet2") == 1, "the robot refuses while things are left out")
    for (st in r5.subList(1, r5.size - 2)) o.run(st)
    o.run(tap("c1", 662, 251)); o.run(Sel("sheet2")); o.run(tap("c1", 312, 294))
    check(o.st.f("c_end") == 0, "the robot refuses in the dark")
    o.run(tap("c1", 662, 251)); o.run(Sel("sheet2")); o.run(tap("c1", 312, 294))
    check(o.st.f("stage") == 31, "tidied and in the light, the interview ends")
    // the test room
    val t = Sim(pack, "test2")
    t.run(Ask("t_word", "いぬ"))
    check(t.st.f("t_box") == 0, "test room: a wrong word keeps the box shut")
    check(Rules.normalize("ネコ") == Rules.normalize("ねこ") && Rules.normalize("ＮＥＫＯ") == "neko", "typed answers ignore kana kind and width")
}

/** Every first argument of op [name] anywhere inside [ops], nested branches included. */
fun opArgs(ops: List<Any?>, name: String, out: MutableCollection<String>) {
    for (o in ops) {
        val l = o as? List<*> ?: continue
        if (l.firstOrNull() == name && l.size > 1 && l[1] is String) out.add(l[1] as String)
        @Suppress("UNCHECKED_CAST")
        for (x in l) if (x is List<*>) opArgs(x as List<Any?>, name, out)
    }
}

val VOLATILE = Regex("^(a_kt|a_lt|b_t\\d\\d|b_j3|b_j5|b_fire|b_lock|c_bk\\d+|c_gf|c_glock|c_dark|t_d\\d|h_.*|n_hint|n_skip|t0|t1)$")
val SLOT_ITEM = mapOf(1 to "pa", 2 to "pb", 3 to "pc", 4 to "pd")

/** Forgets what can always be set again: dials, timers, the light, pulled books, parcels on the shelf, the card on the paper. */
fun canon(pack: Pack, st: GameState): GameState {
    val f = HashMap<String, Int>()
    val items = HashMap(st.items)
    for ((k, v) in st.flags) if (!VOLATILE.matches(k)) f[k] = v
    for ((k, v) in pack.initial.flags) if (VOLATILE.matches(k)) f[k] = v
    if ((f["a_sorted"] ?: 0) == 0) for (k in 1..4) {
        val v = f.remove("a_s$k") ?: continue
        val id = SLOT_ITEM.getValue(v)
        items[id] = (items[id] ?: 0) + 1
    }
    if (f.remove("c_ov") != null) items["card"] = (items["card"] ?: 0) + 1
    return GameState(f, items)
}

fun deadEnds(pack: Pack, mode: String, script: Map<String, List<Step>>, goal: (Int) -> Boolean) {
    val now = 1_800_000_000
    val ids = HashMap<GameState, Int>()
    val states = ArrayList<GameState>()
    val back = ArrayList<ArrayList<Int>>()
    fun idOf(s: GameState): Int = ids.getOrPut(s) { states.add(s); back.add(ArrayList()); states.size - 1 }
    idOf(canon(pack, Rules.initialState(pack, mode)))
    // a typed question only opens from something on screen, so only those of the current stage can be answered
    val asksIn = HashMap<Int, MutableSet<String>>()
    for (v in pack.views.values) for (sp in v.spots) opArgs(sp.ops, "ask", asksIn.getOrPut(v.stage) { HashSet() })
    var maxHeld = 0
    var worst: GameState? = null
    fun note(s: GameState) { if (s.items.size > maxHeld) { maxHeld = s.items.size; worst = s } }
    var i = 0
    var edges = 0L
    val t0 = System.currentTimeMillis()
    while (i < states.size) {
        val st = states[i]
        val stage = st.f("stage")
        val next = HashSet<GameState>()
        fun add(o: Outcome?) {
            if (o == null || !o.changed) return
            note(o.state)
            next.add(canon(pack, o.state))
        }
        if (!goal(stage)) {
            val sels = listOf<String?>(null) + st.items.keys
            for (v in pack.views.values) {
                if (v.stage != stage || Rules.resolve(pack, st, v.id, now) != v.id) continue
                for (sp in v.spots) for (sel in sels) {
                    val x = sp.x + sp.w / 2
                    val y = sp.y + sp.h / 2
                    val sw = sp.swipe
                    if (sw == null) add(Rules.tap(pack, st, v.id, x, y, sel, now))
                    else for (dir in if (sw == Spot.ANY) listOf(-1, 0, 1, 2, 3) else listOf(sw)) add(Rules.swipe(pack, st, v.id, x, y, dir, sel, now))
                }
            }
            val held = st.items.keys.sorted()
            for (a in held) for (b in held) if (a < b) add(Rules.combine(pack, st, a, b, now))
            for (id in asksIn[stage] ?: emptySet<String>()) for (text in listOf(pack.asks[id]!!.answers.first(), "x")) add(Rules.answer(pack, st, id, text, now))
            for (p in Rules.openPuzzles(pack, st, now)) {
                val steps = script[p.id] ?: continue
                for (from in steps.indices) {
                    val sim = Sim(pack, mode)
                    sim.st = st
                    sim.now = now
                    for (step in steps.subList(from, steps.size)) { sim.run(step); note(sim.st) }
                    next.add(canon(pack, sim.st))
                }
            }
        }
        for (n in next) if (n != st) { back[idOf(n)].add(i); edges++ }
        i++
    }
    val good = BooleanArray(states.size)
    val q = ArrayDeque<Int>()
    for ((k, s) in states.withIndex()) if (goal(s.f("stage"))) { good[k] = true; q.add(k) }
    while (q.isNotEmpty()) for (p in back[q.removeFirst()]) if (!good[p]) { good[p] = true; q.add(p) }
    val stuck = states.indices.filter { !good[it] }
    val secs = (System.currentTimeMillis() - t0) / 1000
    check(stuck.isEmpty(), "$mode: no dead end in ${states.size} reachable situations ($edges moves, ${secs}s)")
    if (stuck.isNotEmpty()) println("      first stuck: " + states[stuck.first()].toJson())
    check(maxHeld <= 6, "$mode: never more than 6 things held in any reachable situation ($maxHeld)")
    if (maxHeld > 6) println("      held: " + worst!!.toJson())
}

fun navigation(pack: Pack) {
    for ((id, stage) in pack.stages) {
        val start = stage.start ?: continue
        val seen = HashSet<String>(); val q = ArrayDeque<String>(); q.add(start); seen.add(start)
        while (q.isNotEmpty()) {
            val v = pack.views[q.removeFirst()]!!
            val outs = mutableListOf<String>()
            listOf(v.left, v.right, v.back).forEach { if (it != null) outs.add(it) }
            for (sp in v.spots) opArgs(sp.ops, "go", outs)
            for (o in outs) if (seen.add(o)) q.add(o)
        }
        val all = pack.views.values.filter { it.stage == id }.map { it.id }.toSet()
        check(seen == all, "stage $id: every view can be walked to (${all.size})")
        val walls = pack.views.values.filter { it.stage == id && it.back == null }
        if (walls.size > 1) check(walls.all { v -> v.left != null && v.right != null }, "stage $id: walls are linked")
    }
    val missing = HashSet<String>()
    for (v in pack.views.values) {
        if (pack.imgRange(v.bg) == null) missing.add(v.bg)
        for (l in v.layers) { l.img?.let { if (pack.imgRange(it) == null) missing.add(it) }; for (fr in l.frames) if (pack.imgRange(fr) == null) missing.add(fr) }
    }
    for (it in pack.items.values) for (img in listOfNotNull(it.img, it.big, it.back)) if (pack.imgRange(img) == null) missing.add(img)
    check(missing.isEmpty(), "every picture named by a view or a thing exists $missing")
    check(pack.items.values.all { it.name.isNotBlank() && it.big != null }, "every thing has a name and a large picture")
    check(pack.title.isNotBlank() && pack.tagline.isNotBlank(), "the episode has a title and a tagline")
    check(pack.startStage == mapOf("main2" to 1, "test2" to 9), "episode 2 starts in its own modes ${pack.startStage}")
    // nothing to tap hides under the arrows, the back button or the column of held things
    val ui = listOf(floatArrayOf(14f, 238f, 44f, 64f), floatArrayOf(826f, 238f, 44f, 64f), floatArrayOf(14f, 472f, 78f, 54f), floatArrayOf(884f, 66f, 64f, 384f))
    val under = ArrayList<String>()
    for (v in pack.views.values) for (sp in v.spots) {
        if (sp.w >= 900 && sp.h >= 500) continue
        for ((k, r) in ui.withIndex()) {
            if ((k == 0 && v.left == null) || (k == 1 && v.right == null) || (k == 2 && v.back == null)) continue
            val inside = sp.x >= r[0] && sp.y >= r[1] && sp.x + sp.w <= r[0] + r[2] && sp.y + sp.h <= r[1] + r[3]
            val coversCentre = sp.x + sp.w / 2 in r[0]..(r[0] + r[2]) && sp.y + sp.h / 2 in r[1]..(r[1] + r[3])
            if (inside || coversCentre) under.add("${v.id}@${sp.x.toInt()},${sp.y.toInt()}")
        }
    }
    check(under.isEmpty(), "no tap area sits under the screen buttons $under")
}

fun twoPlayers(pack: Pack, transport: Transport, label: String) {
    val client = RoomClient(transport, System.getenv("EI_KEY") ?: "")
    val a = client.create("pid-a", "test2", Rules.initialState(pack, "test2"))
    val b = client.join(a.code, "pid-b")
    check(a.slot == 0 && b.slot == 1 && a.snap.mode == "test2", "$label: a test2 room keeps its mode")
    val sa = Session(pack, client, a.code, 0, a.snap)
    val sb = Session(pack, client, a.code, 1, b.snap)
    val now = (System.currentTimeMillis() / 1000).toInt()
    val n = 150
    fun spin(s: Session, x: Float) = Thread { repeat(n) { s.submit { st -> Rules.tap(pack, st, "t1", x, 152f, null, now) }; s.flush(null) } }
    val ta = spin(sa, 640f); val tb = spin(sb, 740f)
    ta.start(); tb.start(); ta.join(); tb.join()
    sa.poll("t1"); sb.poll("t1")
    check(sa.snap.state == sb.snap.state && sa.snap.state.f("t_d1") == n % 10 && sa.snap.state.f("t_d2") == n % 10,
        "$label: ${2 * n} taps on two dials at the same time, none lost")
    val m = 30
    fun same(s: Session, seed: Long) = Thread {
        val rnd = java.util.Random(seed)
        repeat(m) { s.submit { st -> Rules.tap(pack, st, "t1", 640f, 152f, null, now) }; s.flush(null); Thread.sleep(5L + rnd.nextInt(30)) }
        var guard = 0
        while (s.hasPending() && guard++ < 400) { s.flush(null); Thread.sleep(5L + rnd.nextInt(20)) }
    }
    val tc = same(sa, 1); val td = same(sb, 2)
    tc.start(); td.start(); tc.join(); td.join()
    sa.poll(null); sb.poll(null)
    check(!sa.hasPending() && !sb.hasPending() && sa.snap.state == sb.snap.state && sa.snap.state.f("t_d1") == (n + 2 * m) % 10,
        "$label: ${2 * m} taps on the same dial at the same time, none lost")
    // the shutter: one turns the key, the other pulls the lever before having heard of the key
    val c = client.create("pid-c", "main2", Rules.initialState(pack, "main2"))
    val d = client.join(c.code, "pid-d")
    val sc = Session(pack, client, c.code, 0, c.snap)
    val sd = Session(pack, client, c.code, 1, d.snap)
    val sim = runAll(pack, "main2", MAIN, upTo = "p5")
    sim.run(tap("a2", 480, 88))
    val ready = sim.st
    sc.submit { _ -> Outcome(ready, Fx(), true, emptySet()) }
    sc.flush(null)
    sd.poll(null)
    val t = now + 10
    sc.submit { st -> Rules.tap(pack, st, "a1", 726f, 292f, "skey", t) }
    sc.flush(null)
    sd.submit { st -> Rules.tap(pack, st, "a4", 124f, 383f, null, t + 2) }
    sd.flush(null)
    var guard = 0
    while (sd.hasPending() && guard++ < 10) sd.flush(null)
    sc.poll(null); sd.poll(null)
    check(sc.snap.state.f("a_open") == 1 && sc.snap.state == sd.snap.state, "$label: key and lever by two players open the shutter")
    // a whole game, taking turns, over the network
    val e = client.create("pid-e", "main2", Rules.initialState(pack, "main2"))
    val g = client.join(e.code, "pid-g")
    val se = Session(pack, client, e.code, 0, e.snap)
    val sg = Session(pack, client, e.code, 1, g.snap)
    var sel: String? = null
    var turn = 0
    for ((_, steps) in MAIN) for (s in steps) {
        if (s is Sel) { sel = s.item; continue }
        repeat(timesOf(s)) {
            val me = if (turn++ % 2 == 0) se else sg
            me.poll(null)
            val at = now + turn
            val held = sel
            val o = me.submit { st -> act(pack, st, s, held, at) }
            me.flush(null)
            if (o != null && (o.fx.unsel || (s is Combine && o.changed))) sel = null
        }
    }
    for (me in listOf(se, sg)) {
        var left = 0
        while (me.hasPending() && left++ < 10) me.flush(null)
    }
    se.poll(null); sg.poll(null)
    check(se.snap.state.f("stage") == 31 && se.snap.state == sg.snap.state, "$label: two players taking turns reach the ending")
}

fun main(args: Array<String>) {
    val pack = Pack.decode(File(args[0]).readBytes())
    println("pack: ${pack.views.size} views, ${pack.puzzles.size} puzzles, ${pack.imageIds().size} pictures")
    navigation(pack)
    walkthroughs(pack)
    grades(pack)
    wrongAnswers(pack)
    deadEnds(pack, "test2", TEST) { it == 90 }
    deadEnds(pack, "main2", MAIN) { it in ENDS }
    twoPlayers(pack, LocalTransport(), "in memory")
    if (args.size > 1) twoPlayers(pack, HttpTransport(args[1]), "over http")
    println(if (failures == 0) "ALL OK" else "$failures FAILED")
    exitProcess(if (failures == 0) 0 else 1)
}
