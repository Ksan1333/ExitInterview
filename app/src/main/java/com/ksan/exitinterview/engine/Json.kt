package com.ksan.exitinterview.engine

/** Minimal JSON reader/writer. Objects become LinkedHashMap, arrays ArrayList, integers Long. */
object Json {
    fun parse(s: String): Any? {
        val p = Parser(s)
        val v = p.value()
        p.ws()
        if (p.i != s.length) p.fail()
        return v
    }

    fun str(v: Any?): String {
        val sb = StringBuilder()
        write(sb, v)
        return sb.toString()
    }

    private fun write(sb: StringBuilder, v: Any?) {
        when (v) {
            null -> sb.append("null")
            is Boolean -> sb.append(if (v) "true" else "false")
            is Int, is Long, is Short, is Byte -> sb.append(v.toString())
            is Number -> {
                val d = v.toDouble()
                if (d == Math.floor(d) && Math.abs(d) < 1e15) sb.append(d.toLong().toString()) else sb.append(d.toString())
            }
            is String -> quote(sb, v)
            is Map<*, *> -> {
                sb.append('{')
                var first = true
                for ((k, x) in v) {
                    if (!first) sb.append(',')
                    first = false
                    quote(sb, k.toString())
                    sb.append(':')
                    write(sb, x)
                }
                sb.append('}')
            }
            is Iterable<*> -> {
                sb.append('[')
                var first = true
                for (x in v) {
                    if (!first) sb.append(',')
                    first = false
                    write(sb, x)
                }
                sb.append(']')
            }
            else -> quote(sb, v.toString())
        }
    }

    private fun quote(sb: StringBuilder, s: String) {
        sb.append('"')
        for (c in s) {
            when (c) {
                '"' -> sb.append("\\\"")
                '\\' -> sb.append("\\\\")
                '\n' -> sb.append("\\n")
                '\r' -> sb.append("\\r")
                '\t' -> sb.append("\\t")
                else -> if (c < ' ') sb.append(String.format("\\u%04x", c.code)) else sb.append(c)
            }
        }
        sb.append('"')
    }

    private class Parser(val s: String) {
        var i = 0

        fun fail(): Nothing = throw IllegalArgumentException("json error at $i")

        fun ws() {
            while (i < s.length) {
                val c = s[i]
                if (c == ' ' || c == '\n' || c == '\r' || c == '\t') i++ else break
            }
        }

        fun value(): Any? {
            ws()
            if (i >= s.length) fail()
            return when (s[i]) {
                '{' -> obj()
                '[' -> arr()
                '"' -> string()
                't' -> lit("true", true)
                'f' -> lit("false", false)
                'n' -> lit("null", null)
                else -> num()
            }
        }

        private fun lit(word: String, v: Any?): Any? {
            if (!s.startsWith(word, i)) fail()
            i += word.length
            return v
        }

        private fun obj(): Map<String, Any?> {
            val m = LinkedHashMap<String, Any?>()
            i++
            ws()
            if (i < s.length && s[i] == '}') {
                i++
                return m
            }
            while (true) {
                ws()
                if (i >= s.length || s[i] != '"') fail()
                val k = string()
                ws()
                if (i >= s.length || s[i] != ':') fail()
                i++
                m[k] = value()
                ws()
                if (i >= s.length) fail()
                if (s[i] == ',') {
                    i++
                    continue
                }
                if (s[i] == '}') {
                    i++
                    return m
                }
                fail()
            }
        }

        private fun arr(): List<Any?> {
            val a = ArrayList<Any?>()
            i++
            ws()
            if (i < s.length && s[i] == ']') {
                i++
                return a
            }
            while (true) {
                a.add(value())
                ws()
                if (i >= s.length) fail()
                if (s[i] == ',') {
                    i++
                    continue
                }
                if (s[i] == ']') {
                    i++
                    return a
                }
                fail()
            }
        }

        private fun string(): String {
            val sb = StringBuilder()
            i++
            while (true) {
                if (i >= s.length) fail()
                val c = s[i++]
                if (c == '"') return sb.toString()
                if (c != '\\') {
                    sb.append(c)
                    continue
                }
                if (i >= s.length) fail()
                when (val e = s[i++]) {
                    '"' -> sb.append('"')
                    '\\' -> sb.append('\\')
                    '/' -> sb.append('/')
                    'n' -> sb.append('\n')
                    'r' -> sb.append('\r')
                    't' -> sb.append('\t')
                    'b' -> sb.append('\b')
                    'f' -> sb.append('\u000C')
                    'u' -> {
                        if (i + 4 > s.length) fail()
                        sb.append(s.substring(i, i + 4).toInt(16).toChar())
                        i += 4
                    }
                    else -> {
                        sb.append(e)
                    }
                }
            }
        }

        private fun num(): Any {
            val st = i
            if (i < s.length && (s[i] == '-' || s[i] == '+')) i++
            var isInt = true
            while (i < s.length) {
                val c = s[i]
                if (c in '0'..'9') {
                    i++
                } else if (c == '.' || c == 'e' || c == 'E' || c == '-' || c == '+') {
                    isInt = false
                    i++
                } else {
                    break
                }
            }
            if (i == st) fail()
            val t = s.substring(st, i)
            return if (isInt) (t.toLongOrNull() ?: fail()) else (t.toDoubleOrNull() ?: fail())
        }
    }
}

@Suppress("UNCHECKED_CAST")
internal fun Any?.asMap(): Map<String, Any?> = this as? Map<String, Any?> ?: emptyMap()

@Suppress("UNCHECKED_CAST")
internal fun Any?.asList(): List<Any?> = this as? List<Any?> ?: emptyList()

internal fun Any?.asInt(d: Int = 0): Int = when (this) {
    is Number -> this.toInt()
    is String -> this.toIntOrNull() ?: d
    is Boolean -> if (this) 1 else 0
    else -> d
}

internal fun Any?.asF(d: Float = 0f): Float = (this as? Number)?.toFloat() ?: d

internal fun Any?.asStr(): String? = this as? String
