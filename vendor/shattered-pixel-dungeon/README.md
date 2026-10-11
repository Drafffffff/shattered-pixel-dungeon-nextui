# Shattered Pixel Dungeon - Better controller support 

This is a GPL-3 mod based on Shattered Pixel Dungeon 3.3.8 that aims to improve controller support on the game. Shattered is now completely playable without a pointer device or analog sticks.
The motivation behind the mod was to make the game more accesible for all the newcoming Linux handhelds. 

## Controls

| Button | Action |
| --- | --- |
| D-Pad | Move the hero; navigate menus, inventory, and tile selection |
| A | Confirm/select; pick up an item beneath the hero when the blue loot button is available; confirm a target tile for weapons, wands, and other targeted items |
| B | Back/cancel |
| X | Open or close inventory |
| Y | Use the selected hotbar entry; hold on an occupied quickslot to reassign it |
| L1 / R1 | Change selected hotbar entry; switch Journal and other tabbed-window tabs |
| L2 / R2 | Zoom out/in |
| Start | Open the pause/options menu |
| Select | Open Hero Info, skills, and active effects |
| Left-stick click | Wait or pick up, as an alternative to A |
| Right-stick click | Virtual left click, retained for advanced compatibility |

## Hotbar

- The hotbar contains eight navigable entries: six quickslots, Search, and Wait
- L1/R1 changes the selected entry
- Y uses the selected entry
- Selecting an empty quickslot opens its item-selection dialog
- Holding Y on an occupied quickslot opens reassignment

## Target Selection

- Weapons, wands, and items that require a target tile can be aimed with the D-Pad
- Moving the D-Pad exits auto-targeting and switches to manual tile selection
- A confirms the selected tile; B cancels

## Inventory and Menus

- The inventory can be fully navigated with the D-Pad
- Dialogs, the title screen, Journal, changelog, hero selection, and run selection are all D-Pad navigable
- L1/R1 switches tabs where applicable

## Camera and Cursor

- The camera remains locked to the hero throughout the run
- Zoom level is preserved without leaving the camera offset after movement

[Shattered Pixel Dungeon](https://shatteredpixel.com/shatteredpd/) is an open-source traditional roguelike dungeon crawler with randomized levels and enemies, and hundreds of items to collect and use. It's based on the [source code of Pixel Dungeon](https://github.com/00-Evan/pixel-dungeon-gradle), by [Watabou](https://watabou.itch.io/).

Shattered Pixel Dungeon currently compiles for Android, iOS, and Desktop platforms. You can find official releases of the game on:

[![Get it on Google Play](https://shatteredpixel.com/assets/images/badges/gplay.png)](https://play.google.com/store/apps/details?id=com.shatteredpixel.shatteredpixeldungeon)
[![Download on the App Store](https://shatteredpixel.com/assets/images/badges/appstore.png)](https://apps.apple.com/app/shattered-pixel-dungeon/id1563121109)
[![Steam](https://shatteredpixel.com/assets/images/badges/steam.png)](https://store.steampowered.com/app/1769170/Shattered_Pixel_Dungeon/)<br>
[![GOG.com](https://shatteredpixel.com/assets/images/badges/gog.png)](https://www.gog.com/game/shattered_pixel_dungeon)
[![Itch.io](https://shatteredpixel.com/assets/images/badges/itch.png)](https://shattered-pixel.itch.io/shattered-pixel-dungeon)
[![Github Releases](https://shatteredpixel.com/assets/images/badges/github.png)](https://github.com/00-Evan/shattered-pixel-dungeon/releases)

If you like this game, please consider [supporting me on Patreon](https://www.patreon.com/ShatteredPixel)!

There is an official blog for this project at [ShatteredPixel.com](https://www.shatteredpixel.com/blog/).

The game also has a translation project hosted on [Transifex](https://explore.transifex.com/shattered-pixel/shattered-pixel-dungeon/).

Note that **this repository does not accept pull requests!** The code here is provided in hopes that others may find it useful for their own projects, not to allow community contribution. Issue reports of all kinds (bug reports, feature requests, etc.) are welcome.

If you'd like to work with the code, you can find the following guides in `/docs`:
- [Compiling for Android.](docs/getting-started-android.md)
    - **[If you plan to distribute on Google Play please read the end of this guide.](docs/getting-started-android.md#distributing-your-app)**
- [Compiling for desktop platforms.](docs/getting-started-desktop.md)
- [Compiling for iOS.](docs/getting-started-ios.md)
- [Recommended changes for making your own version.](docs/recommended-changes.md)