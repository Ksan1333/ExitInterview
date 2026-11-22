@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.text.font

interface Font

class FontFamily

fun Font(resId: Int): Font = object : Font {}

fun FontFamily(vararg fonts: Font): FontFamily = FontFamily()
