#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/../.."
TARGET=${1:-rg34xx}
BUILD="$PWD/build/shattered-rg34xx"
test -f "$BUILD/dist/.build-ok"
test -f "$BUILD/dist/shattered-rg34xx.jar"
# Stage the archive before replacing files; never install over a running JVM.
tar -czf "$BUILD/install.tar.gz" -C "$BUILD/dist" .
scp "$BUILD/install.tar.gz" "$TARGET:/tmp/shattered-rg34xx-install.tar.gz"
scp ports/shattered-rg34xx/launch.sh "$TARGET:/tmp/shattered-rg34xx-launch.sh"
ssh "$TARGET" 'set -e
D="/mnt/SDCARD/Roms/Ports (PORTS)/.ports/shattered-rg34xx"
STAGE="$D.installing"
if pgrep -f "[o]rg.nextui.shattered.RgLauncher" >/dev/null; then echo "Game is running; save and exit before installing."; exit 1; fi
mkdir /tmp/shattered-rg34xx.lock
trap "rmdir /tmp/shattered-rg34xx.lock" EXIT
mkdir -p "$STAGE"
tar -xzf /tmp/shattered-rg34xx-install.tar.gz -C "$STAGE"
test -f "$STAGE/.build-ok"
if [ -d "$D.previous" ]; then rm -rf "$D.previous"; fi
if [ -d "$D" ]; then mv "$D" "$D.previous"; fi
mv "$STAGE" "$D"
PORTS="/mnt/SDCARD/Roms/Ports (PORTS)"
BACKUP="$PORTS/.ports/shattered-entry-backup"
mkdir -p "$BACKUP"
for NAME in "Shattered Pixel Dungeon.sh" "Shattered RG34XX.sh"; do
 if [ -f "$PORTS/$NAME" ] && [ ! -f "$BACKUP/$NAME" ]; then cp "$PORTS/$NAME" "$BACKUP/$NAME"; fi
done
cp /tmp/shattered-rg34xx-launch.sh "$PORTS/Shattered Pixel Dungeon.sh"
chmod +x "$PORTS/Shattered Pixel Dungeon.sh"
rm -f "$PORTS/Shattered RG34XX.sh"
sync'
