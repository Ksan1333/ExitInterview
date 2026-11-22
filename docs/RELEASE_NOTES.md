# Exit Interview 0.1.1

Android 12 以前のスマホにも入れられるようにした版です。

- 0.1.0 は Android 13 以上専用だったため、Android 12 以前のスマホでは KsanHub から入れられませんでした。0.1.1 は Android 8.0 以上で入れられます。
- Android 8〜10 でも、ステータスバーとナビゲーションバーを隠した全画面で遊べるようにしました。
- ゲームの中身は 0.1.0 と同じです。

## Exit Interview について

- 2人用の脱出ゲーム（3ステージ、目安は 90〜120 分）。別々のスマホから同じ部屋に入り、通話しながら遊びます。
- 1台で操作を確かめられるテスト部屋つき。
- 遊ぶには部屋サーバーの URL が要ります（ゲームの「設定」→「クリップボードから貼り付け」）。
- Android 8.0 以上。

## 確かめたこと

- 持ち主の PC で `gradlew lintRelease distApk`（JDK 17）が通り、配布用の APK ができること（Android 8.0 で使えない API の呼び出しがないことを lint で確認）。
- APK が配布用の鍵で署名されていること（APK Signature Scheme v2、証明書の SHA-256 `4c0bc0e2e3bcc25ad59213d5b57d1b6c28cede824fd9f4a7975759b68e22f080`。0.1.0 と同じ鍵）。
- パッケージ名 `com.ksan1333.exitinterview`、版 0.1.1（versionCode 2）、minSdk 26。
- APK にサーバーの URL が入っていないこと（`assets/server.txt` は空）。

## 分かっている問題

- 実機では未確認です（インストール・起動・2台での通しプレイ）。
- `tools/verify.sh` は、ビルドした PC に Python がないため、この版では動かしていません（そのうちアプリの型検査 `tools/typecheck/run.sh` だけは単独で動かし、通りました）。

## 添付

| ファイル | SHA-256 |
| --- | --- |
| `ExitInterview-0.1.1.apk` | `b04132d02dc84b7b92dcadf487a5db80b1bcfebaf4f545f3803df8d8245c4b7f` |
