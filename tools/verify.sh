#!/usr/bin/env bash
# Runs every automatic check that works without the Android SDK:
#   1. rebuilds the stage pack and confirms the build is reproducible
#   2. engine + real stage pack: walkthrough, skips, dead-end search, two players (in memory and over HTTP)
#   3. room server against memory and a DynamoDB mock
#   4. deploy.sh carries the current server code, and deploys and removes cleanly against a mock of AWS
#   5. the engine's handling of the server setting
#   6. the app's Kotlin type-checks against stand-ins for Android and Compose
# Needs: Python 3 (Pillow, cryptography; optional boto3, moto[server], awscli), rsvg-convert, the Yomogi font, Java, a Gradle install.
set -uo pipefail
cd "$(dirname "$0")/.."
FAIL=0
step() { printf '\n### %s\n' "$*"; }

step "1. stage pack"
python3 spoiler/build_pack.py > /tmp/ei-build.log 2>&1 || { cat /tmp/ei-build.log; FAIL=1; }
tail -1 /tmp/ei-build.log
cp app/src/main/assets/stage.pack /tmp/ei-pack-1
python3 spoiler/build_pack.py > /dev/null 2>&1
cmp -s /tmp/ei-pack-1 app/src/main/assets/stage.pack && echo "ok    the pack build is reproducible" || { echo "FAIL  pack differs between two builds"; FAIL=1; }

step "2. engine and stage"
EI_KEY=verify-key python3 server/local_server.py 18080 > /tmp/ei-local.log 2>&1 &
SERVER=$!
sleep 1.5
EI_KEY=verify-key tools/kt.sh /tmp/ei-verify VerifyKt spoiler/verify -- app/src/main/assets/stage.pack http://127.0.0.1:18080/ > /tmp/ei-verify.log 2>&1 || FAIL=1
kill $SERVER 2>/dev/null
grep -c "^ok" /tmp/ei-verify.log | sed 's/^/checks passed: /'
grep -v "^ok" /tmp/ei-verify.log

step "3. room server"
python3 server/test_server.py > /tmp/ei-server.log 2>&1 || FAIL=1
grep -c "^ok" /tmp/ei-server.log | sed 's/^/checks passed: /'
grep -v "^ok" /tmp/ei-server.log

step "4. deploy script"
python3 server/make_deploy.py --check || FAIL=1
bash -n server/deploy.sh && bash -n server/remove.sh || FAIL=1
python3 server/test_deploy.py > /tmp/ei-deploy.log 2>&1 || FAIL=1
grep -c "^ok" /tmp/ei-deploy.log | sed 's/^/checks passed: /'
grep -v "^ok" /tmp/ei-deploy.log

step "5. engine parts outside the stages"
tools/kt.sh /tmp/ei-enginecheck EngineCheckKt tools/enginecheck > /tmp/ei-engine.log 2>&1 || FAIL=1
grep -c "^ok" /tmp/ei-engine.log | sed 's/^/checks passed: /'
grep -v "^ok" /tmp/ei-engine.log

step "6. app type-check"
tools/typecheck/run.sh > /tmp/ei-type.log 2>&1
grep -q "TYPECHECK OK" /tmp/ei-type.log || FAIL=1
grep -v "warning:\|^ *\^\|^        val c = URL" /tmp/ei-type.log

echo
[ "$FAIL" = 0 ] && echo "=== EVERYTHING PASSED ===" || echo "=== SOMETHING FAILED ==="
exit $FAIL
