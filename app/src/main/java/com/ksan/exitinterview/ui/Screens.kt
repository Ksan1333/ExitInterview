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
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ksan.exitinterview.app.GameApp
import com.ksan.exitinterview.app.Overlay
import com.ksan.exitinterview.app.Screen
import com.ksan.exitinterview.engine.Rules

@Composable
fun AppRoot(game: GameApp) {
    Box(Modifier.fillMaxSize().background(Color.Black), contentAlignment = Alignment.Center) {
        when (game.screen) {
            Screen.LOADING -> Label("よみこみ ちゅう…", 20.sp)
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
        Label("でられたら ごうかく", 15.sp, color = Ui.Dim)
        Spacer(Modifier.height(6.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("へやを つくる", 18.sp, enabled = !game.busy, strong = true) { game.createRoom("main", false, false) }
            PlainButton("へやに はいる", 18.sp, enabled = !game.busy) { game.screen = Screen.JOIN }
        }
        val saved = game.savedCode
        if (saved.isNotEmpty()) {
            PlainButton("つづきから（$saved）", 16.sp, enabled = !game.busy) { game.joinRoom(saved) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("テストべや", 15.sp, enabled = !game.busy) { game.screen = Screen.TEST_MENU }
            PlainButton("せってい", 15.sp) { game.screen = Screen.SETTINGS }
        }
        if (!game.hasServer()) Label("サーバーが まだ せってい されて いません（せってい から）", 13.sp, color = Ui.Red)
    }
}

@Composable
private fun TestMenu(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("テストべや", 26.sp, color = Ui.Accent)
        PlainButton("ひとりで（つうしん なし）", 17.sp, enabled = !game.busy) { game.createRoom("test", true, true) }
        PlainButton("ひとりで（サーバーを つかう）", 17.sp, enabled = !game.busy && game.hasServer()) { game.createRoom("test", true, false) }
        PlainButton("ふたりで", 17.sp, enabled = !game.busy && game.hasServer()) { game.createRoom("test", false, false) }
        PlainButton("もどる", 15.sp) { game.screen = Screen.TITLE }
    }
}

@Composable
private fun JoinScreen(game: GameApp) {
    var code by remember { mutableStateOf("") }
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Label("あいことば", 16.sp, color = Ui.Dim)
        Label(code.padEnd(4, '・'), 44.sp, color = Ui.Accent)
        for (row in listOf("12345", "67890")) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (d in row) {
                    PlainButton(d.toString(), 22.sp, Modifier.width(58.dp)) { if (code.length < 4) code += d }
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("もどる", 16.sp) { game.screen = Screen.TITLE }
            PlainButton("けす", 16.sp) { code = code.dropLast(1) }
            PlainButton("はいる", 16.sp, enabled = code.length == 4 && !game.busy, strong = true) { game.joinRoom(code) }
        }
    }
}

@Composable
private fun LobbyScreen(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Label("あいことば", 16.sp, color = Ui.Dim)
        Label(game.roomCode, 64.sp, color = Ui.Accent)
        Label(if (game.partnerJoined) "あいぼうが きました" else "あいぼうを まっています…", 18.sp)
        Spacer(Modifier.height(4.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("やめる", 16.sp) { game.leaveToTitle(true) }
            PlainButton("はじめる", 18.sp, strong = true) { game.beginPlay() }
        }
    }
}

@Composable
private fun SettingsScreen(game: GameApp) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Label("せってい", 26.sp, color = Ui.Accent)
        PlainButton(if (game.soundOn) "おと：オン" else "おと：オフ", 17.sp) { game.toggleSound() }
        val host = game.server.substringAfter("//").substringBefore("/").take(34)
        Label(if (game.hasServer()) "サーバー：$host" else "サーバー：みせってい", 14.sp, color = Ui.Dim)
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PlainButton("クリップボードから はりつけ", 15.sp) { game.pasteServer() }
            PlainButton("もとに もどす", 15.sp) { game.clearServer() }
        }
        PlainButton("もどる", 15.sp) { game.screen = Screen.TITLE }
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
        Label("かかった じかん：${sec / 60}ふん ${sec % 60}びょう", 16.sp)
        Label("ヒント：${game.state.f(Rules.N_HINT)}かい　スキップ：${game.state.f(Rules.N_SKIP)}かい", 16.sp)
        Spacer(Modifier.height(4.dp))
        PlainButton("タイトルへ", 16.sp) { game.leaveToTitle(true) }
    }
}
