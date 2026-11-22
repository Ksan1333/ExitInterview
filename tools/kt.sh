#!/usr/bin/env bash
# Compiles the pure-Kotlin engine (plus any extra source dirs) with the Kotlin compiler that ships
# inside a local Gradle install, then runs a main class. For machines without Android Studio.
#   tools/kt.sh <out-dir> <MainClassKt> [extra source dirs...] [-- program args...]
set -euo pipefail
L="${GRADLE_LIB:-/opt/gradle/lib}"
V="$(ls "$L" | sed -n 's/^kotlin-compiler-embeddable-\(.*\)\.jar$/\1/p' | head -1)"
KC="$L/kotlin-compiler-embeddable-$V.jar:$L/kotlin-stdlib-$V.jar:$L/kotlin-script-runtime-$V.jar:$L/kotlin-reflect-$V.jar:$L/kotlin-daemon-embeddable-$V.jar:$(ls $L/trove4j-*.jar):$(ls $L/annotations-*.jar | head -1):$(ls $L/kotlinx-coroutines-core-jvm-*.jar)"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$1"; MAIN="$2"; shift 2
SRC=("$ROOT/app/src/main/java/com/ksan/exitinterview/engine")
while [ $# -gt 0 ] && [ "$1" != "--" ]; do SRC+=("$1"); shift; done
[ "${1:-}" = "--" ] && shift
mkdir -p "$OUT"
java -cp "$KC" org.jetbrains.kotlin.cli.jvm.K2JVMCompiler -no-stdlib -no-reflect -jvm-target 17 -nowarn \
  -cp "$L/kotlin-stdlib-$V.jar" -d "$OUT" "${SRC[@]}" 2>&1 | grep -v "^Picked up" || true
[ "$MAIN" = "-" ] && exit 0
java -cp "$OUT:$L/kotlin-stdlib-$V.jar" "$MAIN" "$@" 2>&1 | grep -v "^Picked up"
