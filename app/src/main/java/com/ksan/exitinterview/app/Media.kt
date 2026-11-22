package com.ksan.exitinterview.app

import android.content.Context
import android.graphics.BitmapFactory
import android.media.AudioAttributes
import android.media.SoundPool
import android.util.LruCache
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import com.ksan.exitinterview.R
import com.ksan.exitinterview.engine.Pack

/** Decodes pictures from the stage pack when they are first drawn and keeps the recent ones. */
class Images {
    private val cache = object : LruCache<String, ImageBitmap>(120 * 1024 * 1024) {
        override fun sizeOf(key: String, value: ImageBitmap): Int = value.width * value.height * 4
    }

    fun get(pack: Pack, id: String): ImageBitmap? {
        cache.get(id)?.let { return it }
        val range = pack.imgRange(id) ?: return null
        val bmp = BitmapFactory.decodeByteArray(pack.imgData(), range[0], range[1]) ?: return null
        val img = bmp.asImageBitmap()
        cache.put(id, img)
        return img
    }
}

/** Short sound effects. */
class Sfx(ctx: Context) {
    var enabled = true

    private val pool: SoundPool = SoundPool.Builder()
        .setMaxStreams(4)
        .setAudioAttributes(
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build(),
        )
        .build()

    private val ids: Map<String, Int> = mapOf(
        "tick" to R.raw.sfx_tick,
        "ok" to R.raw.sfx_ok,
        "buzz" to R.raw.sfx_buzz,
        "get" to R.raw.sfx_get,
        "door" to R.raw.sfx_door,
        "move" to R.raw.sfx_move,
        "coin" to R.raw.sfx_coin,
        "water" to R.raw.sfx_water,
        "meow" to R.raw.sfx_meow,
        "lever" to R.raw.sfx_lever,
        "plop" to R.raw.sfx_plop,
        "boing" to R.raw.sfx_boing,
        "launch" to R.raw.sfx_launch,
        "pon" to R.raw.sfx_pon,
    ).mapValues { pool.load(ctx, it.value, 1) }

    fun play(name: String) {
        if (!enabled) return
        val id = ids[name] ?: return
        pool.play(id, 1f, 1f, 1, 0, 1f)
    }

    fun release() {
        pool.release()
    }
}
