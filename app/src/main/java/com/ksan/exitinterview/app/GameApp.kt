package com.ksan.exitinterview.app

import android.content.ClipboardManager
import android.content.Context
import android.content.SharedPreferences
import android.graphics.Typeface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.ksan.exitinterview.R
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

enum class Screen { LOADING, TITLE, TEST_MENU, JOIN, SETTINGS, LOBBY, GAME, ENDING }

enum class Overlay { NONE, MENU, HINT }

/** Everything the screens show, plus the actions they can trigger. Holds no puzzle knowledge. */
class GameApp(private val ctx: Context) {
    private val prefs: SharedPreferences = ctx.getSharedPreferences("exit_interview", Context.MODE_PRIVATE)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var loop: Job? = null
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

    /** The server address built into the APK (server_base.txt, made at build time; no key). Empty when there is none. */
    val builtInBase: String = readAsset("server_base.txt")

    /** The key made from the server passphrase (the passphrase itself is not kept). */
    var passKey by mutableStateOf(prefs.getString("pass_key", "") ?: "")
        private set

    init {
        sfx.enabled = soundOn
        server = prefs.getString("server", null) ?: readAsset("server.txt")
        scope.launch {
            try {
                pack = withContext(Dispatchers.IO) { Pack.decode(ctx.assets.open("stage.pack").use { it.readBytes() }) }
                screen = Screen.TITLE
            } catch (e: Exception) {
                notice = "ステージを読み込めません"
            }
        }
    }

    private fun readAsset(name: String): String = try {
        ctx.assets.open(name).use { it.readBytes().toString(Charsets.UTF_8).trim() }
    } catch (e: IOException) {
        ""
    }

    fun nowSec(): Int = (System.currentTimeMillis() / 1000).toInt()

    fun hasServer(): Boolean = endpoint() != null

    /** True when the APK has a server address built in, so the players only need the passphrase. */
    fun usesPassphrase(): Boolean = ServerAddress.base(builtInBase) != null

    /** A pasted URL (with its key) wins; otherwise the built-in address with the passphrase's key. */
    private fun endpoint(): Pair<String, String>? {
        ServerAddress.parse(server)?.let { return it }
        val base = ServerAddress.base(builtInBase) ?: return null
        if (passKey.isEmpty()) return null
        return Pair(base, passKey)
    }

    private fun client(local: Boolean): RoomClient? {
        if (local) return RoomClient(LocalTransport(), "")
        val e = endpoint() ?: return null
        return RoomClient(HttpTransport(e.first), e.second)
    }

    private fun netMessage(e: IOException): String = when ((e as? RoomException)?.reason) {
        "nf" -> "その合言葉の部屋はありません"
        "full" -> "その部屋は満員です"
        "key" -> if (ServerAddress.parse(server) == null && usesPassphrase()) "サーバーの合言葉が違います（「設定」で入れ直してください）" else "サーバーの URL が違います（鍵が合いません）"
        else -> "通信できません"
    }

    // ---------------------------------------------------------------- rooms

    /** [alone]: one device plays both seats. [local]: no server at all (rooms live inside the app). */
    fun createRoom(roomMode: String, alone: Boolean, local: Boolean) {
        val p = pack ?: return
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

    fun joinRoom(code: String) {
        val p = pack ?: return
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
        roomCode = s.code
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
            prefs.edit().putString("code", s.code).apply()
            savedCode = s.code
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
        shownStage = -1
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
            while (isActive) {
                val s = session ?: break
                if (!resumed) {
                    delay(300)
                    continue
                }
                try {
                    val v = viewId
                    val t = System.currentTimeMillis()
                    val tell = if (v != null && (v != lastView || s.slot != lastSlot || t - lastBeat > 5000)) v else null
                    var did = s.flush(tell)
                    if (!did && (tell != null || t - lastPoll >= 1000)) {
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
                if (opened != null && screen == Screen.GAME && captions.isEmpty()) {
                    hintFocus = opened.id
                    overlay = Overlay.HINT
                }
            }
        }
        if (screen != Screen.GAME && screen != Screen.ENDING) return
        val stage = next.f(Rules.STAGE)
        if (stage != shownStage) {
            shownStage = stage
            selected = null
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
        for (name in out.fx.sfx) sfx.play(name)
        if (out.fx.shake) shake += 1
        if (out.fx.unsel) selected = null
        val target = out.fx.go
        if (target != null) viewId = target
        syncUi(false)
    }

    fun go(id: String?) {
        val p = pack ?: return
        if (id == null || id.isEmpty()) return
        viewId = Rules.resolve(p, state, id, nowSec())
        sfx.play("move")
    }

    fun jumpToPartner() = go(partnerView)

    fun selectItem(id: String) {
        selected = if (selected == id) null else id
        sfx.play("tick")
    }

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

    /** Keeps the key made from the passphrase. Both players type the same passphrase once. */
    fun setPassphrase(text: String): Boolean {
        val k = ServerAddress.keyOf(text)
        if (k == null) {
            notice = "合言葉を入れてください"
            return false
        }
        passKey = k
        prefs.edit().putString("pass_key", k).apply()
        notice = "サーバーの合言葉を設定しました"
        return true
    }

    fun clearPassphrase() {
        passKey = ""
        prefs.edit().remove("pass_key").apply()
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
