#!/usr/bin/env bash
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
  printf '%s' 'H4sIAAAAAAAC/7VabW/byBH+rl+xpRGUbBRWTgzDUE+HOokDBJeXwvb1ehAEHS2ubJ4pkuauZAuG/3ufmV2SK4pSnBTVB4fcnZ2ZnfcZxvO88zxfCCXLlSzFPC/F2UOixcdMYyWR92Gv9zWTopSzvIxFAZgS8KG4vJHiOlpgZ5lKJdJkJUWSCY3lqCjUP/jJYr2VslC8QGf/qsQ8ja6ViLJYJFouVL93g2eGWIh8qfu8BTRpAtSRmGH7Woo8S9cimYss1zdJdg3wSFd7sSxkFssYQOI+wqEU/OP1ak1Ye0VU6gycWA4XMsp0AuZ9Gc1uwN8aF1zIxZUsGz4FWFdJnhk6aaQqYsR1EPbOl5kicqe/XYhP0eIqjoT/YZnNNJ359fyTeCner7Nokb9/G9CF+kBU5svrG5HmsyidGuGExbpPWKJsLWb5oliC77DneV4vWRR5qcVVpOTxUfX2p8qz6jlX1VMJ9PmieqOb9Xq/nP0uRoAJZbZKyjwLr6X2vbOPU2x4feF5Qe/y9O2ns24g3iIwsobaGMhUFA6ef/36efr+9PcLHH4z6H0+/c/04vL0knAdD/Dr9XozCEyJz3JxofNSDnsCP88Ym4LAC026gMjzci18FkhlLaR7LZVWQUhi4JOxnIvpNMkSPZ36SqbzwGCkH72GJeMdicen5gDdhTb7EGws6W+mEqVlpkcfolRJBwfre+SgYkHQsaCBkXpZZiJOZtonmIBskQ9KIBNf8kw2tGeljLS05AmoD7O9dyjmabxNkJ7GHpH1Jg1hkCFokgv+HXvyofAm4mdC2OBzOOTLdYhn7KKfgHpzlfYlL8ulc5llETeXMbJUUqu+ACdypqfQ2oiu/50CrcSXKBaeQOzxG4y0DE83W3R3wz12cPm/jBzaQacUWB8uO2F9DZjWbq3Wtmucd5/5RrWDCx1dpVLc3+SwBAonYP4Puu0fe2y4b0457Fcun+v8zaYCDf6R2QpLqfJlOZO+FzMD8ZUXhJcE4huUhuI/lY50MltIfZPHDQ9FGiWZT5HXJT3nWFwp4xkiNWuPt0PhJ5n2V4GNzUCRZKCcgb9VX/hKl33wnadBYDwFkJRnbvtiRVIksiHnAT942sv4PEpSGfuydFVu+YB5RVqXtImoBQEV8HaJCPb4FNioVpZ56S68I0cIxGgk8JjFCQXuKH13I2e3H5jS2cMMmsaq92NBxXDG+rNCb3RJLEzp1v4vcj16NF45ZKRPffGuxnouo3jUELGsf8RBLwi+I97ocr2pU4cVJB3DCqEdmdO1RM4eCkiTEuHIIwknV0hRU+h5Kh/Ak/IPZoH4ei4OpPhJDEHU62/Q6fo1OE8rjF9QSyjI4WAGKRhpQI8HJBMOeBBKx6l/R+mSjzHhId35KegyXQ5o1ZpkvYpavQIFA+xmKMQBMNxFQ4HkNxgcbiCCcRtNdlrh3hDMG1Gi/reQmpGE4DN85b6gkoYzniuyJzLvvhhP6lPkaQm8kLwtIHeT2XIhyyoQVo7XugrTGnsH0YvYEy9EQtnidgPCsDH2hisHZLUBwhyGKONQmfmMCyAVvA+mkqDRFUycth0Ta8zLc6NUd4boZt8kC2Clh2725YohGqwbYMzVSyAQp1/eC8JHV8CZ3X5VVmnP+JZR9G5P/5X3XSe7OLsEvZeC7D/8M0fUYEEG3T5JHH7b4b7ld9a2dntYZXXnbN920Tv99Gn65ew3r9Pl3LhXjr0ao3Jrm/+/K24kLccTe5xSSlmka9+EvBw+wulDpbl242eV6rz8FoojMA9weDTJxirUra6wSkiwanCxAQ7dEoYgdL2Ex8mmFr0VNm3FthoQvH0+RO1Gh5tt5Wwru10cYp+Srq0p8T6BBXkLl9dFxWsTPCu5kGRNLt0lBg5xLUls4aG+DkXJHWRKdRRj47jWpyrJjXAok04zdU8NWM795h0sTAs/4tIsEPeJvhHmhUsqdvP8Hs5GxQe1PCH98W0Vcl9XlVxy0CX4CNVmI0G9EcBsodaAYaFnDaxVyOAGzMdWdjeS8q6i2Os3ZCxyKlvvTMa+RaWBqhWru1Bgy0WRF2DUHs4L62KQSL0Im6mJKb1VLvutGyhNSigDKrNTiVIEQv1Z1K3b7psl1y5b1AY2PNBbwwXvfYsPAtrkhFaIlzevnyPeihjJB4HZFD5ec7BIuLFCKWh5xILHtNDyjofHR5u5cUo5saS23j8etDsJ08TUIdt7MTji5GX67ZD+MUcPqesNaj8/rLwbemHCxvMIxeOT17ihw+XCFKMEvUDEJFZPJt2B3SsGOItrVX7O+FeD+qleUwPjjvRIi4O+KaZ4ESmm6eP/Jk6OjwaDp604S24b2uqyq65s68sNqFR09YVx94FjQx36Xar1hoJJ4o2ZsfyDHa5pqydrULTpH4qfRmxa3HDSy8lO08rmrnlTuAbdQ6JT+RkFcm4TDk2UGLRtkJL0j1lg1SazlKsO2Qhub59s4rcZBOB2uyYBnVe0KJnLkcUEi5q02gMjiEGTqVMr+iahNJzwG7ABaSeaQweNkvt4nS/TtM0tFarsh8rUjoTUphnXVJkUaLX7HK0qBom/btnberypxIPqcr3nWnhTNbTtA4r1NjrtdqDsDDsdjD16K1cCJpRuSyXYJ+0ui9tpa99nVT8uIXSgjoRo5ImCBp0vKs77ErWzclIOIiwirX0rjWONJ/XKvVl53LCNdhIyFFA51DHD2bSE00R1bhuGbD2wFQdtTmMclNQwD63WzEHOdINB10EiFKWp7xC7tZGNMinhuOVodnRiJiiUu4jNitxL82YJBc+ksbKSIBrb8xue3DA5ntYY3KHpB/z9NG7Hw9cTOgS3HlI+SoZe0HBesbnPyFp1VUfWPgmeYeDtkPqDYfU5TkA/JHOwQLP6MM2hGfaFOs/bXIBKYIshfAXwAcGgUP2AjIVs9Vnqfl5Srup28qMNl2wHTTNNbzG4P3I18daJUzwYwLEdkGoTEqy0aZr7dVDCxE9uy9l0U90iro+FII4GJVqm0MncTAWfAZnsgDSDAXdC/VIcbkG5U0/rR3b8Muws9KjvZ1MGG2PQnnBfMR5wqsW7KUfs9tybdCIhpRH8YLhzSkB0wiIv4LCvhxMTrYNO6O180sYzZhzbwyDHNca3vN0atdTtDaszXi4K5fPV0JRnalnKaaRmSTKy9qskqEVwcjXyvT4FlyGlBYX5+RSdlBptO7yVRkfz032lvX1Q25Drrwt6RJ0WrjlyLoLXHSyDZ5r10WeMtt2TjxHq7y+2d3h1TGFuZ8WzMXt0THmLL0azNwZs8hczT9/g7xv9wOY2+uFqszfl6+Ba5gMcjx1S/hw7NdMHfBNYYXLOo3otH6oe/jrNr/DR0RznFfO5AZjMAVtgmEHEO3PW/Xxwo3Vh3k29YZcNFtLuv75eXDZdi8WOGYDZcMqdPF5zectzFSMnjyZyZvad6FdJ9QHWMwF50w3LiDpyh2dC2CSZjeFpA5Sot/xl+SwjE0BSaqVRRmo+PodXx0exJDAfy0Fon72lnr86cSLs1iz0rhWdo/utyR+PEvnTzPbRjdEduLeq7qxNazNwPtv5/BU7aAu6GUqZQ8HmdIuCzlK9Mx366wH1zDfIt5hM4Z1mARl9iHml1wUriP+bwiyi4eXf6a40gzcaGLqhjFa6Ilnw1PsvoGHzrIQhAAA=' | base64 -d | gunzip > "$W/lambda_function.py" || return 1
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
