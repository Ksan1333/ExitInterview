@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.input.pointer

import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.platform.ViewConfiguration
import androidx.compose.ui.unit.IntSize

interface PointerInputScope {
    val size: IntSize
    val viewConfiguration: ViewConfiguration
}

interface AwaitPointerEventScope {
    val size: IntSize
    val viewConfiguration: ViewConfiguration
    suspend fun awaitPointerEvent(): PointerEvent
}

class PointerEvent(val changes: List<PointerInputChange>)

class PointerId(val value: Long)

class PointerInputChange(val id: PointerId, val position: Offset, val pressed: Boolean)

fun Modifier.pointerInput(key1: Any?, block: suspend PointerInputScope.() -> Unit): Modifier = this
