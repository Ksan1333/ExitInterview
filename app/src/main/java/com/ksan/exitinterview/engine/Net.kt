package com.ksan.exitinterview.engine

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/** Sends one JSON request to the room server and returns the JSON reply. */
interface Transport {
    @Throws(IOException::class)
    fun post(body: String): String
}

/**
 * Posts over HTTP(S). A reply that was read to the end leaves its connection open for the next request: making a
 * new connection costs a TCP and TLS handshake (about three times as long as the request itself), so the connection
 * is closed only after a failure.
 */
class HttpTransport(private val url: String) : Transport {
    override fun post(body: String): String {
        val c = URL(url).openConnection() as HttpURLConnection
        var reusable = false
        try {
            val bytes = body.toByteArray(Charsets.UTF_8)
            c.requestMethod = "POST"
            c.connectTimeout = 8000
            c.readTimeout = 8000
            c.doOutput = true
            c.useCaches = false
            c.setFixedLengthStreamingMode(bytes.size)
            c.setRequestProperty("Content-Type", "application/json")
            c.outputStream.use { it.write(bytes) }
            val code = c.responseCode
            if (code !in 200..299) throw IOException("http $code")
            val text = c.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
            reusable = true
            return text
        } finally {
            if (!reusable) c.disconnect()
        }
    }
}

/**
 * The server setting a player pastes in. Two spellings:
 *  - "https://host/k/KEY": what a deploy prints, and what KsanHub keeps as the site's URL
 *  - "http://host:8080/#KEY": the older form, still used for a server on your own computer (the key may be empty)
 * Returns the address to post to and the key, or null when the text is neither.
 */
object ServerAddress {
    private val keyed = Regex("""^(https?://[^/?#]+)/k/([A-Za-z0-9_-]+)/?$""")

    fun parse(text: String): Pair<String, String>? {
        val t = text.trim()
        if (!t.startsWith("http://") && !t.startsWith("https://")) return null
        if (t.any { it.isWhitespace() }) return null
        val hash = t.indexOf('#')
        if (hash >= 0) return if (t.substring(0, hash).length > "https://".length) Pair(t.substring(0, hash), t.substring(hash + 1)) else null
        val m = keyed.find(t) ?: return null
        return Pair(m.groupValues[1] + "/", m.groupValues[2])
    }

    /** The host, for showing which server is set without showing the key. */
    fun host(text: String): String = (parse(text)?.first ?: "").substringAfter("//").substringBefore("/")

    /**
     * The address built into the APK at build time (no key in it), as the address to post to.
     * Null when it is empty or not an http(s) address.
     */
    fun base(text: String): String? {
        val t = text.trim()
        if (!t.startsWith("http://") && !t.startsWith("https://")) return null
        if (t.any { it.isWhitespace() } || t.contains('#') || t.contains('?')) return null
        val host = t.substringAfter("//").substringBefore("/")
        if (host.isEmpty()) return null
        return t.substringBefore("//") + "//" + host + "/"
    }

    /**
     * The room code for a passphrase the two players agreed on ("m" and 24 hex characters, for the server's meet).
     * The passphrase itself never leaves the phone. Full-width and half-width letters count as the same (NFKC),
     * spaces around it are ignored, and the mode is part of it so a test room never meets a real one.
     */
    fun roomCodeOf(mode: String, passphrase: String): String? {
        val t = java.text.Normalizer.normalize(passphrase, java.text.Normalizer.Form.NFKC).trim()
        if (t.isEmpty()) return null
        val d = java.security.MessageDigest.getInstance("SHA-256").digest("exit-interview-room:$mode:$t".toByteArray(Charsets.UTF_8))
        return "m" + d.joinToString("") { "%02x".format(it) }.take(24)
    }

    /** True for a room met by passphrase (its code is a hash, not something to show). */
    fun isPassphraseRoom(code: String): Boolean = code.startsWith("m")
}

/** The same protocol as the real server, kept in memory. Used for offline solo tests. */
class LocalTransport(private val clock: () -> Int = { (System.currentTimeMillis() / 1000).toInt() }) : Transport {
    private class Room(val code: String, st: GameState, val mode: String, var p0: String) {
        var ver = 1
        var p1 = ""
        val flags = HashMap(st.flags)
        val items = HashMap(st.items)
        val mod = HashMap<String, Int>()
        val v = arrayOf("", "")
        val s = intArrayOf(0, 0)
    }

    private val rooms = HashMap<String, Room>()
    private val rnd = java.util.Random()

    @Synchronized
    override fun post(body: String): String {
        val q = Json.parse(body).asMap()
        val now = clock()
        val op = q["op"].asStr()
        if (op == "create") {
            var code: String
            do {
                code = String.format("%04d", rnd.nextInt(10000))
            } while (rooms.containsKey(code))
            val r = Room(code, GameState.fromJson(q["st"].asStr() ?: ""), q["mode"].asStr() ?: "main", q["pid"].asStr() ?: "")
            r.s[0] = now
            rooms[code] = r
            return reply(r, true, null, 0, now)
        }
        val r = rooms[q["code"].asStr() ?: ""] ?: return Json.str(mapOf("ok" to false, "err" to "nf", "now" to now))
        val slot = if (q["slot"].asInt() == 1) 1 else 0
        q["view"].asStr()?.let {
            r.v[slot] = it
            r.s[slot] = now
        }
        when (op) {
            "join" -> {
                val pid = q["pid"].asStr() ?: ""
                val got = when {
                    pid == r.p0 -> 0
                    r.p1.isEmpty() || r.p1 == pid -> 1
                    else -> return Json.str(mapOf("ok" to false, "err" to "full", "now" to now))
                }
                if (got == 1) r.p1 = pid
                r.s[got] = now
                return reply(r, true, null, got, now)
            }
            "get" -> return reply(r, true, null, slot, now)
            "put" -> {
                val base = q["ver"].asInt()
                val writes = q["w"].asMap()
                val keys = q["r"].asList().mapNotNull { it.asStr() } + writes.keys
                if (keys.any { (r.mod[it] ?: 0) > base }) return reply(r, false, "ver", slot, now)
                if (writes.isNotEmpty()) {
                    r.ver += 1
                    for ((k, raw) in writes) {
                        val target = if (k.startsWith("i:")) r.items else r.flags
                        val v = raw.asInt()
                        if (v == 0) target.remove(k.substring(2)) else target[k.substring(2)] = v
                        r.mod[k] = r.ver
                    }
                }
                return reply(r, true, null, slot, now)
            }
        }
        return Json.str(mapOf("ok" to false, "err" to "op", "now" to now))
    }

    private fun reply(r: Room, ok: Boolean, err: String?, slot: Int, now: Int): String = Json.str(
        mapOf(
            "ok" to ok, "err" to err, "code" to r.code, "slot" to slot, "ver" to r.ver,
            "st" to GameState(r.flags, r.items).toJson(),
            "v" to r.v.toList(), "s" to r.s.toList(), "p1" to r.p1.isNotEmpty(), "mode" to r.mode, "now" to now,
        ),
    )
}

class RoomException(val reason: String) : IOException(reason)

/** What the server knows about a room at one moment. */
class Snapshot(
    val ver: Int,
    val state: GameState,
    val views: List<String>,
    val seen: List<Int>,
    val partnerJoined: Boolean,
    val mode: String,
    val now: Int,
)

/** [made]: the room was made by this request (meet), so the partner has not come yet. */
class Joined(val code: String, val slot: Int, val snap: Snapshot, val made: Boolean = false)

class RoomClient(private val transport: Transport, private val key: String) {
    private fun call(req: Map<String, Any?>): Map<String, Any?> {
        // No key: the server takes requests without one (meeting by passphrase). An empty key is not sent.
        val text = transport.post(Json.str(if (key.isEmpty()) req else req + ("k" to key)))
        try {
            return Json.parse(text).asMap()
        } catch (e: IllegalArgumentException) {
            throw IOException("bad reply")
        }
    }

    private fun snap(r: Map<String, Any?>): Snapshot = Snapshot(
        ver = r["ver"].asInt(),
        state = GameState.fromJson(r["st"].asStr() ?: ""),
        views = r["v"].asList().map { it.asStr() ?: "" },
        seen = r["s"].asList().map { it.asInt() },
        partnerJoined = r["p1"] == true,
        mode = r["mode"].asStr() ?: "main",
        now = r["now"].asInt(),
    )

    private fun joined(r: Map<String, Any?>): Joined {
        if (r["ok"] != true) throw RoomException(r["err"].asStr() ?: "err")
        return Joined(r["code"].asStr() ?: "", r["slot"].asInt(), snap(r), r["made"] == true)
    }

    /** Meets the partner by passphrase: takes a seat in the room [code] (from [ServerAddress.roomCodeOf]), or makes it. */
    fun meet(code: String, pid: String, mode: String, init: GameState): Joined =
        joined(call(mapOf("op" to "meet", "code" to code, "pid" to pid, "mode" to mode, "st" to init.toJson())))

    fun create(pid: String, mode: String, init: GameState): Joined =
        joined(call(mapOf("op" to "create", "pid" to pid, "mode" to mode, "st" to init.toJson())))

    fun join(code: String, pid: String): Joined = joined(call(mapOf("op" to "join", "code" to code, "pid" to pid)))

    /** Reads the room. When [view] is given, also records where this player is. */
    fun get(code: String, slot: Int, view: String?): Snapshot {
        val req = HashMap<String, Any?>()
        req["op"] = "get"
        req["code"] = code
        req["slot"] = slot
        if (view != null) req["view"] = view
        val r = call(req)
        if (r["ok"] != true) throw RoomException(r["err"].asStr() ?: "err")
        return snap(r)
    }

    /**
     * Applies [writes] ("f:flag" or "i:item" to new value, 0 removes) if none of the keys in [reads]
     * or [writes] changed after version [ver]. Returns false with the newer room otherwise.
     */
    fun put(code: String, slot: Int, ver: Int, reads: Collection<String>, writes: Map<String, Int>, view: String?): Pair<Boolean, Snapshot> {
        val req = HashMap<String, Any?>()
        req["op"] = "put"
        req["code"] = code
        req["slot"] = slot
        req["ver"] = ver
        req["r"] = reads.sorted()
        req["w"] = writes.toSortedMap()
        if (view != null) req["view"] = view
        val r = call(req)
        if (r["ok"] == true) return Pair(true, snap(r))
        if (r["err"].asStr() == "ver") return Pair(false, snap(r))
        throw RoomException(r["err"].asStr() ?: "err")
    }
}

/** One player action, written so it can be run again on a newer state. Null means nothing happened. */
typealias Intent = (GameState) -> Outcome?

/**
 * One device's connection to a room.
 *
 * Actions are applied to [state] at once so the screen reacts without waiting for the network, and
 * are sent to the server afterwards by [flush]. If the partner changed something an action depended
 * on, the server refuses it and the action is simply run again on the newer state.
 */
class Session(val pack: Pack, private val client: RoomClient, val code: String, slot: Int, first: Snapshot) {
    @Volatile
    var slot: Int = slot

    /** The newest state confirmed by the server (also holds where each player is). */
    @Volatile
    var snap: Snapshot = first
        private set

    /** What the screen shows: the confirmed state plus this device's actions that are still on their way. */
    @Volatile
    var state: GameState = first.state
        private set

    private val lock = Any()
    private val pending = ArrayList<Intent>()

    /**
     * The server's clock minus this device's clock, in seconds, from the newest reply. Timed things are judged
     * by each device, so both phones count in the server's time and agree even when their own clocks do not.
     */
    @Volatile
    var clockOffset: Int = 0
        private set

    init {
        noteClock(first)
    }

    private fun noteClock(s: Snapshot) {
        if (s.now > 0) clockOffset = s.now - (System.currentTimeMillis() / 1000).toInt()
    }

    /** Runs an action now and queues it for sending. Call from the screen. */
    fun submit(intent: Intent): Outcome? = synchronized(lock) {
        val out = intent(state)
        if (out != null && out.changed) {
            pending.add(intent)
            state = out.state
        }
        out
    }

    fun hasPending(): Boolean = synchronized(lock) { pending.isNotEmpty() }

    private fun adopt(s: Snapshot, sent: Int) {
        synchronized(lock) {
            if (s.ver >= snap.ver) snap = s
            repeat(minOf(sent, pending.size)) { pending.removeAt(0) }
            var st = snap.state
            val it = pending.iterator()
            while (it.hasNext()) {
                val o = it.next()(st)
                if (o == null || !o.changed) it.remove() else st = o.state
            }
            state = st
        }
    }

    /** Fetches the newest room state. Pass [view] to tell the partner where this player is. */
    fun poll(view: String?) {
        val s = client.get(code, slot, view)
        noteClock(s)
        adopt(s, 0)
    }

    /** Sends queued actions in one request. Returns true if a request was made. Call from one background loop. */
    fun flush(view: String?): Boolean {
        val base: Snapshot
        val batch: List<Intent>
        synchronized(lock) {
            base = snap
            batch = ArrayList(pending)
        }
        if (batch.isEmpty()) return false
        var st = base.state
        val reads = HashSet<String>()
        for (intent in batch) {
            val o = intent(st) ?: continue
            reads.addAll(o.reads)
            st = o.state
        }
        val writes = diff(base.state, st)
        if (writes.isEmpty()) {
            adopt(base, batch.size)
            return false
        }
        val (ok, next) = client.put(code, slot, base.ver, reads, writes, view)
        noteClock(next)
        adopt(next, if (ok) batch.size else 0)
        return true
    }

    companion object {
        /** Keys whose value differs between two states, with the value in [b]. */
        fun diff(a: GameState, b: GameState): Map<String, Int> {
            val out = HashMap<String, Int>()
            for (k in a.flags.keys + b.flags.keys) if (a.f(k) != b.f(k)) out["f:$k"] = b.f(k)
            for (k in a.items.keys + b.items.keys) if (a.n(k) != b.n(k)) out["i:$k"] = b.n(k)
            return out
        }
    }
}
