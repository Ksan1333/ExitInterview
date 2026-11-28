@file:Suppress("UNUSED_PARAMETER", "unused")

package android.graphics

class Typeface

class Bitmap {
    fun prepareToDraw() {}
}

object BitmapFactory {
    fun decodeByteArray(data: ByteArray, offset: Int, length: Int): Bitmap? = null
}

object Color {
    fun parseColor(colorString: String): Int = 0
}

class Paint {
    enum class Align { LEFT, CENTER, RIGHT }

    var isAntiAlias: Boolean = false
    var textAlign: Align = Align.LEFT
    var typeface: Typeface? = null
    var textSize: Float = 0f
    var color: Int = 0
    fun ascent(): Float = 0f
    fun descent(): Float = 0f
}

class Canvas {
    fun drawText(text: String, x: Float, y: Float, paint: Paint) {}
}
