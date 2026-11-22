# Exit Interview

通話しながら遊ぶ、2人専用の脱出ゲーム（Android）。一般公開はしません。

## 開いてはいけない場所

| 場所 | 中身 | けいさんは |
| --- | --- | --- |
| `app/` | アプリ本体（画面、通信、音）。謎の内容は入っていない | 開いてよい |
| `server/` | 部屋サーバー（AWS用と手元用） | 開いてよい |
| `tools/` | 検証スクリプト、効果音の生成 | 開いてよい |
| `spoiler/` | ステージ定義、絵の生成、答え入りの検証 | **開かない** |
| `app/src/main/assets/stage.pack` | 暗号化したステージ一式 | 開いても読めない |

- `[spoiler]` で始まるコミットは、差分を開かないでください。
- `tools/verify.sh` が失敗したときの出力には、謎の手がかりが混じることがあります。読まずにそのまま Claude に貼ってください。

## 作るもの

| 部分 | 技術 |
| --- | --- |
| アプリ | Kotlin 2.0.21、Jetpack Compose、minSdk 33（Android 13）、横画面 |
| サーバー | AWS Lambda（関数URL）＋ DynamoDB、ap-southeast-2 |
| 同期 | 1秒ごとの問い合わせ。操作は手元ですぐ反映し、あとからサーバーへ送る |

## ビルド（Android Studio）

1. このリポジトリを Android Studio で開く。
2. Gradle の同期が終わったら、`app` を実機で実行する（または Build → Build APK(s)）。
3. できた APK を友人に渡す。同じ APK を2人で使う。

- Gradle 8.10.2、Android Gradle Plugin 8.7.3、compileSdk 35 を使います。
- Gradle JDK は 17〜21 を選んでください（Settings → Build Tools → Gradle → Gradle JDK）。
- GitHub Actions は使いません。

## サーバーを置く

置き方は2つあります。どちらも同じ [`server/deploy.sh`](server/deploy.sh) を使い、何度実行しても同じ結果になります（2回目からは関数の中身だけ入れ替えます）。

### KsanHub から（「AWS に配置」）

KsanHub の一覧（`Ksan1333/scoop-bucket` の `catalog.json`）に、次の項目を足しておきます。`group` などの見た目の項目は、一覧のほかの Web アプリに合わせてください。

```json
{
  "id": "exitinterview-server",
  "name": "Exit Interview（部屋サーバー）",
  "kind": "web",
  "tagline": "2人用脱出ゲーム Exit Interview の部屋サーバー（Lambda と DynamoDB）",
  "repo": "Ksan1333/ExitInterview",
  "deployScript": "server/deploy.sh",
  "treePath": "server",
  "group": "web"
}
```

1. KsanHub の「Exit Interview（部屋サーバー）」で「AWS に配置」を押す。
2. 終わると、サーバーの URL（`https://…on.aws/k/…`）が KsanHub に登録される。カードの「URL」で見られる。
3. その URL をコピーし、ゲームの「設定」→「クリップボードから貼り付け」。友人にも同じ URL を送って、同じ操作をしてもらう。

- スクリプトは最後に `KSANHUB_SITE_URL=<URL>` の行を出します。KsanHub はこれをサイトの URL として覚えます。
- 配置が最新かどうかは、`server` フォルダのハッシュで比べます。配置した版は `<URL>/build.json`（`tree` と `deployedAt`）で返します。
- URL の `/k/` の後ろは鍵です。この URL を知っている人だけが部屋を作れます。公開の場所（このリポジトリを含む）に書かないでください。
- 配置に使う鍵（KsanHub の配置用ロール）には、次の操作の権限が要ります。足りないと、最初の配置が AccessDenied で止まります。

| サービス | 操作 | 対象 |
| --- | --- | --- |
| DynamoDB | DescribeTable、CreateTable、UpdateTimeToLive（ListTables は表示用で、なくても進む） | テーブル `ExitInterviewRooms` |
| IAM | GetRole、CreateRole、AttachRolePolicy、PutRolePolicy、PassRole | ロール `exit-interview-lambda` |
| Lambda | GetFunction、GetFunctionConfiguration、CreateFunction、UpdateFunctionCode、GetFunctionUrlConfig、CreateFunctionUrlConfig、AddPermission、PutFunctionConcurrency | 関数 `exit-interview-rooms` |
| STS | GetCallerIdentity | |

2回目からは、IAM の書き直しができない鍵でも、関数の中身の入れ替えまでは進みます。

### AWS CloudShell に貼り付ける

1. AWS コンソールで CloudShell を開く。
2. [`server/deploy.sh`](server/deploy.sh) の中身を全部コピーして貼り付け、Enter。
3. 最後に出る `https://…on.aws/k/…` の1行が、サーバーの URL。

貼り付けて置いたときは、どのコミットの版かを控えられないので、KsanHub では「配置の版不明」と出ます（遊ぶぶんには影響ありません）。

### サーバーの URL をゲームに入れる

- アプリで入れる（おすすめ）：URL をコピー → アプリの「設定」→「クリップボードから貼り付け」。友人も同じ操作をする。
- APK に入れる：`app/src/main/assets/server.txt` にその1行を書いてビルドする。友人は何もしなくてよい。ただしこのリポジトリは公開なので、書いた `server.txt` はコミットしないでください。

消すときは [`server/remove.sh`](server/remove.sh) を CloudShell に貼り付けます。

### 手元のPCで動かす（予備）

```
python3 server/local_server.py 8080
```

同じネットワークの端末から `http://<PCのアドレス>:8080/#` をサーバーの URL として入れます（`#` の後ろは空でよい）。

## 遊び方

| ボタン | すること |
| --- | --- |
| 部屋を作る | 4桁の合言葉が出る。友人に通話で伝える |
| 部屋に入る | 合言葉を入れる |
| 続きから | 前の部屋に戻る |
| テスト部屋 | 動作確認用の小さな部屋。「1人で」は1台で2人分を切り替えて操作する |

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
| 配置 | `server/deploy.sh` と `server/remove.sh` を、AWS のモック（moto）に対して最初から最後まで実行する（クローンから・貼り付け・権限の足りない鍵・消してからの再配置） |
| サーバーの URL | アプリが URL と鍵を正しく読み分けること |
| アプリ | Android と Compose の代用品に対する型検査（実ビルドの代わりにはならない） |

## 使っているもの

- フォント：Yomogi（SIL Open Font License 1.1、[`licenses/Yomogi-OFL.txt`](licenses/Yomogi-OFL.txt)）
- 効果音：`tools/make_sounds.py` で合成したもの
- 絵：`spoiler/` のスクリプトで描いたもの
