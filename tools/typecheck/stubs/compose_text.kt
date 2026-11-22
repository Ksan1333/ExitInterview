@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.text

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.TextUnit

class TextStyle(
    val color: Color = Color.Black,
    val fontSize: TextUnit = TextUnit(14f),
    val fontFamily: FontFamily? = null,
    val textAlign: TextAlign = TextAlign.Start,
    val lineHeight: TextUnit = TextUnit(14f),
)
