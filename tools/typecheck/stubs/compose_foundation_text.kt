@file:Suppress("UNUSED_PARAMETER", "unused")

package androidx.compose.foundation.text

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.ImeAction

class KeyboardOptions(val imeAction: ImeAction = ImeAction.Default)

interface KeyboardActionScope

class KeyboardActions(val onDone: (KeyboardActionScope.() -> Unit)? = null)

@Composable
fun BasicTextField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    textStyle: TextStyle = TextStyle(),
    keyboardOptions: KeyboardOptions = KeyboardOptions(),
    keyboardActions: KeyboardActions = KeyboardActions(),
    singleLine: Boolean = false,
    cursorBrush: androidx.compose.ui.graphics.Brush = androidx.compose.ui.graphics.SolidColor(androidx.compose.ui.graphics.Color.Black),
) {}

@Composable
fun BasicText(text: String, modifier: Modifier = Modifier, style: TextStyle = TextStyle()) {}
