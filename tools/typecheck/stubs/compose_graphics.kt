@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.graphics

class Color(val value: Long) {
    companion object {
        val Black = Color(0xFF000000)
        val White = Color(0xFFFFFFFF)
    }
}

abstract class Brush

class SolidColor(val value: Color) : Brush()

interface ImageBitmap {
    val width: Int
    val height: Int
}

fun android.graphics.Bitmap.asImageBitmap(): ImageBitmap = object : ImageBitmap {
    override val width = 0
    override val height = 0
}

class Path {
    fun moveTo(x: Float, y: Float) {}
    fun lineTo(x: Float, y: Float) {}
    fun close() {}
}

interface Shape

val RectangleShape: Shape = object : Shape {}

interface Canvas

val Canvas.nativeCanvas: android.graphics.Canvas get() = android.graphics.Canvas()
