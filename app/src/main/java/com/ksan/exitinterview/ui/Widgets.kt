package com.ksan.exitinterview.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import com.ksan.exitinterview.R

object Ui {
    val Ink = Color(0xFF101316)
    val Dark = Color(0xFF0F1719)
    val Panel = Color(0xEE0F1719)
    val Scrim = Color(0xB3000000)
    val Line = Color(0xFF6D7B7D)
    val Text = Color(0xFFE9E4D2)
    val Dim = Color(0xFF8D9796)
    val Accent = Color(0xFFF0D98A)
    val Red = Color(0xFFD0503F)
    val Hand = FontFamily(Font(R.font.yomogi_regular))
    val Corner = RoundedCornerShape(6.dp)
}

@Composable
fun Label(
    text: String,
    size: TextUnit,
    modifier: Modifier = Modifier,
    color: Color = Ui.Text,
    align: TextAlign = TextAlign.Start,
) {
    BasicText(
        text = text,
        modifier = modifier,
        style = TextStyle(color = color, fontSize = size, fontFamily = Ui.Hand, textAlign = align, lineHeight = size * 1.45f),
    )
}

@Composable
fun PlainButton(
    text: String,
    size: TextUnit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    strong: Boolean = false,
    onClick: () -> Unit,
) {
    Box(
        modifier = modifier
            .background(if (enabled) Ui.Dark else Color(0xFF1B2224), Ui.Corner)
            .border(2.dp, if (strong && enabled) Ui.Accent else Ui.Line, Ui.Corner)
            .clickable(enabled = enabled, onClick = onClick)
            .padding(horizontal = 18.dp, vertical = 9.dp),
        contentAlignment = Alignment.Center,
    ) {
        Label(text, size, color = if (enabled) Ui.Text else Ui.Dim, align = TextAlign.Center)
    }
}
