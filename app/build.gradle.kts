import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

// 配布用（Release）の署名は、リポジトリの直下に置く signing.properties（コミットしない）から読む。
// 鍵は 1 つだけで、作り直さない・消さない（作り直すと、入っている Exit Interview を更新できなくなる）。
// Android Studio の「実行」（debug）には要らない。
val signing = Properties().apply {
    val f = rootProject.file("signing.properties")
    if (f.isFile) f.inputStream().use(::load)
}
val hasReleaseSigning = listOf("storeFile", "storePassword", "keyAlias", "keyPassword").all { !signing.getProperty(it).isNullOrBlank() }

// サーバーのアドレス（鍵なし）。リポジトリの直下に置く server-base.txt（コミットしない）から読み、APK の assets/server_base.txt に入れる。
// 遊ぶ人は、2人で決めたサーバーの合言葉を入れるだけでよくなる（鍵は合言葉から作る。server/set-passphrase.sh）。
// リポジトリは公開なので、鍵（/k/ の後ろ）は書かない。書いてあればビルドを止める。
val serverBase = rootProject.file("server-base.txt").takeIf { it.isFile }?.readText()?.trim().orEmpty()
if (serverBase.contains("/k/") || serverBase.contains("#") || serverBase.contains("?")) {
    throw GradleException("server-base.txt には鍵を書かないでください（https://<ホスト>/ だけ）")
}
val serverBaseDir = layout.buildDirectory.dir("generated/serverBase").get().asFile
serverBaseDir.mkdirs()
File(serverBaseDir, "server_base.txt").writeText(serverBase)

// 版。GitHub の Release のタグ（v0.1.0）と同じにする。KsanHub はこれを比べて更新があるかを決める。上げるときは versionCode も 1 増やす
val appVersion = "0.1.2"

android {
    namespace = "com.ksan.exitinterview"
    compileSdk = 35

    defaultConfig {
        // ほかの自作アプリと同じ com.ksan1333.* にそろえる（KsanHub の一覧の package と同じ値）。コードの置き場所（namespace）は別
        applicationId = "com.ksan1333.exitinterview"
        minSdk = 26
        targetSdk = 35
        versionCode = 3
        versionName = appVersion
    }

    signingConfigs {
        if (hasReleaseSigning) {
            create("release") {
                storeFile = file(signing.getProperty("storeFile"))
                storePassword = signing.getProperty("storePassword")
                keyAlias = signing.getProperty("keyAlias")
                keyPassword = signing.getProperty("keyPassword")
            }
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            if (hasReleaseSigning) signingConfig = signingConfigs.getByName("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    sourceSets {
        getByName("main").assets.srcDir(serverBaseDir)
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.activity:activity-compose:1.9.3")
    // 全画面表示を Android 8〜10 でも行う（WindowCompat）
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
}

// release の APK を作るときは署名が要る（debug は署名の設定なしで動く）
gradle.taskGraph.whenReady {
    if (!hasReleaseSigning && allTasks.any { it.project == project && (it.name.startsWith("assembleRelease") || it.name.startsWith("packageRelease")) }) {
        throw GradleException("Release の署名が設定されていません。signing.properties をリポジトリの直下に置いてください（README の「配布用の APK」）")
    }
    if (serverBase.isEmpty() && allTasks.any { it.project == project && it.name == "distApk" }) {
        throw GradleException("サーバーのアドレスがありません。server-base.txt をリポジトリの直下に置いてください（README の「配布用の APK」）")
    }
}

// 配布物: dist\ExitInterview-<版>.apk（GitHub の Release に添付するのはこれだけ）
tasks.register<Copy>("distApk") {
    dependsOn("assembleRelease")
    from(layout.buildDirectory.file("outputs/apk/release/app-release.apk"))
    into(rootProject.file("dist"))
    rename { "ExitInterview-$appVersion.apk" }
}
