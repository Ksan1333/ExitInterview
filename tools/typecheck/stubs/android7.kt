@file:Suppress("UNUSED_PARAMETER", "unused")

package android.view

class Window {
    var attributes: WindowManager.LayoutParams = WindowManager.LayoutParams()
    val insetsController: WindowInsetsController? = null
    fun addFlags(flags: Int) {}
}

interface WindowManager {
    class LayoutParams {
        var layoutInDisplayCutoutMode: Int = 0

        companion object {
            const val FLAG_KEEP_SCREEN_ON = 0x80
            const val LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES = 1
        }
    }
}

class WindowInsets {
    object Type {
        fun systemBars(): Int = 0
    }
}

interface WindowInsetsController {
    var systemBarsBehavior: Int
    fun hide(types: Int)

    companion object {
        const val BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE = 2
    }
}
