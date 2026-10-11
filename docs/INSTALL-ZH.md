# 中文安装教程：把破碎地牢装到 RG34XX

适用：**普通 RG34XX（H700，720×480，1GB 内存）＋ NextUI**。这是社区适配版，游戏默认简体中文。其他系统和机型暂未验证。

**安装流程：下载游戏和 Java 文件 → 关机取出 SD 卡 → 按下方路径复制 → 插卡开机 → Ports 中启动。无需编译，也不用终端。**

[返回仓库首页](../README.md) · [打开下载页面](https://github.com/Drafffffff/shattered-pixel-dungeon-nextui/releases/latest)

## 1. 下载哪些文件？

| 要下载的文件 | 点击下载 | 用途 |
| --- | --- | --- |
| `Shattered-Pixel-Dungeon-v3.3.8-nextui.1-RG34XX.zip`（约 40 MB） | **[下载游戏安装包](https://github.com/Drafffffff/shattered-pixel-dungeon-nextui/releases/download/v3.3.8-nextui.1/Shattered-Pixel-Dungeon-v3.3.8-nextui.1-RG34XX.zip)** | 必下，解压后复制游戏文件 |
| `zulu17.54.21-ca-jre17.0.13-linux.squashfs`（约 45 MB） | **[下载 Java 运行库](https://github.com/PortsMaster/PortMaster-New/releases/download/2025-01-20_2237/zulu17.54.21-ca-jre17.0.13-linux.squashfs)** | SD 卡里没有同名文件时下载；保持原样，不解压 |

游戏直链对应目前的 `v3.3.8-nextui.1`。以后更新时，打开[最新 Release](https://github.com/Drafffffff/shattered-pixel-dungeon-nextui/releases/latest)，选择文件名以 **`-RG34XX.zip`** 结尾的附件。

**只想玩游戏，不需要下载** `source.tar.gz`、`third-party-sources.tar.gz`、`Source code (zip)` 或 `Source code (tar.gz)`。它们是给开发者看的源码。`SHA256SUMS` 是可选的下载校验文件。

Java 文件来自 [PortMaster 官方项目](https://github.com/PortsMaster/PortMaster-New)，不是 Windows 的 Java 安装程序。请使用上面的同名文件，不要换成其他架构或版本。

## 2. 先找到 SD 卡的正确位置

1. 如果正在玩游戏，先保存退出；本游戏可以按 **Select＋Start** 保存退出。
2. 正常关闭掌机，取出 SD 卡，用读卡器插到电脑。
3. 打开卡里**能看到 `Roms` 和 `Emus` 的位置**，这就是本教程所说的“SD 卡根目录”。不用把卡名改成 `SDCARD`。
4. 如果电脑提示格式化而你看不到这些文件夹，先取消，确认打开的是 NextUI 的游戏数据分区；安装本游戏不需要格式化。

先确认卡里有：

```text
SD 卡根目录/
└── Emus/
    └── h700/
        └── PORTS.pak/
```

**已经有 `PORTS.pak`：直接去第 3 步，不要重复覆盖它。**

如果没有，这是尚未安装 NextUI 的 H700 Ports 支持包：下载社区项目的 [PORTS.pak.zip](https://github.com/Logarythms/nextui-portmaster-h700/releases/download/v0.4.0/PORTS.pak.zip)，解压，把得到的 **`PORTS.pak` 文件夹**放到卡里的 **`Emus/h700/`**。该支持包要求 NextUI rc11 或更新版本；具体准备步骤见它的[安装说明](https://github.com/Logarythms/nextui-portmaster-h700#install)。本教程后面的操作都以这个目录已经存在为前提。

## 3. 放好 Java 运行库

打开 SD 卡里的：

```text
Emus/h700/PORTS.pak/PortMaster/libs/
```

如果缺少 `PortMaster` 或 `libs` 文件夹，就在上述位置按名字新建。把下载的 **`zulu17.54.21-ca-jre17.0.13-linux.squashfs`** 放进 `libs`。

放好后的完整位置必须是：

```text
SD 卡根目录/Emus/h700/PORTS.pak/PortMaster/libs/zulu17.54.21-ca-jre17.0.13-linux.squashfs
```

**不要解压、不要改名。** 已经有这个同名文件，可以跳过这一步。

## 4. 解压游戏，复制两个部分

在电脑上解压下载的 **`…-RG34XX.zip`**，然后打开解压内容里的 **`Roms` → `Ports (PORTS)`**。

里面有两个需要复制的部分：

```text
Roms/
└── Ports (PORTS)/
    ├── Shattered Pixel Dungeon.sh       ← 菜单入口
    └── .ports/                         ← 隐藏文件夹
        └── shattered-rg34xx/           ← 游戏程序，整个文件夹都要复制
```

**先让电脑显示隐藏文件，否则会漏掉 `.ports`：**

- **Mac**：在 Finder 中按 **Command＋Shift＋句号（.）**。
- **Windows 11**：资源管理器 → 查看 → 显示 → 隐藏的项目。Windows 10 在“查看”选项卡勾选“隐藏的项目”。

接下来按这两行复制，文件夹不存在时按名字新建：

| 从解压包里复制 | 放到 SD 卡的哪里 |
| --- | --- |
| `Roms/Ports (PORTS)/Shattered Pixel Dungeon.sh` | `Roms/Ports (PORTS)/` 里面 |
| `Roms/Ports (PORTS)/.ports/shattered-rg34xx` **整个文件夹** | `Roms/Ports (PORTS)/.ports/` 里面 |

更新时允许替换**这个游戏**的同名文件。不要把整张卡的 `Roms`、整个 `Ports (PORTS)` 或整个 `.ports` 文件夹删掉再换，也不要多套一层 `shattered-rg34xx`。

完成后，卡里的目录应当像这样：

```text
SD 卡根目录/
├── Emus/
│   └── h700/
│       └── PORTS.pak/
│           └── PortMaster/
│               └── libs/
│                   └── zulu17.54.21-ca-jre17.0.13-linux.squashfs
└── Roms/
    └── Ports (PORTS)/
        ├── Shattered Pixel Dungeon.sh
        └── .ports/
            └── shattered-rg34xx/
                ├── shattered-rg34xx.jar
                ├── lib/
                │   ├── libshattered_sdl.so
                │   └── ……其他 jar 文件，全部保留
                └── ……许可与版本说明文件，全部保留
```

`INSTALL.md` 是说明书，不用放进游戏目录。游戏素材已包含在包里，无需另找数据文件。

## 5. 插卡开机，开始游戏

1. 在电脑上安全弹出 SD 卡，再插回掌机。
2. 开机进入 NextUI，打开 **Ports**。
3. 选择 **Shattered Pixel Dungeon**，按 A 启动。首次启动请稍等加载。
4. 首页选择新的冒险；有本适配版存档时可以继续冒险。

**看到首页，能用十字键选择并按 A 确认，就完成安装了。** 本游戏无需每次先打开 PortMaster，也不需要连接电脑。

## 6. 先记住这些按键

| 按键 | 做什么 |
| --- | --- |
| 十字键 | 行走、选择菜单和目标；相邻方向一起按可以斜走 |
| A | 确定、互动、捡脚下的物品，附近有怪也能捡 |
| 短按 B | 查看目标；菜单中返回，选目标时取消 |
| 长按 B 至少半秒后松开 | 搜索周围，**会消耗回合**；只在正常探索时生效 |
| X | 打开背包 |
| Y / 长按 Y | 使用当前快捷格 / 更换或清空当前快捷格 |
| L1 / R1 | 向左 / 向右切换快捷格；弹窗里切换标签页 |
| 短按 Select | 查看英雄、技能和当前效果 |
| 长按 Select | 全屏地图；方向移动视野，L2/R2 缩放，A 回到角色，B 退出 |
| Start | 暂停菜单、设置、日志与图鉴、搜索周围等 |
| Menu | 等待一回合 |
| Select＋Start | **保存退出游戏** |

地图只显示已知区域，不会揭开未探索的房间。查看目标不耗回合，搜索会耗回合。角色升级不会自动加力量，力量通常通过喝力量药剂提升。

[查看完整按键和功能说明](../README.md#controls--按键)

## 以后怎么更新？存档会不会丢？

保存退出、正常关机，再按第 4 步复制新版的两个部分即可。Java 同名文件已经存在时，不必重新下载。

本适配版的存档和设置在：

```text
SD 卡根目录/.userdata/shared/shattered-rg34xx/
```

更新包不包含这个目录，按教程复制不会覆盖它。更新前可以把整个 `shattered-rg34xx` 存档文件夹复制到电脑备份。原 PortMaster 版与本适配版的存档目录不同，不会自动导入原版存档。

原封面位于 `Roms/Ports (PORTS)/.media/Shattered Pixel Dungeon.png`，安装包不会覆盖它；没有旧封面时不显示封面并不影响游玩。

如果菜单里还留着早期入口 **Shattered RG34XX**，只删除 `Roms/Ports (PORTS)/Shattered RG34XX.sh`，保留新的 `Shattered Pixel Dungeon.sh`。**不要删除 `.ports/shattered-rg34xx`，它仍然是当前版本的程序目录。**

## 遇到问题，先对照这里

| 现象 | 先检查什么 |
| --- | --- |
| NextUI 没有 Ports 分类 | 第 2 步的 `Emus/h700/PORTS.pak` 是否存在；`Roms/Ports (PORTS)` 中是否放了游戏 `.sh` 文件；然后正常重启 |
| Ports 里没有 Shattered Pixel Dungeon | `.sh` 是否放在 `Roms/Ports (PORTS)/` 的第一层，而不是又多套了一层下载包文件夹 |
| 点开后回到菜单 | 最常见是漏复制隐藏的 `.ports/shattered-rg34xx`，或 Java 文件路径/名字不对；对照第 4 步目录图 |
| Windows 把脚本当文本文档 | 直接复制包里的 `.sh` 原文件，不要自行创建 `.sh.txt` |
| 提示已在运行，实际已经退出 | 正常关机后重新开机再试，不要反复启动多个副本 |
| 更新后没有找到原来的角色 | 确认原来玩的是本适配版；不要删除 `.userdata` 或重建存档 |

仍无法启动时，打开卡里的 `.userdata/shared/shattered-rg34xx/launch.log`，到本仓库[提交问题](https://github.com/Drafffffff/shattered-pixel-dungeon-nextui/issues)，附上机型、NextUI 版本、出现问题的步骤和日志末尾相关部分。发日志前检查并遮掉个人信息；不需要公开上传存档。

[返回仓库首页](../README.md) · [下载最新版本](https://github.com/Drafffffff/shattered-pixel-dungeon-nextui/releases/latest)
