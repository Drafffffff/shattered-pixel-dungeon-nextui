"""Controller interaction pass, applied to the pinned build copy only."""
from pathlib import Path
import shutil

def apply(root):
 base=root/'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon'
 def patch(rel,marker,fn):
  p=base/rel;s=p.read_text()
  if marker not in s:
   n=fn(s);assert n!=s,rel
   p.write_text(n)
 shutil.copyfile(Path(__file__).parent/'source-overrides/ControllerNavigator.java',base/'ui/ControllerNavigator.java')
 patch('scenes/AlchemyScene.java','nextui-alchemy-controls',lambda s:s.replace('private IconButton cancel;','''// nextui-alchemy-controls: the standalone scene needs its own focus owner.
    private final com.shatteredpixel.shatteredpixeldungeon.ui.ControllerNavigator rgNavigator=new com.shatteredpixel.shatteredpixeldungeon.ui.ControllerNavigator();
    private boolean rgInitialized,rgCovered;
    public Component rgFocused(){return rgNavigator.focused();}
    public String rgFocusId(){
        Component f=rgNavigator.focused();
        for(int i=0;i<inputs.length;i++)if(inputs[i]!=null && f==inputs[i].slot)return "input"+i;
        for(int i=0;i<combines.length;i++)if(combines[i]!=null && f==combines[i].button)return "combine"+i;
        for(int i=0;i<outputs.length;i++)if(outputs[i]!=null && f==outputs[i].slot)return "output"+i;
        if(f==cancel)return "clear";if(f==repeat)return "repeat";if(f==energyAdd)return "energy";
        if(f instanceof ExitButton)return "exit";return f instanceof StyledButton?"guide":"";
    }
    public boolean rgInput(int key,boolean down){
        if(Window.rgTop()!=null)return false;
        com.watabou.input.GameAction action=KeyBindings.getActionForKey(new com.watabou.input.KeyEvent(key,down));
        if(action==SPDAction.ACCEPT || key==com.badlogic.gdx.Input.Keys.BUTTON_Y){
            if(rgNavigator.ensureFocus(this))rgNavigator.accept(down);return true;
        }
        if(action==SPDAction.N || action==SPDAction.S || action==SPDAction.E || action==SPDAction.W){
            if(down)rgNavigator.move(this,action);return true;
        }
        if(key==com.badlogic.gdx.Input.Keys.BUTTON_L1 || key==com.badlogic.gdx.Input.Keys.BUTTON_R1){
            if(down)rgNavigator.cycle(this,key==com.badlogic.gdx.Input.Keys.BUTTON_L1?-1:1);return true;
        }
        if(key==com.badlogic.gdx.Input.Keys.BUTTON_B){if(down)onBackPressed();return true;}
        if(key==com.badlogic.gdx.Input.Keys.BUTTON_X){
            if(down){
                boolean empty=false;for(InputButton b:inputs)if(b.item()==null)empty=true;
                if(empty)addToFront(WndBag.getBag(itemSelector));
                else addToFront(new WndMessage(org.nextui.shattered.RgPlatform.chinese()?"材料槽已满，请先选择一个材料槽更换。":"All material slots are full. Select a slot to replace it."));
            }return true;
        }
        return false;
    }
    private void rgUpdateFocus(){
        if(!Boolean.getBoolean("nextui.sdl"))return;
        boolean covered=Window.rgTop()!=null;
        if(!covered){
            if(inputs[0]!=null && (!rgInitialized || rgNavigator.focused()==null || !rgNavigator.focused().isActive() || !rgNavigator.focused().isVisible())){rgNavigator.focus(inputs[0].slot);rgInitialized=true;}
            rgNavigator.ensureFocus(this);if(rgCovered)rgNavigator.revealFocus();
        }
        rgCovered=covered;
    }
    @Override public synchronized void draw(){super.draw();if(Boolean.getBoolean("nextui.sdl") && Window.rgTop()==null)rgNavigator.draw();}
    private IconButton cancel;''',1).replace('desc.text( Messages.get(AlchemyScene.class, "text") );','desc.text(Boolean.getBoolean("nextui.sdl")?(org.nextui.shattered.RgPlatform.chinese()?"方向选择 · A确定 · X材料 · B返回":"D-pad select · A use · X items · B back"):Messages.get(AlchemyScene.class,"text"));',1).replace('water.offset( 0, -5 * Game.elapsed );','water.offset( 0, -5 * Game.elapsed );\n        rgUpdateFocus();',1).replace('public void destroy() {','public void destroy() {\n        rgNavigator.destroy();',1))
 patch('scenes/PixelScene.java','nextui-alchemy-cursor',lambda s:s.replace('public boolean shouldDrawControllerCursor() {','public boolean shouldDrawControllerCursor() {\n        if(Boolean.getBoolean("nextui.sdl") && this instanceof AlchemyScene)return false; // nextui-alchemy-cursor',1))
 patch('windows/WndHero.java','implements org.nextui.shattered.RgFocusable',lambda s:s.replace('class BuffSlot extends Component {','class BuffSlot extends Component implements org.nextui.shattered.RgFocusable {'))
 patch('ui/BadgesList.java','implements org.nextui.shattered.RgFocusable',lambda s:s.replace('class ListItem extends Component {','class ListItem extends Component implements org.nextui.shattered.RgFocusable {'))
 patch('ui/Window.java','nextui-modal-focus',lambda s:s.replace('controllerNavigator.clear();','controllerNavigator.destroy();',1).replace('public void onBackPressed() {','''// nextui-modal-focus: initialize after subclass layout and restore when exposed.
    public static Window rgTop() {
        if (Game.scene()==null) return null;
        Window last=null;
        for (com.watabou.noosa.Gizmo g:Game.scene().members()) if(g instanceof Window && g.visible)last=(Window)g;
        return last;
    }
    public boolean rgHasFocus(){return controllerNavigator.focused()!=null;}
    public com.watabou.noosa.ui.Component rgFocused(){return controllerNavigator.focused();}
    @Override public void update(){super.update();if(Boolean.getBoolean("nextui.sdl") && rgTop()==this)controllerNavigator.ensureFocus(this);}
    @Override public void draw(){super.draw();if(Boolean.getBoolean("nextui.sdl") && rgTop()==this)controllerNavigator.draw();}
    public void onBackPressed() {''',1).replace('controllerNavigator.ensureFocus(this); controllerNavigator.accept(event.pressed); return true;', 'if(controllerNavigator.ensureFocus(this)) controllerNavigator.accept(event.pressed); else if(event.pressed)onBackPressed(); return true;').replace('private ControllerNavigator controllerNavigator','protected ControllerNavigator controllerNavigator'))
 patch('scenes/PixelScene.java','nextui-focus-border',lambda s:s.replace('if (GameScene.selectingCell()) return true;', '''// nextui-focus-border: modal navigation draws a border, not a pointer over text.
        if (com.shatteredpixel.shatteredpixeldungeon.ui.Window.rgTop()!=null) return false;
        if (org.nextui.shattered.RgMap.active()) return false;
        if (GameScene.selectingCell()) return true;''',1).replace('org.nextui.shattered.RgSystemOverlay.draw();','org.nextui.shattered.RgMap.draw();\n        org.nextui.shattered.RgSystemOverlay.draw();'))
 patch('ui/Toolbar.java','nextui-six-slots',lambda s:s.replace('private void useSelectedHotbar(boolean assign) {','''private void useSelectedHotbar(boolean assign) {
        // nextui-six-slots: manage occupied slots explicitly, without cancel-first Y.
        if(Boolean.getBoolean("nextui.sdl")) {
            if(GameScene.showingWindow() || Dungeon.hero==null || !Dungeon.hero.ready || GameScene.selectingCell())return;
            if(selectedHotbarSlot>=QuickSlot.SIZE)selectedHotbarSlot=0;
            if(assign)org.nextui.shattered.RgQuickslot.manage(selectedHotbarSlot);
            else if(Dungeon.quickslot.getItem(selectedHotbarSlot)==null || Dungeon.quickslot.isPlaceholder(selectedHotbarSlot))org.nextui.shattered.RgQuickslot.assign(selectedHotbarSlot);
            else btnQuick[selectedHotbarSlot].activate();
            return;
        }''',1).replace('btnInventory.setSize(0, btnInventory.height());','''btnInventory.setSize(0, btnInventory.height());
            btnSearch.visible=false;btnSearch.setSize(0,btnSearch.height());
            btnWait.visible=false;btnWait.setSize(0,btnWait.height());''',1))
 patch('scenes/CellSelector.java','nextui-target-cycle',lambda s:s.replace('private int dpadTarget = -1;','''// nextui-target-cycle
    private int dpadTarget = -1;
    public void rgConfirm(){if(dpadTarget>=0 && Dungeon.hero.ready)select(dpadTarget,PointerEvent.LEFT);}
    public int rgTarget(){return dpadTarget;}
    public void rgCycle(int direction){
        java.util.ArrayList<Integer> cells=new java.util.ArrayList<>();cells.add(Dungeon.hero.pos);
        for(com.shatteredpixel.shatteredpixeldungeon.actors.mobs.Mob m:Dungeon.level.mobs)
            if(m.isAlive() && Dungeon.level.heroFOV[m.pos])cells.add(m.pos);
        for(com.shatteredpixel.shatteredpixeldungeon.items.Heap h:Dungeon.level.heaps.valueList())
            if(Dungeon.level.heroFOV[h.pos] && !cells.contains(h.pos))cells.add(h.pos);
        cells.subList(1,cells.size()).sort(Integer::compare);
        int i=cells.indexOf(dpadTarget);dpadTarget=cells.get(i<0?0:(i+direction+cells.size())%cells.size());
        updateDpadTarget();
    }''',1))
 patch('scenes/CellSelector.java','nextui-target-camera',lambda s:s.replace('private int dpadTarget = -1;','''private int dpadTarget = -1;
    // nextui-target-camera: keep the reticle inside the unobstructed play area.
    private boolean rgTargetCamera;
    public void rgEndTargetCamera(){
        if(!rgTargetCamera)return;
        rgTargetCamera=false;
        if(Dungeon.hero!=null && Dungeon.hero.sprite!=null)camera.panFollow(Dungeon.hero.sprite,5f);
    }
    private void rgFollowTarget(PointF world){
        float dx=world.x-Math.max(camera.scroll.x+camera.width*.2f,Math.min(camera.scroll.x+camera.width*.8f,world.x));
        float dy=world.y-Math.max(camera.scroll.y+camera.height*.25f,Math.min(camera.scroll.y+camera.height*.7f,world.y));
        camera.snapTo(camera.scroll.x+camera.width/2f+dx-camera.centerOffset.x,
                      camera.scroll.y+camera.height/2f+dy-camera.centerOffset.y);
    }''',1).replace('public void beginDpadTarget() {','public void beginDpadTarget() {\n        rgTargetCamera=true;',1).replace('PointF world = DungeonTilemap.tileCenterToWorld(dpadTarget);','PointF world = DungeonTilemap.tileCenterToWorld(dpadTarget);\n        if(rgTargetCamera)rgFollowTarget(world);',1).replace('public void update() {\n\t\tsuper.update();','public void update() {\n\t\tsuper.update();\n        if(Boolean.getBoolean("nextui.sdl") && rgTargetCamera && GameScene.selectingCell() && !GameScene.showingWindow())updateDpadTarget();',1))
 patch('scenes/GameScene.java','nextui-end-target-camera',lambda s:s.replace('cellSelector.listener = listener;','// nextui-end-target-camera\n        if(Boolean.getBoolean("nextui.sdl") && listener==defaultCellListener)cellSelector.rgEndTargetCamera();\n        cellSelector.listener = listener;',1))
 patch('scenes/GameScene.java','nextui-context-actions',lambda s:s.replace('public static boolean selectingCell() {','''// nextui-context-actions: reach every turn action without mouse-only indicators.
    public static void rgConfirmTarget(){if(cellSelector!=null)cellSelector.rgConfirm();}
    public static void rgCycleTarget(int direction){if(cellSelector!=null)cellSelector.rgCycle(direction);}
    public static int rgTarget(){return cellSelector==null?-1:cellSelector.rgTarget();}
    public static void rgInteract(){
        if(scene==null || Dungeon.hero==null || !Dungeon.hero.ready)return;
        if(Dungeon.level.heaps.get(Dungeon.hero.pos)!=null || Dungeon.hero.canSelfTrample()
                || Dungeon.level.map[Dungeon.hero.pos]==Terrain.ENTRANCE || Dungeon.level.map[Dungeon.hero.pos]==Terrain.EXIT){
            if(Dungeon.hero.handle(Dungeon.hero.pos))Dungeon.hero.next();return;
        }
        boolean zh=org.nextui.shattered.RgPlatform.chinese();
        java.util.ArrayList<String> names=new java.util.ArrayList<>();java.util.ArrayList<Runnable> actions=new java.util.ArrayList<>();
        names.add(zh?"取消":"Cancel");actions.add(()->{});
        if(ActionIndicator.action!=null){names.add(ActionIndicator.action.actionName());actions.add(()->{if(ActionIndicator.action!=null)ActionIndicator.action.doAction();});}
        boolean canAttack=false;
        for(Mob m:Dungeon.level.mobs)if(m.isAlive() && Dungeon.level.heroFOV[m.pos] && Dungeon.hero.canAttack(m))canAttack=true;
        if(canAttack){names.add(zh?"选择攻击目标":"Choose attack target");actions.add(()->selectCell(new CellSelector.Listener(){
            public void onSelect(Integer c){if(c==null)return;Char target=Actor.findChar(c);
                if(target!=null && target!=Dungeon.hero && Dungeon.level.heroFOV[c] && Dungeon.hero.canAttack(target)){
                    QuickSlotButton.target(target);if(Dungeon.hero.handle(c))Dungeon.hero.next();
                }else GLog.w(zh?"此处没有可攻击目标":"No attackable target here");}
            public String prompt(){return zh?"攻击：方向选格 · L1/R1目标 · A/Y确认 · B取消":"Attack: D-pad aim · L1/R1 targets · A/Y confirm · B cancel";}
        }));}
        if(Dungeon.hero.lastAction!=null){names.add(zh?"继续行动":"Resume action");actions.add(()->Dungeon.hero.resume());}
        if(names.size()==1){GLog.i(zh?"脚下没有可拾取物品或可用动作":"No item or action here");return;}
        show(new com.shatteredpixel.shatteredpixeldungeon.windows.WndOptions(zh?"当前动作":"Actions",null,names.toArray(new String[0])){
            protected void onSelect(int i){if(Dungeon.hero.ready)actions.get(i).run();}
        });
    }
    public static boolean selectingCell() {''',1).replace('public void destroy() {','public void destroy() {\n        org.nextui.shattered.RgMap.close();',1))
 patch('scenes/GameScene.java','nextui-once-guide',lambda s:s.replace('if (scene != null) {\n\t\t\tif (doc == Document.ADVENTURERS_GUIDE){','''if (scene != null) {
            // nextui-once-guide: preserve unread pages; only their first alert is proactive.
            if(Boolean.getBoolean("nextui.sdl") && doc==Document.ADVENTURERS_GUIDE) {
                String key="rg-guide-alert-"+page;
                com.badlogic.gdx.Preferences prefs=com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction");
                if(doc.isPageRead(page) || prefs.getBoolean(key,false))return;
                prefs.putBoolean(key,true).flush();
            }
            if (doc == Document.ADVENTURERS_GUIDE){''',1))
 patch('windows/WndJournal.java','nextui-journal-memory',lambda s:s.replace('int height = PixelScene.landscape() ? HEIGHT_L : HEIGHT_P;','int height = Boolean.getBoolean("nextui.sdl") ? 110 : PixelScene.landscape() ? HEIGHT_L : HEIGHT_P;',1).replace('select(last_index);','''// nextui-journal-memory
        if(Boolean.getBoolean("nextui.sdl")) last_index=Math.max(0,Math.min(4,com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction").getInteger("journal-tab",1)));
        select(last_index);''',1).replace('public boolean onSignal(KeyEvent event) {','''@Override public void hide(){
        if(Boolean.getBoolean("nextui.sdl"))com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction").putInteger("journal-tab",last_index).flush();
        super.hide();
    }

    public boolean onSignal(KeyEvent event) {''',1).replace('@Override\n\t@Override public void hide()', '@Override public void hide()').replace('ShatteredPixelDungeon.scene().addToFront( new WndStory( Document.ADVENTURERS_GUIDE.pageSprite(page),\n\t\t\t\t\t\t\t\t\tDocument.ADVENTURERS_GUIDE.pageTitle(page),\n\t\t\t\t\t\t\t\t\tDocument.ADVENTURERS_GUIDE.pageBody(page) ));','''if(Boolean.getBoolean("nextui.sdl"))ShatteredPixelDungeon.scene().addToFront(new org.nextui.shattered.RgGuide.Page(page));
                            else ShatteredPixelDungeon.scene().addToFront(new WndStory(Document.ADVENTURERS_GUIDE.pageSprite(page),Document.ADVENTURERS_GUIDE.pageTitle(page),Document.ADVENTURERS_GUIDE.pageBody(page)));''',1))
 patch('windows/WndBag.java','nextui-bag-assign',lambda s:s.replace('public boolean onSignal(KeyEvent event) {','''public boolean onSignal(KeyEvent event) {
        // nextui-bag-assign
        if(Boolean.getBoolean("nextui.sdl") && event.code==com.badlogic.gdx.Input.Keys.BUTTON_Y){
            if(event.pressed && selector==null && rgFocused() instanceof InventorySlot){
                Item item=((InventorySlot)rgFocused()).item();
                if(item!=null && item.defaultAction()!=null)org.nextui.shattered.RgQuickslot.forItem(item);
            }return true;
        }''',1))
 patch('ui/RadialMenu.java','nextui-list-menu',lambda s:s.replace('int size = SPDSettings.interfaceSize()', '''// nextui-list-menu: keep original onSelect callbacks, replace pointer-only layout.
        if(Boolean.getBoolean("nextui.sdl")) {
            resize(192,120);
            com.watabou.noosa.ui.Component content=new com.watabou.noosa.ui.Component();
            for(int i=0;i<optionTexts.length;i++){
                final int idx=i;
                RedButton button=new RedButton(optionTexts[i],7){
                    protected void onClick(){RadialMenu.this.hide();RadialMenu.this.onSelect(idx,false);}
                    protected boolean onLongClick(){RadialMenu.this.hide();RadialMenu.this.onSelect(idx,true);return true;}
                };
                button.setRect(0,i*21,188,20);content.add(button);
            }
            content.setSize(188,optionTexts.length*21);
            ScrollPane pane=new ScrollPane(content);add(pane);pane.setRect(2,2,188,116);return;
        }
        int size = SPDSettings.interfaceSize()''',1).replace('super.update();','super.update();\n        if(Boolean.getBoolean("nextui.sdl"))return;',1))
 patch('ui/Window.java','nextui-bounded-window',lambda s:s.replace('public boolean rgHasFocus()',"""// nextui-bounded-window: long text/actions remain inside the small panel.
    private boolean rgWasTop,rgBounded;
    private void rgBound(){
        if(rgBounded || this instanceof com.shatteredpixel.shatteredpixeldungeon.windows.WndTabbed)return;
        rgBounded=true;
        int max=(int)com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene.uiCamera.height-20;
        if(height<=max)return;
        com.watabou.noosa.ui.Component content=new com.watabou.noosa.ui.Component();
        for(com.watabou.noosa.Gizmo g:members.toArray(new com.watabou.noosa.Gizmo[0]))
            if(g!=null && g!=blocker && g!=chrome && g!=shadow){erase(g);content.add(g);}
        content.setSize(width,height);ScrollPane pane=new ScrollPane(content);add(pane);pane.setRect(0,0,width,max);resize(width,max);
    }
    public boolean rgHasFocus()""",1).replace('if(Boolean.getBoolean("nextui.sdl") && rgTop()==this)controllerNavigator.ensureFocus(this);','if(Boolean.getBoolean("nextui.sdl")){rgBound();boolean top=rgTop()==this;if(top){controllerNavigator.ensureFocus(this);if(!rgWasTop)controllerNavigator.revealFocus();}rgWasTop=top;}'))
 patch('windows/WndJournal.java','nextui-journal-position',lambda s:s.replace('private static WndJournal INSTANCE',"""// nextui-journal-position: persist tab-specific focus and content positions.
    private int rgTab=-1;
    @Override public void update(){
        if(Boolean.getBoolean("nextui.sdl") && rgTab!=last_index){
            if(rgTab>=0)rgRemember(rgTab);
            rgTab=last_index;
            controllerNavigator.clear();
            controllerNavigator.restore(this,com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction").getInteger("journal-focus-"+rgTab,0));
        }
        super.update();
    }
    private void rgRemember(int tab){
        com.badlogic.gdx.Preferences p=com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction");
        int index=controllerNavigator.index(this);
        if(index>=0)p.putInteger("journal-focus-"+tab,index);
        p.putInteger("journal-catalog-category",CatalogTab.currentItemIdx).putInteger("journal-alchemy-category",AlchemyTab.currentPageIdx).flush();
    }
    private static WndJournal INSTANCE""",1).replace('if (INSTANCE != null){',"""if(Boolean.getBoolean("nextui.sdl")){
            com.badlogic.gdx.Preferences p=com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction");
            CatalogTab.currentItemIdx=Math.max(0,Math.min(3,p.getInteger("journal-catalog-category",0)));
            AlchemyTab.currentPageIdx=Math.max(0,Math.min(8,p.getInteger("journal-alchemy-category",0)));
        }
        if (INSTANCE != null){""",1).replace('@Override public void hide(){','@Override public void hide(){\n        if(Boolean.getBoolean("nextui.sdl"))rgRemember(last_index);',1).replace('if (!found){','if(Boolean.getBoolean("nextui.sdl"))item.active=found;\n                if (!found){',1))
 patch('windows/WndInfoItem.java','nextui-strength-help',lambda s:s.replace('RenderedTextBlock txtInfo = PixelScene.renderTextBlock( item.info(), 6 );',"""// nextui-strength-help: use only requirements already disclosed by the item.
        String description=item.info();
        if(Boolean.getBoolean("nextui.sdl") && com.shatteredpixel.shatteredpixeldungeon.Dungeon.hero!=null){
            boolean zh=org.nextui.shattered.RgPlatform.chinese();
            int required=item instanceof com.shatteredpixel.shatteredpixeldungeon.items.weapon.Weapon?((com.shatteredpixel.shatteredpixeldungeon.items.weapon.Weapon)item).STRReq():item instanceof com.shatteredpixel.shatteredpixeldungeon.items.armor.Armor?((com.shatteredpixel.shatteredpixeldungeon.items.armor.Armor)item).STRReq():-1;
            if(required>=0){
                int strength=com.shatteredpixel.shatteredpixeldungeon.Dungeon.hero.STR();
                description+=(zh?"\\n\\n当前力量：":"\\n\\nStrength: ")+strength+(item.levelKnown?(zh?" / 装备要求：":" / Required: ")+required:(zh?" / 要求待鉴定确认":" / Identify to confirm requirement"));
                if(!item.levelKnown || strength<required)description+=zh?"\\n升级不加力量；普通力量药剂永久+1。":"\\nLevels do not add strength. Strength potion: +1 permanently.";
            }
        }
        RenderedTextBlock txtInfo = PixelScene.renderTextBlock(description,6);""",1))
 patch('windows/WndHero.java','nextui-short-hero',lambda s:s.replace('resize( WIDTH, HEIGHT );','resize(WIDTH,Boolean.getBoolean("nextui.sdl")?110:HEIGHT); // nextui-short-hero',1))
 patch('windows/WndJournal.java','nextui-scroll-memory',lambda s:s.replace('if(rgTab>=0)rgRemember(rgTab);','// Save the previous tab before select() changes active children.',1).replace('private void rgRemember(int tab){','''// nextui-scroll-memory
    @Override public void select(Tab tab){
        if(Boolean.getBoolean("nextui.sdl") && rgTab>=0 && tab!=selected)rgRemember(rgTab);
        super.select(tab);
    }
    private void rgRemember(int tab){''',1).replace('p.putInteger("journal-catalog-category",','org.nextui.shattered.RgUiMemory.save(this,"journal-scroll-"+tab);\n        p.putInteger("journal-catalog-category",',1).replace('controllerNavigator.restore(this,com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction").getInteger("journal-focus-"+rgTab,0));','controllerNavigator.restore(this,com.badlogic.gdx.Gdx.app.getPreferences("rg-interaction").getInteger("journal-focus-"+rgTab,0));\n            org.nextui.shattered.RgUiMemory.restore(this,"journal-scroll-"+rgTab);',1).replace('if(Boolean.getBoolean("nextui.sdl"))item.active=found;','if(Boolean.getBoolean("nextui.sdl")){item.active=found;if(found && !Document.ADVENTURERS_GUIDE.isPageRead(page))item.hardlight(TITLE_COLOR);}',1))
 patch('windows/WndTextInput.java','nextui-input-cancel',lambda s:s.replace('protected TextInput textBox;','protected TextInput textBox;\n    private String rgInitial; // nextui-input-cancel',1).replace('super();','super();\n        rgInitial=initialValue==null?"":initialValue;',1).replace('if (Boolean.getBoolean("nextui.sdl")) { hide(); return; }','if (Boolean.getBoolean("nextui.sdl")) { textBox.setText(rgInitial); onSelect(false,rgInitial); hide(); return; }',1))
 patch('windows/WndJournal.java','nextui-journal-lifecycle',lambda s:s.replace('@Override public void hide(){','''private boolean rgClosed; // nextui-journal-lifecycle
    @Override public void hide(){
        if(rgClosed)return;rgClosed=true;
        if(INSTANCE==this)INSTANCE=null;''',1))
 # Do not route a HUD reader back into a duplicate guide directory.
 for rel in ['ui/MenuPane.java','windows/WndGame.java']:
  p=base/rel;s=p.read_text().replace('new org.nextui.shattered.RgGuide()','new com.shatteredpixel.shatteredpixeldungeon.windows.WndJournal()');p.write_text(s)

 patch('ui/Button.java','nextui-direct-button',lambda s:s.replace('private Signal.Listener<KeyEvent> keyListener;','''// nextui-direct-button: ScrollPane owns pointer events, so focused buttons use their own lifecycle.
    public void rgAccept(boolean down){
        if(!active || !visible)return;
        if(down){pressedButton=this;pressTime=0;clickReady=true;onPointerDown();}
        else {onPointerUp();if(pressedButton==this){pressedButton=null;if(clickReady){killTooltip();onClick();}}}
    }
    private Signal.Listener<KeyEvent> keyListener;''',1).replace('protected void onHoverStart(PointerEvent event) {','protected void onHoverStart(PointerEvent event) {\n                if(Boolean.getBoolean("nextui.sdl"))return;',1))

 patch('scenes/PixelScene.java','nextui-scene-focus-return',lambda s:s.replace('super.update();','super.update();\n        if(menuNavigation!=null)menuNavigation.update(); // nextui-scene-focus-return',1))
 patch('windows/WndTextInput.java','nextui-negative-rollback',lambda s:s.replace('onSelect(false, textBox.getText());','onSelect(false, Boolean.getBoolean("nextui.sdl")?rgInitial:textBox.getText()); // nextui-negative-rollback',1))

 patch('windows/WndBag.java','nextui-unassignable-help',lambda s:s.replace('if(item!=null && item.defaultAction()!=null)org.nextui.shattered.RgQuickslot.forItem(item);','if(item!=null && item.defaultAction()!=null)org.nextui.shattered.RgQuickslot.forItem(item);\n                else if(item!=null)GameScene.show(new WndMessage(org.nextui.shattered.RgPlatform.chinese()?"该物品没有快捷使用动作；按A查看可用操作。":"No quick-use action. Press A to view available actions.")); // nextui-unassignable-help',1))

 # Noosa Camera inherits visible but Group.draw previously ignored it.
 p=root/'SPD-classes/src/main/java/com/watabou/noosa/Group.java';s=p.read_text()
 if 'nextui-camera-visibility' not in s:
  s=s.replace('if (g != null && g.exists && g.isVisible()) {','if (g != null && g.exists && g.isVisible() && (!Boolean.getBoolean("nextui.sdl") || g.camera()==null || g.camera().visible)) { // nextui-camera-visibility',1)
  assert 'nextui-camera-visibility' in s;p.write_text(s)

 patch('ui/ScrollPane.java','nextui-viewport-follow',lambda s:s.replace('public synchronized void update() {','''public synchronized void update() {
        // nextui-viewport-follow: parent windows can resize/recenter after child layout.
        if(Boolean.getBoolean("nextui.sdl") && content!=null){
            Point position=camera().cameraToScreen(x,y);
            if(content.camera.x!=position.x || content.camera.y!=position.y)layout();
        }''',1))

 patch('scenes/PixelScene.java','nextui-transition-cursor',lambda s:s.replace('if (!ControllerHandler.controllerPointerActive()) return false;','if(Boolean.getBoolean("nextui.sdl") && this instanceof InterlevelScene)return false; // nextui-transition-cursor\n        if (!ControllerHandler.controllerPointerActive()) return false;',1))

 patch('Dungeon.java','nextui-hotbar-memory',lambda s:s.replace('public static QuickSlot quickslot = new QuickSlot();','public static QuickSlot quickslot = new QuickSlot();\n    public static int rgSelectedHotbarSlot; // nextui-hotbar-memory',1).replace('quickslot.reset();','quickslot.reset();\n        rgSelectedHotbarSlot=0;').replace('quickslot.storePlaceholders( bundle );','quickslot.storePlaceholders( bundle );\n            if(Boolean.getBoolean("nextui.sdl"))bundle.put("nextui_selected_hotbar",rgSelectedHotbarSlot);',1).replace('quickslot.restorePlaceholders( bundle );','quickslot.restorePlaceholders( bundle );\n        rgSelectedHotbarSlot=Math.max(0,Math.min(QuickSlot.SIZE-1,bundle.getInt("nextui_selected_hotbar")));',1))
 patch('ui/Toolbar.java','nextui-restore-hotbar',lambda s:s.replace('instance = this;','''instance = this;
        // nextui-restore-hotbar: selected slot belongs to the run, not this floor's toolbar.
        if(Boolean.getBoolean("nextui.sdl")){
            selectedHotbarSlot=Math.max(0,Math.min(QuickSlot.SIZE-1,Dungeon.rgSelectedHotbarSlot));
            updateHotbarSelection();
        }''',1).replace('selectedHotbarSlot = slots.get(index < 0 ? 0 : (index + direction + slots.size()) % slots.size());','selectedHotbarSlot = slots.get(index < 0 ? 0 : (index + direction + slots.size()) % slots.size());\n            Dungeon.rgSelectedHotbarSlot=selectedHotbarSlot;',1))
