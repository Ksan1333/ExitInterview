#!/usr/bin/env bash
# Type-checks every Kotlin file of the app against small stand-ins for Android and Compose.
# It cannot replace a real build (no Compose compiler plugin, no resources), but it catches
# typos, missing imports and mismatches between the screens and the engine without the Android SDK.
set -euo pipefail
L="${GRADLE_LIB:-/opt/gradle/lib}"
V="$(ls "$L" | sed -n 's/^kotlin-compiler-embeddable-\(.*\)\.jar$/\1/p' | head -1)"
KC="$L/kotlin-compiler-embeddable-$V.jar:$L/kotlin-stdlib-$V.jar:$L/kotlin-script-runtime-$V.jar:$L/kotlin-reflect-$V.jar:$L/kotlin-daemon-embeddable-$V.jar:$(ls $L/trove4j-*.jar):$(ls $L/annotations-*.jar | head -1):$(ls $L/kotlinx-coroutines-core-jvm-*.jar)"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$(mktemp -d)"
java -cp "$KC" org.jetbrains.kotlin.cli.jvm.K2JVMCompiler -no-stdlib -no-reflect -jvm-target 17 \
  -cp "$L/kotlin-stdlib-$V.jar:$(ls $L/kotlinx-coroutines-core-jvm-*.jar)" -d "$OUT" \
  "$ROOT/app/src/main/java" "$ROOT/tools/typecheck/stubs" 2>&1 | grep -v "^Picked up" | grep -v "tools/typecheck/stubs" || true
ls "$OUT/com/ksan/exitinterview/MainActivity.class" >/dev/null && echo "TYPECHECK OK"
