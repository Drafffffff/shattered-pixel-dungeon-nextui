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
 private static Camera camera;
 private static Visual follow;
 private static PointF scroll,centerOffset;
 private static float zoom,overviewZoom;
 private static long hintUntil;
 private static final ColorBlock[] marker=new ColorBlock[4];
 private static com.shatteredpixel.shatteredpixeldungeon.ui.RenderedTextBlock hint;
 public static boolean active(){return active;}
 public static void open(){
  if(!(Game.scene() instanceof GameScene) || GameScene.showingWindow() || Dungeon.hero==null || !Dungeon.hero.ready)return;
  GameScene.cancel();camera=Camera.main;zoom=camera.zoom;scroll=new PointF(camera.scroll);follow=camera.followTarget();
  centerOffset=new PointF(camera.centerOffset);camera.setCenterOffset(0,0);
  overviewZoom=Math.min(1f,Math.min((camera.screenWidth()-24)/(Dungeon.level.width()*16f),(camera.screenHeight()-24)/(Dungeon.level.height()*16f)));
  camera.zoom(overviewZoom);camera.snapTo(Dungeon.level.width()*8f,Dungeon.level.height()*8f);
  uiVisible=PixelScene.uiCamera.visible;PixelScene.uiCamera.visible=false;active=true;hintUntil=System.nanoTime()+2500000000L;
 }
 public static void close(){
  if(!active)return;active=false;PixelScene.uiCamera.visible=uiVisible;
  camera.zoom(zoom);camera.setCenterOffset(centerOffset.x,centerOffset.y);camera.snapTo(scroll.x+camera.width/2f-centerOffset.x,scroll.y+camera.height/2f-centerOffset.y);
  if(follow!=null)camera.panFollow(follow,5f);
  if(hint!=null){hint.destroy();hint=null;}
  for(int i=0;i<marker.length;i++)if(marker[i]!=null){marker[i].destroy();marker[i]=null;}
 }
 public static boolean input(int key,boolean down){
  if(!active)return false;
  if(!(Game.scene() instanceof GameScene)){close();return false;}
  if(!down)return true;
  int directionKey=key>=1000 && key<1100?key-1000:key;
  int dx=directionKey==Keys.DPAD_LEFT?-1:directionKey==Keys.DPAD_RIGHT?1:0,dy=directionKey==Keys.DPAD_UP?-1:directionKey==Keys.DPAD_DOWN?1:0;
  if(dx!=0 || dy!=0){
   float cx=Math.max(0,Math.min(Dungeon.level.width()*16,camera.scroll.x+camera.width/2f+dx*24));
   float cy=Math.max(0,Math.min(Dungeon.level.height()*16,camera.scroll.y+camera.height/2f+dy*24));camera.snapTo(cx,cy);
  }else if(key==Keys.BUTTON_A)camera.snapTo(Dungeon.hero.sprite.center());
  else if(key==Keys.BUTTON_L2 || key==Keys.BUTTON_R2)camera.zoom(Math.max(overviewZoom,Math.min(PixelScene.maxZoom,camera.zoom*(key==Keys.BUTTON_L2?0.8f:1.25f))));
  else if(key==Keys.BUTTON_B || key==Keys.BUTTON_SELECT)close();
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
   if(System.nanoTime()<hintUntil){
    if(hint==null)hint=PixelScene.renderTextBlock(RgPlatform.chinese()?"青框：当前位置 · 方向浏览 · L2/R2缩放 · A回角色 · B返回":"Cyan: you · D-pad pan · L2/R2 zoom · A center · B back",6);
    hint.camera=c;hint.setPos((c.width-hint.width())/2,c.height-10);hint.draw();
   }
  }finally{c.visible=old;}
 }
}
