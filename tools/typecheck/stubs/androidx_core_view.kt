@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.core.view

import android.view.View
import android.view.Window

object WindowCompat {
    fun getInsetsController(window: Window, view: View): WindowInsetsControllerCompat = WindowInsetsControllerCompat()
}

class WindowInsetsCompat {
    object Type {
        fun systemBars(): Int = 0
    }
}

class WindowInsetsControllerCompat {
    var systemBarsBehavior: Int = 0
    fun hide(types: Int) {}

    companion object {
        const val BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE = 2
    }
}
