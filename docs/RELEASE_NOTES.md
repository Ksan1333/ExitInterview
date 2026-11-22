# Exit Interview 0.1.0

最初の版です。

- 2人用の脱出ゲーム（3ステージ、目安は 90〜120 分）。別々のスマホから同じ部屋に入り、通話しながら遊びます。
- 1台で操作を確かめられるテスト部屋つき。
- 遊ぶには部屋サーバーの URL が要ります（ゲームの「設定」→「クリップボードから貼り付け」）。
- Android 13 以上。

## 確かめたこと

- 持ち主の PC で `gradlew distApk`（JDK 17）が通り、配布用の APK ができること。
- APK が配布用の鍵で署名されていること（APK Signature Scheme v2、証明書の SHA-256 `4c0bc0e2e3bcc25ad59213d5b57d1b6c28cede824fd9f4a7975759b68e22f080`）。
- パッケージ名 `com.ksan1333.exitinterview`、版 0.1.0（versionCode 1）。
- APK にサーバーの URL が入っていないこと（`assets/server.txt` は空）。

## 分かっている問題

- 実機では未確認です（インストール・起動・2台での通しプレイ）。
- `tools/verify.sh` は、ビルドした PC に Python がないため、この版では動かしていません。

## 添付

| ファイル | SHA-256 |
| --- | --- |
| `ExitInterview-0.1.0.apk` | `9536e1b31f8f5b0d87c80f6d5998ad7f94ad110dd429fc73a5fdb42c01128b4d` |
