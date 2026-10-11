#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT="$PWD"
BUILD="$ROOT/build/shattered-rg34xx"
OUT="$BUILD/dist"
mkdir -p "$OUT/lib" "$BUILD/jni"
rm -f "$OUT/.build-ok"
python3 ports/shattered-rg34xx/fetch.py
python3 ports/shattered-rg34xx/prepare-source.py "$BUILD/source"
docker run --rm -v "$ROOT:/work" -w /work eclipse-temurin@sha256:5d6042fb8cdc14d614e4e421f52e3211fc5aeadddce44cbf9de8ed37c791f824 bash -c '
set -e
B=build/shattered-rg34xx
cp -R "$JAVA_HOME/include/." "$B/jni/"
rm -rf "$B/classes"
mkdir -p "$B/classes"
find "$B/source/SPD-classes/src/main/java" "$B/source/core/src/main/java" "$B/source/services/src/main/java" ports/shattered-rg34xx/java -name "*.java" > "$B/sources.txt"
printf "%s\n" "$B/source/desktop/src/main/java/com/shatteredpixel/shatteredpixeldungeon/desktop/DesktopPlatformSupport.java" >> "$B/sources.txt"
javac --release 11 -encoding UTF-8 -cp "$B/deps/*" -d "$B/classes" @"$B/sources.txt"
jar --create --file "$B/dist/shattered-rg34xx.jar" -C "$B/classes" . -C "$B/source/core/src/main/assets" . -C "$B/source/desktop/src/main/assets" .
'
docker run --rm -v "$ROOT:/work" -w /work ghcr.io/loveretro/h700-toolchain@sha256:c9d160c407570a771683e6a471757b44f6e155a7df7d1804c70f901ee3890da3 bash -c '
set -e
B=build/shattered-rg34xx
/opt/aarch64-nextui-linux-gnu/bin/aarch64-nextui-linux-gnu-gcc -O2 -fPIC -shared -I"$B/jni" -I"$B/jni/linux" -I/opt/nextui/include/SDL2 -D_REENTRANT ports/shattered-rg34xx/native/sdl_bridge.c -o "$B/dist/lib/libshattered_sdl.so" -L/opt/nextui/lib -lSDL2
'
# Remove obsolete dependency versions when the lock file changes.
rm -f "$OUT"/lib/*.jar
python3 - "$BUILD" "$OUT" <<'PY'
import json, pathlib, shutil, sys
build,out=map(pathlib.Path,sys.argv[1:])
for item in json.loads(pathlib.Path('ports/shattered-rg34xx/dependencies.json').read_text()):
    shutil.copy2(build/'deps'/item['file'],out/'lib'/item['file'])
PY
cp "$BUILD/source/LICENSE.txt" "$OUT/" 2>/dev/null || cp "$BUILD/source/LICENSE" "$OUT/"
touch "$OUT/.build-ok"
echo "Built $OUT"
