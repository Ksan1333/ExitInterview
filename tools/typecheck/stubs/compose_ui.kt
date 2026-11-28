@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui

interface Modifier {
    infix fun then(other: Modifier): Modifier = this

    companion object : Modifier
}

interface Alignment {
    interface Horizontal
    interface Vertical

    companion object {
        val TopStart: Alignment = object : Alignment {}
        val TopCenter: Alignment = object : Alignment {}
        val Center: Alignment = object : Alignment {}
        val BottomCenter: Alignment = object : Alignment {}
        val BottomEnd: Alignment = object : Alignment {}
        val Start: Horizontal = object : Horizontal {}
        val CenterHorizontally: Horizontal = object : Horizontal {}
        val Top: Vertical = object : Vertical {}
        val CenterVertically: Vertical = object : Vertical {}
    }
}
