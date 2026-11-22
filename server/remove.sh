#!/usr/bin/env bash
# Exit Interview のサーバーを AWS から消します（CloudShell に貼り付けるか、bash server/remove.sh）。部屋のデータも消えます。
EI_R="${EI_REGION:-${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-southeast-2}}}"
export AWS_REGION="$EI_R" AWS_DEFAULT_REGION="$EI_R" AWS_PAGER=""
FN=exit-interview-rooms; ROLE=exit-interview-lambda; TABLE=ExitInterviewRooms
aws lambda delete-function-url-config --function-name "$FN" >/dev/null 2>&1
aws lambda delete-function --function-name "$FN" >/dev/null 2>&1
aws iam delete-role-policy --role-name "$ROLE" --policy-name rooms-table 2>/dev/null
aws iam detach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null
aws iam delete-role --role-name "$ROLE" 2>/dev/null
aws dynamodb delete-table --table-name "$TABLE" >/dev/null 2>&1
echo "消しました。"
