#!/usr/bin/env python3
"""Apply narrowly scoped backend changes to the pinned upstream checkout."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
# UI callbacks can enqueue a hover event while pointer events are dispatched.
# Drain a snapshot, preserving newly queued events for the following frame.
p=root/'SPD-classes/src/main/java/com/watabou/input/PointerEvent.java'
s=p.read_text()
if 'processingEvents' not in s:
    marker='//handle any hover events separately first as we may need to add drag events'
    s=s.replace(marker, 'java.util.ArrayList<PointerEvent> processingEvents = new java.util.ArrayList<>(pointerEvents);\n        pointerEvents.clear();\n\n        '+marker)
    s=s.replace('for (PointerEvent p : pointerEvents)', 'for (PointerEvent p : processingEvents)')
    s=s.replace('\n\t\tpointerEvents.clear();\n\n\t\t//add drag events', '\n\n\t\t//add drag events')
p.write_text(s)
p=root/'SPD-classes/src/main/java/com/watabou/input/ControllerHandler.java'
s=p.read_text()
if 'Boolean.getBoolean("nextui.sdl")' in s:
    s=s.replace('\n\t\tif (Boolean.getBoolean("nextui.sdl")) return false;','').replace('\n\t\tif (Boolean.getBoolean("nextui.sdl")) return true;','')
s=s.replace('public static boolean controllersSupported() {','public static boolean controllersSupported() {\n\t\tif (Boolean.getBoolean("nextui.sdl")) return false;')
s=s.replace('public static boolean isControllerConnected(){','public static boolean isControllerConnected(){\n\t\tif (Boolean.getBoolean("nextui.sdl")) return true;')
s=s.replace('public static boolean vibrationSupported(){','public static boolean vibrationSupported(){\n\t\tif (Boolean.getBoolean("nextui.sdl")) return false;')
p.write_text(s)
# Upstream D-pad snapshot references this query from InventoryPane but omitted it.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/GameScene.java'
s=p.read_text()
if 'public static boolean selectingCell()' not in s:
    s=s.replace('public static void selectCell(', 'public static boolean selectingCell() {\n        return cellSelector != null && cellSelector.listener != null && cellSelector.listener != defaultCellListener;\n    }\n\n    public static void selectCell(', 1)
p.write_text(s)
# Optional text fields must never trap a device with no hardware keyboard.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/windows/WndTextInput.java'
s=p.read_text()
if 'org.nextui.shattered.RgKeyboard' not in s:
    s=s.replace('final RedButton positiveBtn =', '''if (Boolean.getBoolean("nextui.sdl")) {
            RedButton keyboard = new RedButton("X: 字符键盘", 7) {
                @Override protected void onClick() {
                    Game.scene().addToFront(new org.nextui.shattered.RgKeyboard(textBox));
                }
            };
            keyboard.setRect(MARGIN, pos, width-2*MARGIN, BUTTON_HEIGHT);
            add(keyboard);
            pos += BUTTON_HEIGHT + MARGIN;
        }

        final RedButton positiveBtn =''',1)
    s=s.replace('public void onBackPressed() {', '''public boolean onSignal(com.watabou.input.KeyEvent event) {
        if (Boolean.getBoolean("nextui.sdl") && event.pressed && event.code == com.badlogic.gdx.Input.Keys.BUTTON_X) {
            Game.scene().addToFront(new org.nextui.shattered.RgKeyboard(textBox));
            return true;
        }
        return super.onSignal(event);
    }

    @Override
    public void onBackPressed() {
        if (Boolean.getBoolean("nextui.sdl")) { hide(); return; }''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/WelcomeScene.java'
s=p.read_text()
if 'nextui-resume-welcome' not in s:
    marker='if (ShatteredPixelDungeon.versionCode == previousVersion && !SPDSettings.intro()) {'
    s=s.replace(marker, '''// nextui-resume-welcome: unfinished intro must not force another new hero.
        // Keep intro enabled until the saved run completes its own reader flow.
        if (Boolean.getBoolean("nextui.sdl") && ShatteredPixelDungeon.versionCode == previousVersion
                && SPDSettings.intro() && !GamesInProgress.checkAll().isEmpty()) {
            ShatteredPixelDungeon.switchNoFade(TitleScene.class);
            return;
        }

        '''+marker,1)
for key in ('title','body','okay'):
    original=f'Messages.get(WelcomeScene.class, "controller_{key}")'
    replacement=f'(Boolean.getBoolean("nextui.sdl") ? org.nextui.shattered.RgPlatform.controllerHelp("{key}") : {original})'
    if replacement not in s:
        s=s.replace(original,replacement)
p.write_text(s)
# The fork's snapshot only wired windows; also handle title/hero/run scenes.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/PixelScene.java'
s=p.read_text()
if 'RgMenuNavigation menuNavigation' not in s:
    s=s.replace('private Signal.Listener<KeyEvent> fullscreenListener;', 'private Signal.Listener<KeyEvent> fullscreenListener;\n    private org.nextui.shattered.RgMenuNavigation menuNavigation;')
    s=s.replace('Cursor.setCustomCursor(Cursor.Type.DEFAULT, defaultZoom);', 'Cursor.setCustomCursor(Cursor.Type.DEFAULT, defaultZoom);\n        if (Boolean.getBoolean("nextui.sdl") && !inGameScene) menuNavigation = new org.nextui.shattered.RgMenuNavigation(this);')
    s=s.replace('public void destroy() {', 'public void destroy() {\n        if (menuNavigation != null) menuNavigation.close();',1)
if 'nextui-context-cursor' not in s:
    s=s.replace('if (ControllerHandler.controllerPointerActive()){', 'if (shouldDrawControllerCursor()){',1)
    marker='private Image cursor = null;'
    s=s.replace(marker, '''// nextui-context-cursor: movement must not leave the menu pointer on the map.
    public boolean shouldDrawControllerCursor() {
        if (!ControllerHandler.controllerPointerActive()) return false;
        if (!Boolean.getBoolean("nextui.sdl") || !(this instanceof GameScene)) return true;
        if (GameScene.selectingCell()) return true;
        if (members != null) for (Gizmo member : members.toArray(new Gizmo[0])) {
            if (member instanceof Window && member.visible) return true;
        }
        return false;
    }

    '''+marker,1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/ControllerNavigator.java'
s=p.read_text()
if 'public boolean ensureFocus' not in s:
    s=s.replace('public boolean move(Group root, GameAction action) {', '''public boolean ensureFocus(Group root) {
        ArrayList<Button> buttons = new ArrayList<>();
        collectButtons(root, buttons);
        if (buttons.isEmpty()) return false;
        if (!buttons.contains(focused)) focused = buttons.get(0);
        movePointer(focused);
        return true;
    }

    public boolean move(Group root, GameAction action) {''')
    s=s.replace('focused = buttons.get(0);\n\t\t}', 'focused = buttons.get(0);\n            movePointer(focused);\n            return true;\n\t\t}')
    s=s.replace('Point point = screenCenter(button);', '''// Reveal selected controls inside scrollable panels.
        for (Group parent = button.parent; parent != null; parent = parent.parent) {
            if (parent instanceof ScrollPane) {
                ScrollPane pane = (ScrollPane) parent;
                Camera c = pane.content().camera;
                float y = c.scroll.y;
                if (button.top() < y) y = button.top();
                else if (button.bottom() > y + pane.height()) y = button.bottom() - pane.height();
                pane.scrollTo(c.scroll.x, y);
            }
        }
        Point point = screenCenter(button);''')
    s=s.replace('ControllerHandler.updateControllerPointer(new PointF(point.x, point.y), true);', 'ControllerHandler.updateControllerPointer(new PointF(point.x, point.y), false);\n        ControllerHandler.updateControllerPointer(new PointF(point.x, point.y), true);')
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/Window.java'
s=p.read_text()
marker='if (KeyBindings.getActionForKey(event) == SPDAction.ACCEPT) {'
if 'controllerNavigator.ensureFocus(this)' not in s:
    s=s.replace(marker, marker+'\n            if (Boolean.getBoolean("nextui.sdl")) controllerNavigator.ensureFocus(this);',1)
p.write_text(s)
# Keep selection controls visible; the artwork-only fade button is not useful here.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/HeroSelectScene.java'
s=p.read_text()
if 'nextui.sdl' not in s:
    s=s.replace('public void update() {\n\t\tsuper.update();', 'public void update() {\n\t\tsuper.update();\n        if (Boolean.getBoolean("nextui.sdl")) { resetFade(); if (btnFade != null) { btnFade.visible = btnFade.active = false; } }',1)
p.write_text(s)
# In target mode directions must move the reticle, never cancel targeting and walk.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/CellSelector.java'
s=p.read_text()
if 'private int dpadTarget' not in s:
    s=s.replace('private float mouseZoom;', '''private float mouseZoom;
    private int dpadTarget = -1;
    public void beginDpadTarget() {
        resetKeyHold();
        dpadTarget = Dungeon.hero.pos;
        if (com.shatteredpixel.shatteredpixeldungeon.ui.QuickSlotButton.lastTarget != null
                && Dungeon.level.heroFOV[com.shatteredpixel.shatteredpixeldungeon.ui.QuickSlotButton.lastTarget.pos]) {
            dpadTarget = com.shatteredpixel.shatteredpixeldungeon.ui.QuickSlotButton.lastTarget.pos;
        }
        updateDpadTarget();
    }
    private void updateDpadTarget() {
        PointF world = DungeonTilemap.tileCenterToWorld(dpadTarget);
        Point screen = camera.cameraToScreen(world.x, world.y);
        ControllerHandler.setControllerPointer(true);
        ControllerHandler.updateControllerPointer(new PointF(screen.x, screen.y), false);
        ControllerHandler.updateControllerPointer(new PointF(screen.x, screen.y), true);
    }''')
    s=s.replace('GameAction action = KeyBindings.getActionForKey( event );', '''GameAction action = KeyBindings.getActionForKey( event );
            if (Boolean.getBoolean("nextui.sdl") && GameScene.selectingCell() && !GameScene.showingWindow()) {
                Point direction = directionFromAction(action);
                if (!direction.isZero()) {
                    if (event.pressed) {
                        int x = dpadTarget % Dungeon.level.width() + direction.x;
                        int y = dpadTarget / Dungeon.level.width() + direction.y;
                        if (x >= 0 && x < Dungeon.level.width() && y >= 0 && y < Dungeon.level.height()) {
                            dpadTarget = x + y * Dungeon.level.width();
                            com.shatteredpixel.shatteredpixeldungeon.ui.QuickSlotButton.cancel();
                            updateDpadTarget();
                        }
                    }
                    return true;
                }
                if (action == SPDAction.ACCEPT) {
                    if (event.pressed) select(dpadTarget, PointerEvent.LEFT);
                    return true;
                }
            }''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/GameScene.java'
s=p.read_text()
if 'cellSelector.beginDpadTarget()' not in s:
    s=s.replace('cellSelector.enabled = Dungeon.hero.ready;', 'cellSelector.enabled = Dungeon.hero.ready;\n        if (Boolean.getBoolean("nextui.sdl") && listener != defaultCellListener) cellSelector.beginDpadTarget();',1)
if 'nextui-resume-intro' not in s:
    marker='if (!SPDSettings.intro() &&'
    s=s.replace(marker, '''// nextui-resume-intro: recover saves made by the reader that missed endIntro.
        // Only floor 1 has the tutorial entrance doors that endIntro reveals.
        if (Boolean.getBoolean("nextui.sdl") && Dungeon.depth == 1 && SPDSettings.intro()
                && Document.ADVENTURERS_GUIDE.isPageRead(Document.GUIDE_INTRO)) {
            endIntro();
            System.err.println("Tutorial recovered: previously read Intro on floor 1");
        }

        '''+marker,1)
p.write_text(s)
# All HUD-only actions need a reachable button path in compact, controller-only UI.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/windows/WndGame.java'
s=p.read_text()
if 'RgPlatform.menuLabel' not in s:
    s=s.replace('// Challenges window', '''if (Boolean.getBoolean("nextui.sdl")) {
            addButton(new RedButton(org.nextui.shattered.RgPlatform.menuLabel("journal")) {
                @Override protected void onClick() { hide(); GameScene.show(new WndJournal()); }
            });
            addButton(new RedButton(org.nextui.shattered.RgPlatform.menuLabel("search")) {
                @Override protected void onClick() { hide(); if (Dungeon.hero != null && Dungeon.hero.ready) Dungeon.hero.search(true); }
            });
            addButton(new RedButton(org.nextui.shattered.RgPlatform.menuLabel("exit")) {
                @Override protected void onClick() { Game.instance.finish(); }
            });
        }

        // Challenges window''',1)
s=s.replace('hide(); GameScene.show(new WndJournal());', 'hide(); GameScene.show(new org.nextui.shattered.RgGuide());')
p.write_text(s)
# Replace keyboard/stick-only onboarding instructions in this dedicated build.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/MenuPane.java'
s=p.read_text()
if 'nextui-guide-read' not in s:
    s=s.replace('if (flashingPage != null){\n\t\t\t\tjournalIcon.am', '''// nextui-guide-read: controller reader marks pages without clicking this HUD icon.
            if (flashingPage != null && flashingDoc != null && flashingDoc.isPageRead(flashingPage)) {
                flashingPage = null;
                flashingDoc = null;
                journalIcon.am = keyIcon.am = 1;
                updateKeyDisplay();
            }
            if (flashingPage != null){
                journalIcon.am''',1)
p.write_text(s)
for relative, values in {
    'scenes/scenes_zh.properties': {
        'scenes.gamescene.tutorial_move_controller': '使用十字键移动并与相邻目标互动。',
        'scenes.gamescene.tutorial_guidebook_mobile': '按Start，选择教程与日志，再按A阅读新书页。',
        'scenes.gamescene.tutorial_ui_mobile': 'B查看目标，X背包，Y使用快捷栏；L1向左、R1向右。Start菜单有按键说明；A拾取脚下物品，Menu等待。'},
    'items/items_zh.properties': {'items.journal.guidebook.hint_mobile':'按Start，选择教程与日志，再按A阅读新书页。'},
    'journal/journal_zh.properties': {'journal.document.adventurers_guide.intro.body':'你好冒险家，你正在阅读《地牢探索指南》！本指南会在合适时机提示你阅读新的教程。\\n\\n右上角书本闪烁时，按Start选择“教程与日志”，用十字键选择金色的新书页，再按A阅读。正文上下滚动，A或B返回。\\n\\n指南遗失了部分书页，继续探索地牢，寻找其余部分吧！',
        'journal.document.adventurers_guide.examining.body':'行动前，先观察敌人、物品和地形，可以避免许多危险。\\n\\n正常游戏时按B进入查看模式，十字键选择目标格，A查看，B取消。查看本身不消耗回合。\\n\\nSelect可查看英雄、天赋和当前状态。',
        'journal.document.adventurers_guide.searching.body':'地牢中存在看不见的暗门和陷阱。怀疑附近有隐藏通道时，可以花费回合搜索周围。\\n\\n按Start，选择“搜索周围”并按A。也可以用L1/R1选中放大镜，连续使用Y进行搜索。查看目标与搜索周围是两种不同操作。'},
    'windows/windows_zh.properties': {'windows.wndkeybindings.controller_info':'十字键移动与选择，A确定，B返回。A拾取脚下物品，Menu等待；L2/R2缩放。'},
    'scenes/scenes.properties': {'scenes.gamescene.tutorial_move_controller':'Use the D-pad to move and interact with adjacent objects.'},
}.items():
    p=root/'core/src/main/assets/messages'/relative
    if not p.exists(): continue
    s=p.read_text()
    if '# RG34XX dedicated controls' in s:
        s=s.split('\n# RG34XX dedicated controls')[0]
    s+='\n# RG34XX dedicated controls\n'+'\n'.join(k+'='+v for k,v in values.items())+'\n'
    p.write_text(s)
# RG34XX interaction pass: the physical shoulder direction follows screen order.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/Toolbar.java'
s=p.read_text()
if 'nextui-spatial-hotbar' not in s:
    marker='selectedHotbarSlot = (selectedHotbarSlot + direction + QuickSlot.SIZE + 2) % (QuickSlot.SIZE + 2);'
    s=s.replace(marker, '''// nextui-spatial-hotbar: toolbar flip must not reverse L1/R1.
        if (Boolean.getBoolean("nextui.sdl")) {
            ArrayList<Integer> slots = new ArrayList<>();
            for (int i=0; i<QuickSlot.SIZE+2; i++) if (hotbarControl(i).isVisible()) slots.add(i);
            if (slots.isEmpty()) return;
            slots.sort((a,b) -> Float.compare(hotbarControl(a).centerX(), hotbarControl(b).centerX()));
            int index = slots.indexOf(selectedHotbarSlot);
            selectedHotbarSlot = slots.get(index < 0 ? 0 : (index + direction + slots.size()) % slots.size());
        } else {
            '''+marker+'''
        }''',1)
    s=s.replace('private void cycleHotbar(int direction) {', '''private Component hotbarControl(int slot) {
        return slot < QuickSlot.SIZE ? btnQuick[slot] : slot == QuickSlot.SIZE ? btnSearch : btnWait;
    }

    private void cycleHotbar(int direction) {''',1)
p.write_text(s)
# B is context-sensitive: back/cancel in a modal, Examine while exploring.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/GameScene.java'
s=p.read_text()
if 'nextui-examine-back' not in s:
    marker='protected void onBackPressed() {\n\t\tif (!cancel()) {'
    s=s.replace(marker, '''protected void onBackPressed() {
        // nextui-examine-back: Start owns the pause menu.
        if (Boolean.getBoolean("nextui.sdl")) {
            if (!cancel() && Dungeon.hero != null && Dungeon.hero.ready) {
                selectCell(new CellSelector.Listener() {
                    @Override public void onSelect(Integer cell) { if (cell != null) examineCell(cell); }
                    @Override public String prompt() { return org.nextui.shattered.RgPlatform.chinese()
                        ? "查看目标：十字键选格 · A查看 · B取消" : "Examine: D-pad selects · A inspect · B cancel"; }
                });
            }
            return;
        }
        if (!cancel()) {''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/Window.java'
s=p.read_text()
if 'nextui-start-toggle' not in s:
    marker='public boolean onSignal( KeyEvent event ) {'
    s=s.replace(marker,marker+'''
        // nextui-start-toggle: Start closes its own pause window; B backs out of all windows.
        if (Boolean.getBoolean("nextui.sdl") && event.pressed
                && KeyBindings.getActionForKey(event) == SPDAction.MENU
                && this instanceof com.shatteredpixel.shatteredpixeldungeon.windows.WndGame) {
            hide(); return true;
        }
''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/StartScene.java'
s=p.read_text()
if 'new org.nextui.shattered.RgRunDetails(slot)' not in s:
    s=s.replace('new WndGameInProgress(slot)', '(Boolean.getBoolean("nextui.sdl") ? new org.nextui.shattered.RgRunDetails(slot) : new WndGameInProgress(slot))')
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/TitleScene.java'
s=p.read_text()
if 'RgHome.class' not in s:
    s=s.replace('super.create();', '''super.create();
        if (Boolean.getBoolean("nextui.sdl")) {
            ShatteredPixelDungeon.switchNoFade(org.nextui.shattered.RgHome.class); return;
        }''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/windows/WndGame.java'
s=p.read_text()
if 'RgPause.fill' not in s:
    s=s.replace('super();', '''super();
        if (Boolean.getBoolean("nextui.sdl")) { org.nextui.shattered.RgPause.fill(this); return; }''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/PixelScene.java'
s=p.read_text()
if 'nextui-system-overlay' not in s:
    marker='\n\t//this system only preserves windows with a public zero-arg constructor'
    # Draw after the scene and cursor; both menus and gameplay get an OSD.
    pos=s.index(marker)
    before=s[:pos]
    close=before.rfind('\n\t}')
    s=before[:close]+'''\n        // nextui-system-overlay
        if (Boolean.getBoolean("nextui.sdl")) org.nextui.shattered.RgSystemOverlay.draw();'''+before[close:]+s[pos:]
p.write_text(s)
# Sliders are not Buttons upstream. Include them and use left/right to adjust.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/OptionSlider.java'
s=p.read_text()
if 'public void controllerAdjust' not in s:
    s=s.replace('public int getSelectedValue(){', '''public void controllerAdjust(int delta) {
        int value = Math.max(minVal, Math.min(selectedVal + delta, maxVal));
        if (value != selectedVal) { setSelectedValue(value); onChange(); }
    }

    public int getSelectedValue(){''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/ControllerNavigator.java'
s=p.read_text()
if 'public void accept(boolean down)' not in s:
    s=s.replace('import com.watabou.noosa.Group;', 'import com.watabou.noosa.Group;\nimport com.watabou.noosa.ui.Component;')
    s=s.replace('Button focused','Component focused').replace('ArrayList<Button>','ArrayList<Component>').replace('Button candidate','Component candidate').replace('screenCenter(Button button)','screenCenter(Component button)').replace('movePointer(Button button)','movePointer(Component button)').replace('(Button) child','(Component) child')
    s=s.replace('child instanceof Button &&', '(child instanceof Button || child instanceof OptionSlider) &&')
    s=s.replace('Point origin = screenCenter(focused);', '''if (dx != 0 && focused instanceof OptionSlider) {
            ((OptionSlider) focused).controllerAdjust(dx);
            movePointer(focused);
            return true;
        }
        Point origin = screenCenter(focused);''')
    s=s.replace('Button next = null;', 'Component next = null;')
    s=s.replace('public boolean ensureFocus(Group root) {', '''public void accept(boolean down) {
        if (!(focused instanceof OptionSlider)) {
            com.watabou.noosa.Game.inputHandler.emulateTouch(ControllerHandler.CONTROLLER_POINTER_ID, com.watabou.input.PointerEvent.LEFT, down);
        }
    }

    public boolean ensureFocus(Group root) {''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/Window.java'
s=p.read_text().replace('if (Boolean.getBoolean("nextui.sdl")) controllerNavigator.ensureFocus(this);', 'if (Boolean.getBoolean("nextui.sdl")) { controllerNavigator.ensureFocus(this); controllerNavigator.accept(event.pressed); return true; }')
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/ControllerNavigator.java'
s=p.read_text().replace('(child instanceof Button || child instanceof OptionSlider)', '(child instanceof Button || child instanceof OptionSlider || child instanceof ScrollingListPane.ListItem)')
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/InventoryPane.java'
s=p.read_text()
if 'controllerNavigator.ensureFocus(InventoryPane.this)' not in s:
    s=s.replace('Game.inputHandler.emulateTouch(ControllerHandler.CONTROLLER_POINTER_ID, PointerEvent.LEFT, event.pressed);', 'if (Boolean.getBoolean("nextui.sdl")) { controllerNavigator.ensureFocus(InventoryPane.this); controllerNavigator.accept(event.pressed); return true; }\n                    Game.inputHandler.emulateTouch(ControllerHandler.CONTROLLER_POINTER_ID, PointerEvent.LEFT, event.pressed);')
    s=s.replace('return event.pressed && InventoryPane.this.visible && !GameScene.showingWindow()', 'return event.pressed && InventoryPane.this.visible && !GameScene.showingWindow() && !GameScene.selectingCell()')
p.write_text(s)
# Target instructions belong in the existing log, not over the dungeon.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/GameScene.java'
s=p.read_text()
if 'nextui-log-prompt' not in s:
    marker='\n\t\tif (text != null) {\n\t\t\tprompt = new Toast( text ) {'
    assert marker in s
    s=s.replace(marker,'''\n        // nextui-log-prompt: keep target selection unobstructed.
        if (Boolean.getBoolean("nextui.sdl")) {
            if (text != null) GLog.i("%s", text);
            return;
        }
'''+marker,1)
# Game-over actions are scene buttons, not a Window; give them modal-style focus.
if 'nextui-death-navigation' not in s:
    marker='public static void gameOver() {\n\t\tif (scene == null) return;'
    assert marker in s
    s=s.replace(marker,marker+'''\n        // nextui-death-navigation
        Group deathActions = new Group();
        scene.add(deathActions);''',1)
    s=s.replace('scene.add(restart);','deathActions.add(restart);',1)
    s=s.replace('scene.add(menu);','''deathActions.add(menu);
        if (Boolean.getBoolean("nextui.sdl")) scene.enableMenuNavigation(deathActions);''',1)
p.write_text(s)
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/PixelScene.java'
s=p.read_text()
if 'public void enableMenuNavigation' not in s:
    marker='private org.nextui.shattered.RgMenuNavigation menuNavigation;'
    assert marker in s
    s=s.replace(marker,marker+'''
    public void enableMenuNavigation(com.watabou.noosa.Group controls) {
        if (menuNavigation != null) menuNavigation.close();
        menuNavigation = new org.nextui.shattered.RgMenuNavigation(controls,true);
    }''',1)
    s=s.replace('if (GameScene.selectingCell()) return true;', '''if (GameScene.selectingCell()) return true;
        if (com.shatteredpixel.shatteredpixeldungeon.Dungeon.hero != null
                && !com.shatteredpixel.shatteredpixeldungeon.Dungeon.hero.isAlive()) return true;''',1)
p.write_text(s)
# Preserve X's key listener while removing the redundant on-screen bag and gap.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/ui/Toolbar.java'
s=p.read_text()
if 'nextui-keyboard-inventory' not in s:
    marker='\t@Override\n\tprotected void layout() {'
    assert marker in s
    s=s.replace(marker,marker+'''\n        // nextui-keyboard-inventory
        if (Boolean.getBoolean("nextui.sdl")) {
            btnInventory.visible = false;
            btnInventory.setSize(0, btnInventory.height());
        }''',1)
p.write_text(s)

# Upgrade existing staged patches to immediate focus only for death actions.
p=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/scenes/PixelScene.java'
s=p.read_text().replace('new org.nextui.shattered.RgMenuNavigation(controls);','new org.nextui.shattered.RgMenuNavigation(controls,true);')
p.write_text(s)

# Full controller state pass; kept separate from backend compatibility patches.
import importlib.util
spec=importlib.util.spec_from_file_location('interaction_patches',Path(__file__).with_name('interaction-patches.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.apply(root)
