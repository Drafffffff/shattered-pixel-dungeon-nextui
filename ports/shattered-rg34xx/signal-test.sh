#!/bin/bash
# Regression: simulate SDL replacing HotSpot signal handlers, then exercise JIT.
set -euo pipefail
cd "$(dirname "$0")/../.."
B=build/shattered-rg34xx
mkdir -p "$B/signal-probe"
docker run --rm -v "$PWD:/work" -w /work ghcr.io/loveretro/h700-toolchain@sha256:c9d160c407570a771683e6a471757b44f6e155a7df7d1804c70f901ee3890da3 bash -c '
/opt/aarch64-nextui-linux-gnu/bin/aarch64-nextui-linux-gnu-gcc -O2 -fPIC -shared -Ibuild/shattered-rg34xx/jni -Ibuild/shattered-rg34xx/jni/linux -I/opt/nextui/include/SDL2 -D_REENTRANT ports/shattered-rg34xx/native/sdl_bridge.c ports/shattered-rg34xx/tests/signal_wrap.c -Wl,--wrap=SDL_Init -o build/shattered-rg34xx/signal-probe/libshattered_sdl.so -L/opt/nextui/lib -lSDL2'
docker run --rm -v "$PWD:/work" -w /work eclipse-temurin@sha256:5d6042fb8cdc14d614e4e421f52e3211fc5aeadddce44cbf9de8ed37c791f824 javac --release 11 -cp "$B/dist/shattered-rg34xx.jar" -d "$B/signal-probe" ports/shattered-rg34xx/tests/SignalProbe.java
docker run --rm --init -v "$PWD/$B:/test" shattered-rg34xx-smoke:local xvfb-run -a java -Xmx64m -XX:+UseSerialGC -Djava.library.path=/test/signal-probe -cp /test/signal-probe:/test/dist/shattered-rg34xx.jar org.nextui.shattered.SignalProbe
