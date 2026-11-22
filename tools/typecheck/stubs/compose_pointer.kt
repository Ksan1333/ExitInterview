@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.input.pointer

import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.IntSize

interface PointerInputScope {
    val size: IntSize
}

fun Modifier.pointerInput(key1: Any?, block: suspend PointerInputScope.() -> Unit): Modifier = this
