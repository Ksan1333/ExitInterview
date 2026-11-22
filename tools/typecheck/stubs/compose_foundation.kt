@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.foundation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.unit.Dp

@Composable
fun Canvas(modifier: Modifier, onDraw: DrawScope.() -> Unit) {}

@Composable
fun Image(bitmap: ImageBitmap, contentDescription: String?, modifier: Modifier = Modifier, alpha: Float = 1f) {}

fun Modifier.background(color: Color, shape: Shape = RectangleShape): Modifier = this

fun Modifier.border(width: Dp, color: Color, shape: Shape = RectangleShape): Modifier = this

fun Modifier.clickable(enabled: Boolean = true, onClickLabel: String? = null, role: Any? = null, onClick: () -> Unit): Modifier = this

class ScrollState

@Composable
fun rememberScrollState(initial: Int = 0): ScrollState = ScrollState()

fun Modifier.verticalScroll(state: ScrollState, enabled: Boolean = true): Modifier = this
