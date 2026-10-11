// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;

import com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene;
import com.shatteredpixel.shatteredpixeldungeon.ui.RenderedTextBlock;
import com.watabou.noosa.ColorBlock;
import com.watabou.noosa.Camera;
import java.nio.*;
import java.nio.file.*;

/** Read-only H700 SettingsV1 observer. keymon remains the sole hardware owner. */
public final class RgSystemOverlay {
 private static int volume=-1,brightness=-1,color=-1,requested;
 private static long nextPoll,until;
 private static String label="";
 private static RenderedTextBlock text;
 private static ColorBlock background;
 public static void hardwareKey(boolean menu,boolean select) {
  requested=menu?2:select?3:1;until=System.nanoTime()+2000000000L;nextPoll=0;
 }
 public static String label(){return System.nanoTime()<until?label:"";}
 public static void draw() {
  long now=System.nanoTime();
  if(now>=nextPoll) {
   nextPoll=now+100000000L;
   String path="/dev/shm/SharedSettings";
   if(System.getProperty("nextui.commands")!=null)path=System.getProperty("nextui.settingsFile",path);
   try {
    byte[] bytes=Files.readAllBytes(Paths.get(path));
    if(bytes.length!=64)return;
    IntBuffer settings=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).asIntBuffer();
    if(settings.get(0)!=1)return;
    int v=settings.get(settings.get(10)!=0 || settings.get(11)!=0?3:4),b=settings.get(1),c=settings.get(2);
    if(v<0 || v>20 || b<0 || b>10 || c<0 || c>40)return;
    if(volume>=0 && (v!=volume || b!=brightness || c!=color)) {
     requested=b!=brightness?2:c!=color?3:1;until=now+2000000000L;
    }
    volume=v;brightness=b;color=c;
    label=requested==2?(RgPlatform.chinese()?"亮度 ":"Brightness ")+b+" / 10"
     :requested==3?(RgPlatform.chinese()?"色温 ":"Color temp ")+c+" / 40"
     :(RgPlatform.chinese()?"音量 ":"Volume ")+v+" / 20";
   } catch(java.io.IOException ignored) {return;}
  }
  if(now>=until || label.isEmpty())return;
  Camera camera=PixelScene.uiCamera;
  if(camera==null)return;
  if(text==null) {text=PixelScene.renderTextBlock(8);background=new ColorBlock(124,24,0xEE161C24);}
  text.text(label);text.camera=background.camera=camera;
  background.x=(camera.width-124)/2f;background.y=10;
  text.setPos((camera.width-text.width())/2f,16);
  boolean old=camera.visible;camera.visible=true;background.draw();text.draw();camera.visible=old;
 }
 public static void close() {
  if(text!=null)text.destroy();if(background!=null)background.destroy();text=null;background=null;
 }
}
