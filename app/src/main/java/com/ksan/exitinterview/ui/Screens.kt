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
            Screen.MEET -> MeetScreen(game)
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
        Screen.MEET -> game.screen = if (game.meetMode == "test") Screen.TEST_MENU else Screen.TITLE
        else -> game.screen = Screen.TITLE
    }
}

@Composable
private fun TitleScreen(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("Exit Interview", 46.sp, color = Ui.Accent)
        Label("出られたら合格", 15.sp, color = Ui.Dim)
        Spacer(Modifier.height(6.dp))
        PlainButton("遊ぶ", 20.sp, Modifier.width(180.dp), enabled = !game.busy, strong = true) {
            game.meetMode = "main"
            game.screen = Screen.MEET
        }
        val saved = game.savedCode
        if (saved.isNotEmpty()) {
            val label = if (ServerAddress.isPassphraseRoom(saved)) "続きから" else "続きから（$saved）"
            PlainButton(label, 16.sp, enabled = !game.busy) { game.joinRoom(saved) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("テスト部屋", 15.sp, enabled = !game.busy) { game.screen = Screen.TEST_MENU }
            PlainButton("設定", 15.sp) { game.screen = Screen.SETTINGS }
        }
        if (!game.hasServer()) Label("サーバーがまだ設定されていません（「設定」から）", 13.sp, color = Ui.Red)
    }
}

@Composable
private fun TestMenu(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("テスト部屋", 26.sp, color = Ui.Accent)
        PlainButton("1人で（通信なし）", 17.sp, enabled = !game.busy) { game.createRoom("test", true, true) }
        PlainButton("1人で（サーバーを使う）", 17.sp, enabled = !game.busy && game.hasServer()) { game.createRoom("test", true, false) }
        PlainButton("2人で（合言葉でつなぐ）", 17.sp, enabled = !game.busy && game.hasServer()) {
            game.meetMode = "test"
            game.screen = Screen.MEET
        }
        PlainButton("戻る", 15.sp) { game.screen = Screen.TITLE }
    }
}

@Composable
private fun MeetScreen(game: GameApp) {
    var pass by remember { mutableStateOf("") }
    val test = game.meetMode == "test"
    // 欄は上のほうに置く（キーボードが出ても隠れにくい）
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label(if (test) "テスト部屋（2人で）" else "合言葉", 26.sp, color = Ui.Accent)
        Label("2人で同じ合言葉を入れると、同じ部屋につながります", 15.sp, color = Ui.Dim)
        Box(
            Modifier.width(320.dp).background(Ui.Dark, Ui.Corner).border(2.dp, Ui.Accent, Ui.Corner)
                .padding(horizontal = 14.dp, vertical = 11.dp),
        ) {
            if (pass.isEmpty()) Label("合言葉を入れる", 18.sp, color = Ui.Dim)
            BasicTextField(
                value = pass,
                onValueChange = { pass = it.replace("\n", "") },
                modifier = Modifier.width(292.dp),
                textStyle = TextStyle(color = Ui.Text, fontSize = 18.sp, fontFamily = Ui.Hand),
                singleLine = true,
                cursorBrush = SolidColor(Ui.Accent),
            )
        }
        Label("前と同じ合言葉なら、続きから遊べます", 13.sp, color = Ui.Dim)
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("戻る", 16.sp) { game.screen = if (test) Screen.TEST_MENU else Screen.TITLE }
            PlainButton("つなぐ", 18.sp, enabled = pass.isNotBlank() && !game.busy, strong = true) { game.meetRoom(pass) }
        }
    }
}

@Composable
private fun LobbyScreen(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (ServerAddress.isPassphraseRoom(game.roomCode)) {
            Label("合言葉の部屋", 26.sp, color = Ui.Accent)
            Label(if (game.partnerJoined) "相棒が来ました" else "相棒が同じ合言葉を入れるのを待っています…", 18.sp)
        } else {
            Label("合言葉", 16.sp, color = Ui.Dim)
            Label(game.roomCode, 64.sp, color = Ui.Accent)
            Label(if (game.partnerJoined) "相棒が来ました" else "相棒を待っています…", 18.sp)
        }
        Spacer(Modifier.height(4.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("やめる", 16.sp) { game.leaveToTitle(true) }
            PlainButton("始める", 18.sp, strong = true) { game.beginPlay() }
        }
    }
}

@Composable
private fun SettingsScreen(game: GameApp) {
    val pasted = ServerAddress.parse(game.server) != null
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("設定", 26.sp, color = Ui.Accent)
        PlainButton(if (game.soundOn) "音：オン" else "音：オフ", 17.sp) { game.toggleSound() }
        val host = ServerAddress.host(game.server).take(34)
        val urlLabel = when {
            pasted -> "サーバー：$host（貼り付けた URL を使う）"
            game.hasServer() -> "サーバー：アプリに入っているものを使う（設定は要りません）"
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
