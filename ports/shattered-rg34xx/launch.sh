#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -eu
SDCARD_PATH=${SDCARD_PATH:-/mnt/SDCARD}
SYSTEM_PATH=${SYSTEM_PATH:-$SDCARD_PATH/.system/h700}
GAMEDIR="$SDCARD_PATH/Roms/Ports (PORTS)/.ports/shattered-rg34xx"
export SPD_SAVE_DIR="$SDCARD_PATH/.userdata/shared/shattered-rg34xx"
RUNTIME="$SDCARD_PATH/Emus/h700/PORTS.pak/PortMaster/libs/zulu17.54.21-ca-jre17.0.13-linux.squashfs"
MOUNT="/tmp/shattered-rg34xx-java"
mkdir -p "$SPD_SAVE_DIR" "$MOUNT"
exec >>"$SPD_SAVE_DIR/launch.log" 2>&1
# PortMaster's SDL interposer uses RTLD_NEXT, which cannot resolve SDL loaded
# through JVM/JNI's local library scope. This port handles raw buttons itself.
unset LD_PRELOAD
unset GT_INPUT_REMAP GT_HUD
# Atomic lock avoids two JVMs sharing a framebuffer and save directory.
LOCK=/tmp/shattered-rg34xx.lock
if ! mkdir "$LOCK" 2>/dev/null; then
 echo 'Shattered Pixel Dungeon is already running (or stale lock).'; exit 1
fi
mounted=0
cleanup() { [ "$mounted" = 0 ] || umount "$MOUNT"; rmdir "$LOCK"; }
trap cleanup EXIT
JAVA_PID=
stop() { [ -z "$JAVA_PID" ] || kill -TERM "$JAVA_PID" 2>/dev/null || true; }
trap stop INT TERM
[ -f "$RUNTIME" ] || { echo 'Missing PortMaster Zulu 17 runtime'; exit 1; }
mount -t squashfs -o loop,ro "$RUNTIME" "$MOUNT"
mounted=1
export JAVA_HOME="$MOUNT"
export SDL_VIDEODRIVER=mali SDL_AUDIODRIVER=alsa
export SDL_JOYSTICK_DISABLE_UDEV=1 SDL_HIDAPI_DISABLE_UDEV=1
export SDL_VIDEO_EGL_DRIVER=/usr/lib/libEGL.so
export SDL_VIDEO_GL_DRIVER=/usr/lib/libGLESv2.so
export LD_LIBRARY_PATH="$SYSTEM_PATH/lib:/usr/lib:/usr/lib/aarch64-linux-gnu:/lib/aarch64-linux-gnu"
export ALSOFT_DRIVERS=alsa
cd "$GAMEDIR"
"$JAVA_HOME/bin/java" -Xms32m -Xmx192m -Xss512k -XX:+UseSerialGC \
 -XX:MaxDirectMemorySize=64m -XX:ActiveProcessorCount=2 \
 -Djava.library.path="$GAMEDIR/lib" -Dorg.lwjgl.opengles.libname=/usr/lib/libGLESv2.so \
 ${SPD_TEST_OPTIONS:-} -cp "$GAMEDIR/shattered-rg34xx.jar:$GAMEDIR/lib/*" org.nextui.shattered.RgLauncher &
JAVA_PID=$!
status=0
wait "$JAVA_PID" || status=$?
# A signal can interrupt wait before the child finishes saving.
if kill -0 "$JAVA_PID" 2>/dev/null; then wait "$JAVA_PID" || status=$?; fi
exit "$status"
