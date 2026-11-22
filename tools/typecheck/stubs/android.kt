// Minimal look-alikes of the Android classes the app touches, so that the app's own Kotlin can be
// type-checked on a machine without the Android SDK. Never shipped; signatures follow the real ones.
@file:Suppress("UNUSED_PARAMETER", "unused")

package android.content

import android.content.res.AssetManager
import android.content.res.Resources

abstract class Context {
    abstract val applicationContext: Context
    abstract val assets: AssetManager
    abstract val resources: Resources
    abstract fun getSharedPreferences(name: String, mode: Int): SharedPreferences
    abstract fun getSystemService(name: String): Any?

    companion object {
        const val MODE_PRIVATE = 0
        const val CLIPBOARD_SERVICE = "clipboard"
    }
}

interface SharedPreferences {
    fun getString(key: String, defValue: String?): String?
    fun getBoolean(key: String, defValue: Boolean): Boolean
    fun getInt(key: String, defValue: Int): Int
    fun edit(): Editor

    interface Editor {
        fun putString(key: String, value: String?): Editor
        fun putBoolean(key: String, value: Boolean): Editor
        fun putInt(key: String, value: Int): Editor
        fun remove(key: String): Editor
        fun apply()
    }
}

class ClipData {
    val itemCount: Int = 0
    fun getItemAt(index: Int): Item = Item()

    class Item {
        fun coerceToText(context: Context): CharSequence = ""
    }
}

class ClipboardManager {
    val primaryClip: ClipData? = null
}
