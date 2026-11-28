@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.foundation.gestures

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.input.pointer.AwaitPointerEventScope
import androidx.compose.ui.input.pointer.PointerInputChange
import androidx.compose.ui.input.pointer.PointerInputScope

suspend fun PointerInputScope.detectTapGestures(
    onDoubleTap: ((Offset) -> Unit)? = null,
    onLongPress: ((Offset) -> Unit)? = null,
    onPress: suspend (Offset) -> Unit = {},
    onTap: ((Offset) -> Unit)? = null,
) {}

suspend fun PointerInputScope.awaitEachGesture(block: suspend AwaitPointerEventScope.() -> Unit) {}

suspend fun AwaitPointerEventScope.awaitFirstDown(requireUnconsumed: Boolean = true): PointerInputChange =
    PointerInputChange(androidx.compose.ui.input.pointer.PointerId(0), Offset(0f, 0f), true)
