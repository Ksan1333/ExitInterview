#!/usr/bin/env bash
# Exit Interview のサーバーの鍵を、2人で決めた「サーバーの合言葉」に替えます。
# AWS の CloudShell に、このファイルの中身を全部貼り付けて Enter（bash server/set-passphrase.sh でも動きます）。
# 合言葉は画面に出ず、どこにも保存しません。関数には合言葉から作った鍵（ハッシュ）だけを置きます。
# サーバーの URL と部屋のデータは変わりません。このあとの「AWS に配置」は、この鍵を引き継ぎます。
# 鍵の作り方はアプリ（app/.../engine/Net.kt の ServerAddress.keyOf）と同じにしてあります。片方だけ直さないでください。
ei_set_passphrase() (
  REGION="${EI_REGION:-${AWS_REGION:-${AWS_DEFAULT_REGION:-}}}"
  [ -n "$REGION" ] || REGION=$(aws configure get region 2>/dev/null)
  export AWS_REGION="${REGION:-ap-southeast-2}" AWS_PAGER=""
  export AWS_DEFAULT_REGION="$AWS_REGION"
  export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*"
  aws() { command aws "$@" | tr -d '\r'; return "${PIPESTATUS[0]}"; }
  FN=exit-interview-rooms
  PY=$(command -v python3 || command -v python) || { echo "Python がないため鍵を作れません（CloudShell で実行してください）。"; return 1; }
  aws lambda get-function --function-name "$FN" >/dev/null 2>&1 || { echo "関数 $FN がありません（リージョン: $AWS_REGION）。先に server/deploy.sh で配置してください。"; return 1; }

  read -rsp "サーバーの合言葉: " P1; echo
  read -rsp "もう一度: " P2; echo
  [ "$P1" = "$P2" ] || { echo "2回の入力が違います。やり直してください。"; return 1; }
  # 全角と半角を同じに扱い（NFKC）、前後の空白を除いてから、SHA-256 の先頭 32 文字を鍵にする
  KEY=$(EI_P="$P1" "$PY" -c 'import os,unicodedata,hashlib; t=unicodedata.normalize("NFKC",os.environ["EI_P"]).strip(); print(hashlib.sha256(("exit-interview:"+t).encode("utf-8")).hexdigest()[:32] if t else "")')
  unset P1 P2
  [ -n "$KEY" ] || { echo "合言葉が空です。"; return 1; }

  # 環境変数はまとめて置き換わるので、今の値（テーブル名など）を残して EI_KEY だけ替える
  ENVJSON=$(aws lambda get-function-configuration --function-name "$FN" --query 'Environment' --output json) || return 1
  NEWENV=$(EI_ENV="$ENVJSON" EI_K="$KEY" "$PY" -c 'import os,json; e=json.loads(os.environ["EI_ENV"] or "{}") or {}; v=e.get("Variables") or {}; v["EI_KEY"]=os.environ["EI_K"]; print(json.dumps({"Variables":v}))')
  aws lambda update-function-configuration --function-name "$FN" --environment "$NEWENV" >/dev/null || { echo "鍵を替えられませんでした（この AWS の鍵に権限がないかもしれません。CloudShell で実行してください）。"; return 1; }
  aws lambda wait function-updated --function-name "$FN" || return 1

  URL=$(aws lambda get-function-url-config --function-name "$FN" --query FunctionUrl --output text) || return 1
  for i in 1 2 3 4 5; do
    OK=$(curl -s -m 20 -X POST "$URL" -H 'content-type: application/json' -d "{\"op\":\"join\",\"k\":\"$KEY\",\"code\":\"\"}")
    case "$OK" in *'"nf"'*) break ;; esac
    sleep 3
  done
  case "$OK" in
    *'"nf"'*) ;;
    *) echo "鍵を替えましたが、確かめられませんでした。返事: $OK"; return 1 ;;
  esac
  printf '\n==================================================\n'
  echo "サーバーの合言葉を設定しました。"
  echo "2人とも、ゲームの「設定」→「サーバーの合言葉」に同じ言葉を入れてください。"
  echo "前の URL（/k/ のあるもの）は使えなくなりました。"
  printf '==================================================\n'
)
ei_set_passphrase
