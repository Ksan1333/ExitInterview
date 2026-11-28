@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.ui.focus

import androidx.compose.ui.Modifier

class FocusRequester {
    fun requestFocus() {}
}

fun Modifier.focusRequester(focusRequester: FocusRequester): Modifier = this
