@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.graphics.drawscope

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Canvas
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize

sealed class DrawStyle

object Fill : DrawStyle()

class Stroke(val width: Float = 0f) : DrawStyle()

interface DrawContext {
    val canvas: Canvas
}

interface DrawScope {
    val size: Size
    val center: Offset
    val drawContext: DrawContext

    fun drawImage(
        image: ImageBitmap,
        srcOffset: IntOffset = IntOffset(0, 0),
        srcSize: IntSize = IntSize(image.width, image.height),
        dstOffset: IntOffset = IntOffset(0, 0),
        dstSize: IntSize = srcSize,
        alpha: Float = 1f,
    )

    fun drawOval(color: Color, topLeft: Offset = Offset(0f, 0f), size: Size = this.size, alpha: Float = 1f, style: DrawStyle = Fill)

    fun drawCircle(color: Color, radius: Float = 1f, center: Offset = this.center, alpha: Float = 1f, style: DrawStyle = Fill)

    fun drawPath(path: Path, color: Color, alpha: Float = 1f, style: DrawStyle = Fill)
}
