// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.badlogic.gdx.*;
import com.badlogic.gdx.backends.lwjgl3.*;
import com.badlogic.gdx.backends.lwjgl3.audio.OpenALLwjgl3Audio;
import com.badlogic.gdx.backends.lwjgl3.angle.Lwjgl3GLES20;
import com.badlogic.gdx.backends.headless.mock.input.MockInput;
import com.badlogic.gdx.utils.*;
import com.badlogic.gdx.graphics.*;
import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.messages.Languages;
import com.watabou.input.*;
import com.watabou.noosa.Game;
import com.watabou.utils.FileUtils;
import org.lwjgl.opengles.GLES;
import java.lang.reflect.Proxy;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.nio.file.*;

public final class RgLauncher {
 private static volatile boolean running=true;
 private static final CountDownLatch stopped=new CountDownLatch(1);
 private static final java.util.Queue<Runnable> queue=new ConcurrentLinkedQueue<>();
 private static ShatteredPixelDungeon game;
 private static final Clipboard clipboard=new Clipboard(){
  private String content=""; public String getContents(){return content;} public void setContents(String s){content=s==null?"":s;} public boolean hasContents(){return !content.isEmpty();}
 };
 private static long selectPressed;
 private static com.watabou.noosa.Scene selectMapOwner;
 private static final Set<Integer> held=new HashSet<>();
 private static final Set<Integer> suppressedModifiers=new HashSet<>();
 private static final java.util.List<LifecycleListener> listeners=new ArrayList<>();
 private static class RgInput extends MockInput {
  InputProcessor processor;
  @Override public void setInputProcessor(InputProcessor p){processor=p;}
  @Override public InputProcessor getInputProcessor(){return processor;}
  @Override public boolean isKeyPressed(int key){return key==Input.Keys.ANY_KEY?!held.isEmpty():held.contains(key);}
  @Override public int getMaxPointers(){return 20;}
 }
 public static void main(String[] args) throws Exception {
  System.setProperty("nextui.sdl","true");
  String saves=System.getenv().getOrDefault("SPD_SAVE_DIR","./saves")+"/";
  java.nio.file.Files.createDirectories(Paths.get(saves));
  Map<String,Preferences> prefs=new HashMap<>();
  Gdx.app=(Application)Proxy.newProxyInstance(RgLauncher.class.getClassLoader(),new Class[]{Application.class},(p,m,a)->{
   switch(m.getName()) {
    case "getType": return Application.ApplicationType.Desktop;
    case "getVersion": return 0;
    case "getJavaHeap": return Runtime.getRuntime().totalMemory()-Runtime.getRuntime().freeMemory();
    case "getNativeHeap": return 0L;
    case "getApplicationListener":return game;
    case "getClipboard":return clipboard;
    case "getGraphics":return Gdx.graphics;
    case "getInput":return Gdx.input;
    case "getAudio":return Gdx.audio;
    case "getFiles":return Gdx.files;
    case "getNet":return Gdx.net;
    case "getPreferences":return prefs.computeIfAbsent((String)a[0],n->new Lwjgl3Preferences(new Lwjgl3FileHandle(saves+n,com.badlogic.gdx.Files.FileType.Absolute)));
    case "postRunnable":queue.add((Runnable)a[0]);return null;
    case "exit":running=false;return null;
    case "addLifecycleListener":listeners.add((LifecycleListener)a[0]);return null;
    case "removeLifecycleListener":listeners.remove(a[0]);return null;
    case "getLogLevel":return Application.LOG_INFO;
    case "log":case "error":case "debug":System.err.println(a[0]+": "+a[1]);if(a.length>2)((Throwable)a[2]).printStackTrace();return null;
    case "toString":return "NextUI SDL Application";
    default: if(m.getReturnType()==boolean.class)return false; if(m.getReturnType()==int.class)return 0; return null;
   }
  });
  Gdx.files=new Lwjgl3Files(); Gdx.input=new RgInput();
  Gdx.net=new com.badlogic.gdx.backends.headless.HeadlessNet(new com.badlogic.gdx.backends.headless.HeadlessApplicationConfiguration());
  com.badlogic.gdx.utils.GdxNativesLoader.load();
  Sdl.init();
  try {
   GLES.createCapabilities();
   Gdx.gl=Gdx.gl20=new Lwjgl3GLES20();
   RgGraphics graphics=new RgGraphics(Gdx.gl); Gdx.graphics=graphics;
   System.err.println("GPU: "+Gdx.gl.glGetString(GL20.GL_RENDERER)+" / "+Gdx.gl.glGetString(GL20.GL_VERSION));
   OpenALLwjgl3Audio audio=new OpenALLwjgl3Audio(12,4,512); Gdx.audio=audio;
   SPDSettings.set(Gdx.app.getPreferences(SPDSettings.DEFAULT_PREFS_FILE));
   FileUtils.setDefaultFileProperties(com.badlogic.gdx.Files.FileType.Absolute,saves);
   if(!Gdx.app.getPreferences(SPDSettings.DEFAULT_PREFS_FILE).getBoolean("rg34xx-profile-v1",false)) {
    SPDSettings.language(Languages.CHI_SMPL); SPDSettings.interfaceSize(0); SPDSettings.scale(3);
    Gdx.app.getPreferences(SPDSettings.DEFAULT_PREFS_FILE).putBoolean("rg34xx-profile-v1",true).flush();
   }
   ControllerHandler.controllerActive=true; ControllerHandler.lastUsedType=ControllerHandler.ControllerType.NINTENDO;
   Game.version="4.0.2"; Game.versionCode=922;
   game=new ShatteredPixelDungeon(new RgPlatform());
   game.create(); game.resize(720,480);
   Runtime.getRuntime().addShutdownHook(new Thread(()->{running=false;try{stopped.await(3,TimeUnit.SECONDS);}catch(InterruptedException ignored){Thread.currentThread().interrupt();}}));
   long start=System.nanoTime(); int smoke=Integer.getInteger("nextui.smokeSeconds",0); long frames=0;
   long peakRss=0;String lastScene="";
   while(running) {
    long frameStart=System.nanoTime();
    for(int k:Sdl.poll()) {if(k==99999){running=false;continue;} input(k);}
    // Test commands are opt-in, local to this process, and never touch other apps.
    String commands=System.getProperty("nextui.commands");
    if(commands!=null && java.nio.file.Files.exists(Paths.get(commands))) {
     for(String line:java.nio.file.Files.readAllLines(Paths.get(commands))) {
      if(line.equals("exit"))running=false;
      else if(line.startsWith("fixture-ux "))RgTestFixtures.run(line.substring(11));
      else if(line.equals("fixture-death")) {Dungeon.hero.HP=0;Dungeon.hero.ready=false;com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene.gameOver();}
      else if(line.equals("fixture-guide"))com.shatteredpixel.shatteredpixeldungeon.journal.Document.ADVENTURERS_GUIDE.findPage(0);
      else if(line.startsWith("state ")) writeTestState(line.substring(6));
      else if(line.startsWith("down ")) input(Integer.parseInt(line.substring(5)));
      else if(line.startsWith("up ")) input(-Integer.parseInt(line.substring(3)));
      else if(line.startsWith("key ")) {int k=Integer.parseInt(line.substring(4));input(k);input(-k);}
      else if(line.startsWith("shot ")) screenshot(line.substring(5));
     }
     java.nio.file.Files.deleteIfExists(Paths.get(commands));
    }
    updateHeldShortcuts();
    Runnable r;while((r=queue.poll())!=null)r.run();
    graphics.updateTime();graphics.incrementFrameId(); audio.update();game.render();
    String scene=Game.scene()==null?"loading":Game.scene().getClass().getSimpleName();
    if(!scene.equals(lastScene)){System.err.println("Scene: "+scene);lastScene=scene;}
    Sdl.swap();frames++;
    if(frames%150==0){long rss=rssKiB();peakRss=Math.max(peakRss,rss);System.err.printf("Metrics: fps=%d RSS=%d KiB heap=%.1f MiB%n",graphics.getFramesPerSecond(),rss,(Runtime.getRuntime().totalMemory()-Runtime.getRuntime().freeMemory())/1048576.0);}
    if(smoke>0 && System.nanoTime()-start>smoke*1000000000L) {screenshot(saves+"smoke.png");running=false;}
    long remaining=33333333L-(System.nanoTime()-frameStart);if(remaining>0)Thread.sleep(remaining/1000000,(int)(remaining%1000000));
   }
   peakRss=Math.max(peakRss,rssKiB());
   game.pause();for(LifecycleListener l:listeners)l.pause();game.dispose();audio.dispose();
   System.err.printf("Peak sampled RSS: %d KiB%n",peakRss);
   System.err.printf("Completed: %d frames, %.1f fps, heap %.1f MiB%n",frames,frames/((System.nanoTime()-start)/1e9),(Runtime.getRuntime().totalMemory()-Runtime.getRuntime().freeMemory())/1048576.0);
  } finally { RgSystemOverlay.close(); Sdl.close(); stopped.countDown(); }
 }
 private static void input(int event) {
  int k=Math.abs(event);boolean down=event>0;
  if(!down && k==Input.Keys.BUTTON_SELECT)updateHeldShortcuts();
  boolean firstDown=down && !held.contains(k);
  if(down)held.add(k);else held.remove(k);
  if(k==Input.Keys.BUTTON_SELECT && firstDown){
   selectPressed=System.nanoTime();selectMapOwner=canHoldMap()?Game.scene():null;
  }
  if(k==20001 || k==20002) {
   if(down) {
    boolean menu=held.contains(Input.Keys.BUTTON_THUMBL),select=held.contains(Input.Keys.BUTTON_SELECT);
    if(menu)suppressedModifiers.add(Input.Keys.BUTTON_THUMBL);
    if(select)suppressedModifiers.add(Input.Keys.BUTTON_SELECT);
    RgSystemOverlay.hardwareKey(menu,select);
   }
   return;
  }
  if(held.contains(Input.Keys.BUTTON_SELECT)&&held.contains(Input.Keys.BUTTON_START)){running=false;return;}
  ControllerHandler.controllerActive=true;
  // Delay short modifier actions until release: brightness/color adjustments must
  // not also spend a turn or open the hero window.
  if(k==Input.Keys.BUTTON_THUMBL || k==Input.Keys.BUTTON_SELECT) {
   if(!down && !suppressedModifiers.remove(k)) {
    if(!RgInteraction.handle(k,true)) {
      KeyEvent.addKeyEvent(new KeyEvent(k,true));KeyEvent.addKeyEvent(new KeyEvent(k,false));
     }
   }
   if(!down && k==Input.Keys.BUTTON_SELECT)selectMapOwner=null;
   return;
  }
  if(RgSearchShortcut.input(k,down))return;
  if(!RgInteraction.handle(k,down))KeyEvent.addKeyEvent(new KeyEvent(k,down));
 }
 private static boolean canHoldMap(){
  return Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene
   && !com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene.showingWindow()
   && !com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene.selectingCell()
   && Dungeon.hero!=null && Dungeon.hero.isAlive();
 }
 private static void updateHeldShortcuts(){
  RgMap.update();
  RgSearchShortcut.update();
  if(selectMapOwner==null || !held.contains(Input.Keys.BUTTON_SELECT))return;
  if(Game.scene()!=selectMapOwner || !canHoldMap() || suppressedModifiers.contains(Input.Keys.BUTTON_SELECT)){
   selectMapOwner=null;return;
  }
  if(System.nanoTime()-selectPressed>=550000000L){
   selectMapOwner=null;suppressedModifiers.add(Input.Keys.BUTTON_SELECT);
   if(RgMap.active())RgMap.close();else RgMap.open();
  }
 }
 private static long rssKiB() {
  try {for(String line:java.nio.file.Files.readAllLines(Paths.get("/proc/self/status")))if(line.startsWith("VmRSS:"))return Long.parseLong(line.trim().split("\\s+")[1]);}catch(Exception ignored){}
  return -1;
 }
 private static void screenshot(String path) {
  Pixmap pix=Pixmap.createFromFrameBuffer(0,0,720,480);
  try {PixmapIO.writePNG(Gdx.files.absolute(path),pix,-1,true);} finally {pix.dispose();}
 }
 private static void writeTestState(String path) throws Exception {
  com.badlogic.gdx.utils.ObjectMap<String,Object> state=new com.badlogic.gdx.utils.ObjectMap<>();
  state.put("intro",SPDSettings.intro());
  state.put("gameVersion",Game.version);state.put("versionCode",Game.versionCode);state.put("settingsVersion",SPDSettings.version());
  state.put("heroClass",Dungeon.hero==null?"":Dungeon.hero.heroClass.name());state.put("heroLevel",Dungeon.hero==null?0:Dungeon.hero.lvl);
  state.put("inputText",RgTestFixtures.textValue());
  state.put("mapOverview",RgMap.overview());state.put("mapCursorCell",RgMap.cursorCell());
  state.put("mapMode",RgMap.active());state.put("uiVisible",com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene.uiCamera.visible);
  state.put("ready",Dungeon.hero!=null && Dungeon.hero.ready);
  state.put("heroAction",Dungeon.hero==null || Dungeon.hero.curAction==null?"":Dungeon.hero.curAction.getClass().getName());
  state.put("actorProcessing",com.shatteredpixel.shatteredpixeldungeon.actors.Actor.processing());
  state.put("heap",Dungeon.hero!=null && Dungeon.level!=null && Dungeon.level.heaps.get(Dungeon.hero.pos)!=null);
  state.put("pos",Dungeon.hero==null?-1:Dungeon.hero.pos);state.put("gold",Dungeon.gold);
  state.put("targetCell",com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene.rgTarget());
  if(Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene && Dungeon.hero!=null){
   com.watabou.utils.PointF pointer=ControllerHandler.getControllerPointerPos();
   state.put("pointerX",pointer.x);state.put("pointerY",pointer.y);
   state.put("heroCameraFollow",com.watabou.noosa.Camera.main.followTarget()==Dungeon.hero.sprite);
   state.put("exploredTiles",java.util.stream.IntStream.range(0,Dungeon.level.length()).filter(i->Dungeon.level.visited[i] || Dungeon.level.mapped[i]).count());
  }
  state.put("journalTab",com.shatteredpixel.shatteredpixeldungeon.windows.WndJournal.last_index);
  state.put("heroTab",com.shatteredpixel.shatteredpixeldungeon.windows.WndHero.lastIdx);
  state.put("cameraX",com.watabou.noosa.Camera.main.scroll.x);state.put("cameraY",com.watabou.noosa.Camera.main.scroll.y);
  state.put("cameraZoom",com.watabou.noosa.Camera.main.zoom);
  state.put("cameraWorldWidth",com.watabou.noosa.Camera.main.width);state.put("cameraWorldHeight",com.watabou.noosa.Camera.main.height);
  state.put("mapWidth",Dungeon.level==null?0:Dungeon.level.width()*16);state.put("mapHeight",Dungeon.level==null?0:Dungeon.level.height()*16);
  com.shatteredpixel.shatteredpixeldungeon.ui.Window top=com.shatteredpixel.shatteredpixeldungeon.ui.Window.rgTop();
  com.watabou.noosa.ui.Component focus=top==null?(Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.AlchemyScene?((com.shatteredpixel.shatteredpixeldungeon.scenes.AlchemyScene)Game.scene()).rgFocused():null):top.rgFocused();
  state.put("focusItem",focus instanceof com.shatteredpixel.shatteredpixeldungeon.ui.InventorySlot && ((com.shatteredpixel.shatteredpixeldungeon.ui.InventorySlot)focus).item()!=null?((com.shatteredpixel.shatteredpixeldungeon.ui.InventorySlot)focus).item().getClass().getSimpleName():"");
  state.put("energy",Dungeon.energy);state.put("itemsCrafted",Statistics.itemsCrafted);
  if(Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.AlchemyScene){
   state.put("alchemyFocus",((com.shatteredpixel.shatteredpixeldungeon.scenes.AlchemyScene)Game.scene()).rgFocusId());
   java.lang.reflect.Field field=Game.scene().getClass().getDeclaredField("inputs");field.setAccessible(true);Object[] inputs=(Object[])field.get(null);String materials="";
   for(Object input:inputs){java.lang.reflect.Method method=input.getClass().getDeclaredMethod("item");method.setAccessible(true);com.shatteredpixel.shatteredpixeldungeon.items.Item item=(com.shatteredpixel.shatteredpixeldungeon.items.Item)method.invoke(input);materials+=(item==null?"empty":item.getClass().getSimpleName()+":"+item.quantity())+";";}
   state.put("alchemyMaterials",materials);
  }
  if(Dungeon.hero!=null){String inventory="";for(com.shatteredpixel.shatteredpixeldungeon.items.Item item:Dungeon.hero.belongings.backpack.items)inventory+=item.getClass().getSimpleName()+":"+item.quantity()+";";state.put("inventoryItems",inventory);}
  state.put("focusType",focus==null?"":focus.getClass().getName());
  if(focus!=null){com.watabou.utils.Point point=focus.camera().cameraToScreen(focus.centerX(),focus.centerY());state.put("focusScreenX",point.x);state.put("focusScreenY",point.y);}
  com.shatteredpixel.shatteredpixeldungeon.ui.Window topWindow=com.shatteredpixel.shatteredpixeldungeon.ui.Window.rgTop();
  if(topWindow!=null){state.put("windowLeft",topWindow.camera.x);state.put("windowTop",topWindow.camera.y);state.put("windowRight",topWindow.camera.x+topWindow.camera.screenWidth());state.put("windowBottom",topWindow.camera.y+topWindow.camera.screenHeight());}
  state.put("focusX",focus==null?-1:focus.centerX());state.put("focusY",focus==null?-1:focus.centerY());
  state.put("focusText",focus instanceof com.shatteredpixel.shatteredpixeldungeon.ui.StyledButton?((com.shatteredpixel.shatteredpixeldungeon.ui.StyledButton)focus).text():"");
  String slots="";for(int slot=0;slot<QuickSlot.SIZE;slot++)slots+=Dungeon.quickslot.getItem(slot)==null?"empty;":Dungeon.quickslot.getItem(slot).getClass().getSimpleName()+";";
  state.put("quickslots",slots);
  state.put("depth",Dungeon.depth);state.put("branch",Dungeon.branch);
  state.put("levelType",Dungeon.level==null?"":Dungeon.level.getClass().getSimpleName());
  state.put("fixtureDirection",RgTestFixtures.directionKey);
  state.put("fixtureNpcPresent",RgTestFixtures.testNpc!=null && Dungeon.level!=null && Dungeon.level.mobs.contains(RgTestFixtures.testNpc));
  state.put("mirrorUsed",com.shatteredpixel.shatteredpixeldungeon.actors.mobs.npcs.Imp.Quest.mirrorUsed);
  state.put("overlay",RgSystemOverlay.label());
  state.put("scene",Game.scene().getClass().getSimpleName());
  String windows="";int windowCount=0;
  for(com.watabou.noosa.Gizmo member:Game.scene().members())
   if(member instanceof com.shatteredpixel.shatteredpixeldungeon.ui.Window && member.visible){String type=member.getClass().getSimpleName();if(type.isEmpty())type=member.getClass().getSuperclass().getSimpleName();windows+=type+";";windowCount++;}
  state.put("windows",windows);
  state.put("windowCount",windowCount);
  state.put("alive",Dungeon.hero==null || Dungeon.hero.isAlive());
  state.put("targetPrompt",false);
  if(Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene) {
   java.lang.reflect.Field promptField=Game.scene().getClass().getDeclaredField("prompt");promptField.setAccessible(true);
   state.put("targetPrompt",promptField.get(Game.scene())!=null);
  }
  state.put("targeting",com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene.selectingCell());
  state.put("turn",com.shatteredpixel.shatteredpixeldungeon.actors.Actor.now());
  int hidden=0;
  if(Dungeon.level!=null)for(int tile:Dungeon.level.map)if(tile==com.shatteredpixel.shatteredpixeldungeon.levels.Terrain.SECRET_DOOR)hidden++;
  state.put("hiddenDoors",hidden);
  if(Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene)
   state.put("cursor",((com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene)Game.scene()).shouldDrawControllerCursor());
  if(Game.scene() instanceof com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene) {
   for(String name:new String[]{"status","toolbar"}) {
    java.lang.reflect.Field field=Game.scene().getClass().getDeclaredField(name);field.setAccessible(true);
    com.watabou.noosa.Gizmo widget=(com.watabou.noosa.Gizmo)field.get(Game.scene());
    state.put(name,widget.visible && widget.active);
    if(name.equals("toolbar")) {
     java.lang.reflect.Field index=widget.getClass().getDeclaredField("selectedHotbarSlot");index.setAccessible(true);
     int slot=index.getInt(widget);state.put("hotbar",slot);
     java.lang.reflect.Method control=widget.getClass().getDeclaredMethod("hotbarControl",int.class);control.setAccessible(true);
     com.watabou.noosa.ui.Component button=(com.watabou.noosa.ui.Component)control.invoke(widget,slot);
     state.put("hotbarX",button.centerX());
     String positions="";
     for(int i=0;i<QuickSlot.SIZE+2;i++) {
      com.watabou.noosa.ui.Component candidate=(com.watabou.noosa.ui.Component)control.invoke(widget,i);
      if(candidate.isVisible())positions+=i+":"+candidate.centerX()+",";
     }
     state.put("hotbarPositions",positions);
    }
   }
  }
  com.badlogic.gdx.utils.Json json=new com.badlogic.gdx.utils.Json();
  json.setOutputType(com.badlogic.gdx.utils.JsonWriter.OutputType.json);
  java.nio.file.Files.writeString(Paths.get(path),json.toJson(state));
 }
}
