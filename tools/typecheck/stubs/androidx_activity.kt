@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.activity

import android.content.Context
import android.os.Bundle
import android.view.Window

open class ComponentActivity {
    val window: Window = Window()
    val applicationContext: Context get() = throw IllegalStateException()
    protected open fun onCreate(savedInstanceState: Bundle?) {}
    open fun onWindowFocusChanged(hasFocus: Boolean) {}
    protected open fun onResume() {}
    protected open fun onPause() {}
    protected open fun onDestroy() {}
}
