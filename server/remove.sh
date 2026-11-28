#!/usr/bin/env bash
# Exit Interview のサーバーを AWS から消します（CloudShell に貼り付けるか、bash server/remove.sh）。部屋のデータも消えます。
# 消すのは東京（ap-northeast-1）のもの。ほかのリージョンのもの（移す前のシドニーなど）を消すときは、先に
# export EI_REGION=ap-southeast-2 のように決めます。CloudShell が決めているリージョンには従いません。
# IAM ロールはどのリージョンでも同じ 1 つなので、ほかのリージョンに関数が残っていれば消しません。
EI_R="${EI_REGION:-ap-northeast-1}"
export AWS_REGION="$EI_R" AWS_DEFAULT_REGION="$EI_R" AWS_PAGER=""
FN=exit-interview-rooms; ROLE=exit-interview-lambda; TABLE=ExitInterviewRooms
echo "リージョン: $EI_R"
aws lambda delete-function-url-config --function-name "$FN" >/dev/null 2>&1
aws lambda delete-function --function-name "$FN" >/dev/null 2>&1
aws dynamodb delete-table --table-name "$TABLE" >/dev/null 2>&1
LEFT=""
for r in ap-northeast-1 ap-southeast-2; do
  [ "$r" = "$EI_R" ] && continue
  AWS_REGION="$r" AWS_DEFAULT_REGION="$r" aws lambda get-function --function-name "$FN" >/dev/null 2>&1 && LEFT="$LEFT $r"
done
if [ -n "$LEFT" ]; then
  echo "（ほかのリージョン（${LEFT# }）にもサーバーがあるので、共通の IAM ロールは残しました）"
else
  aws iam delete-role-policy --role-name "$ROLE" --policy-name rooms-table 2>/dev/null
  aws iam detach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null
  aws iam delete-role --role-name "$ROLE" 2>/dev/null
fi
echo "消しました。"
