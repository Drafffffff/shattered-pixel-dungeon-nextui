# Shattered Pixel Dungeon for NextUI

Unofficial, open-source RG34XX adaptation of Shattered Pixel Dungeon **4.0.2**. Designed for the ordinary RG34XX: H700, 720×480, 1 GB RAM, D-pad and buttons, no analog sticks. 简体中文默认开启。

Based on [Shattered Pixel Dungeon](https://github.com/00-Evan/shattered-pixel-dungeon) by Evan Debenham, [Pixel Dungeon](https://github.com/00-Evan/pixel-dungeon-gradle) by Watabou, and the controller work from [avvstrk's 3.3.8 fork](https://github.com/avvstrk/shattered-pixel-dungeon-dpad) at `914561b0b8b98493bd77431f9578ab58fae67029`. The game source now tracks official **v4.0.2**, commit `57a4e06a4caf162446d1c28caa7983f0493fecf0`. This community port is not an official Shattered Pixel release. Please support the original developers.

## Install / 安装

1. Download the **RG34XX.zip** asset from Releases. This targets **NextUI on the ordinary RG34XX**, not stock firmware or all XX models.
2. Install PortMaster and its Zulu 17 runtime first. Required file:
   `Emus/h700/PORTS.pak/PortMaster/libs/zulu17.54.21-ca-jre17.0.13-linux.squashfs` on the SD card. The runtime is not included in this release.
3. Save and exit the game, then shut down normally before removing the SD card. Back up existing saves before updating.
4. Extract the zip into the SD card root, **merging** its `Roms` directory. Hidden `.ports` contents must also be copied. Allow replacement of this game's files. Never replace the whole Ports directory.
5. Open **Ports → Shattered Pixel Dungeon**. Existing `.media/Shattered Pixel Dungeon.png` artwork is preserved: this package does not overwrite covers.

The canonical launcher is `Roms/Ports (PORTS)/Shattered Pixel Dungeon.sh`. If updating an early development install, delete only the obsolete `Shattered RG34XX.sh` launcher. Keep `.ports/shattered-rg34xx`, which is still the program directory.

Saves/settings: `.userdata/shared/shattered-rg34xx/`. Updates do not ship or overwrite this directory. Existing saves from this adaptation continue here; the original PortMaster port uses a separate directory and is not automatically imported. Log: `launch.log` in the save directory.

## Upgrading from 3.3.8 / 从旧版升级

[迁移说明、旧存档与回退注意事项](../../docs/MIGRATION-4.0.2.md)

Save and exit, back up `.userdata/shared/shattered-rg34xx/`, and install the new game package into the same paths. Java and controls are unchanged. Legacy saves are loaded through upstream compatibility logic; unfinished tutorials with an existing hero continue to the home screen instead of creating another character. Existing saves may retain old quest content according to upstream rules; start a new adventure to experience the complete 4.0 quest flow. A save written by 4.0.2 should not be opened with 3.3.8: restore the pre-upgrade backup if rolling back.

## Controls / 按键

| Button | Action |
| --- | --- |
| D-pad | Move; navigate menus, inventory and target tiles. Adjacent directions together move diagonally. |
| A | Confirm/interact; pick up underfoot even near enemies; confirm selected target. |
| B (short) | Inspect target, equivalent to PC E; back in windows; cancel targeting. |
| B (hold ≥0.55 s, then release) | **Search surroundings** while exploring; consumes a turn. Start → Search is an alternative. |
| X | Inventory; character keyboard when editing text. |
| Y | Use selected quickslot; hold to replace/clear it. In inventory, assign item to a slot. A/Y both confirm targeting. |
| L1 / R1 | Previous/next quickslot in actual screen order; switch tabs/targets where applicable. |
| L2 / R2 | Zoom out/in. |
| Start | Pause menu: settings, journal/catalog, search, map, rest, controls, save/exit. |
| Select (short) | Hero, talents and active effects; D-pad/A opens each effect description. |
| Select (hold) | Fullscreen map of the known floor: D-pad pans, L2/R2 zoom, A centers hero, B exits. |
| Menu (release) | Wait one turn. |
| Select + Start | Save and exit normally. |
| Volume | System volume with numeric overlay (0–20). |
| Menu + Volume | Brightness with numeric overlay (0–10); no wait action. |
| Select + Volume | Color temperature (0–40); no hero window. |

**B gestures apply only during exploration.** In a window, target selection, or map, B cancels immediately; holding it does not search. Search is distinct from inspecting yourself, which shows hero information.

Full map opens at floor overview, hides HUD and highlights the hero in cyan. It retains fog of war and consumes no turns. Closing it restores the prior camera. Six quickslots support replacement and clearing; selected slot, including an empty slot, survives stairs and save/reload. Journal opens directly and remembers tabs, selection and scroll. Windows use border focus and move focus into new dialogs. Transition scenes hide the pointer.

Home retains the original background and three compact entries. Saves can be deleted with a confirmation defaulting to cancel. Tutorial reminders appear once per page; game progression and unread pages retain upstream rules. Strength increases through strength potions, not ordinary character levels. Equipment descriptions clarify known strength requirements without identifying hidden stats.

## Build / 构建

Requires Python 3, Git, the `patch` command, Docker and internet access for checksum-pinned Maven dependencies and two digest-pinned Docker images. Run from the repository root:

```sh
./ports/shattered-rg34xx/build.sh
```

The public repository includes the complete upstream source snapshot in `vendor/shattered-pixel-dungeon/` and its SHA256 manifest. `fetch.py` verifies it and copies it into `build/shattered-rg34xx/source/`; patches apply only to that build copy. The original D-pad changes are carried as `controller-base.patch`, rebased onto 4.0.2; RG34XX patches are then applied by `prepare-source.py` and `interaction-patches.py`. The same fetch script can download the official pinned Git revision when a vendored snapshot is not present. To rebuild from pristine sources, remove the build source directory first.

Outputs: `build/shattered-rg34xx/dist/`. Java is compiled with `--release 11` using JDK 17; the JNI bridge uses the pinned H700 toolchain. Binary dependency hashes are in `dependencies.json`. Dependency source/notice hashes are in `third-party/sources-lock.json`; the corresponding archives are supplied as a separate Release asset.

For SSH installation after building, with the game saved and exited:

```sh
./ports/shattered-rg34xx/install.sh root@DEVICE_IP
```

Installer stages a new program directory, keeps the previous version at `.ports/shattered-rg34xx.previous`, preserves saves and artwork, and removes the obsolete duplicate launcher. It never stops NextUI. Do not send signals to `nextui.elf`: on this device that can shut the machine down.

For a release from a clean committed public checkout, run `python3 ports/shattered-rg34xx/package-release.py v4.0.2-nextui.1` after building. This verifies and downloads corresponding dependency sources, packages the SD-card zip, archives the committed source, and writes SHA256SUMS under `build/shattered-rg34xx/release/`.

## Rendering, memory and verification

SDL2 Mali backend creates a GLES2 context directly; no Weston/X11 or mouse emulation. Raw H700 evdev mapping matches NextUI (A=304, B=305, X=307, Y=306). The bridge preserves JVM signal handlers across SDL initialization. The launcher clears inherited PortMaster SDL interposers.

Default Chinese, compact landscape UI, 3× scaling (240×160 logical canvas); Chinese glyphs are generated on demand. Frame cap 30 fps, Java heap 32–192 MiB, direct buffers capped at 64 MiB, SerialGC. Heap limits are not total process memory limits.

The previous 3.3.8 adaptation measured around **29–30 fps and 149–181 MiB RSS** on representative RG34XX dungeon gameplay. These numbers are a historical baseline, not measurements of this 4.0.2 release. These samples do not establish worst-case memory or long-session stability for every class, effect or audio path. Other handhelds and firmware are unverified. Text entry supports a D-pad Latin/digit keyboard; Chinese display is supported, but Pinyin input is not included.

ARM64/Mesa real-rendering regression covers onboarding/recovery, inspect/search gestures, target cancellation, modal focus and scroll alignment, map isolation/zoom/HUD/hero marker, Buff and catalog entries, journal memory, quickslot management and persistence, combat pickup, text rollback, alchemy, death menus, and system combinations. Tests run on local save copies and do not replace physical hardware testing:

```sh
docker build -t shattered-rg34xx-smoke:local -f ports/shattered-rg34xx/Dockerfile.smoke .
python3 ports/shattered-rg34xx/interaction-test.py --resume-from /path/to/save-copy
python3 ports/shattered-rg34xx/hotbar-memory-test.py --resume-from /path/to/save-copy
python3 ports/shattered-rg34xx/migration-test.py --resume-from /path/to/3.3.8-save-copy
./ports/shattered-rg34xx/signal-test.sh
```

Test command handling is disabled by default; it requires the explicit JVM `nextui.commands` property. No personal saves or device logs are distributed.

## License and attribution

Game and original adaptation code: **GPL-3.0-or-later**; upstream copyright and asset notices remain intact in the vendored tree. `java/Lwjgl3GLES20.java` is derived from libGDX under Apache-2.0 and preserves its header. See root `LICENSE.txt`, `THIRD_PARTY_NOTICES.md` and `licenses/`. Third-party components retain their own licenses. Java, system SDL2/Mali and NextUI are external prerequisites, not bundled software. Distributed LGPL libraries remain separate, replaceable files in `lib/`; their source archives accompany the Release.
