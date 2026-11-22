@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.foundation.text

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle

@Composable
fun BasicTextField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    textStyle: TextStyle = TextStyle(),
    singleLine: Boolean = false,
    cursorBrush: androidx.compose.ui.graphics.Brush = androidx.compose.ui.graphics.SolidColor(androidx.compose.ui.graphics.Color.Black),
) {}

@Composable
fun BasicText(text: String, modifier: Modifier = Modifier, style: TextStyle = TextStyle()) {}
