@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.platform

import androidx.compose.ui.unit.Density

class CompositionLocal<T> {
    val current: T get() = throw IllegalStateException()
}

val LocalDensity = CompositionLocal<Density>()
