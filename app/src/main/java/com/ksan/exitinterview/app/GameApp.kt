package com.ksan.exitinterview.app

import android.content.ClipboardManager
import android.content.Context
import android.content.SharedPreferences
import android.graphics.Typeface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.ksan.exitinterview.R
import com.ksan.exitinterview.engine.Fx
import com.ksan.exitinterview.engine.GameState
import com.ksan.exitinterview.engine.HttpTransport
import com.ksan.exitinterview.engine.LocalTransport
import com.ksan.exitinterview.engine.Pack
import com.ksan.exitinterview.engine.Puzzle
import com.ksan.exitinterview.engine.RoomClient
import com.ksan.exitinterview.engine.RoomException
import com.ksan.exitinterview.engine.Rules
import com.ksan.exitinterview.engine.ServerAddress
import com.ksan.exitinterview.engine.Session
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.IOException
import java.util.UUID

enum class Screen { LOADING, TITLE, TEST_MENU, MEET, SETTINGS, LOBBY, GAME, ENDING }

enum class Overlay { NONE, MENU, HINT, ITEM, ASK }

/**
 * One story, with its own stage pack and room modes. Episode 1 keeps the modes it always had ("main", "test"),
 * so the rooms of players who are in the middle of it stay where they are. Modes are at most 8 letters (the server keeps 8).
 */
class Episode(val no: Int, val asset: String, val mainMode: String, val testMode: String, val fallbackTagline: String)

val EPISODES = listOf(
    Episode(1, "stage.pack", "main", "test", "出られたら合格"),
    Episode(2, "stage2.pack", "main2", "test2", ""),
)

fun episodeOf(mode: String): Episode = EPISODES.firstOrNull { it.mainMode == mode || it.testMode == mode } ?: EPISODES[0]

fun isTestMode(mode: String): Boolean = EPISODES.any { it.testMode == mode }

/** How long a line over the scene stays up. */
const val TOAST_MS = 3500L

/** How long after the last change in the room the faster polling lasts, and the two polling gaps. */
const val BUSY_MS = 30_000L
const val FAST_POLL_MS = 500L
const val QUIET_POLL_MS = 1000L

/** Where a player is, sent again this often even when it has not changed. */
const val RESEND_VIEW_MS = 60_000L

/** Everything the screens show, plus the actions they can trigger. Holds no puzzle knowledge. */
class GameApp(private val ctx: Context) {
    private val prefs: SharedPreferences = ctx.getSharedPreferences("exit_interview", Context.MODE_PRIVATE)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var loop: Job? = null
    private var warmJob: Job? = null
    private var resumed = true
    private var shownStage = -1
    private var offline = false
    private val seatView = arrayOfNulls<String>(2)
    private val seatSelected = arrayOfNulls<String>(2)
    private val pid: String = prefs.getString("pid", null)
        ?: UUID.randomUUID().toString().also { prefs.edit().putString("pid", it).apply() }

    val images = Images()
    val sfx = Sfx(ctx)
    val typeface: Typeface = ctx.resources.getFont(R.font.yomogi_regular)

    /** Stage packs by episode number (only the ones shipped in the APK). */
    private val packs = HashMap<Int, Pack>()

    /** Episodes that can be played, in order. */
    var episodes by mutableStateOf<List<Episode>>(emptyList())
        private set

    /** The episode picked on the title screen ("遊ぶ" and the test room use it). */
    var episode by mutableStateOf(prefs.getInt("episode", 1))
        private set

    /** The pack of the room being played (or of the picked episode before any room). */
    var pack: Pack? = null
        private set
    var session: Session? = null
        private set

    var screen by mutableStateOf(Screen.LOADING)
    var notice by mutableStateOf<String?>(null)
    var busy by mutableStateOf(false)
    var overlay by mutableStateOf(Overlay.NONE)
    var roomCode by mutableStateOf("")
    var solo by mutableStateOf(false)
    var slot by mutableStateOf(0)
    var state by mutableStateOf(GameState.EMPTY)
    var partnerView by mutableStateOf("")
    var partnerJoined by mutableStateOf(false)
    var netOk by mutableStateOf(true)
    var viewId by mutableStateOf<String?>(null)
    var selected by mutableStateOf<String?>(null)
    var captions by mutableStateOf<List<String>>(emptyList())
    var captionAt by mutableStateOf(0)
    var shake by mutableStateOf(0)
    var tick by mutableStateOf(0)
    var hintFocus by mutableStateOf<String?>(null)
    var soundOn by mutableStateOf(prefs.getBoolean("sound", true))
    var server by mutableStateOf("")
    var savedCode by mutableStateOf(prefs.getString("code", "") ?: "")

    /** Episode of the saved room (rooms saved before episode 2 existed are episode 1). */
    var savedEpisode by mutableStateOf(prefs.getInt("code_ep", 1))

    /** The item shown large (Overlay.ITEM), and whether its other side is up. */
    var zoomItem by mutableStateOf<String?>(null)
    var zoomBack by mutableStateOf(false)

    /** The question being answered by typing (Overlay.ASK), and the line under it after a wrong answer. */
    var askId by mutableStateOf<String?>(null)
    var askNote by mutableStateOf<String?>(null)

    /** A short line shown over the scene for a few seconds, on this device only. */
    var toast by mutableStateOf<String?>(null)
        private set
    private var toastAt = 0L

    /** The server address built into the APK (server_base.txt, made at build time; no key). Empty when there is none. */
    val builtInBase: String = readAsset("server_base.txt")

    /** Which room the passphrase screen meets in ("main", or "test" from the test menu). */
    var meetMode by mutableStateOf("main")

    init {
        sfx.enabled = soundOn
        prefs.edit().remove("pass_key").apply() // 0.1.2 kept a server key made from a passphrase; no longer used
        server = prefs.getString("server", null) ?: readAsset("server.txt")
        scope.launch {
            val got = withContext(Dispatchers.IO) { EPISODES.mapNotNull { e -> loadPack(e)?.let { e.no to it } }.toMap() }
            if (got[1] == null) {
                notice = "ステージを読み込めません"
                return@launch
            }
            packs.putAll(got)
            episodes = EPISODES.filter { it.no in got }
            if (episode !in got) episode = 1
            pack = got[episode]
            screen = Screen.TITLE
        }
    }

    private fun loadPack(e: Episode): Pack? = try {
        ctx.assets.open(e.asset).use { Pack.decode(it.readBytes()) }
    } catch (x: Exception) {
        null // not shipped in this APK, or unreadable
    }

    val currentEpisode: Episode get() = EPISODES.firstOrNull { it.no == episode } ?: EPISODES[0]

    fun packOf(e: Episode): Pack? = packs[e.no]

    fun chooseEpisode(no: Int) {
        if (no !in packs) return
        episode = no
        pack = packs[no]
        prefs.edit().putInt("episode", no).apply()
    }

    fun episodeTitle(e: Episode): String = packs[e.no]?.title?.takeIf { it.isNotEmpty() } ?: "第${e.no}話"

    fun episodeTagline(e: Episode): String = packs[e.no]?.tagline?.takeIf { it.isNotEmpty() } ?: e.fallbackTagline

    private fun readAsset(name: String): String = try {
        ctx.assets.open(name).use { it.readBytes().toString(Charsets.UTF_8).trim() }
    } catch (e: IOException) {
        ""
    }

    /** The time the game runs on: the server's clock while in a room, so that both phones agree. */
    fun nowMillis(): Long = System.currentTimeMillis() + (session?.clockOffset ?: 0) * 1000L

    fun nowSec(): Int = (nowMillis() / 1000).toInt()

    fun hasServer(): Boolean = endpoint() != null

    /** A pasted URL (with its key) wins; otherwise the address built into the APK, without a key. */
    private fun endpoint(): Pair<String, String>? {
        ServerAddress.parse(server)?.let { return it }
        val base = ServerAddress.base(builtInBase) ?: return null
        return Pair(base, "")
    }

    private fun client(local: Boolean): RoomClient? {
        if (local) return RoomClient(LocalTransport(), "")
        val e = endpoint() ?: return null
        return RoomClient(HttpTransport(e.first), e.second)
    }

    private fun netMessage(e: IOException): String = when ((e as? RoomException)?.reason) {
        "nf" -> "その合言葉の部屋はありません"
        "full" -> "その合言葉の部屋は、もう2人そろっています（別の合言葉にしてください）"
        "key" -> "貼り付けたサーバーの URL が違います（「設定」の「元に戻す」で、アプリのサーバーに戻せます）"
        else -> "通信できません"
    }

    // ---------------------------------------------------------------- rooms

    /** [alone]: one device plays both seats. [local]: no server at all (rooms live inside the app). */
    fun createRoom(roomMode: String, alone: Boolean, local: Boolean) {
        val p = packs[episodeOf(roomMode).no] ?: return
        if (busy) return
        val c = client(local)
        if (c == null) {
            notice = "サーバーが設定されていません"
            return
        }
        busy = true
        scope.launch {
            try {
                val j = withContext(Dispatchers.IO) { c.create(pid, roomMode, Rules.initialState(p, roomMode)) }
                enter(Session(p, c, j.code, j.slot, j.snap), alone, local)
                if (alone) beginPlay() else screen = Screen.LOBBY
            } catch (e: IOException) {
                notice = netMessage(e)
            } finally {
                busy = false
            }
        }
    }

    /**
     * Two players who type the same passphrase meet in one room. The first one makes it and waits in the lobby;
     * the second one (or either of them coming back later) goes straight into the game.
     */
    fun meetRoom(passphrase: String) {
        val roomMode = meetMode
        val p = packs[episodeOf(roomMode).no] ?: return
        if (busy) return
        val code = ServerAddress.roomCodeOf(roomMode, passphrase)
        if (code == null) {
            notice = "合言葉を入れてください"
            return
        }
        val c = client(false)
        if (c == null) {
            notice = "サーバーが設定されていません"
            return
        }
        busy = true
        scope.launch {
            try {
                val j = withContext(Dispatchers.IO) { c.meet(code, pid, roomMode, Rules.initialState(p, roomMode)) }
                enter(Session(p, c, j.code, j.slot, j.snap), false, false)
                if (j.made) screen = Screen.LOBBY else beginPlay()
            } catch (e: IOException) {
                notice = netMessage(e)
            } finally {
                busy = false
            }
        }
    }

    fun joinRoom(code: String) {
        if (packs.isEmpty()) return
        if (busy) return
        val c = client(false)
        if (c == null) {
            notice = "サーバーが設定されていません"
            return
        }
        busy = true
        scope.launch {
            try {
                val j = withContext(Dispatchers.IO) { c.join(code, pid) }
                // the room knows its mode, and the mode tells which episode (and pack) it is
                val p = packs[episodeOf(j.snap.mode).no]
                if (p == null) {
                    notice = "この部屋の話は、このアプリに入っていません"
                    return@launch
                }
                enter(Session(p, c, j.code, j.slot, j.snap), false, false)
                beginPlay()
            } catch (e: IOException) {
                notice = netMessage(e)
                if (e is RoomException && e.reason == "nf" && code == savedCode) forgetSaved()
            } finally {
                busy = false
            }
        }
    }

    private fun enter(s: Session, alone: Boolean, local: Boolean) {
        session = s
        pack = s.pack
        roomCode = s.code
        zoomItem = null
        askId = null
        toast = null
        solo = alone
        offline = local
        slot = s.slot
        shownStage = -1
        state = s.state
        partnerJoined = s.snap.partnerJoined || alone
        partnerView = ""
        seatView[0] = null
        seatView[1] = null
        seatSelected[0] = null
        seatSelected[1] = null
        viewId = null
        selected = null
        captions = emptyList()
        overlay = Overlay.NONE
        netOk = true
        if (!local && !alone) {
            val ep = episodeOf(s.snap.mode).no
            prefs.edit().putString("code", s.code).putInt("code_ep", ep).apply()
            savedCode = s.code
            savedEpisode = ep
        }
        startLoop()
    }

    fun beginPlay() {
        screen = Screen.GAME
        syncUi(false)
    }

    fun leaveToTitle(forget: Boolean) {
        loop?.cancel()
        loop = null
        session = null
        overlay = Overlay.NONE
        captions = emptyList()
        viewId = null
        selected = null
        zoomItem = null
        askId = null
        toast = null
        shownStage = -1
        pack = packs[episode]
        screen = Screen.TITLE
        if (forget && roomCode == savedCode) forgetSaved()
    }

    private fun forgetSaved() {
        prefs.edit().remove("code").apply()
        savedCode = ""
    }

    private fun startLoop() {
        loop?.cancel()
        loop = scope.launch(Dispatchers.IO) {
            var lastPoll = 0L
            var lastBeat = 0L
            var lastView: String? = null
            var lastSlot = -1
            var lastVer = -1
            var lastViews: List<String> = emptyList()
            var busyAt = 0L
            while (isActive) {
                val s = session ?: break
                if (!resumed) {
                    delay(300)
                    continue
                }
                try {
                    val v = viewId
                    val t = System.currentTimeMillis()
                    if (s.hasPending()) busyAt = t
                    // While either player is doing something, look for the partner's moves twice a second.
                    val gap = if (t - busyAt < BUSY_MS) FAST_POLL_MS else QUIET_POLL_MS
                    // Where this player is goes along when it changes. The room keeps it, so it is sent again only
                    // rarely (every write costs the whole room record on the server).
                    val tell = if (v != null && (v != lastView || s.slot != lastSlot || t - lastBeat > RESEND_VIEW_MS)) v else null
                    var did = s.flush(tell)
                    if (!did && (tell != null || t - lastPoll >= gap)) {
                        s.poll(tell)
                        did = true
                    }
                    if (did) {
                        lastPoll = t
                        if (tell != null) {
                            lastView = tell
                            lastSlot = s.slot
                            lastBeat = t
                        }
                        val sn = s.snap
                        if (sn.ver != lastVer || sn.views != lastViews) {
                            if (lastVer != -1) busyAt = t
                            lastVer = sn.ver
                            lastViews = sn.views
                        }
                        withContext(Dispatchers.Main) {
                            netOk = true
                            if (session === s) syncUi(true)
                        }
                    }
                } catch (e: RoomException) {
                    withContext(Dispatchers.Main) {
                        if (e.reason == "nf") {
                            notice = "部屋がなくなりました"
                            leaveToTitle(true)
                        } else {
                            netOk = false
                        }
                    }
                    delay(1500)
                } catch (e: IOException) {
                    withContext(Dispatchers.Main) { netOk = false }
                    delay(1500)
                }
                delay(if (s.hasPending()) 20L else 100L)
            }
        }
    }

    // ---------------------------------------------------------------- keeping the screen in step

    private fun syncUi(fromNet: Boolean) {
        val s = session ?: return
        val p = pack ?: return
        val old = state
        val next = s.state
        partnerJoined = s.snap.partnerJoined || solo
        partnerView = if (solo) (seatView[1 - slot] ?: "") else (s.snap.views.getOrNull(1 - slot) ?: "")
        if (next != old) {
            state = next
            if (fromNet) {
                sfx.play("pon")
                val opened = p.puzzles.firstOrNull { next.f("h_" + it.id) > old.f("h_" + it.id) }
                if (opened != null && screen == Screen.GAME && captions.isEmpty() && overlay != Overlay.ASK) {
                    hintFocus = opened.id
                    overlay = Overlay.HINT
                }
            }
        }
        if (screen != Screen.GAME && screen != Screen.ENDING) return
        val stage = next.f(Rules.STAGE)
        if (stage != shownStage) {
            shownStage = stage
            warmStage(p, stage)
            selected = null
            zoomItem = null
            askId = null
            toast = null
            overlay = Overlay.NONE
            viewId = null
            val lines = p.stages[stage]?.captions ?: emptyList()
            val seen = !offline && prefs.getString("cap_code", "") == roomCode && prefs.getInt("cap_stage", -1) == stage
            if (lines.isEmpty() || seen) {
                afterCaptions()
            } else {
                captions = lines
                captionAt = 0
            }
            return
        }
        if (captions.isEmpty() && screen == Screen.GAME) {
            viewId = Rules.resolve(p, next, viewId, nowSec())
            val sel = selected
            if (sel != null && next.n(sel) <= 0) selected = null
            val z = zoomItem
            if (z != null && next.n(z) <= 0) {
                zoomItem = null
                if (overlay == Overlay.ITEM) overlay = Overlay.NONE
            }
        }
    }

    /**
     * Decodes the pictures of [stage] in the background, the start view and its neighbours first, so that moving
     * around does not stop the screen while a picture is decoded.
     */
    private fun warmStage(p: Pack, stage: Int) {
        warmJob?.cancel()
        val start = p.views[p.stages[stage]?.start ?: ""]
        val near = listOfNotNull(start) + listOfNotNull(start?.left, start?.right, start?.back).mapNotNull { p.views[it] }
        val order = (near + p.views.values.filter { it.stage == stage }).distinct()
        warmJob = scope.launch(Dispatchers.Default) {
            var budget = images.warmBudget
            for (v in order) {
                for (id in listOf(v.bg) + v.layers.flatMap { listOfNotNull(it.img) + it.frames }) {
                    if (!isActive || budget <= 0) return@launch
                    budget -= images.warm(p, id)
                }
            }
        }
    }

    fun nextCaption() {
        if (captionAt + 1 < captions.size) {
            captionAt += 1
            return
        }
        captions = emptyList()
        captionAt = 0
        if (!offline) prefs.edit().putString("cap_code", roomCode).putInt("cap_stage", shownStage).apply()
        afterCaptions()
    }

    private fun afterCaptions() {
        val p = pack ?: return
        if (p.stages[shownStage]?.end == true) {
            viewId = null
            screen = Screen.ENDING
        } else {
            screen = Screen.GAME
            viewId = Rules.resolve(p, state, null, nowSec())
        }
    }

    // ---------------------------------------------------------------- actions from the game screen

    fun tap(x: Float, y: Float) {
        val s = session ?: return
        val p = pack ?: return
        val v = viewId ?: return
        if (captions.isNotEmpty() || overlay != Overlay.NONE) return
        val sel = selected
        val t = nowSec()
        val out = s.submit { st -> Rules.tap(p, st, v, x, y, sel, t) } ?: return
        react(out.fx)
    }

    /** A finger drawn across the scene from (x, y) in direction [dir] (0 up, 1 right, 2 down, 3 left). */
    fun swipe(x: Float, y: Float, dir: Int) {
        val s = session ?: return
        val p = pack ?: return
        val v = viewId ?: return
        if (captions.isNotEmpty() || overlay != Overlay.NONE) return
        val sel = selected
        val t = nowSec()
        val out = s.submit { st -> Rules.swipe(p, st, v, x, y, dir, sel, t) } ?: return
        react(out.fx)
    }

    /** What this device does right after one of its own actions. */
    private fun react(fx: Fx) {
        for (name in fx.sfx) sfx.play(name)
        if (fx.shake) shake += 1
        if (fx.unsel) selected = null
        fx.msg?.let { say(it) }
        val target = fx.go
        if (target != null) viewId = target
        val q = fx.ask
        if (q != null && pack?.asks?.containsKey(q) == true) {
            askId = q
            askNote = null
            overlay = Overlay.ASK
        }
        syncUi(false)
    }

    /** The typed answer to the open question. A wrong one keeps the question open. */
    fun answer(text: String) {
        val s = session ?: return
        val p = pack ?: return
        val q = askId ?: return
        val t = nowSec()
        val out = s.submit { st -> Rules.answer(p, st, q, text, t) }
        if (out == null) {
            closeAsk() // answered already (by the partner), or nothing typed
            if (text.isNotBlank()) say("もう答えが出ているみたい")
            return
        }
        val right = p.asks[q]?.answers?.any { Rules.normalize(it) == Rules.normalize(text) } == true
        if (!right) {
            for (name in out.fx.sfx) sfx.play(name)
            if (out.fx.shake) shake += 1
            askNote = out.fx.msg ?: "ちがうみたい"
            syncUi(false)
        } else {
            closeAsk()
            react(out.fx)
        }
    }

    fun closeAsk() {
        askId = null
        askNote = null
        if (overlay == Overlay.ASK) overlay = Overlay.NONE
    }

    fun go(id: String?) {
        val p = pack ?: return
        if (id == null || id.isEmpty()) return
        viewId = Rules.resolve(p, state, id, nowSec())
        sfx.play("move")
    }

    fun jumpToPartner() = go(partnerView)

    /**
     * First tap on an item picks it (to use it on the scene) and says what it is; a tap on the picked item
     * shows it large, where it can also be put down.
     */
    fun selectItem(id: String) {
        val held = selected
        if (held == id) {
            sfx.play("tick")
            zoomItem = id
            zoomBack = false
            overlay = Overlay.ITEM
            return
        }
        // a picked thing tapped onto another one: the two may go together
        val s = session
        val p = pack
        if (held != null && s != null && p != null && p.combos.isNotEmpty()) {
            val t = nowSec()
            val out = s.submit { st -> Rules.combine(p, st, held, id, t) }
            if (out != null && out.changed) {
                selected = null
                react(out.fx)
                return
            }
        }
        sfx.play("tick")
        selected = id
        val name = pack?.items?.get(id)?.name ?: ""
        say(if (name.isEmpty()) "もう一度タップで大きく見る" else "$name（もう一度タップで大きく見る）")
    }

    fun putDownItem() {
        selected = null
        closeZoom()
    }

    fun closeZoom() {
        zoomItem = null
        zoomBack = false
        if (overlay == Overlay.ITEM) overlay = Overlay.NONE
    }

    fun flipZoom() {
        zoomBack = !zoomBack
        sfx.play("tick")
    }

    /** Shows [text] over the scene for a few seconds. */
    fun say(text: String) {
        toast = text
        toastAt = System.currentTimeMillis()
    }

    /** The line to show now, or null once it has been up long enough. */
    fun toastNow(): String? = toast?.takeIf { System.currentTimeMillis() - toastAt < TOAST_MS }

    fun openPuzzles(): List<Puzzle> {
        val p = pack ?: return emptyList()
        return Rules.openPuzzles(p, state, nowSec())
    }

    fun revealHint(id: String) {
        val s = session ?: return
        val p = pack ?: return
        val t = nowSec()
        s.submit { st -> Rules.revealHint(p, st, id, t) }
        syncUi(false)
    }

    fun skipPuzzle(id: String) {
        val s = session ?: return
        val p = pack ?: return
        val t = nowSec()
        s.submit { st -> Rules.skip(p, st, id, t) }
        sfx.play("ok")
        hintFocus = null
        overlay = Overlay.NONE
        syncUi(false)
    }

    /** Solo play: hand control to the other seat. */
    fun switchSeat() {
        val s = session ?: return
        seatView[slot] = viewId
        seatSelected[slot] = selected
        slot = 1 - slot
        s.slot = slot
        viewId = seatView[slot]
        selected = seatSelected[slot]
        syncUi(false)
    }

    // ---------------------------------------------------------------- settings

    fun toggleSound() {
        soundOn = !soundOn
        sfx.enabled = soundOn
        prefs.edit().putBoolean("sound", soundOn).apply()
    }

    fun pasteServer() {
        val cm = ctx.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = cm.primaryClip
        val text = if (clip != null && clip.itemCount > 0) clip.getItemAt(0).coerceToText(ctx).toString().trim() else ""
        if (ServerAddress.parse(text) != null) {
            server = text
            prefs.edit().putString("server", text).apply()
            notice = "サーバーを設定しました"
        } else {
            notice = "クリップボードにサーバーの URL がありません"
        }
    }

    fun clearServer() {
        prefs.edit().remove("server").apply()
        server = readAsset("server.txt")
    }

    // ---------------------------------------------------------------- lifecycle

    fun onResume() {
        resumed = true
    }

    fun onPause() {
        resumed = false
    }

    fun close() {
        scope.cancel()
        sfx.release()
    }
}
