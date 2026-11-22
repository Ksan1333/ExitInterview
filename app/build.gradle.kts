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

// 版。GitHub の Release のタグ（v0.1.0）と同じにする。KsanHub はこれを比べて更新があるかを決める。上げるときは versionCode も 1 増やす
val appVersion = "0.1.0"

android {
    namespace = "com.ksan.exitinterview"
    compileSdk = 35

    defaultConfig {
        // ほかの自作アプリと同じ com.ksan1333.* にそろえる（KsanHub の一覧の package と同じ値）。コードの置き場所（namespace）は別
        applicationId = "com.ksan1333.exitinterview"
        minSdk = 33
        targetSdk = 35
        versionCode = 1
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
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
}

// release の APK を作るときは署名が要る（debug は署名の設定なしで動く）
gradle.taskGraph.whenReady {
    if (!hasReleaseSigning && allTasks.any { it.project == project && (it.name.startsWith("assembleRelease") || it.name.startsWith("packageRelease")) }) {
        throw GradleException("Release の署名が設定されていません。signing.properties をリポジトリの直下に置いてください（README の「配布用の APK」）")
    }
}

// 配布物: dist\ExitInterview-<版>.apk（GitHub の Release に添付するのはこれだけ）
tasks.register<Copy>("distApk") {
    dependsOn("assembleRelease")
    from(layout.buildDirectory.file("outputs/apk/release/app-release.apk"))
    into(rootProject.file("dist"))
    rename { "ExitInterview-$appVersion.apk" }
}
