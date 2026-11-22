// Checks the real stage pack with the real engine: a full walkthrough, every skip, a search for
// dead ends, and two players acting at the same time. Contains the answers. Do not open.
import com.ksan.exitinterview.engine.*
import java.io.File
import kotlin.system.exitProcess

sealed class Step
class Tap(val view: String, val x: Float, val y: Float, val times: Int = 1) : Step()
class Sel(val item: String?) : Step()

fun tap(view: String, x: Int, y: Int, times: Int = 1) = Tap(view, x.toFloat(), y.toFloat(), times)

class Sim(val pack: Pack, mode: String) {
    var st = Rules.initialState(pack, mode)
    var sel: String? = null
    var now = 1_800_000_000

    /** Returns false when the step could not be done (view closed, nothing to tap, item missing). */
    fun run(step: Step): Boolean {
        when (step) {
            is Sel -> {
                if (step.item != null && st.n(step.item) <= 0) return false
                sel = step.item
            }
            is Tap -> repeat(step.times) {
                if (Rules.resolve(pack, st, step.view, now) != step.view) return false
                val o = Rules.tap(pack, st, step.view, step.x, step.y, sel, now) ?: return false
                st = o.state
                if (o.fx.unsel || (sel != null && st.n(sel!!) <= 0)) sel = null
                now += 1
            }
        }
        return true
    }
}

val UP = tap("s3maze", 705, 226)
val RIGHT = tap("s3maze", 771, 292)
val DOWN = tap("s3maze", 705, 358)
val LEFT = tap("s3maze", 639, 292)

val MAIN: LinkedHashMap<String, List<Step>> = linkedMapOf(
    "s1a" to listOf(tap("s1v3", 150, 371, 3), tap("s1v3", 198, 371, 8), tap("s1v3", 246, 371, 8), tap("s1v3", 294, 371, 9), tap("s1v3", 351, 371)),
    "s1b" to listOf(Sel("handle"), tap("s1v3", 793, 240), tap("s1v2", 416, 229, 4), tap("s1v3", 560, 255)),
    "s1c" to listOf(tap("s1v1", 212, 464), Sel("fuse"), tap("s1v2", 655, 340), tap("s1v3", 288, 270),
        tap("s1v1", 734, 266), tap("s1v1", 784, 266), tap("s1v1", 634, 266), tap("s1v1", 684, 266)),
    "x1" to listOf(tap("s1v1", 480, 255)),
    "s2a" to listOf(tap("s2v2", 142, 259)),
    "s2b" to listOf(tap("s2v3", 180, 260), Sel("coin"), tap("s2fridge", 300, 200), tap("s2fridge", 170, 384), tap("s2fridge", 430, 384), tap("s2fridge", 300, 384)),
    "s2c" to listOf(tap("s2v3", 535, 300), Sel("milk"), tap("s2bandai", 440, 190), Sel("fhandle"), tap("s2v1", 254, 286),
        tap("s2v1", 254, 286, 3), tap("s2v1", 654, 286)),
    "s2d" to listOf(tap("s2v1", 452, 384), tap("s2v3", 740, 280), Sel("key"), tap("s2chair", 480, 300),
        tap("s2chair", 420, 300), tap("s2chair", 540, 300, 3), tap("s2chair", 420, 300, 2)),
    "s2e" to listOf(tap("s2v1", 450, 150), tap("s2exit", 362, 303, 4), tap("s2exit", 442, 303, 2), tap("s2exit", 522, 303, 7), tap("s2exit", 602, 303, 6), tap("s2exit", 672, 303)),
    "x2" to listOf(tap("s2exit", 480, 200)),
    "s3a" to listOf(tap("s3v1", 434, 304), tap("s3v1", 472, 304), tap("s3v1", 396, 342), tap("s3v1", 472, 342), tap("s3v1", 396, 380), tap("s3v1", 540, 372)),
    "s3b" to listOf(Sel("food"), tap("s3v3", 212, 180), tap("s3v3", 365, 478), UP, UP, UP, LEFT, LEFT, DOWN, LEFT, LEFT, UP, LEFT, UP, UP),
    "s3c" to listOf(tap("s3v2", 360, 120), tap("s3shelf", 360, 215), tap("s3shelf", 550, 215), tap("s3shelf", 740, 215), tap("s3shelf", 170, 215)),
    "s3d" to listOf(tap("s3v1", 750, 236), Sel("grip"), tap("s3v2", 688, 223),
        tap("s3v2", 190, 412), tap("s3v2", 240, 412), tap("s3v2", 290, 412), tap("s3v2", 340, 412), tap("s3v3", 332, 286),
        tap("s3v2", 688, 223), tap("s3v3", 450, 373), Sel("mikan"), tap("s3under", 350, 320, 5), tap("s3under", 685, 318)),
    "s3e" to listOf(Sel("ekey"), tap("s3v3", 450, 292), tap("s3v3", 450, 292), tap("s3panel", 200, 356), tap("s3panel", 340, 356), tap("s3panel", 620, 356), tap("s3panel", 480, 356)),
    "x3" to listOf(tap("s3panel", 694, 152)),
)

val TEST: LinkedHashMap<String, List<Step>> = linkedMapOf(
    "t1" to listOf(tap("t1", 368, 238), tap("t1", 264, 238), tap("t1", 472, 238)),
    "x" to listOf(tap("t2", 634, 458), Sel("tkey"), tap("t2", 480, 180)),
)

var failures = 0
fun check(ok: Boolean, what: String) {
    println((if (ok) "ok    " else "FAIL  ") + what)
    if (!ok) failures++
}

fun runAll(pack: Pack, mode: String, script: Map<String, List<Step>>, skip: String? = null, upTo: String? = null): Sim {
    val sim = Sim(pack, mode)
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

fun walkthroughs(pack: Pack) {
    val a = runAll(pack, "main", MAIN)
    check(a.st.f("stage") == 4 && a.st.f("t1") != 0, "walkthrough reaches the ending")
    check(a.st.items.isEmpty(), "no item is left over at the end (${a.st.items})")
    val swapped = LinkedHashMap<String, List<Step>>()
    for (k in listOf("s1a", "s1b", "s1c", "x1", "s2a", "s2b", "s2c", "s2d", "s2e", "x2", "s3a", "s3c", "s3b", "s3d", "s3e", "x3")) swapped[k] = MAIN[k]!!
    check(runAll(pack, "main", swapped).st.f("stage") == 4, "walkthrough with the two free puzzles swapped")
    val t = runAll(pack, "test", TEST)
    check(t.st.f("stage") == 90, "test room walkthrough")
    for (p in pack.puzzles) {
        val script = if (p.stage == 9) TEST else MAIN
        val goal = if (p.stage == 9) 90 else 4
        val ok = try {
            val s = runAll(pack, if (p.stage == 9) "test" else "main", script, skip = p.id)
            s.st.f("stage") == goal && s.st.f(Rules.N_SKIP) == 1
        } catch (e: IllegalStateException) {
            println("      " + e.message)
            false
        }
        check(ok, "skip ${p.id} then finish")
    }
    // every puzzle shows up as open exactly while its part of the walkthrough is being played
    for (p in pack.puzzles.filter { it.stage != 9 }) {
        val before = runAll(pack, "main", MAIN, upTo = p.id)
        check(Rules.openPuzzles(pack, before.st, before.now).any { it.id == p.id }, "hint for ${p.id} is offered when needed")
    }
}

fun wrongAnswers(pack: Pack) {
    val s = Sim(pack, "main")
    s.run(tap("s1v3", 351, 371))
    check(s.st.f("s1_drawer") == 0, "wrong drawer code stays shut")
    val b = runAll(pack, "main", MAIN, upTo = "s2a")
    b.run(tap("s2v2", 142, 123))
    val during = Rules.tap(pack, b.st, "s2v2", 142f, 259f, null, b.now)
    b.now += 11
    val after = Rules.tap(pack, b.st, "s2v2", 142f, 259f, null, b.now)
    check(during == null && after != null && after.state.f("s2_locker") == 1, "wrong locker blocks taps for 10 seconds, then the right one opens")
    val c = runAll(pack, "main", MAIN, upTo = "s3d")
    for (st in listOf(tap("s3v1", 750, 236), Sel("grip"), tap("s3v2", 688, 223), tap("s3v2", 190, 412), tap("s3v2", 240, 412), tap("s3v2", 290, 412),
        tap("s3v2", 688, 223), tap("s3v3", 450, 373), Sel("mikan"), tap("s3under", 350, 320, 3), tap("s3under", 685, 318))) c.run(st)
    check(c.st.f("s3_fuel") == 0 && c.st.n("mikan") == 3 && c.st.f("s3_fc") == 0, "wrong fuel count gives the fruit back")
    val d = runAll(pack, "main", MAIN, upTo = "s3b")
    for (st in listOf(Sel("food"), tap("s3v3", 212, 180), tap("s3v3", 365, 478), UP, UP, UP, UP, UP, UP, UP)) d.run(st)
    check(d.st.f("mz") == 5 && d.st.f("s3_fish") == 0, "maze: a move off the board is ignored")
    d.run(DOWN)
    val beforeReset = d.st.f("mz")
    d.run(LEFT)
    check(beforeReset == 4 && d.st.f("mz") == 0, "maze: entering a marked cell sends the fish back to the start")
}

fun mazeFacts(pack: Pack) {
    val m = pack.mazes["m1"]!!
    val dist = IntArray(m.w * m.h) { -1 }
    val ways = LongArray(m.w * m.h)
    dist[m.start] = 0; ways[m.start] = 1
    val q = ArrayDeque<Int>(); q.add(m.start)
    while (q.isNotEmpty()) {
        val p = q.removeFirst()
        val c = p % m.w; val r = p / m.w
        for ((dc, dr) in listOf(0 to 1, 1 to 0, 0 to -1, -1 to 0)) {
            val nc = c + dc; val nr = r + dr
            if (nc !in 0 until m.w || nr !in 0 until m.h) continue
            val n = nr * m.w + nc
            if (n in m.blocked) continue
            if (dist[n] == -1) { dist[n] = dist[p] + 1; ways[n] = ways[p]; q.add(n) } else if (dist[n] == dist[p] + 1) ways[n] += ways[p]
        }
    }
    check(dist[m.goal] == 12 && ways[m.goal] == 1L, "maze: goal is 12 moves away by exactly one shortest path")
    check((0 until m.w * m.h).all { it in m.blocked || dist[it] >= 0 }, "maze: every free cell can be reached")
}

val VOLATILE = Regex("^(s1_d\\d|s2_e\\d|q[0-9t](_n)?|s3_l\\d|s2_tv|mz|s1_la|s1_lb|s2_cool|s2_fx|s3_fxb|s2_scale|h_.*|n_hint|n_skip|t0|t1)$")

/** Forgets puzzle inputs that can always be set again (dials, half-entered sequences, timers). */
fun canon(pack: Pack, st: GameState): GameState {
    val f = HashMap<String, Int>()
    for ((k, v) in st.flags) if (!VOLATILE.matches(k)) f[k] = v
    for ((k, v) in pack.initial.flags) if (VOLATILE.matches(k)) f[k] = v
    return GameState(f, st.items)
}

fun deadEnds(pack: Pack, mode: String, script: Map<String, List<Step>>, goal: Int) {
    val now = 1_800_000_000
    val start = canon(pack, Rules.initialState(pack, mode))
    val ids = HashMap<GameState, Int>()
    val states = ArrayList<GameState>()
    val back = ArrayList<ArrayList<Int>>()
    fun idOf(s: GameState): Int = ids.getOrPut(s) { states.add(s); back.add(ArrayList()); states.size - 1 }
    idOf(start)
    var i = 0
    var edges = 0L
    while (i < states.size) {
        val st = states[i]
        val stage = st.f("stage")
        val next = HashSet<GameState>()
        if (stage != goal) {
            for (v in pack.views.values) {
                if (v.stage != stage || Rules.resolve(pack, st, v.id, now) != v.id) continue
                for (sp in v.spots) for (sel in listOf<String?>(null) + st.items.keys) {
                    val o = Rules.tap(pack, st, v.id, sp.x + sp.w / 2, sp.y + sp.h / 2, sel, now) ?: continue
                    if (o.changed) next.add(canon(pack, o.state))
                }
            }
            for (p in Rules.openPuzzles(pack, st, now)) {
                // any run of legal taps gives a legal situation, so try the solution from every starting point
                val steps = script[p.id] ?: continue
                for (from in steps.indices) {
                    val sim = Sim(pack, mode)
                    sim.st = st
                    for (step in steps.subList(from, steps.size)) sim.run(step)
                    next.add(canon(pack, sim.st))
                }
            }
        }
        for (n in next) if (n != st) { back[idOf(n)].add(i); edges++ }
        i++
    }
    val good = BooleanArray(states.size)
    val q = ArrayDeque<Int>()
    for ((k, s) in states.withIndex()) if (s.f("stage") == goal) { good[k] = true; q.add(k) }
    while (q.isNotEmpty()) for (p in back[q.removeFirst()]) if (!good[p]) { good[p] = true; q.add(p) }
    val stuck = states.indices.filter { !good[it] }
    check(stuck.isEmpty(), "$mode: no dead end in ${states.size} reachable situations ($edges moves)")
    if (stuck.isNotEmpty()) println("      first stuck: " + states[stuck.first()].toJson())
}

fun navigation(pack: Pack) {
    for ((id, stage) in pack.stages) {
        val start = stage.start ?: continue
        val seen = HashSet<String>(); val q = ArrayDeque<String>(); q.add(start); seen.add(start)
        fun gos(ops: List<Any?>, out: MutableList<String>) {
            for (o in ops) {
                val l = o as? List<*> ?: continue
                if (l.firstOrNull() == "go") out.add(l[1] as String)
                for (x in l) if (x is List<*>) @Suppress("UNCHECKED_CAST") gos(x as List<Any?>, out)
            }
        }
        while (q.isNotEmpty()) {
            val v = pack.views[q.removeFirst()]!!
            val outs = mutableListOf<String>()
            listOf(v.left, v.right, v.back).forEach { if (it != null) outs.add(it) }
            for (sp in v.spots) gos(sp.ops, outs)
            for (o in outs) if (seen.add(o)) q.add(o)
        }
        val all = pack.views.values.filter { it.stage == id }.map { it.id }.toSet()
        check(seen == all, "stage $id: every view can be walked to (${all.size})")
        check(pack.views.values.filter { it.stage == id && it.back == null }.all { v -> v.left != null || v.right != null }, "stage $id: walls are linked")
    }
    val missing = HashSet<String>()
    for (v in pack.views.values) {
        if (pack.imgRange(v.bg) == null) missing.add(v.bg)
        for (l in v.layers) { l.img?.let { if (pack.imgRange(it) == null) missing.add(it) }; for (fr in l.frames) if (pack.imgRange(fr) == null) missing.add(fr) }
    }
    for (it in pack.items.values) if (pack.imgRange(it.img) == null) missing.add(it.img)
    check(missing.isEmpty(), "every picture named by a view exists $missing")
}

fun twoPlayers(pack: Pack, transport: Transport, label: String) {
    val client = RoomClient(transport, System.getenv("EI_KEY") ?: "")
    val a = client.create("pid-a", "main", Rules.initialState(pack, "main"))
    val b = client.join(a.code, "pid-b")
    check(b.slot == 1 && a.slot == 0, "$label: second player gets the second seat")
    val again = client.join(a.code, "pid-a")
    check(again.slot == 0, "$label: rejoining keeps the seat")
    val full = try { client.join(a.code, "pid-c"); false } catch (e: RoomException) { e.reason == "full" }
    check(full, "$label: a third player is refused")
    val none = try { client.join("xxxx", "pid-c"); false } catch (e: RoomException) { e.reason == "nf" }
    check(none, "$label: an unknown room code is refused")
    val sa = Session(pack, client, a.code, 0, a.snap)
    val sb = Session(pack, client, a.code, 1, b.snap)
    val now = (System.currentTimeMillis() / 1000).toInt()
    // both players spin different dials of the same drawer at the same moment: nothing should clash
    val n = 150
    fun spin(s: Session, x: Float) = Thread { repeat(n) { s.submit { st -> Rules.tap(pack, st, "s1v3", x, 371f, null, now) }; s.flush(null) } }
    val ta = spin(sa, 150f); val tb = spin(sb, 198f)
    ta.start(); tb.start(); ta.join(); tb.join()
    sa.poll("s1v3"); sb.poll("s1v1")
    // only the very first taps can clash (both start the game clock); after that every tap goes straight through
    check(sa.snap.state == sb.snap.state && sa.snap.state.f("s1_d1") == n % 10 && sa.snap.state.f("s1_d2") == n % 10 && sa.snap.ver in (2 * n - 3)..(1 + 2 * n),
        "$label: ${2 * n} taps on different dials at the same time, none lost (room version ${sa.snap.ver})")
    // both players spin the same dial, tapping about as fast as people do
    val m = 30
    fun same(s: Session, seed: Long) = Thread {
        val rnd = java.util.Random(seed)
        repeat(m) {
            s.submit { st -> Rules.tap(pack, st, "s1v3", 246f, 371f, null, now) }
            s.flush(null)
            Thread.sleep(5L + rnd.nextInt(30))
        }
        var guard = 0
        while (s.hasPending() && guard++ < 400) { s.flush(null); Thread.sleep(5L + rnd.nextInt(20)) }
    }
    val tc = same(sa, 1); val td = same(sb, 2)
    tc.start(); td.start(); tc.join(); td.join()
    sa.poll(null); sb.poll(null)
    check(!sa.hasPending() && !sb.hasPending() && sa.snap.state == sb.snap.state && sa.snap.state.f("s1_d3") == (2 * m) % 10 && sa.state == sa.snap.state,
        "$label: ${2 * m} taps on the same dial at the same time, none lost")
    check(sa.snap.views == listOf("s1v3", "s1v1"), "$label: each player sees where the other is")
    // a tap shows on the tapping device before the server has heard of it
    val before = sa.snap.ver
    sa.submit { st -> Rules.tap(pack, st, "s1v3", 294f, 371f, null, now) }
    check(sa.state.f("s1_d4") == 1 && sa.snap.ver == before && sa.hasPending(), "$label: a tap shows at once on the tapping device")
    repeat(9) { sa.submit { st -> Rules.tap(pack, st, "s1v3", 294f, 371f, null, now) } }
    sa.flush(null)
    check(sa.snap.ver == before && !sa.hasPending(), "$label: taps that cancel out are not sent")
    // then they finish the game taking turns (all four dials are back at 0 here)
    var sel: String? = null
    var turn = 0
    for ((_, steps) in MAIN) for (s in steps) {
        when (s) {
            is Sel -> sel = s.item
            is Tap -> repeat(s.times) {
                val me = if (turn++ % 2 == 0) sa else sb
                me.poll(null)
                val t = now + turn
                val held = sel
                val o = me.submit { st -> Rules.tap(pack, st, s.view, s.x, s.y, held, t) }
                me.flush(null)
                if (o != null && o.fx.unsel) sel = null
            }
        }
    }
    sa.poll(null); sb.poll(null)
    check(sa.snap.state.f("stage") == 4 && sa.snap.state == sb.snap.state, "$label: two players taking turns reach the ending")
}

fun main(args: Array<String>) {
    val pack = Pack.decode(File(args[0]).readBytes())
    println("pack: ${pack.views.size} views, ${pack.puzzles.size} puzzles, ${pack.imageIds().size} pictures")
    navigation(pack)
    walkthroughs(pack)
    wrongAnswers(pack)
    mazeFacts(pack)
    deadEnds(pack, "test", TEST, 90)
    deadEnds(pack, "main", MAIN, 4)
    twoPlayers(pack, LocalTransport(), "in memory")
    if (args.size > 1) twoPlayers(pack, HttpTransport(args[1]), "over http")
    println(if (failures == 0) "ALL OK" else "$failures FAILED")
    exitProcess(if (failures == 0) 0 else 1)
}
