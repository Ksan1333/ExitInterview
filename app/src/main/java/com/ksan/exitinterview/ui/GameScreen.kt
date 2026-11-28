package com.ksan.exitinterview.ui

import android.graphics.Paint
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ksan.exitinterview.app.GameApp
import com.ksan.exitinterview.app.Overlay
import com.ksan.exitinterview.engine.Pack
import com.ksan.exitinterview.engine.Rules
import com.ksan.exitinterview.engine.ViewDef
import kotlinx.coroutines.delay
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.roundToInt

/** How far (a part of the scene's width) a finger has to move to count as drawn across rather than a tap. */
private const val SWIPE_PART = 0.05f

/** The scene is laid out in a 960x540 space; [u] is the size of one such unit on this screen. */
@Composable
fun GameScreen(game: GameApp) {
    val pack = game.pack ?: return
    LaunchedEffect(Unit) {
        while (true) {
            delay(250)
            game.tick += 1
        }
    }
    val view = pack.views[game.viewId ?: ""]
    BoxWithConstraints(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        val u: Dp = if (maxWidth / 960 < maxHeight / 540) maxWidth / 960 else maxHeight / 540
        val density = LocalDensity.current
        val fs: (Float) -> TextUnit = { px -> with(density) { (u * px).toSp() } }
        var dx by remember { mutableStateOf(0) }
        LaunchedEffect(game.shake) {
            if (game.shake > 0) {
                for (i in 0 until 6) {
                    dx = if (i % 2 == 0) 7 else -7
                    delay(45)
                }
                dx = 0
            }
        }
        Box(Modifier.size(u * 960, u * 540).offset(x = u * dx, y = 0.dp)) {
            if (view != null) {
                SceneCanvas(game, pack, view, Modifier.fillMaxSize())
                Hud(game, pack, view, u, fs)
                Toast(game, u, fs)
            }
        }
        if (!game.netOk) {
            Label("通信中…", 13.sp, Modifier.align(Alignment.BottomCenter).padding(bottom = 6.dp), color = Ui.Accent)
        }
        when (game.overlay) {
            Overlay.MENU -> MenuOverlay(game)
            Overlay.HINT -> HintOverlay(game, pack)
            Overlay.ITEM -> ItemOverlay(game, pack)
            Overlay.ASK -> AskOverlay(game, pack)
            Overlay.NONE -> Unit
        }
    }
}

/** A line over the top of the scene. It has no tap handling, so taps go through to the scene below. */
@Composable
private fun Toast(game: GameApp, u: Dp, fs: (Float) -> TextUnit) {
    @Suppress("UNUSED_VARIABLE") val tick = game.tick // read so that the line goes away on time
    val line = game.toastNow() ?: return
    Box(Modifier.offset(x = u * 180, y = u * 62).size(u * 600, u * 46), contentAlignment = Alignment.Center) {
        Box(
            Modifier.background(Ui.Panel, Ui.Corner).border(2.dp, Ui.Accent, Ui.Corner).padding(horizontal = u * 16, vertical = u * 6),
            contentAlignment = Alignment.Center,
        ) {
            Label(line, fs(16f), align = TextAlign.Center)
        }
    }
}

/** The item picked from the bar, shown large with what it is. */
@Composable
private fun ItemOverlay(game: GameApp, pack: Pack) {
    val def = pack.items[game.zoomItem ?: ""] ?: return
    Sheet(onDismiss = { game.closeZoom() }) {
        Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(Modifier.weight(1.4f).fillMaxHeight(), contentAlignment = Alignment.Center) {
                val side = if (game.zoomBack) def.back else null
                val img = game.images.get(pack, side ?: def.big ?: def.img)
                if (img != null) Image(bitmap = img, contentDescription = null, modifier = Modifier.fillMaxSize())
            }
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(9.dp)) {
                if (def.name.isNotEmpty()) Label(def.name, 19.sp, color = Ui.Accent)
                for (line in def.desc) Label(line, 15.sp)
                Spacer(Modifier.height(4.dp))
                if (def.back != null) PlainButton(if (game.zoomBack) "表にする" else "裏返す", 15.sp) { game.flipZoom() }
                PlainButton("閉じる", 15.sp, strong = true) { game.closeZoom() }
                PlainButton("選ぶのをやめる", 15.sp) { game.putDownItem() }
            }
        }
    }
}

/** A question answered by typing. It sits at the top so that the keyboard does not cover it. */
@Composable
private fun AskOverlay(game: GameApp, pack: Pack) {
    val q = pack.asks[game.askId ?: ""] ?: return
    var text by remember(q.id) { mutableStateOf("") }
    val focus = remember { FocusRequester() }
    Box(Modifier.fillMaxSize().background(Ui.Scrim).clickable { game.closeAsk() }, contentAlignment = Alignment.TopCenter) {
        Column(
            Modifier.padding(top = 10.dp).fillMaxWidth(0.8f)
                .background(Ui.Panel, Ui.Corner).border(2.dp, Ui.Line, Ui.Corner)
                .pointerInput(Unit) { detectTapGestures { } }
                .padding(horizontal = 22.dp, vertical = 12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Label(q.prompt, 18.sp, align = TextAlign.Center)
            Box(
                Modifier.width(360.dp).background(Ui.Dark, Ui.Corner).border(2.dp, Ui.Accent, Ui.Corner)
                    .padding(horizontal = 14.dp, vertical = 10.dp),
            ) {
                if (text.isEmpty()) Label("ここに入れる", 18.sp, color = Ui.Dim)
                BasicTextField(
                    value = text,
                    onValueChange = {
                        text = it.replace("\n", "")
                        game.askNote = null
                    },
                    modifier = Modifier.width(332.dp).focusRequester(focus),
                    textStyle = TextStyle(color = Ui.Text, fontSize = 18.sp, fontFamily = Ui.Hand),
                    singleLine = true,
                    cursorBrush = SolidColor(Ui.Accent),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = { if (text.isNotBlank()) game.answer(text) }),
                )
            }
            val note = game.askNote
            if (note != null) Label(note, 15.sp, color = Ui.Accent)
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                PlainButton("やめる", 16.sp) { game.closeAsk() }
                PlainButton("答える", 18.sp, enabled = text.isNotBlank(), strong = true) { game.answer(text) }
            }
        }
    }
    LaunchedEffect(q.id) { focus.requestFocus() }
}

@Composable
private fun SceneCanvas(game: GameApp, pack: Pack, view: ViewDef, modifier: Modifier) {
    val state = game.state
    val tick = game.tick
    val paint = remember { Paint().apply { isAntiAlias = true; textAlign = Paint.Align.CENTER } }
    Canvas(
        modifier.pointerInput(view.id) {
            // A touch that stays put is a tap. One that moves is a finger drawn across the scene: in the direction it
            // went furthest, or, when it went back and forth (rubbing), in no direction.
            awaitEachGesture {
                val down = awaitFirstDown()
                val start = down.position
                var last = start
                var travel = 0f
                var moved = false
                while (true) {
                    val c = awaitPointerEvent().changes.firstOrNull { it.id == down.id } ?: break
                    travel += (c.position - last).getDistance()
                    last = c.position
                    if ((last - start).getDistance() > viewConfiguration.touchSlop) moved = true
                    if (!c.pressed) break
                }
                val x = start.x / size.width * 960f
                val y = start.y / size.height * 540f
                val dx = last.x - start.x
                val dy = last.y - start.y
                val far = size.width * SWIPE_PART
                when {
                    !moved -> game.tap(x, y)
                    max(abs(dx), abs(dy)) > far -> game.swipe(x, y, if (abs(dx) > abs(dy)) (if (dx > 0) 1 else 3) else (if (dy > 0) 2 else 0))
                    travel > far * 2 -> game.swipe(x, y, -1)
                }
            }
        },
    ) {
        val k = size.width / 960f
        val millis = game.nowMillis() + tick * 0L
        val now = (millis / 1000).toInt()

        fun put(id: String?, x: Float, y: Float, w: Float, h: Float) {
            val img = game.images.get(pack, id ?: return) ?: return
            drawImage(
                image = img,
                dstOffset = IntOffset((x * k).roundToInt(), (y * k).roundToInt()),
                dstSize = IntSize((w * k).roundToInt().coerceAtLeast(1), (h * k).roundToInt().coerceAtLeast(1)),
            )
        }

        put(view.bg, 0f, 0f, 960f, 540f)
        for (l in view.layers) {
            if (!Rules.test(l.cond, state, null, now)) continue
            val flag = l.posFlag
            if (l.frames.isNotEmpty()) {
                put(l.frames[((millis / l.frameMs.coerceAtLeast(1)) % l.frames.size).toInt()], l.x, l.y, l.w, l.h)
            } else if (flag != null) {
                val p = l.pos.getOrNull(state.f(flag)) ?: continue
                put(l.img, p[0], p[1], l.w, l.h)
            } else {
                put(l.img, l.x, l.y, l.w, l.h)
            }
        }
        for (t in view.texts) {
            if (!Rules.test(t.cond, state, null, now)) continue
            val v = state.f(t.flag)
            val text = when (t.kind) {
                "cool" -> (v - now).coerceAtLeast(0).toString()
                "map" -> t.map.getOrNull(v) ?: ""
                else -> v.toString()
            }
            paint.typeface = game.typeface
            paint.textSize = t.size * k
            paint.color = android.graphics.Color.parseColor(t.color)
            drawContext.canvas.nativeCanvas.drawText(text, t.x * k, t.y * k - (paint.ascent() + paint.descent()) / 2f, paint)
        }
    }
}

@Composable
private fun Hud(game: GameApp, pack: Pack, view: ViewDef, u: Dp, fs: (Float) -> TextUnit) {
    fun at(x: Int, y: Int, w: Int, h: Int): Modifier = Modifier.offset(x = u * x, y = u * y).size(u * w, u * h)
    val chip = Modifier.background(Ui.Panel, Ui.Corner).border(2.dp, Ui.Line, Ui.Corner)

    val partner = pack.views[game.partnerView]
    if (partner != null) {
        Row(
            at(12, 10, 250, 44).then(chip).clickable { game.jumpToPartner() }.padding(horizontal = u * 10),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Canvas(Modifier.size(u * 26, u * 17)) {
                drawOval(color = Ui.Text, style = Stroke(width = size.height * 0.13f))
                drawCircle(color = Ui.Text, radius = size.height * 0.24f)
            }
            Spacer(Modifier.width(u * 8))
            Label("相棒：" + partner.name, fs(15f))
        }
    }
    if (game.solo) {
        Box(at(748, 10, 124, 44).then(chip).clickable { game.switchSeat() }, contentAlignment = Alignment.Center) {
            Label("操作：" + (game.slot + 1), fs(15f), color = Ui.Accent)
        }
    }
    Box(at(884, 10, 64, 44).then(chip).clickable { game.overlay = Overlay.MENU }, contentAlignment = Alignment.Center) {
        Label("メニュー", fs(13f))
    }
    if (view.left != null) Arrow(at(14, 238, 44, 64).then(chip), true) { game.go(view.left) }
    if (view.right != null) Arrow(at(826, 238, 44, 64).then(chip), false) { game.go(view.right) }
    if (view.back != null) {
        Box(at(14, 472, 78, 54).then(chip).clickable { game.go(view.back) }, contentAlignment = Alignment.Center) {
            Label("戻る", fs(15f))
        }
    }

    val held = pack.items.keys.filter { game.state.n(it) > 0 }
    for (i in 0 until 6) {
        val id = held.getOrNull(i)
        Box(
            at(884, 66 + i * 64, 64, 56)
                .background(Color(0xB30F1719), Ui.Corner)
                .border(2.dp, if (id != null && id == game.selected) Ui.Accent else Ui.Line, Ui.Corner)
                .clickable(enabled = id != null) { if (id != null) game.selectItem(id) },
        ) {
            if (id != null) {
                val img = game.images.get(pack, pack.items[id]?.img ?: "")
                if (img != null) Image(bitmap = img, contentDescription = null, modifier = Modifier.fillMaxSize().padding(u * 3))
                val n = game.state.n(id)
                if (n > 1) Label("×$n", fs(15f), Modifier.align(Alignment.BottomEnd).padding(end = u * 4), color = Ui.Accent)
            }
        }
    }
}

@Composable
private fun Arrow(modifier: Modifier, left: Boolean, onClick: () -> Unit) {
    Box(modifier.clickable(onClick = onClick), contentAlignment = Alignment.Center) {
        Canvas(Modifier.fillMaxSize(0.42f)) {
            val p = Path()
            if (left) {
                p.moveTo(size.width, 0f)
                p.lineTo(0f, size.height / 2f)
                p.lineTo(size.width, size.height)
            } else {
                p.moveTo(0f, 0f)
                p.lineTo(size.width, size.height / 2f)
                p.lineTo(0f, size.height)
            }
            p.close()
            drawPath(p, Ui.Text)
        }
    }
}

@Composable
private fun Sheet(onDismiss: () -> Unit, content: @Composable () -> Unit) {
    Box(Modifier.fillMaxSize().background(Ui.Scrim).clickable(onClick = onDismiss), contentAlignment = Alignment.Center) {
        Box(
            Modifier.fillMaxWidth(0.8f).fillMaxHeight(0.88f)
                .background(Ui.Panel, Ui.Corner).border(2.dp, Ui.Line, Ui.Corner)
                .pointerInput(Unit) { detectTapGestures { } }
                .padding(horizontal = 22.dp, vertical = 14.dp),
            contentAlignment = Alignment.Center,
        ) {
            content()
        }
    }
}

@Composable
private fun MenuOverlay(game: GameApp) {
    Sheet(onDismiss = { game.overlay = Overlay.NONE }) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(9.dp)) {
            if (!com.ksan.exitinterview.engine.ServerAddress.isPassphraseRoom(game.roomCode)) Label("合言葉 " + game.roomCode, 15.sp, color = Ui.Dim)
            PlainButton("ヒント", 18.sp, strong = true) {
                game.hintFocus = null
                game.overlay = Overlay.HINT
            }
            PlainButton(if (game.soundOn) "音：オン" else "音：オフ", 16.sp) { game.toggleSound() }
            PlainButton("タイトルへ戻る", 16.sp) { game.leaveToTitle(false) }
            PlainButton("閉じる", 16.sp) { game.overlay = Overlay.NONE }
        }
    }
}

@Composable
private fun HintOverlay(game: GameApp, pack: Pack) {
    val open = game.openPuzzles()
    val focus = open.firstOrNull { it.id == game.hintFocus }
    Sheet(onDismiss = { game.overlay = Overlay.NONE }) {
        if (focus == null) {
            Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(9.dp)) {
                Label(if (open.isEmpty()) "今はヒントがありません" else "どこのヒント？", 18.sp, color = Ui.Accent)
                for (p in open) PlainButton(p.name, 17.sp) { game.hintFocus = p.id }
                PlainButton("閉じる", 15.sp) { game.overlay = Overlay.NONE }
            }
        } else {
            val level = Rules.hintLevel(game.state, focus.id)
            var armed by remember(focus.id) { mutableStateOf(false) }
            Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Label(focus.name, 18.sp, color = Ui.Accent)
                Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    if (level == 0) Label("ヒントは3段階。開くと2人の画面に出ます。", 15.sp, color = Ui.Dim)
                    for (i in 0 until minOf(level, 3)) Label("ヒント${i + 1}：" + focus.hints.getOrElse(i) { "" }, 16.sp)
                    if (level >= Rules.MAX_HINT) Label("答え：" + focus.answer, 16.sp, color = Ui.Accent)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    if (level < 3) {
                        PlainButton("ヒント${level + 1}を開く", 15.sp, strong = true) { game.revealHint(focus.id) }
                    } else if (level == 3) {
                        PlainButton("答えを見る", 15.sp, strong = true) { game.revealHint(focus.id) }
                    } else {
                        PlainButton(if (armed) "本当にスキップ" else "スキップする", 15.sp) {
                            if (armed) game.skipPuzzle(focus.id) else armed = true
                        }
                    }
                    PlainButton("別のヒント", 15.sp) { game.hintFocus = null }
                    PlainButton("閉じる", 15.sp) { game.overlay = Overlay.NONE }
                }
            }
        }
    }
}
