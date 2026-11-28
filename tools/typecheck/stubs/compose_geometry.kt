package androidx.compose.ui.geometry

class Size(val width: Float, val height: Float)

class Offset(val x: Float, val y: Float) {
    operator fun minus(other: Offset): Offset = Offset(x - other.x, y - other.y)
    fun getDistance(): Float = kotlin.math.sqrt(x * x + y * y)
}
