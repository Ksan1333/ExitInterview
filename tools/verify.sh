#!/usr/bin/env bash
# Runs every automatic check that works without the Android SDK:
#   1. rebuilds both stage packs, confirms each build is reproducible and that the shipped packs match the sources
#   2. engine + real stage packs: walkthrough, skips, dead-end search, two players (in memory and over HTTP)
#   3. room server against memory and a DynamoDB mock
#   4. deploy.sh carries the current server code, and deploys and removes cleanly against a mock of AWS
#   5. the engine's handling of the server setting
#   6. the app's Kotlin type-checks against stand-ins for Android and Compose
# Needs: Python 3 (Pillow, cryptography; optional boto3, moto[server], awscli), rsvg-convert or resvg (EI_RESVG), the Yomogi
# font, Java, a Gradle install. Set PYTHON when Python 3 is not called python3. The logs stay in the folder printed at the end.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
T="$(mktemp -d)"
FAIL=0
step() { printf '\n### %s\n' "$*"; }

step "1. stage packs"
# The shipped packs are never overwritten here. Pictures drawn by another SVG renderer differ by a few bytes (episode 1
# was drawn with rsvg-convert, episode 2 with resvg), so then the shipped pack is compared by its definitions.
for n in "" 2; do
  "$PY" spoiler/build_pack$n.py --out "$T/stage$n-a.pack" > "$T/build$n.log" 2>&1 || { cat "$T/build$n.log"; FAIL=1; }
  tail -1 "$T/build$n.log"
  "$PY" spoiler/build_pack$n.py --out "$T/stage$n-b.pack" > /dev/null 2>&1
  cmp -s "$T/stage$n-a.pack" "$T/stage$n-b.pack" && echo "ok    stage$n.pack: the build is reproducible" || { echo "FAIL  stage$n.pack: two builds differ"; FAIL=1; }
  if cmp -s "$T/stage$n-a.pack" "app/src/main/assets/stage$n.pack"; then
    echo "ok    stage$n.pack: the shipped pack is exactly the build"
  elif "$PY" spoiler/packdiff.py "app/src/main/assets/stage$n.pack" "$T/stage$n-a.pack"; then
    echo "ok    stage$n.pack: the shipped pack has the same definitions (pictures drawn by another renderer)"
  else
    echo "FAIL  stage$n.pack: the shipped pack is not built from the current sources"; FAIL=1
  fi
done

step "2. engine and stages"
EI_KEY=verify-key "$PY" server/local_server.py 18080 > "$T/local.log" 2>&1 &
SERVER=$!
sleep 1.5
EI_KEY=verify-key tools/kt.sh "$T/verify" VerifyKt spoiler/verify -- app/src/main/assets/stage.pack http://127.0.0.1:18080/ > "$T/verify.log" 2>&1 || FAIL=1
EI_KEY=verify-key tools/kt.sh "$T/verify2" Verify2Kt spoiler/verify2 -- app/src/main/assets/stage2.pack http://127.0.0.1:18080/ > "$T/verify2.log" 2>&1 || FAIL=1
kill $SERVER 2>/dev/null
for n in "" 2; do
  grep -c "^ok" "$T/verify$n.log" | sed "s/^/episode ${n:-1}: checks passed: /"
  grep -v "^ok" "$T/verify$n.log"
done

step "3. room server"
"$PY" server/test_server.py > "$T/server.log" 2>&1 || FAIL=1
grep -c "^ok" "$T/server.log" | sed 's/^/checks passed: /'
grep -v "^ok" "$T/server.log"

step "4. deploy script"
"$PY" server/make_deploy.py --check || FAIL=1
bash -n server/deploy.sh && bash -n server/remove.sh || FAIL=1
"$PY" server/test_deploy.py > "$T/deploy.log" 2>&1 || FAIL=1
grep -c "^ok" "$T/deploy.log" | sed 's/^/checks passed: /'
grep -v "^ok" "$T/deploy.log"

step "5. engine parts outside the stages"
tools/kt.sh "$T/enginecheck" EngineCheckKt tools/enginecheck > "$T/engine.log" 2>&1 || FAIL=1
grep -c "^ok" "$T/engine.log" | sed 's/^/checks passed: /'
grep -v "^ok" "$T/engine.log"

step "6. app type-check"
tools/typecheck/run.sh > "$T/type.log" 2>&1
grep -q "TYPECHECK OK" "$T/type.log" || FAIL=1
grep -v "warning:\|^ *\^\|^        val c = URL" "$T/type.log"

echo
echo "logs: $T"
[ "$FAIL" = 0 ] && echo "=== EVERYTHING PASSED ===" || echo "=== SOMETHING FAILED ==="
exit $FAIL
