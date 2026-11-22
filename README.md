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

## サーバーを置く（AWS CloudShell）

1. AWS コンソールで CloudShell を開く。
2. [`server/deploy.sh`](server/deploy.sh) の中身を全部コピーして貼り付け、Enter。
3. 最後に出る `https://…on.aws/#…` の1行が「サーバーのあいことば」。

あいことばをアプリに入れる方法は2つあります。

- アプリで入れる：あいことばをコピー → アプリの「せってい」→「クリップボードから はりつけ」。友人も同じ操作をする。
- APK に入れる：`app/src/main/assets/server.txt` にその1行を書いてビルドする。友人は何もしなくてよい。

消すときは [`server/remove.sh`](server/remove.sh) を貼り付けます。

### 手元のPCで動かす（予備）

```
python3 server/local_server.py 8080
```

同じネットワークの端末から `http://<PCのアドレス>:8080/#` をあいことばとして入れます（`#` の後ろは空でよい）。

## 遊び方

| ボタン | すること |
| --- | --- |
| へやを つくる | 4けたのあいことばが出る。友人に通話で伝える |
| へやに はいる | あいことばを入れる |
| つづきから | 前の部屋に戻る |
| テストべや | 動作確認用の小さな部屋。「ひとりで」は1台で2人ぶんを切り替えて操作する |

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
| サーバー | メモリ版と DynamoDB のモックに対する動作 |
| アプリ | Android と Compose の代用品に対する型検査（実ビルドの代わりにはならない） |

## 使っているもの

- フォント：Yomogi（SIL Open Font License 1.1、[`licenses/Yomogi-OFL.txt`](licenses/Yomogi-OFL.txt)）
- 効果音：`tools/make_sounds.py` で合成したもの
- 絵：`spoiler/` のスクリプトで描いたもの
