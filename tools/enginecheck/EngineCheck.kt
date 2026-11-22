import com.ksan.exitinterview.engine.ServerAddress
import kotlin.system.exitProcess

/** Checks of engine parts that have nothing to do with the stages (so this file is free of spoilers). */
fun main() {
    var fails = 0
    fun check(ok: Boolean, what: String) {
        println((if (ok) "ok    " else "FAIL  ") + what)
        if (!ok) fails++
    }
    val p = ServerAddress::parse
    val host = "https://abc123.lambda-url.ap-southeast-2.on.aws"
    check(p("$host/k/0123abcdef") == Pair("$host/", "0123abcdef"), "the URL a deploy prints gives the address and the key")
    check(p("  $host/k/0123abcdef/\n") == Pair("$host/", "0123abcdef"), "spaces around it and a closing slash are fine")
    check(p("$host/#0123abcdef") == Pair("$host/", "0123abcdef"), "the older form with # still works")
    check(p("http://192.168.0.5:8080/#") == Pair("http://192.168.0.5:8080/", ""), "a server on your own computer needs no key")
    check(p("http://192.168.0.5:8080/k/abc") == Pair("http://192.168.0.5:8080/", "abc"), "a port is kept")
    check(p("https://sub.site.example/k/a_b-C9") == Pair("https://sub.site.example/", "a_b-C9"), "a host with an s in it is read whole")
    check(p("$host/") == null && p(host) == null && p("$host/k/") == null, "an address without a key is refused")
    check(p("$host/k/abc/build.json") == null && p("$host/x/k/abc") == null && p("$host/k/a b") == null, "other paths are refused")
    check(p("") == null && p("abc") == null && p("ftp://x/k/abc") == null && p("https:///k/abc") == null && p("https://#k") == null, "text that is not a server is refused")
    check(ServerAddress.host("$host/k/0123abcdef") == "abc123.lambda-url.ap-southeast-2.on.aws" && ServerAddress.host("nonsense") == "", "the host is shown without the key")
    val b = ServerAddress::base
    check(b("$host/") == "$host/" && b(host) == "$host/" && b("  $host\n") == "$host/", "the built-in address is read with or without a closing slash")
    check(b("http://192.168.0.5:8080") == "http://192.168.0.5:8080/", "a built-in address keeps its port")
    check(b("") == null && b("abc") == null && b("https://") == null && b("$host/#k") == null && b("$host/?k=1") == null, "an empty or odd built-in address is refused")
    // The room code two players meet in (the same values Node gives). Changing it would part players who already play.
    val c = ServerAddress::roomCodeOf
    check(c("main", "テスト合言葉") == "m106d8902ccb82f09b26b9f1c", "the passphrase gives a fixed room code")
    check(c("main", "  ﾃｽﾄ合言葉　") == c("main", "テスト合言葉"), "half-width kana and spaces around the passphrase do not matter")
    check(c("main", "ＡＢＣ１２３") == "m07183eef3cb60ff65e7426f3" && c("main", "ABC123") == c("main", "ＡＢＣ１２３"), "full-width and half-width letters give the same room")
    check(c("test", "テスト合言葉") == "m8ccab5c1b6f36b9b6b162362", "a test room never meets a real one with the same passphrase")
    check(c("main", "") == null && c("main", "   ") == null, "an empty passphrase gives no room")
    check(c("main", "abc") != c("main", "ABC"), "upper and lower case letters are different")
    check(c("main", "x")!!.length == 25 && ServerAddress.isPassphraseRoom(c("main", "x")!!) && !ServerAddress.isPassphraseRoom("0427"),
        "a passphrase room code is m and 24 characters, unlike a numbered room")
    println(if (fails == 0) "ALL OK" else "$fails FAILED")
    exitProcess(if (fails == 0) 0 else 1)
}
