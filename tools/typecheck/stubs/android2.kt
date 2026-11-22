@file:Suppress("UNUSED_PARAMETER", "unused")

package android.content.res

import android.graphics.Typeface
import java.io.InputStream

class AssetManager {
    fun open(fileName: String): InputStream = throw java.io.IOException()
}

class Resources {
    fun getFont(id: Int): Typeface = Typeface()
}
