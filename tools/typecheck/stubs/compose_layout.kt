@file:Suppress("UNUSED_PARAMETER", "unused", "NOTHING_TO_INLINE")

package androidx.compose.foundation.layout

import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

interface BoxScope {
    fun Modifier.align(alignment: Alignment): Modifier
}

interface BoxWithConstraintsScope : BoxScope {
    val maxWidth: Dp
    val maxHeight: Dp
}

interface ColumnScope {
    fun Modifier.weight(weight: Float, fill: Boolean = true): Modifier
    fun Modifier.align(alignment: Alignment.Horizontal): Modifier
}

interface RowScope {
    fun Modifier.weight(weight: Float, fill: Boolean = true): Modifier
    fun Modifier.align(alignment: Alignment.Vertical): Modifier
}

object Arrangement {
    interface Horizontal
    interface Vertical
    interface HorizontalOrVertical : Horizontal, Vertical

    val Start: Horizontal = object : Horizontal {}
    val Top: Vertical = object : Vertical {}
    fun spacedBy(space: Dp): HorizontalOrVertical = object : HorizontalOrVertical {}
}

@Composable
inline fun Box(
    modifier: Modifier = Modifier,
    contentAlignment: Alignment = Alignment.TopStart,
    propagateMinConstraints: Boolean = false,
    content: @Composable BoxScope.() -> Unit,
) {}

@Composable
fun BoxWithConstraints(
    modifier: Modifier = Modifier,
    contentAlignment: Alignment = Alignment.TopStart,
    propagateMinConstraints: Boolean = false,
    content: @Composable BoxWithConstraintsScope.() -> Unit,
) {}

@Composable
inline fun Column(
    modifier: Modifier = Modifier,
    verticalArrangement: Arrangement.Vertical = Arrangement.Top,
    horizontalAlignment: Alignment.Horizontal = Alignment.Start,
    content: @Composable ColumnScope.() -> Unit,
) {}

@Composable
inline fun Row(
    modifier: Modifier = Modifier,
    horizontalArrangement: Arrangement.Horizontal = Arrangement.Start,
    verticalAlignment: Alignment.Vertical = Alignment.Top,
    content: @Composable RowScope.() -> Unit,
) {}

@Composable
fun Spacer(modifier: Modifier) {}

fun Modifier.fillMaxSize(fraction: Float = 1f): Modifier = this
fun Modifier.fillMaxWidth(fraction: Float = 1f): Modifier = this
fun Modifier.fillMaxHeight(fraction: Float = 1f): Modifier = this
fun Modifier.offset(x: Dp = 0.dp, y: Dp = 0.dp): Modifier = this
fun Modifier.padding(start: Dp = 0.dp, top: Dp = 0.dp, end: Dp = 0.dp, bottom: Dp = 0.dp): Modifier = this
fun Modifier.padding(horizontal: Dp = 0.dp, vertical: Dp = 0.dp): Modifier = this
fun Modifier.padding(all: Dp): Modifier = this
fun Modifier.size(size: Dp): Modifier = this
fun Modifier.size(width: Dp, height: Dp): Modifier = this
fun Modifier.width(width: Dp): Modifier = this
fun Modifier.height(height: Dp): Modifier = this
