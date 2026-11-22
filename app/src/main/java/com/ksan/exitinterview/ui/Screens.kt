package com.ksan.exitinterview.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ksan.exitinterview.app.GameApp
import com.ksan.exitinterview.app.Overlay
import com.ksan.exitinterview.app.Screen
import com.ksan.exitinterview.engine.Rules
import com.ksan.exitinterview.engine.ServerAddress

@Composable
fun AppRoot(game: GameApp) {
    Box(Modifier.fillMaxSize().background(Color.Black), contentAlignment = Alignment.Center) {
        when (game.screen) {
            Screen.LOADING -> Label("読み込み中…", 20.sp)
            Screen.TITLE -> TitleScreen(game)
            Screen.TEST_MENU -> TestMenu(game)
            Screen.JOIN -> JoinScreen(game)
            Screen.SETTINGS -> SettingsScreen(game)
            Screen.LOBBY -> LobbyScreen(game)
            Screen.GAME -> GameScreen(game)
            Screen.ENDING -> EndingScreen(game)
        }
        if (game.captions.isNotEmpty()) CaptionOverlay(game)
        val note = game.notice
        if (note != null) {
            Box(
                Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp)
                    .background(Ui.Panel, Ui.Corner).border(2.dp, Ui.Accent, Ui.Corner)
                    .clickable { game.notice = null }
                    .padding(horizontal = 20.dp, vertical = 10.dp),
            ) {
                Label(note, 16.sp)
            }
        }
    }
    BackHandler(enabled = game.screen != Screen.TITLE && game.screen != Screen.LOADING) { onBack(game) }
}

private fun onBack(game: GameApp) {
    when (game.screen) {
        Screen.GAME -> when {
            game.captions.isNotEmpty() -> Unit
            game.overlay != Overlay.NONE -> game.overlay = Overlay.NONE
            else -> {
                val back = game.pack?.views?.get(game.viewId ?: "")?.back
                if (back != null) game.go(back) else game.overlay = Overlay.MENU
            }
        }
        Screen.LOBBY -> game.leaveToTitle(true)
        Screen.ENDING -> Unit
        else -> game.screen = Screen.TITLE
    }
}

@Composable
private fun TitleScreen(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("Exit Interview", 46.sp, color = Ui.Accent)
        Label("出られたら合格", 15.sp, color = Ui.Dim)
        Spacer(Modifier.height(6.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("部屋を作る", 18.sp, enabled = !game.busy, strong = true) { game.createRoom("main", false, false) }
            PlainButton("部屋に入る", 18.sp, enabled = !game.busy) { game.screen = Screen.JOIN }
        }
        val saved = game.savedCode
        if (saved.isNotEmpty()) {
            PlainButton("続きから（$saved）", 16.sp, enabled = !game.busy) { game.joinRoom(saved) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("テスト部屋", 15.sp, enabled = !game.busy) { game.screen = Screen.TEST_MENU }
            PlainButton("設定", 15.sp) { game.screen = Screen.SETTINGS }
        }
        if (!game.hasServer()) {
            val msg = if (game.usesPassphrase()) "サーバーの合言葉がまだです（「設定」から）" else "サーバーがまだ設定されていません（「設定」から）"
            Label(msg, 13.sp, color = Ui.Red)
        }
    }
}

@Composable
private fun TestMenu(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("テスト部屋", 26.sp, color = Ui.Accent)
        PlainButton("1人で（通信なし）", 17.sp, enabled = !game.busy) { game.createRoom("test", true, true) }
        PlainButton("1人で（サーバーを使う）", 17.sp, enabled = !game.busy && game.hasServer()) { game.createRoom("test", true, false) }
        PlainButton("2人で", 17.sp, enabled = !game.busy && game.hasServer()) { game.createRoom("test", false, false) }
        PlainButton("戻る", 15.sp) { game.screen = Screen.TITLE }
    }
}

@Composable
private fun JoinScreen(game: GameApp) {
    var code by remember { mutableStateOf("") }
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Label("合言葉", 16.sp, color = Ui.Dim)
        Label(code.padEnd(4, '・'), 44.sp, color = Ui.Accent)
        for (row in listOf("12345", "67890")) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (d in row) {
                    PlainButton(d.toString(), 22.sp, Modifier.width(58.dp)) { if (code.length < 4) code += d }
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("戻る", 16.sp) { game.screen = Screen.TITLE }
            PlainButton("消す", 16.sp) { code = code.dropLast(1) }
            PlainButton("入る", 16.sp, enabled = code.length == 4 && !game.busy, strong = true) { game.joinRoom(code) }
        }
    }
}

@Composable
private fun LobbyScreen(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Label("合言葉", 16.sp, color = Ui.Dim)
        Label(game.roomCode, 64.sp, color = Ui.Accent)
        Label(if (game.partnerJoined) "相棒が来ました" else "相棒を待っています…", 18.sp)
        Spacer(Modifier.height(4.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("やめる", 16.sp) { game.leaveToTitle(true) }
            PlainButton("始める", 18.sp, strong = true) { game.beginPlay() }
        }
    }
}

@Composable
private fun SettingsScreen(game: GameApp) {
    var pass by remember { mutableStateOf("") }
    val pasted = ServerAddress.parse(game.server) != null
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Label("設定", 26.sp, color = Ui.Accent)
        if (game.usesPassphrase()) {
            // 合言葉の欄は上に置く（キーボードが出ても隠れにくい）
            Label(
                if (game.passKey.isNotEmpty()) "サーバーの合言葉：設定済み（2人で同じ言葉）" else "サーバーの合言葉：未設定（2人で同じ言葉を入れる）",
                14.sp,
                color = if (game.passKey.isNotEmpty() || pasted) Ui.Dim else Ui.Red,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(
                    Modifier.width(230.dp).background(Ui.Dark, Ui.Corner).border(2.dp, Ui.Line, Ui.Corner)
                        .padding(horizontal = 12.dp, vertical = 9.dp),
                ) {
                    if (pass.isEmpty()) Label("合言葉", 15.sp, color = Ui.Dim)
                    BasicTextField(
                        value = pass,
                        onValueChange = { pass = it.replace("\n", "") },
                        modifier = Modifier.width(206.dp),
                        textStyle = TextStyle(color = Ui.Text, fontSize = 15.sp, fontFamily = Ui.Hand),
                        singleLine = true,
                        cursorBrush = SolidColor(Ui.Accent),
                    )
                }
                PlainButton("決める", 15.sp, enabled = pass.isNotBlank(), strong = true) { if (game.setPassphrase(pass)) pass = "" }
                PlainButton("消す", 15.sp, enabled = game.passKey.isNotEmpty()) { game.clearPassphrase() }
            }
        }
        PlainButton(if (game.soundOn) "音：オン" else "音：オフ", 17.sp) { game.toggleSound() }
        val host = ServerAddress.host(game.server).take(34)
        val urlLabel = when {
            pasted -> "サーバー：$host（貼り付けた URL を使う）"
            game.usesPassphrase() -> "サーバーの URL を貼り付けて使うこともできます"
            else -> "サーバー：未設定"
        }
        Label(urlLabel, 14.sp, color = Ui.Dim)
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("クリップボードから貼り付け", 15.sp) { game.pasteServer() }
            PlainButton("元に戻す", 15.sp, enabled = pasted) { game.clearServer() }
        }
        PlainButton("戻る", 15.sp) { game.screen = Screen.TITLE }
    }
}

@Composable
private fun CaptionOverlay(game: GameApp) {
    val line = game.captions.getOrNull(game.captionAt) ?: ""
    Box(Modifier.fillMaxSize().background(Color.Black).clickable { game.nextCaption() }, contentAlignment = Alignment.Center) {
        Label(line, 22.sp, Modifier.padding(horizontal = 56.dp), align = TextAlign.Center)
        Label("▼", 16.sp, Modifier.align(Alignment.BottomCenter).padding(bottom = 22.dp), color = Ui.Dim)
    }
}

@Composable
private fun EndingScreen(game: GameApp) {
    val def = game.pack?.stages?.get(game.state.f(Rules.STAGE))
    val sec = Rules.playSeconds(game.state, game.nowSec())
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        for (line in def?.credits ?: emptyList()) Label(line, 15.sp, color = Ui.Dim)
        val letter = def?.letter ?: emptyList()
        if (letter.isNotEmpty()) {
            Column(
                Modifier.padding(vertical = 6.dp).background(Ui.Text, Ui.Corner).border(2.dp, Ui.Ink, Ui.Corner).padding(horizontal = 28.dp, vertical = 14.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                for (line in letter) Label(line, 22.sp, color = Ui.Ink)
            }
        }
        Label("かかった時間：${sec / 60}分${sec % 60}秒", 16.sp)
        Label("ヒント：${game.state.f(Rules.N_HINT)}回　スキップ：${game.state.f(Rules.N_SKIP)}回", 16.sp)
        Spacer(Modifier.height(4.dp))
        PlainButton("タイトルへ", 16.sp) { game.leaveToTitle(true) }
    }
}
