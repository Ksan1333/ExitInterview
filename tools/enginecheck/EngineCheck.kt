import com.ksan.exitinterview.engine.LocalTransport
import com.ksan.exitinterview.engine.Pack
import com.ksan.exitinterview.engine.RoomClient
import com.ksan.exitinterview.engine.Rules
import com.ksan.exitinterview.engine.ServerAddress
import com.ksan.exitinterview.engine.Session
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
    check(c("main2", "テスト合言葉") == "mfcf013badef451394b60719a" && c("test2", "テスト合言葉") == "m2aca8940373e6f058f37d8a8",
        "episode 2 has its own fixed room codes")
    check(listOf("main", "test", "main2", "test2").map { c(it, "テスト合言葉") }.toSet().size == 4,
        "the same passphrase meets in a different room in each episode and test room")

    // a tiny pack written here, for the parts of the engine that every episode shares
    fun packOf(json: String): Pack {
        val js = json.toByteArray(Charsets.UTF_8)
        val head = "EIP1".toByteArray(Charsets.US_ASCII) +
            byteArrayOf((js.size ushr 24).toByte(), (js.size ushr 16).toByte(), (js.size ushr 8).toByte(), js.size.toByte())
        return Pack.fromPlain(head + js)
    }
    val tiny = packOf(
        """{"v":1,"start":{"main":1},"stages":{"1":{"start":"a"}},"views":{"a":{"st":1,"bg":"a","name":"A","layers":[],"texts":[],""" +
            """"spots":[{"r":[0,0,100,100],"ops":[["msg","かぎがかかっている"]]}]}},""" +
            """"items":{"old":{"img":"it.old"},"new":{"img":"it.new","name":"メモ","desc":["裏に何か書いてある"],"big":"itz.new"}},""" +
            """"puzzles":[],"mazes":{},"init":{"f":{},"i":{}},"imgs":{},"meta":{"title":"第2話","tagline":"tag"}}""",
    )
    val start = Rules.initialState(tiny, "main")
    val out = Rules.tap(tiny, start, "a", 50f, 50f, null, 1000)
    check(out?.fx?.msg == "かぎがかかっている", "a spot can show a line on the tapping device")
    check(out != null && Session.diff(start, out.state).keys == setOf("f:t0"), "the line is not part of the shared state")
    val old = tiny.items["old"]!!
    val nw = tiny.items["new"]!!
    check(old.name == "" && old.desc.isEmpty() && old.big == null, "an item of an older pack has no name, text or large picture")
    check(nw.name == "メモ" && nw.desc == listOf("裏に何か書いてある") && nw.big == "itz.new", "an item can carry a name, a text and a large picture")
    check(tiny.title == "第2話" && tiny.tagline == "tag", "a pack can carry its episode title")

    // the room's clock: a phone whose clock is 100 seconds behind the server counts in the server's time
    val rc = RoomClient(LocalTransport { (System.currentTimeMillis() / 1000).toInt() + 100 }, "")
    val j = rc.create("pid", "main", start)
    val sess = Session(tiny, rc, j.code, j.slot, j.snap)
    check(sess.clockOffset in 99..101, "a session counts in the server's time (offset ${sess.clockOffset})")
    sess.poll(null)
    check(sess.clockOffset in 99..101, "the offset follows each reply")

    // one connection for many requests: a new TLS connection to the server costs about three requests' time
    val ports = java.util.Collections.synchronizedList(ArrayList<Int>())
    val srv = com.sun.net.httpserver.HttpServer.create(java.net.InetSocketAddress("127.0.0.1", 0), 0)
    srv.createContext("/") { ex ->
        ports.add(ex.remoteAddress.port)
        ex.requestBody.readBytes()
        val fail = ex.requestURI.path == "/fail"
        val reply = (if (fail) "no" else """{"ok":true}""").toByteArray()
        ex.sendResponseHeaders(if (fail) 500 else 200, reply.size.toLong())
        ex.responseBody.use { it.write(reply) }
    }
    srv.start()
    try {
        val base = "http://127.0.0.1:${srv.address.port}/"
        val http = com.ksan.exitinterview.engine.HttpTransport(base)
        val replies = (1..3).map { http.post("""{"op":"get"}""") }
        check(replies.all { it == """{"ok":true}""" }, "the reply is read whole")
        check(ports.size == 3 && ports.toSet().size == 1, "three requests go over one connection (ports $ports)")
        val failed = try {
            com.ksan.exitinterview.engine.HttpTransport(base + "fail").post("{}")
            false
        } catch (e: java.io.IOException) {
            true
        }
        check(failed && http.post("{}") == """{"ok":true}""", "a failed request is an error and the next one still works")
    } finally {
        srv.stop(0)
    }
    println(if (fails == 0) "ALL OK" else "$fails FAILED")
    exitProcess(if (fails == 0) 0 else 1)
}
