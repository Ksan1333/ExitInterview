package com.ksan.exitinterview.engine

import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/** One drawable layer of a view: a fixed picture, a looping animation, or a sprite placed by a flag. */
class Layer(
    val img: String?,
    val frames: List<String>,
    val frameMs: Int,
    val x: Float, val y: Float, val w: Float, val h: Float,
    val cond: Any?,
    val posFlag: String?,
    val pos: List<FloatArray>,
)

/** Text drawn by the app from a flag value (dial digits, counters, countdowns). */
class DynText(
    val x: Float, val y: Float, val size: Float,
    val color: String,
    val flag: String,
    val kind: String,
    val map: List<String>,
    val cond: Any?,
)

class Spot(val x: Float, val y: Float, val w: Float, val h: Float, val cond: Any?, val ops: List<Any?>) {
    fun hit(px: Float, py: Float): Boolean = px >= x && px <= x + w && py >= y && py <= y + h
}

class ViewDef(
    val id: String,
    val stage: Int,
    val bg: String,
    val name: String,
    val left: String?,
    val right: String?,
    val back: String?,
    val cond: Any?,
    val layers: List<Layer>,
    val texts: List<DynText>,
    val spots: List<Spot>,
)

class ItemDef(val id: String, val img: String)

class Puzzle(
    val id: String,
    val stage: Int,
    val name: String,
    val avail: Any?,
    val done: Any?,
    val hints: List<String>,
    val answer: String,
    val skip: List<Any?>,
)

class MazeDef(
    val pos: String,
    val w: Int,
    val h: Int,
    val blocked: Set<Int>,
    val start: Int,
    val goal: Int,
    val remap: List<Int>,
    val ok: List<Any?>,
)

class StageDef(
    val id: Int,
    val start: String?,
    val captions: List<String>,
    val end: Boolean,
    val credits: List<String>,
    val letter: List<String>,
)

/** The decrypted stage pack: definitions plus picture bytes. */
class Pack private constructor(private val data: ByteArray, private val blobStart: Int, root: Map<String, Any?>) {
    val views: Map<String, ViewDef>
    val items: Map<String, ItemDef>
    val puzzles: List<Puzzle>
    val mazes: Map<String, MazeDef>
    val stages: Map<Int, StageDef>
    val initial: GameState
    val startStage: Map<String, Int>
    private val imgs: Map<String, IntArray>

    init {
        val vm = LinkedHashMap<String, ViewDef>()
        for ((id, raw) in root["views"].asMap()) {
            val v = raw.asMap()
            vm[id] = ViewDef(
                id = id,
                stage = v["st"].asInt(),
                bg = v["bg"].asStr() ?: "",
                name = v["name"].asStr() ?: "",
                left = v["l"].asStr(),
                right = v["r"].asStr(),
                back = v["back"].asStr(),
                cond = v["when"],
                layers = v["layers"].asList().map { parseLayer(it.asMap()) },
                texts = v["texts"].asList().map { parseText(it.asMap()) },
                spots = v["spots"].asList().map { parseSpot(it.asMap()) },
            )
        }
        views = vm
        items = root["items"].asMap().mapValues { (id, raw) -> ItemDef(id, raw.asMap()["img"].asStr() ?: "") }
        puzzles = root["puzzles"].asList().map {
            val p = it.asMap()
            Puzzle(
                id = p["id"].asStr() ?: "",
                stage = p["st"].asInt(),
                name = p["name"].asStr() ?: "",
                avail = p["avail"],
                done = p["done"],
                hints = p["hints"].asList().map { h -> h.asStr() ?: "" },
                answer = p["ans"].asStr() ?: "",
                skip = p["skip"].asList(),
            )
        }
        mazes = root["mazes"].asMap().mapValues { (_, raw) ->
            val m = raw.asMap()
            MazeDef(
                pos = m["pos"].asStr() ?: "",
                w = m["w"].asInt(),
                h = m["h"].asInt(),
                blocked = m["blocked"].asList().map { it.asInt() }.toSet(),
                start = m["start"].asInt(),
                goal = m["goal"].asInt(),
                remap = m["remap"].asList().map { it.asInt() },
                ok = m["ok"].asList(),
            )
        }
        val sm = LinkedHashMap<Int, StageDef>()
        for ((id, raw) in root["stages"].asMap()) {
            val s = raw.asMap()
            sm[id.toInt()] = StageDef(
                id = id.toInt(),
                start = s["start"].asStr(),
                captions = s["cap"].asList().map { it.asStr() ?: "" },
                end = s["end"].asInt() != 0,
                credits = s["credits"].asList().map { it.asStr() ?: "" },
                letter = s["letter"].asList().map { it.asStr() ?: "" },
            )
        }
        stages = sm
        initial = GameState.fromAny(root["init"])
        startStage = root["start"].asMap().mapValues { it.value.asInt() }
        imgs = root["imgs"].asMap().mapValues { (_, raw) ->
            val a = raw.asList()
            intArrayOf(blobStart + a[0].asInt(), a[1].asInt())
        }
    }

    /** The byte array that holds every picture; use with [imgRange]. */
    fun imgData(): ByteArray = data

    /** Offset and length of one picture inside [imgData], or null if unknown. */
    fun imgRange(id: String): IntArray? = imgs[id]

    fun imageIds(): Set<String> = imgs.keys

    private fun parseLayer(m: Map<String, Any?>): Layer {
        val r = m["r"].asList()
        return Layer(
            img = m["i"].asStr(),
            frames = m["fr"].asList().map { it.asStr() ?: "" },
            frameMs = m["ms"].asInt(1000),
            x = r.getOrNull(0).asF(), y = r.getOrNull(1).asF(), w = r.getOrNull(2).asF(), h = r.getOrNull(3).asF(),
            cond = m["when"],
            posFlag = m["pf"].asStr(),
            pos = m["ps"].asList().map { p -> floatArrayOf(p.asList().getOrNull(0).asF(), p.asList().getOrNull(1).asF()) },
        )
    }

    private fun parseText(m: Map<String, Any?>): DynText {
        val p = m["p"].asList()
        return DynText(
            x = p.getOrNull(0).asF(), y = p.getOrNull(1).asF(),
            size = m["sz"].asF(24f),
            color = m["c"].asStr() ?: "#101316",
            flag = m["f"].asStr() ?: "",
            kind = m["k"].asStr() ?: "num",
            map = m["m"].asList().map { it.asStr() ?: "" },
            cond = m["when"],
        )
    }

    private fun parseSpot(m: Map<String, Any?>): Spot {
        val r = m["r"].asList()
        return Spot(r.getOrNull(0).asF(), r.getOrNull(1).asF(), r.getOrNull(2).asF(), r.getOrNull(3).asF(), m["when"], m["ops"].asList())
    }

    companion object {
        private const val MAGIC_ENC = "EIX1"
        private const val MAGIC_PLAIN = "EIP1"

        // Not a secret: the pack is encrypted only so that nobody reads the stage by accident.
        private val KEY_PARTS = listOf("exit", "-inter", "view/", "kotatsu", "#2026")

        internal fun key(): ByteArray = MessageDigest.getInstance("SHA-256").digest(KEY_PARTS.joinToString("").toByteArray(Charsets.UTF_8))

        /** Decrypts and parses the pack file shipped in the app's assets. */
        fun decode(file: ByteArray): Pack {
            require(file.size > 16 + 16 && String(file, 0, 4, Charsets.US_ASCII) == MAGIC_ENC) { "bad pack" }
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, SecretKeySpec(key(), "AES"), GCMParameterSpec(128, file, 4, 12))
            val plain = cipher.doFinal(file, 16, file.size - 16)
            return fromPlain(plain)
        }

        fun fromPlain(plain: ByteArray): Pack {
            require(plain.size >= 8 && String(plain, 0, 4, Charsets.US_ASCII) == MAGIC_PLAIN) { "bad pack body" }
            val n = ((plain[4].toInt() and 0xff) shl 24) or ((plain[5].toInt() and 0xff) shl 16) or
                ((plain[6].toInt() and 0xff) shl 8) or (plain[7].toInt() and 0xff)
            val json = String(plain, 8, n, Charsets.UTF_8)
            return Pack(plain, 8 + n, Json.parse(json).asMap())
        }
    }
}
