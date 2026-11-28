#!/usr/bin/env python3
"""Writes deploy.sh, a single script that carries lambda_function.py inside it.

deploy.sh runs two ways: as a file in a clone (KsanHub's "AWS に配置") and pasted whole into AWS CloudShell.

    python3 server/make_deploy.py          rewrite deploy.sh
    python3 server/make_deploy.py --check  fail if deploy.sh is out of date
"""
import base64
import gzip
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(HERE, "lambda_function.py"), "rb").read()
b64 = base64.b64encode(gzip.compress(code, 9, mtime=0)).decode("ascii")

SCRIPT = r'''#!/usr/bin/env bash
# Exit Interview のサーバーを AWS に置きます。使い方は2つあります。
#   1. KsanHub の「AWS に配置」（リポジトリを取ってきて、このファイルを実行します。
#      PC では Git for Windows の bash、スマホからは AWS の CodeBuild が動かします）
#   2. AWS の CloudShell に、このファイルの中身を全部貼り付けて Enter（KsanHub の「CloudShell で配置」も CloudShell で動かします）
# 作るもの: DynamoDB テーブル 1つ / IAM ロール 1つ / Lambda 関数 1つ（関数URLつき）。
# 何度実行しても同じ結果になります（2回目からは関数の中身だけ入れ替えます）。
# 初めての配置は 2 で行います。KsanHub の配置用の鍵は IAM ロールを作れないためです（2回目からは 1 でできます）。
# 置く場所は東京（ap-northeast-1）です（2026-11-28 にシドニーから移しました）。CloudShell・KsanHub・CodeBuild が
# 決めているリージョンには従いません。ほかに置くときだけ、先に EI_REGION=<リージョン> を決めます。
# このファイルは server/make_deploy.py が作ります。手で書き換えないでください。
ei_deploy() (
  export AWS_REGION="${EI_REGION:-ap-northeast-1}" AWS_PAGER=""
  export AWS_DEFAULT_REGION="$AWS_REGION"
  # Windows（Git for Windows の bash）で動くときのため: 引数をパスと見なして書き換えさせない。AWS CLI が行末に付ける CR は取り除く。
  export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*"
  aws() { command aws "$@" | tr -d '\r'; return "${PIPESTATUS[0]}"; }
  FN=exit-interview-rooms; ROLE=exit-interview-lambda; TABLE=ExitInterviewRooms
  NEWROLE=0; HAVEFN=0; TREE=""; SELF="${BASH_SOURCE[0]:-}"
  say() { printf '\n== %s\n' "$*"; }
  ACC=$(aws sts get-caller-identity --query Account --output text) || { echo "AWS に入れていません。"; return 1; }
  echo "リージョン: $AWS_REGION"

  # リポジトリの中のファイルとして実行されていて、server フォルダがコミットのままなら、そのハッシュを控える。
  # KsanHub はこれを GitHub の最新と比べて「配置済み・最新」かどうかを出す。貼り付けて実行したときは空のまま。
  if [ -f "$SELF" ] && [ "$(basename "$SELF")" = deploy.sh ]; then
    DIR=$(dirname "$SELF")
    if [ "$(git -C "$DIR" rev-parse --show-prefix 2>/dev/null | tr -d '\r')" = "server/" ] && git -C "$DIR" diff --quiet HEAD -- . 2>/dev/null; then
      TREE=$(git -C "$DIR" rev-parse HEAD:server 2>/dev/null | tr -d '\r')
    fi
  fi
  aws lambda get-function --function-name "$FN" >/dev/null 2>&1 && HAVEFN=1

  say "1/6 DynamoDB テーブル"
  if ! aws dynamodb describe-table --table-name "$TABLE" >/dev/null 2>&1; then
    aws dynamodb create-table --table-name "$TABLE" \
      --attribute-definitions AttributeName=code,AttributeType=S --key-schema AttributeName=code,KeyType=HASH \
      --billing-mode PROVISIONED --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 >/dev/null || return 1
    aws dynamodb wait table-exists --table-name "$TABLE" || return 1
  fi
  aws dynamodb update-time-to-live --table-name "$TABLE" --time-to-live-specification Enabled=true,AttributeName=exp >/dev/null 2>&1 || true
  if TABLES=$(aws dynamodb list-tables --query 'TableNames[]' --output text 2>/dev/null); then
    echo "このリージョンのテーブルと確保している容量（読み/書き）:"
    R=0; Wc=0
    for t in $TABLES; do
      read -r a b < <(aws dynamodb describe-table --table-name "$t" --query 'Table.ProvisionedThroughput.[ReadCapacityUnits,WriteCapacityUnits]' --output text 2>/dev/null)
      echo "  $t  ${a:-?} / ${b:-?}"
      R=$((R + ${a:-0})); Wc=$((Wc + ${b:-0}))
    done
    echo "  合計  $R / $Wc  （無期限の無料枠は 25 / 25 まで）"
  fi

  say "2/6 実行ロール"
  # ロールが要るのは関数を作るときだけ。KsanHub の配置用の鍵は IAM を扱えないので、関数がすでにあれば今のロールのまま進む。
  # ロールはどのリージョンでも同じ 1 つなので、どのリージョンのテーブルも読み書きできるようにする（移すあいだ、前の場所も動く）。
  set_role() {
    aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    && aws iam put-role-policy --role-name "$ROLE" --policy-name rooms-table --policy-document \
    "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:GetItem\",\"dynamodb:PutItem\",\"dynamodb:UpdateItem\"],\"Resource\":\"arn:aws:dynamodb:*:$ACC:table/$TABLE\"}]}"
  }
  if aws iam get-role --role-name "$ROLE" >/dev/null 2>&1; then
    set_role 2>/dev/null || { [ "$HAVEFN" = 1 ] || { set_role; return 1; }; echo "（この鍵ではロールの権限を書き直せません。今の設定のまま続けます）"; }
  elif [ "$HAVEFN" = 1 ]; then
    echo "（この鍵では IAM を扱えません。関数が今使っているロールのまま続けます）"
  else
    aws iam create-role --role-name "$ROLE" --assume-role-policy-document \
      '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null || {
      echo "IAM ロールを作れませんでした。KsanHub の配置用の鍵では、初めての配置（このリージョンにまだ関数がないとき）はできません。"
      echo "初めての配置だけ、KsanHub の「CloudShell で配置」か、CloudShell への貼り付けで行ってください。"
      return 1
    }
    NEWROLE=1
    set_role || return 1
    sleep 12
  fi

  say "3/6 関数のコード"
  W=$(mktemp -d) || return 1
  printf '%s' '@@CODE@@' | base64 -d | gunzip > "$W/lambda_function.py" || return 1
  printf '{"tree":"%s","deployedAt":"%s"}\n' "$TREE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$W/build.json"
  cd "$W" || return 1
  # zip がない環境（Windows）では Node.js で、それもなければ Python でまとめる（Windows の Python は python3 という名前がないことがある）。
  PYZIP='import zipfile; z = zipfile.ZipFile("fn.zip", "w", zipfile.ZIP_DEFLATED); z.write("lambda_function.py"); z.write("build.json"); z.close()'
  zip -q fn.zip lambda_function.py build.json 2>/dev/null \
    || node -e '@@NODEZIP@@' 2>/dev/null \
    || python3 -c "$PYZIP" 2>/dev/null \
    || python -c "$PYZIP" 2>/dev/null \
    || { echo "zip・Node.js・Python のどれも使えないため、コードをまとめられませんでした。"; return 1; }
  [ -n "$TREE" ] && echo "配置する版: ${TREE:0:12}" || echo "配置する版: 不明（貼り付けて実行したか、server フォルダに未コミットの変更があります）"

  say "4/6 Lambda 関数"
  if [ "$HAVEFN" = 1 ]; then
    KEY=$(aws lambda get-function-configuration --function-name "$FN" --query 'Environment.Variables.EI_KEY' --output text) || return 1
    case "$KEY" in ""|None) echo "関数に鍵がありません。server/remove.sh で消してから、もう一度配置してください。"; return 1 ;; esac
    aws lambda update-function-code --function-name "$FN" --zip-file fileb://fn.zip >/dev/null || return 1
  else
    KEY=$(head -c 12 /dev/urandom | od -An -tx1 | tr -d ' \n')
    for i in 1 2 3 4 5 6; do
      aws lambda create-function --function-name "$FN" --runtime python3.12 --architectures arm64 \
        --handler lambda_function.lambda_handler --role "arn:aws:iam::$ACC:role/$ROLE" --zip-file fileb://fn.zip \
        --timeout 10 --memory-size 256 --environment "Variables={EI_KEY=$KEY,EI_TABLE=$TABLE}" >/dev/null 2>err && break
      sleep 6
    done
    aws lambda get-function --function-name "$FN" >/dev/null 2>&1 || { cat err; return 1; }
  fi
  aws lambda wait function-updated --function-name "$FN" 2>/dev/null || sleep 5

  say "5/6 公開URL"
  URL=$(aws lambda get-function-url-config --function-name "$FN" --query FunctionUrl --output text 2>/dev/null)
  if [ -z "$URL" ] || [ "$URL" = "None" ]; then
    URL=$(aws lambda create-function-url-config --function-name "$FN" --auth-type NONE --query FunctionUrl --output text) || return 1
  fi
  URL="${URL%/}/"
  OUT=$(aws lambda add-permission --function-name "$FN" --statement-id UrlPolicyInvokeURL --action lambda:InvokeFunctionUrl \
    --principal "*" --function-url-auth-type NONE 2>&1 >/dev/null) || { echo "$OUT" | grep -q ResourceConflict || echo "$OUT"; }
  OUT=$(aws lambda add-permission --function-name "$FN" --statement-id UrlPolicyInvokeFunction --action lambda:InvokeFunction \
    --principal "*" --invoked-via-function-url 2>&1 >/dev/null) || { echo "$OUT" | grep -q ResourceConflict || echo "$OUT"; }
  aws lambda put-function-concurrency --function-name "$FN" --reserved-concurrent-executions 4 >/dev/null 2>&1 \
    || echo "（同時実行数の上限は設定できませんでした。遊ぶぶんには影響ありません）"

  say "6/6 動作確認"
  OUT=""
  for i in 1 2 3 4 5; do
    sleep 3
    OUT=$(curl -s -m 20 -X POST "$URL" -H 'content-type: application/json' \
      -d "{\"op\":\"create\",\"k\":\"$KEY\",\"pid\":\"deploy-check\",\"mode\":\"test\",\"st\":\"\"}")
    case "$OUT" in *'"ok": true'*) break ;; esac
  done
  case "$OUT" in
    *'"ok": true'*) ;;
    *)
      echo "サーバーから正しい返事が来ませんでした。"
      echo "返事: $OUT"
      return 1 ;;
  esac
  case "$(curl -s -m 20 "${URL}build.json")" in
    *deployedAt*) ;;
    *) echo "（build.json を読めませんでした。KsanHub では「配置の版不明」と出ますが、遊ぶぶんには影響ありません）" ;;
  esac
  cd / && rm -rf "$W"
  ADDR="${URL}k/${KEY}"
  printf '\n==================================================\n'
  echo "できました。下の1行が、ゲームの「設定」に貼り付けるサーバーの URL です。"
  echo
  echo "$ADDR"
  printf '==================================================\n'
  # KsanHub はこの行を読んで、サイトの URL として覚える（貼り付けて実行したときは出さない）。
  case $- in *i*) ;; *) echo "KSANHUB_SITE_URL=$ADDR" ;; esac
)
ei_deploy
'''

# A zip writer for Node.js, for machines with no zip command (Windows). It holds no single quotes, so it sits inside '...'.
NODEZIP = (
    'const fs=require("fs"),zl=require("zlib"),t=[];'
    'for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0}'
    'const crc=b=>{let c=0xFFFFFFFF;for(const x of b)c=t[(c^x)&255]^(c>>>8);return(c^0xFFFFFFFF)>>>0};'
    'const loc=[],cen=[];let off=0;'
    'for(const name of["lambda_function.py","build.json"]){'
    'const d=fs.readFileSync(name),c=zl.deflateRawSync(d),nm=Buffer.from(name),h=Buffer.alloc(30),e=Buffer.alloc(46);'
    'h.writeUInt32LE(0x04034b50,0);h.writeUInt16LE(20,4);h.writeUInt16LE(8,8);h.writeUInt16LE(0x21,12);'
    'h.writeUInt32LE(crc(d),14);h.writeUInt32LE(c.length,18);h.writeUInt32LE(d.length,22);h.writeUInt16LE(nm.length,26);'
    'e.writeUInt32LE(0x02014b50,0);e.writeUInt16LE(0x0314,4);e.writeUInt16LE(20,6);e.writeUInt16LE(8,10);e.writeUInt16LE(0x21,14);'
    'e.writeUInt32LE(crc(d),16);e.writeUInt32LE(c.length,20);e.writeUInt32LE(d.length,24);e.writeUInt16LE(nm.length,28);'
    'e.writeUInt32LE(0x81A40000,38);e.writeUInt32LE(off,42);'
    'loc.push(h,nm,c);cen.push(e,nm);off+=30+nm.length+c.length}'
    'const cd=Buffer.concat(cen),end=Buffer.alloc(22);'
    'end.writeUInt32LE(0x06054b50,0);end.writeUInt16LE(2,8);end.writeUInt16LE(2,10);end.writeUInt32LE(cd.length,12);end.writeUInt32LE(off,16);'
    'fs.writeFileSync("fn.zip",Buffer.concat([...loc,cd,end]))'
)
assert "'" not in NODEZIP

out = SCRIPT.replace("@@CODE@@", b64).replace("@@NODEZIP@@", NODEZIP)
path = os.path.join(HERE, "deploy.sh")
if "--check" in sys.argv:
    ok = os.path.exists(path) and open(path, encoding="utf-8").read() == out
    print("deploy.sh is up to date" if ok else "deploy.sh is OUT OF DATE: run python3 server/make_deploy.py")
    sys.exit(0 if ok else 1)
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(out)
print("wrote %s (%d bytes, code %d -> %d base64)" % (path, len(out.encode()), len(code), len(b64)))
