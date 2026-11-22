@file:Suppress("UNUSED_PARAMETER", "unused")

package android.util

open class LruCache<K, V>(maxSize: Int) {
    fun get(key: K): V? = null
    fun put(key: K, value: V): V? = null
    protected open fun sizeOf(key: K, value: V): Int = 1
}
