# このフォルダは開かないでください

ここには謎の答え、ステージの絵の描き方、模範解答が入っています。
けいさんと友人が初見で遊ぶために、中身は見ないでください。

- 作業するのは Claude だけです。
- ここを変えたら `python3 spoiler/build_pack.py`（第1話）・`python3 spoiler/build_pack2.py`（第2話）で `app/src/main/assets/stage.pack`・`stage2.pack` を作り直し、`tools/verify.sh` を通します。
- 第1話は rsvg-convert、第2話は resvg で絵を描きました。描画ソフトが違うと絵のバイトが変わるので、第2話を作り直すときは `EI_RESVG` に resvg のパスを入れます。変えていない話は作り直しません。
- このフォルダに触れるコミットは、題名を `[spoiler]` で始めます。
