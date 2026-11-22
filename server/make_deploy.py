#!/usr/bin/env python3
"""Writes deploy.sh, a single paste-able script that carries lambda_function.py inside it.

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
# Exit Interview のサーバーを AWS に置きます。CloudShell に全部貼り付けて Enter を押してください。
# 作るもの: DynamoDB テーブル 1つ / IAM ロール 1つ / Lambda 関数 1つ（関数URLつき）。
# 何度実行しても同じ結果になります（2回目からは関数の中身だけ入れ替えます）。
# このファイルは server/make_deploy.py が作ります。手で書き換えないでください。
ei_deploy() {
  export AWS_DEFAULT_REGION="${EI_REGION:-ap-southeast-2}" AWS_PAGER=""
  local FN=exit-interview-rooms ROLE=exit-interview-lambda TABLE=ExitInterviewRooms
  local ACC W KEY URL OUT NEWROLE=0 i
  say() { printf '\n== %s\n' "$*"; }
  ACC=$(aws sts get-caller-identity --query Account --output text) || { echo "AWS に入れていません。CloudShell で実行してください。"; return 1; }

  say "1/6 DynamoDB テーブル"
  if ! aws dynamodb describe-table --table-name "$TABLE" >/dev/null 2>&1; then
    aws dynamodb create-table --table-name "$TABLE" \
      --attribute-definitions AttributeName=code,AttributeType=S --key-schema AttributeName=code,KeyType=HASH \
      --billing-mode PROVISIONED --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 >/dev/null || return 1
    aws dynamodb wait table-exists --table-name "$TABLE" || return 1
  fi
  aws dynamodb update-time-to-live --table-name "$TABLE" --time-to-live-specification Enabled=true,AttributeName=exp >/dev/null 2>&1 || true
  echo "このリージョンのテーブルと確保している容量（読み/書き）:"
  local R=0 Wc=0 t a b
  for t in $(aws dynamodb list-tables --query 'TableNames[]' --output text); do
    read -r a b < <(aws dynamodb describe-table --table-name "$t" --query 'Table.ProvisionedThroughput.[ReadCapacityUnits,WriteCapacityUnits]' --output text)
    echo "  $t  $a / $b"
    R=$((R + ${a:-0})); Wc=$((Wc + ${b:-0}))
  done
  echo "  合計  $R / $Wc  （無期限の無料枠は 25 / 25 まで）"

  say "2/6 実行ロール"
  if ! aws iam get-role --role-name "$ROLE" >/dev/null 2>&1; then
    aws iam create-role --role-name "$ROLE" --assume-role-policy-document \
      '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null || return 1
    NEWROLE=1
  fi
  aws iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole || return 1
  aws iam put-role-policy --role-name "$ROLE" --policy-name rooms-table --policy-document \
    "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:GetItem\",\"dynamodb:PutItem\",\"dynamodb:UpdateItem\"],\"Resource\":\"arn:aws:dynamodb:$AWS_DEFAULT_REGION:$ACC:table/$TABLE\"}]}" || return 1
  [ "$NEWROLE" = 1 ] && sleep 12

  say "3/6 関数のコード"
  W=$(mktemp -d)
  printf '%s' '@@CODE@@' | base64 -d | gunzip > "$W/lambda_function.py" || return 1
  (cd "$W" && zip -q fn.zip lambda_function.py) || return 1

  say "4/6 Lambda 関数"
  if aws lambda get-function --function-name "$FN" >/dev/null 2>&1; then
    KEY=$(aws lambda get-function-configuration --function-name "$FN" --query 'Environment.Variables.EI_KEY' --output text)
    aws lambda update-function-code --function-name "$FN" --zip-file "fileb://$W/fn.zip" >/dev/null || return 1
  else
    KEY=$(head -c 12 /dev/urandom | od -An -tx1 | tr -d ' \n')
    for i in 1 2 3 4 5 6; do
      aws lambda create-function --function-name "$FN" --runtime python3.12 --architectures arm64 \
        --handler lambda_function.lambda_handler --role "arn:aws:iam::$ACC:role/$ROLE" --zip-file "fileb://$W/fn.zip" \
        --timeout 10 --memory-size 256 --environment "Variables={EI_KEY=$KEY,EI_TABLE=$TABLE}" >/dev/null 2>"$W/err" && break
      sleep 6
    done
    aws lambda get-function --function-name "$FN" >/dev/null 2>&1 || { cat "$W/err"; return 1; }
  fi
  aws lambda wait function-updated --function-name "$FN" 2>/dev/null || sleep 5

  say "5/6 公開URL"
  URL=$(aws lambda get-function-url-config --function-name "$FN" --query FunctionUrl --output text 2>/dev/null)
  if [ -z "$URL" ] || [ "$URL" = "None" ]; then
    URL=$(aws lambda create-function-url-config --function-name "$FN" --auth-type NONE --query FunctionUrl --output text) || return 1
  fi
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
  rm -rf "$W"
  case "$OUT" in
    *'"ok": true'*)
      printf '\n==================================================\n'
      echo "できました。下の1行をそのままチャットに貼ってください。"
      echo
      echo "${URL}#${KEY}"
      printf '==================================================\n' ;;
    *)
      echo "サーバーから正しい返事が来ませんでした。下の返事をチャットに貼ってください。"
      echo "返事: $OUT"
      return 1 ;;
  esac
}
ei_deploy
'''

out = SCRIPT.replace("@@CODE@@", b64)
path = os.path.join(HERE, "deploy.sh")
if "--check" in sys.argv:
    ok = os.path.exists(path) and open(path, encoding="utf-8").read() == out
    print("deploy.sh is up to date" if ok else "deploy.sh is OUT OF DATE: run python3 server/make_deploy.py")
    sys.exit(0 if ok else 1)
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(out)
print("wrote %s (%d bytes, code %d -> %d base64)" % (path, len(out.encode()), len(code), len(b64)))
