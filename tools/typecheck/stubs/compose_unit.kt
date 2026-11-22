@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.unit

class Dp(val value: Float) : Comparable<Dp> {
    operator fun plus(other: Dp): Dp = Dp(value + other.value)
    operator fun minus(other: Dp): Dp = Dp(value - other.value)
    operator fun times(other: Float): Dp = Dp(value * other)
    operator fun times(other: Int): Dp = Dp(value * other)
    operator fun div(other: Float): Dp = Dp(value / other)
    operator fun div(other: Int): Dp = Dp(value / other)
    operator fun div(other: Dp): Float = value / other.value
    override fun compareTo(other: Dp): Int = value.compareTo(other.value)
}

val Int.dp: Dp get() = Dp(toFloat())
val Float.dp: Dp get() = Dp(this)
val Double.dp: Dp get() = Dp(toFloat())

class TextUnit(val value: Float) {
    operator fun times(other: Float): TextUnit = TextUnit(value * other)
    operator fun times(other: Int): TextUnit = TextUnit(value * other)
    operator fun div(other: Float): TextUnit = TextUnit(value / other)
}

val Int.sp: TextUnit get() = TextUnit(toFloat())
val Float.sp: TextUnit get() = TextUnit(this)
val Double.sp: TextUnit get() = TextUnit(toFloat())

interface Density {
    fun Dp.toSp(): TextUnit
    fun Dp.toPx(): Float
}

class IntOffset(val x: Int, val y: Int)

class IntSize(val width: Int, val height: Int)
