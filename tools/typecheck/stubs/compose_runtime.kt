@file:Suppress("UNUSED_PARAMETER", "unused", "NOTHING_TO_INLINE")

package androidx.compose.runtime

import kotlinx.coroutines.CoroutineScope
import kotlin.reflect.KProperty

@Target(AnnotationTarget.FUNCTION, AnnotationTarget.TYPE, AnnotationTarget.TYPE_PARAMETER, AnnotationTarget.PROPERTY_GETTER)
annotation class Composable

interface State<out T> {
    val value: T
}

interface MutableState<T> : State<T> {
    override var value: T
}

fun <T> mutableStateOf(value: T): MutableState<T> = object : MutableState<T> {
    override var value: T = value
}

inline operator fun <T> State<T>.getValue(thisObj: Any?, property: KProperty<*>): T = value

inline operator fun <T> MutableState<T>.setValue(thisObj: Any?, property: KProperty<*>, value: T) {
    this.value = value
}

@Composable
inline fun <T> remember(crossinline calculation: () -> T): T = calculation()

@Composable
inline fun <T> remember(key1: Any?, crossinline calculation: () -> T): T = calculation()

@Composable
fun LaunchedEffect(key1: Any?, block: suspend CoroutineScope.() -> Unit) {}
