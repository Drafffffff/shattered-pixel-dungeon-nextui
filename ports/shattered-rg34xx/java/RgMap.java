// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.badlogic.gdx.Input.Keys;
import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.scenes.*;
import com.watabou.noosa.*;
import com.watabou.utils.PointF;
/** Read-only camera state: consumes all world input and never advances a turn. */
public final class RgMap {
 private static boolean active,uiVisible;
 private static int cursorX,cursorY;
 private static long repeatAt;
 private static final java.util.Set<Integer> directions=new java.util.HashSet<>();
 private static Camera camera;
 private static Visual follow;
 private static PointF scroll,centerOffset;
 private static float zoom,overviewZoom;
 private static long hintUntil;
 private static final ColorBlock[] marker=new ColorBlock[4],cursor=new ColorBlock[4];
 private static com.shatteredpixel.shatteredpixeldungeon.ui.RenderedTextBlock hint;
 public static boolean active(){return active;}
 public static boolean overview(){return active && camera.zoom<=overviewZoom+.0001f;}
 public static int cursorCell(){return active?cursorX+cursorY*Dungeon.level.width():-1;}
 private static PointF cursorWorld(){return new PointF(cursorX*16+8,cursorY*16+8);}
 private static void help(){hintUntil=System.nanoTime()+3000000000L;if(hint!=null){hint.destroy();hint=null;}}
 private static void showOverview(){camera.zoom(overviewZoom);camera.snapTo(Dungeon.level.width()*8f,Dungeon.level.height()*8f);help();}
 private static void focusRegion(float requested){
  camera.zoom(Math.max(overviewZoom,Math.min(PixelScene.maxZoom,requested)));
  if(camera.zoom<=overviewZoom+.0001f)showOverview();else {camera.snapTo(cursorWorld());help();}
 }
 private static int dx(int k){return k==Keys.DPAD_LEFT?-1:k==Keys.DPAD_RIGHT?1:0;}
 private static int dy(int k){return k==Keys.DPAD_UP?-1:k==Keys.DPAD_DOWN?1:0;}
 private static void move(int x,int y){
  cursorX=Math.max(0,Math.min(Dungeon.level.width()-1,cursorX+x));
  cursorY=Math.max(0,Math.min(Dungeon.level.height()-1,cursorY+y));
  if(!overview())camera.snapTo(cursorWorld());
 }
 public static void update(){
  if(!active || directions.isEmpty() || System.nanoTime()<repeatAt)return;
  int x=0,y=0;for(int k:directions){x+=dx(k);y+=dy(k);}
  move(x,y);repeatAt=System.nanoTime()+85000000L;
 }
 public static void open(){
  if(!(Game.scene() instanceof GameScene) || GameScene.showingWindow() || Dungeon.hero==null || !Dungeon.hero.ready)return;
  GameScene.cancel();camera=Camera.main;zoom=camera.zoom;scroll=new PointF(camera.scroll);follow=camera.followTarget();
  centerOffset=new PointF(camera.centerOffset);camera.setCenterOffset(0,0);
  overviewZoom=Math.min(1f,Math.min((camera.screenWidth()-24)/(Dungeon.level.width()*16f),(camera.screenHeight()-24)/(Dungeon.level.height()*16f)));
  cursorX=Dungeon.hero.pos%Dungeon.level.width();cursorY=Dungeon.hero.pos/Dungeon.level.width();directions.clear();
  showOverview();
  uiVisible=PixelScene.uiCamera.visible;PixelScene.uiCamera.visible=false;active=true;
 }
 public static void close(){
  if(!active)return;active=false;directions.clear();PixelScene.uiCamera.visible=uiVisible;
  camera.zoom(zoom);camera.setCenterOffset(centerOffset.x,centerOffset.y);camera.snapTo(scroll.x+camera.width/2f-centerOffset.x,scroll.y+camera.height/2f-centerOffset.y);
  if(follow!=null)camera.panFollow(follow,5f);
  if(hint!=null){hint.destroy();hint=null;}
  for(int i=0;i<marker.length;i++){if(marker[i]!=null){marker[i].destroy();marker[i]=null;}if(cursor[i]!=null){cursor[i].destroy();cursor[i]=null;}}
 }
 public static boolean input(int key,boolean down){
  if(!active)return false;
  if(!(Game.scene() instanceof GameScene)){close();return false;}
  int directionKey=key>=1000 && key<1100?key-1000:key;
  int dx=dx(directionKey),dy=dy(directionKey);
  if(dx!=0 || dy!=0){
   if(down && directions.add(directionKey)){move(dx,dy);repeatAt=System.nanoTime()+250000000L;}
   else if(!down)directions.remove(directionKey);
   return true;
  }
  if(!down)return true;
  if(key==Keys.BUTTON_A)focusRegion(Math.max(camera.zoom,Math.max(PixelScene.defaultZoom,overviewZoom*2f)));
  else if(key==Keys.BUTTON_L2 || key==Keys.BUTTON_R2)focusRegion(camera.zoom*(key==Keys.BUTTON_L2?0.8f:1.25f));
  else if(key==Keys.BUTTON_B){if(overview())close();else showOverview();}
  else if(key==Keys.BUTTON_SELECT)close();
  else if(key==Keys.BUTTON_START){close();GameScene.show(new com.shatteredpixel.shatteredpixeldungeon.windows.WndGame());}
  return true;
 }
 public static void draw(){
  if(!active)return;
  Camera c=PixelScene.uiCamera;boolean old=c.visible;c.visible=true;
  try {
   com.watabou.utils.Point screen=camera.cameraToScreen(Dungeon.hero.sprite.center().x,Dungeon.hero.sprite.center().y);
   if(screen.x>=camera.x && screen.x<camera.x+camera.screenWidth() && screen.y>=camera.y && screen.y<camera.y+camera.screenHeight()){
    PointF point=c.screenToCamera(screen.x,screen.y);float half=Math.max(5f,camera.zoom*8f/c.zoom+2f);
    for(int i=0;i<4;i++){
     if(marker[i]==null)marker[i]=new ColorBlock(1,1,0xFF62E9FF);
     ColorBlock edge=marker[i];edge.camera=c;edge.am=.75f+.25f*(float)Math.sin(System.nanoTime()/220000000d);
     edge.x=point.x-half+(i==3?half*2-1:0);edge.y=point.y-half+(i==1?half*2-1:0);
     edge.size(i<2?half*2:1,i<2?1:half*2);edge.draw();
    }
   }
   PointF world=cursorWorld();com.watabou.utils.Point cs=camera.cameraToScreen(world.x,world.y);
   PointF cp=c.screenToCamera(cs.x,cs.y);
   // Separate white crosshair with a black outline; cyan remains the hero marker.
   for(int i=0;i<cursor.length;i++){
    if(cursor[i]==null)cursor[i]=new ColorBlock(1,1,i<2?0xFF101010:0xFFFFFFFF);
    ColorBlock bar=cursor[i];bar.camera=c;
    float half=Math.max(4f,camera.zoom*8f/c.zoom+1f),thick=i<2?3f:1f;
    boolean horizontal=i%2==0;bar.x=cp.x-(horizontal?half:thick/2);bar.y=cp.y-(horizontal?thick/2:half);
    bar.size(horizontal?half*2:thick,horizontal?thick:half*2);bar.draw();
   }
   if(System.nanoTime()<hintUntil){
    if(hint==null)hint=PixelScene.renderTextBlock(RgPlatform.chinese()?(overview()?"青框是角色 · 方向选区 · A放大 · B退出":"方向浏览 · L2/R2缩放 · B回全览"):(overview()?"Cyan: you · D-pad select · A zoom · B exit":"D-pad browse · L2/R2 zoom · B overview"),6);
    hint.camera=c;hint.setPos((c.width-hint.width())/2,c.height-10);hint.draw();
   }
  }finally{c.visible=old;}
 }
}
