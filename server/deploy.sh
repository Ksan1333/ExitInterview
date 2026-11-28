#!/usr/bin/env bash
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
  printf '%s' 'H4sIAAAAAAACCsUa/W/bNvb3APkfOAbDpKurOW0Q9Hzz7tI2uyvWNUOTXW8wAo+26FizLCoibdco8r/fe4+URFlykq7DnQs0Ej/e9xcfxTl/r9SSaVmsZcFmqmDnHxPD3mQGRhK5iQ4PDg8uMskKOVVFzHJYVcCOiF3NJbsRS5hZpVKzNFlLlmTMwLDIc/03enJwF1LmmgZw7zeazVJxo5nIYpYYudS9w4M5vNCSJVMr06M5gJMmAFuwKUzfSKaydMuSGcuUmSfZDSwXppyLZS6zWMawiG0EbEqBBXidbBHq4UEuCpMBLY7GpRSZSYD8QIrpHCjcAotLuZzIoqaUAfE6UZlFlApdYkO6Q5DN+1WmEeHZh0v2ViwnsWDBD6tsanDTL+/fsifs9TYTS/X6ZYgs9QBSoVY3c5aqqUjHVj5Rvu0hFJFt2VQt8xVQDsA554cHyTJXhWEToeXpSfX6u1ZZ9aJ09VgADrWsXpFBVOCP57+yIayLZLZOCpVFN9IE/PzNGCZ4j3EeHh5cnb18e969iqZwHdpGZRpoOBp3vr+4+Gn8+uzXS9j9vH948NPZf8aXV2dXCO20Dz879OriNY6c9JGiw4NYzth4skrSOAgHhwcMfsDwBxS0QGWmass2hTKSTaROYgmSS8BwklQO2GaegM5AVMvEgDVV1pvGqGANJpllYB/WinSSTSVskVlEEkVMptg6nPjbJGbOFJhPAMznwsyj31VSv8RJASqU1buYaPwbjMdIzXgchiAa4iRCvXB4ldlUxUDBkK/M7OkLDsoH2uceTvzN1AroG5I2o1SJOJjNw3pJIc2qyNwqsPoEONFGADcBjfVYnExNyGSqJft0ZzfKj1OZGxZcXJ4XhSp67N8iXUl6Dgct2LgL/7385c3b10BJqZBaRUk2UwGy6ykJXV9kegPCNgq09c/zqwGrBcCCQgpyvB+1yP61muAqI9MUlQCuVZB/ORWDtqaropAZMALRR4C6bjKmZhBQZrJWGLBPVOAaMNdIQ2QA4/w7D0f966jQpkjygH8LMxAENCoU3nydtHknnu1oKQ2uFnzAroqVBI2izuGNSzD6p0lp9dxJbArRQLOf5PLSqELWsiGvgHACOoBIAwFFFVsWkLeXdopGaaQ2OrT82b3kD+MkS8x4HGiZznyS8T0qCPTQKa3cg06K0z3wh1ji/5lOtAGBDn8QYBkNzjGmDT1o5OK4r212aFsBLgpR+LSTDO2dyqSPfwrKNtKRgMt6EJ43PlZwyzZSfBpxRM2vPeSACpejiODvCISf82v2PYLccR5HJvHYJaiRj+EaCKgZavGKGvd5WuVxzZMVq5ZGg19/zOXUjEGLQ5TDZ8u2lCRYPe5Haw5qmDgMqc1OoQgsCzADMvhq6GEPu4VhdeNTFFWsgLndo2PfqG3GuteuRZXWmBGTFMOrAtvALAo8/IZc/3avcffsPp+PMtMpo57vKNTiGNq5qJBarQqIgjwmIuIJuP0VLgks0BLrPyBammS6hKCjYo+QPBUQ3rHyaOCfUTFS6uZREnZxYzFgAUSIYB266sSP1eseCyA+9YB6lYYuXMNKLLYWPbZGeSLiiEqhILx7iPyZgLQTB7LoiuhgdMKYAmchhoGocogHEpL3p7vQJXTMBf7AK3SRkA2HDB6zOMHiRaSv5nK6+IFQnVNOgVH+hwOPJY6U6cRfKxapGCPzwY9yO/xkXXZAUO967FUF9j1klWGNxVH/BjbyMPy8kNTM/007i6D+suQg6KHdXwnm/GMOQsWicMhR0MkEqrUxqHwMeQJienA0DdnFe3Yk2XdsAGh5r4mo61cDPStBvoPso0EYR1PMQSQS0OeRy0g5B8l07KJkj9sI8wDZvgs7DdmGvHLQVQ2VorFcAQsaMHYEMG7FgEEF2O8fN0GBrVuNdlvk/ZGaZkSivzjwYp6GFWtivcewzqcs6YvuDs29x0bX9TZ0vwRcE10wRB+U2WopizJYlt64yxBhG/Ej8XXM2dcswcyyaC6xlIz4YO2tWTfXEJURHHCgXAkIGqwpNwRAVxJ6egOjx3nP4Gpj440I1p1M9vBgEwvAxYc9PMg1LanhNtcRZU8ABDt795ohROQDNt3na0WZJ62/WaXvjwC/0LzveJfnV4DxCUOXsLU6yTPs9lOk8RFO+JAvOjvb73WlBb4ne3eD/Ozt2/G78w+82w39iFiMeAVSN6qi/4V7NjNbwzvdYa2Ain0b2HiowG0oxehUGQqvPbYUsWyG/mZdjXs4bIJHm52cmv1CDUYRIoxawGSaA78QwhWmGoLH6x3d8jXMuupv3ccN7vkY6kDcXU9rb1q76fwY5jFVuxIV3q/xgLf0iV2WxFZhdpcIFAbM4J87T4aZ3IwRRGCDW57AKU4Dn0t69bJUJTrPFypxHJdC0MYeiCx9GO4+3fGaWCg7AnykRUuwMTguDV60BJb3YS2RYrkneOt+9VSN6b5jlqG4Bqzfs8mIBsEf607AX9iL05N+32fdiIUca8jMUA1BaVlmZsLrMQ5V4yUswq4PuMXWdmwELR7QwZGyuyqbSggQ5YEzs6RAgdAR0+2FEsGteRbZuhobAWy2StPG4RKowALIqRzMwj98gSVCxOq7A3bqSrzaPFC83hvAAXBtAMclAC3bpRHS1vOcEHMQZTFtcwLCsPm8otmCBbiNg6LRJRlIRcOYrEuR9MtzQdP36JRQcuOpDgOIrSi7LJScm/x+x7/rGqSGhX0+KNRvHR0EcWiZh9NDI7mDfs6oy4AtNuxA3kJANSwQru9BbRv7UusSDXHIsBjH5leE/wWuKt9Uxy4qwZEVuwePLUOGTTJY584w9ToYqES+U9rfuhZMW51WZHwiYt7zMB1R29ShULmttAdsVsCZsB8dR8/L/ilbSjSAyRYqBa3zeSGAEmRYrQxKI2JnlUBsF1QUhe2VbgqV3dRUH4HAMmZbYwjYSi3DLitaQIxtyhDJ0SZJU2bw+K1VVLGMxOJZlC84euItvdza2nsBxwY4l8KSvRKAuYYEVA6idttVXmZFbepRCGxhbeOmdSgOdpSgyaYLsttUwsECTON7VjUh71FOctMgDds7NRnU7KkJocmHSMFFTWJwBMl5/uxxRlLhQzlBWWWPMtzbS5GKIrsjFAZ46Ppio8HpyU6NO0atFdi0Dk77rb6BbVrUaYl/3T+heGM7yRH+sZuPsZMbeinLoadUE/py9OsPijXuPNZ5EtsViV9k2EacDQ79XQw7Mlzp7Y4QMajV6qQQF+5zZHfUcIrDyeCYfTckFVILB1/KJvZ+TWazhkGVcR8RlsaNxQ2dtY9tdOm3dY6u72scgsZGuYSmsdPCzDaX9n4FL2C8CAGnCThDlXccNFvf1pBAEgwRc6Hn2GPFRfVuH2OAhYu7O8GwgcKBEhsvXSiAcDhzA1RI6diyxfyazOprk4SuUDC6E49LXJaYiH3A3DuBBI2HAgg1Pka3iAmMb1PZs5c96GnWfJheTadSxvbaCFHZRI9lhS6JUJbxTH7E/LzK4qhxOkLFohQiYsa1iZe88lanavbX7ubPnqD+hV55sscpre+UTUTrDW0PK+Xd0Tfc3zstjbNXBYCHirP2/p1W5qD7gNWUHJZdfB/AhyJAddIIH4hhO6X1/yNOucPQjsoeDFl1DMBD7R+N+o+zn45WtG82EO/29ty7o92XGNX9xvQII/oc49mV9U0z3HYk+/sc1BXSVsaf+Nov12090C7h/aN98zSwV39/UFgdOvoSUeWrhqjwVhq0KkWse1B3JkZqr4CCo2pYuV9hrXV0XY1s7Eh5cVne8u1kZosicdeDO5MOc5rozmlLkavR267sgj4BwRrttN8vx+xOKtz6/c6diEqkaeChW7gKAiMwAllQ1XDywnb6MeAjoSW+J/bNYQofi2TthIFI2hcNdMVA+OhawQKPbGMqeADJYjR4do27wMUGeNpPBjysaS8J/ezUuJPuXvwp6e7RIetRLoE/yA/+Vbwmz6hSh4u1n+54myaRbbHLQmvBBvpoNmi2j9L7I1NMebxGp9qfCsumwV2LxgciWt068OIXta1h376lurkUyGmhtVx2ITNY0rXkbRt6e0Rd7YsAfyxnYpWCcmb2KusxS5N9S23b2r9tfcKO28v8GzvnWu6WYE/1g11pMm2gZATor+lAPepTjwjebXnspmf8uhsKqg839Af7m9iIKcpVDl78bHBtQ3nYvbwj4+xCGhGUjmsLz1lGC5rfvRCoTvOk2Xi1zHVADOJHMXpVyLHQ0yQZOoPWEvBhO08PA97DqDPApKFVYcYLudXDjjDgZNJx1n9UEbp77N817OrK3AxdZ3bo8QKve6gGsvF6Cm/nW36AboewB39e2RtjBOwsQlo3Zp5ht0kjOPdHhiaJMZH1EIkP1rrNBSr3pg8PxsQWsFd+bWKbhyl9Yje2PcQikGuZGbp4NnDgK53wJlUTkTILwg7ZK3QAZ7e4isS2z17Z3f6F+NyY3L7bAsUNWyio7Z8vLq+8ZoID/9XQzfgVkoq31I+cqQZusflZmDkvU/JuT1hgI8pbj2DqFNS88atXJfolfSZ4jl+fyZi3Mi2BtZ8SRpPTk1jiugCGw8g9l9+r3Xd9d7sTt8WmfVVVf3XWsbl51QQ8OHV3F7SVLXjfpQT0SWLYknPdXba7wp1WNUailX5lb0ee9fH+Yg5pWRZ4KYR3LRl+WfAU+yt450EfoE4Ftmm/pc/I8NJKTOfyKa4sVIqLMvWUcPG73XsV0trAj4Q40hUI8aOP/wK6ZoxEjCsAAA==' | base64 -d | gunzip > "$W/lambda_function.py" || return 1
  printf '{"tree":"%s","deployedAt":"%s"}\n' "$TREE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$W/build.json"
  cd "$W" || return 1
  # zip がない環境（Windows）では Node.js で、それもなければ Python でまとめる（Windows の Python は python3 という名前がないことがある）。
  PYZIP='import zipfile; z = zipfile.ZipFile("fn.zip", "w", zipfile.ZIP_DEFLATED); z.write("lambda_function.py"); z.write("build.json"); z.close()'
  zip -q fn.zip lambda_function.py build.json 2>/dev/null \
    || node -e 'const fs=require("fs"),zl=require("zlib"),t=[];for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0}const crc=b=>{let c=0xFFFFFFFF;for(const x of b)c=t[(c^x)&255]^(c>>>8);return(c^0xFFFFFFFF)>>>0};const loc=[],cen=[];let off=0;for(const name of["lambda_function.py","build.json"]){const d=fs.readFileSync(name),c=zl.deflateRawSync(d),nm=Buffer.from(name),h=Buffer.alloc(30),e=Buffer.alloc(46);h.writeUInt32LE(0x04034b50,0);h.writeUInt16LE(20,4);h.writeUInt16LE(8,8);h.writeUInt16LE(0x21,12);h.writeUInt32LE(crc(d),14);h.writeUInt32LE(c.length,18);h.writeUInt32LE(d.length,22);h.writeUInt16LE(nm.length,26);e.writeUInt32LE(0x02014b50,0);e.writeUInt16LE(0x0314,4);e.writeUInt16LE(20,6);e.writeUInt16LE(8,10);e.writeUInt16LE(0x21,14);e.writeUInt32LE(crc(d),16);e.writeUInt32LE(c.length,20);e.writeUInt32LE(d.length,24);e.writeUInt16LE(nm.length,28);e.writeUInt32LE(0x81A40000,38);e.writeUInt32LE(off,42);loc.push(h,nm,c);cen.push(e,nm);off+=30+nm.length+c.length}const cd=Buffer.concat(cen),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50,0);end.writeUInt16LE(2,8);end.writeUInt16LE(2,10);end.writeUInt32LE(cd.length,12);end.writeUInt32LE(off,16);fs.writeFileSync("fn.zip",Buffer.concat([...loc,cd,end]))' 2>/dev/null \
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
