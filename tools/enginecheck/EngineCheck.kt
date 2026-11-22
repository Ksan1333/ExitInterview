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
    // The same values as server/set-passphrase.sh (Python) and Node give; keep the two in step.
    val k = ServerAddress::keyOf
    check(k("テスト合言葉") == "3eb24f415a2976bbe1b55c234b0ec583", "the passphrase gives the same key as server/set-passphrase.sh")
    check(k("  ﾃｽﾄ合言葉　") == k("テスト合言葉"), "half-width kana and spaces around the passphrase do not matter")
    check(k("ＡＢＣ１２３") == "ac9409d69213deef95620c4d09ee139d" && k("ABC123") == k("ＡＢＣ１２３"), "full-width and half-width letters give the same key")
    check(k("") == null && k("   ") == null, "an empty passphrase gives no key")
    check(k("abc") != k("ABC"), "upper and lower case letters are different")
    println(if (fails == 0) "ALL OK" else "$fails FAILED")
    exitProcess(if (fails == 0) 0 else 1)
}
