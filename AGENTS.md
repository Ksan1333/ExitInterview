# AGENTS.md — Exit Interview

<!-- 共通ルール（消さない） -->
> **共通ルール：** 作業の前に、Ksan1333 の全プロジェクト共通のルール（非公開リポジトリ `Ksan1333/AgentRules` の `AGENTS.md`）を読み、それに従うこと。この PC では `%USERPROFILE%\Documents\Claude\AgentRules\AGENTS.md`、ない環境では `gh api repos/Ksan1333/AgentRules/contents/AGENTS.md -H "Accept: application/vnd.github.raw"` で読める。特に、GitHub Actions は使わない（ワークフローを作らない・動かさない。テストとビルドはこの PC で行う）。Release（`gh release create`）はユーザーが実行し、エージェントは実行しない。このファイルには、このプロジェクトだけの決まりを書く。

## このプロジェクトだけの決まり

- 持ち主が自分で遊ぶゲーム。`spoiler/` の中身、`[spoiler]` で始まるコミットの差分、`tools/verify.sh` が失敗したときの出力を、持ち主に見せない（返答・報告・コミットメッセージに書かない）。
- `app/src/main/assets/server.txt` は空のままにする（リポジトリが公開のため。サーバーの URL を書かない・コミットしない）。
- 配布用の APK には、サーバーのアドレス（鍵なし）をリポジトリ直下の `server-base.txt`（コミットしない。控えは `Documents\Claude\.exitinterview\server-base.txt`）から入れる。鍵は 2 人で決めた合言葉から作る（アプリの `ServerAddress.keyOf` と `server/set-passphrase.sh` は同じ作り方にそろえる）。合言葉そのものはエージェントが聞かない・扱わない。
- 配布用の APK の作り方は README の「配布用の APK」。署名の鍵は `Documents\Claude\.exitinterview\exitinterview-release.jks`（唯一の鍵。作り直さない・消さない・コミットしない）。同じフォルダーの `signing.properties`・`server-base.txt` と、`local.properties`（`sdk.dir=C:/Users/Ninji/AppData/Local/Android/Sdk` の 1 行）をリポジトリ直下に置いてから `.\gradlew.bat distApk`。
- コマンドラインのビルドは JDK 17〜21 で行う（`JAVA_HOME` を `%USERPROFILE%\.jdks\corretto-17.0.12` などにする）。Android Studio 付属の JBR は JDK 25 で、Gradle 8.10.2 が動かない（エラーは「What went wrong: 25.0.4」とだけ出る）。
