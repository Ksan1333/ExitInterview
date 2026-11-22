# Exit Interview 0.1.2

サーバーの URL を貼り付けなくても遊べるようにした版です。

- サーバーのアドレスを APK に入れました。2人で決めた「サーバーの合言葉」を、「設定」で一度入れるだけで通信できます。
- 合言葉は、持ち主が `server/set-passphrase.sh`（CloudShell に貼り付け）でサーバーに設定します。サーバーの URL と部屋のデータは変わりません。
- URL の貼り付けも予備として使えます（貼り付けた URL は合言葉より優先します）。
- ゲームの中身は 0.1.1 と同じです。

## Exit Interview について

- 2人用の脱出ゲーム（3ステージ、目安は 90〜120 分）。別々のスマホから同じ部屋に入り、通話しながら遊びます。
- 1台で操作を確かめられるテスト部屋つき。
- Android 8.0 以上。

## 確かめたこと

- 持ち主の PC で `gradlew lintRelease distApk`（JDK 17）が通り、配布用の APK ができること（Android 8.0 で使えない API の呼び出しなし）。
- APK が配布用の鍵で署名されていること（APK Signature Scheme v2、証明書の SHA-256 `4c0bc0e2e3bcc25ad59213d5b57d1b6c28cede824fd9f4a7975759b68e22f080`。0.1.0 と同じ鍵）。
- パッケージ名 `com.ksan1333.exitinterview`、版 0.1.2（versionCode 3）、minSdk 26。
- APK の `assets/server_base.txt` にサーバーのアドレスだけが入り、鍵が入っていないこと。`assets/server.txt` は空。
- `tools/enginecheck`：合言葉から作る鍵が、決まった入力に対して決まった値になること（全角・半角と前後の空白は同じに扱う。Node で計算した値と一致）、APK のアドレスの読み方。
- `tools/typecheck/run.sh`（アプリの型検査）が通ること。
- タイトルと設定の画面を Robolectric で描き、合言葉の欄・表示の切り替わり・知らせを目で確かめたこと。

## 分かっている問題

- 実機では未確認です（キーボードでの合言葉の入力・2台での通信・通しプレイ）。
- `server/set-passphrase.sh` は、本物の AWS ではまだ動かしていません。Python の側で作る鍵がアプリと同じになることも、この PC に Python がないため確かめていません（同じ作り方の Node とは一致）。
- `tools/verify.sh` 全体は、ビルドした PC に Python がないため動かしていません。

## 添付

| ファイル | SHA-256 |
| --- | --- |
| `ExitInterview-0.1.2.apk` | `f4f4078ccca08f773af3ef0dfff233fb1f566f3be2802628024d240f99768ef4` |
