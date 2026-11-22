# Exit Interview

通話しながら遊ぶ、2人専用の脱出ゲーム（Android）。一般公開はしません。

## 開いてはいけない場所

| 場所 | 中身 | けいさんは |
| --- | --- | --- |
| `app/` | アプリ本体（画面、通信、音）。謎の内容は入っていない | 開いてよい |
| `server/` | 部屋サーバー（AWS用と手元用） | 開いてよい |
| `tools/` | 検証スクリプト、効果音とロゴの生成 | 開いてよい |
| `spoiler/` | ステージ定義、絵の生成、答え入りの検証 | **開かない** |
| `app/src/main/assets/stage.pack` | 暗号化したステージ一式 | 開いても読めない |

- `[spoiler]` で始まるコミットは、差分を開かないでください。
- `tools/verify.sh` が失敗したときの出力には、謎の手がかりが混じることがあります。読まずにそのまま Claude に貼ってください。

## 作るもの

| 部分 | 技術 |
| --- | --- |
| アプリ | Kotlin 2.0.21、Jetpack Compose、minSdk 26（Android 8.0）、横画面 |
| サーバー | AWS Lambda（関数URL）＋ DynamoDB、ap-southeast-2 |
| 同期 | 1秒ごとの問い合わせ。操作は手元ですぐ反映し、あとからサーバーへ送る |

## ビルド（Android Studio）

1. このリポジトリを Android Studio で開く。
2. Gradle の同期が終わったら、`app` を実機で実行する（debug 版。署名の設定は要らない）。
3. 友人に渡す・KsanHub から入れるのは、下の「配布用の APK」。同じ APK を2人で使う。

- Gradle 8.10.2、Android Gradle Plugin 8.7.3、compileSdk 35 を使います。
- Gradle JDK は 17〜21 を選んでください（Settings → Build Tools → Gradle → Gradle JDK）。
- GitHub Actions は使いません。
- パッケージ名（applicationId）は `com.ksan1333.exitinterview` です。
- debug 版と配布用の版は署名が違います。同じ端末で入れ替えるときは、前のものを消してから入れます。

### 配布用の APK（KsanHub から入れる版）

KsanHub の「Exit Interview」は、このリポジトリの最新の Release に付けた `ExitInterview-<版>.apk` を入れます。Release を作るまでは、KsanHub には「リリース待ち」と出ます。

1. 初回だけ、署名の鍵を作る。鍵は 1 つだけで、作り直さない・消さない・コミットしない（作り直すと、入っている Exit Interview を更新できなくなる）。

   ```powershell
   mkdir "$env:USERPROFILE\Documents\Claude\.exitinterview"
   keytool -genkeypair -v -keystore "$env:USERPROFILE\Documents\Claude\.exitinterview\exitinterview-release.jks" -alias exitinterview -keyalg RSA -keysize 2048 -validity 10000
   ```

   （`keytool` は Android Studio の `jbr\bin` にあります。）

2. リポジトリの直下に `signing.properties` を置く（`.gitignore` 済み）。パスの区切りは `/` で書く。

   ```properties
   storeFile=C:/Users/<ユーザー名>/Documents/Claude/.exitinterview/exitinterview-release.jks
   storePassword=<鍵を作るときに決めたパスワード>
   keyAlias=exitinterview
   keyPassword=<同じパスワード>
   ```

3. リポジトリの直下に `server-base.txt` を置く（`.gitignore` 済み）。中身はサーバーのアドレスの 1 行だけで、鍵（`/k/` の後ろ）は書かない（書いてあるとビルドが止まる）。APK に入り、遊ぶ人はサーバーの設定をしなくてよくなる。

   ```
   https://<関数URLのホスト>.lambda-url.ap-southeast-2.on.aws/
   ```

4. APK を作る。`dist\ExitInterview-<版>.apk` ができる（`server-base.txt` がないと止まる）。

   ```powershell
   .\gradlew.bat distApk
   ```

5. 持ち主が Release を作る（タグは `v<版>`。添付は APK だけ）。

   ```powershell
   gh release create v0.1.0 dist\ExitInterview-0.1.0.apk --repo Ksan1333/ExitInterview --target main --title "Exit Interview 0.1.0" --notes-file docs\RELEASE_NOTES.md
   ```

版を上げるときは、`app/build.gradle.kts` の `appVersion` と `versionCode`、[`docs/RELEASE_NOTES.md`](docs/RELEASE_NOTES.md) を書き換えます。KsanHub は Release のタグとアプリの版を比べて、更新があるかを決めます。

### ロゴ

ランチャーのアイコンと KsanHub の一覧のアイコンは、[`tools/make_icon.py`](tools/make_icon.py) が描きます（半開きのドア。ステージの絵と同じ描き方）。

```
python3 tools/make_icon.py --ksanhub <scoop-bucket の icons フォルダ>
```

## サーバーを置く

配置には [`server/deploy.sh`](server/deploy.sh) を使います。何度実行しても同じ結果になります（2回目からは関数の中身だけ入れ替えます）。

| 置き方 | 初めての配置 | 2回目から | 配置した版の記録 |
| --- | --- | --- | --- |
| KsanHub の「AWS に配置」（PC・スマホ） | できない | できる | 残る（KsanHub に「配置済み・最新」と出る） |
| KsanHub の「CloudShell で配置」 | できる | できる | 残る |
| CloudShell に `server/deploy.sh` の中身を貼り付ける | できる | できる | 残らない（KsanHub では「配置の版不明」） |

初めての配置を KsanHub の「AWS に配置」でできないのは、KsanHub の配置用の鍵（PC の `ksanhub-pc-deploy`、スマホの CodeBuild のロール）が、この関数用の IAM ロール `exit-interview-lambda` を作れないためです。関数ができたあとは IAM に触らずに中身を入れ替えるので、同じ鍵で配置できます。

### 手順

1. 初回だけ：KsanHub の「Exit Interview（部屋サーバー）」で「CloudShell で配置」を押し、コピーされたコマンドを CloudShell に貼り付ける。
2. 最後に出る `https://…on.aws/k/…` の1行が、サーバーの URL。そのアドレスの部分（`/k/` の前まで）を `server-base.txt` に書いて APK を作る。
3. 2回目から（`server` フォルダを直したあと）：KsanHub の「AWS に配置」を押す。URL は変わらないので、ゲーム側は何もしなくてよい。

- KsanHub の「AWS に配置」で置くと、サーバーの URL が KsanHub に登録されます（スクリプトが最後に出す `KSANHUB_SITE_URL=<URL>` の行）。カードの「URL」で見られます。初回を CloudShell で行ったときは、次の「AWS に配置」で登録されます。
- 配置が最新かどうかは、`server` フォルダのハッシュで比べます。配置した版は `<URL>/build.json`（`tree` と `deployedAt`）で返します。
- URL の `/k/` の後ろは鍵です（0.1.3 からアプリは使いませんが、前の版で URL を貼った人のために残っています）。公開の場所（このリポジトリを含む）に書かないでください。配置のログ（KsanHub の画面と、スマホから配置したときは AWS の CloudWatch Logs）には出ます。
- Windows（Git for Windows の bash）でも動きます。zip コマンドがなければ Node.js で、それもなければ Python でコードをまとめます。

KsanHub の一覧（`Ksan1333/scoop-bucket` の `catalog.json`）では、サーバーが `exitinterview-server`（配置スクリプトは `server/deploy.sh`、判定に使うフォルダは `server`）、ゲーム本体が `exitinterview`（この Release の APK を入れる）です。

### 合言葉でつなぐ（0.1.3 から）

配布用の APK にはサーバーのアドレス（鍵なし）が入っています。遊ぶ人の設定は要りません。「遊ぶ」で2人が同じ合言葉を入れると、同じ部屋につながります。

- 先に入れた人が部屋を作って待ち、あとから入れた人がそこに入ります。前と同じ合言葉なら続きから遊べます（部屋は 30 日で消えます）。3人目は入れません。
- アプリは合言葉をハッシュにした部屋の番号（`m` と 24 文字。`ServerAddress.roomCodeOf`）だけを送ります。合言葉そのものはサーバーに残りません。作り方を変えると、遊んでいる途中の2人が別の部屋に分かれるので変えないでください（`tools/enginecheck` が決まった値になることを確かめます）。
- 全角と半角、前後の空白は区別しません。大文字と小文字は区別します。テスト部屋の合言葉は、本番の部屋とは別の部屋になります。
- サーバーは鍵のない要求も受け付けます（鍵が付いていて違うときだけ断ります）。APK を持っている人なら誰でも部屋を作れ、合言葉を当てられるとその部屋に入られることがあります。長めの合言葉にしてください（謎の中身はサーバーにありません）。
- サーバーの処理は `server/lambda_function.py` の `meet`。2人が同時に入れても、作れる部屋は 1 つです。

### サーバーの URL をゲームに入れる（予備）

- アプリで入れる：URL をコピー → アプリの「設定」→「クリップボードから貼り付け」。貼り付けた URL は、アプリに入っているサーバーより優先します（「元に戻す」で戻る）。
- APK に入れる：`app/src/main/assets/server.txt` にその1行を書いてビルドする。ただしこのリポジトリは公開なので、書いた `server.txt` はコミットしないでください。

消すときは [`server/remove.sh`](server/remove.sh) を CloudShell に貼り付けます。

### 手元のPCで動かす（予備）

```
python3 server/local_server.py 8080
```

同じネットワークの端末から `http://<PCのアドレス>:8080/#` をサーバーの URL として入れます（`#` の後ろは空でよい）。

## 遊び方

| ボタン | すること |
| --- | --- |
| 遊ぶ | 2人で決めた合言葉を入れて「つなぐ」。同じ合言葉を入れた2人が同じ部屋に入る |
| 続きから | 前の部屋に戻る（同じ合言葉を入れても戻れる） |
| テスト部屋 | 動作確認用の小さな部屋。「1人で」は1台で2人分を切り替えて操作する。「2人で」も合言葉でつなぐ |

- 見えるものと持ち物は2人で共通です。
- 左上の目のボタンで、相手が見ている場所へ移動します。
- メニューからヒント（3段階 → 答え → スキップ）を開けます。開くと2人の画面に出ます。

## 検証

Android SDK がなくても動く検証をまとめて実行できます。

```
tools/verify.sh
```

| 検証 | 内容 |
| --- | --- |
| ステージ | 模範解答の通し、全13問のスキップ、行き止まりの探索、間違えたときの動き |
| 同期 | 2人が同時に操作しても取りこぼさないこと（メモリ内と HTTP 経由） |
| サーバー | メモリ版と DynamoDB のモックに対する動作。`build.json` の返し方 |
| 配置 | `server/deploy.sh` と `server/remove.sh` を、AWS のモック（moto）に対して最初から最後まで実行する（クローンから・貼り付け・Windows と同じ条件・KsanHub の配置用の鍵と同じ権限・消してからの再配置）。本物の AWS では確かめていない |
| サーバーの URL | アプリが URL と鍵を正しく読み分けること |
| アプリ | Android と Compose の代用品に対する型検査（実ビルドの代わりにはならない） |

## 使っているもの

- フォント：Yomogi（SIL Open Font License 1.1、[`licenses/Yomogi-OFL.txt`](licenses/Yomogi-OFL.txt)）
- 効果音：`tools/make_sounds.py` で合成したもの
- ロゴ：`tools/make_icon.py` で描いたもの
- 絵：`spoiler/` のスクリプトで描いたもの
