// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.items.Item;
import com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene;
import com.shatteredpixel.shatteredpixeldungeon.ui.QuickSlotButton;
import com.shatteredpixel.shatteredpixeldungeon.windows.*;
public final class RgQuickslot {
 private RgQuickslot(){}
 public static void manage(int slot){
  boolean zh=RgPlatform.chinese();
  GameScene.show(new WndOptions(zh?"快捷格 "+(slot+1):"Quickslot "+(slot+1),zh?"更换前取消会保留原物品":"Cancel keeps the original item",zh?"取消":"Cancel",zh?"更换物品":"Replace",zh?"清空此格":"Clear"){
   @Override protected void onSelect(int i){if(i==1)assign(slot);else if(i==2){Dungeon.quickslot.clearSlot(slot);QuickSlotButton.refresh();}}
  });
 }
 public static void assign(int slot){
  GameScene.selectItem(new WndBag.ItemSelector(){
   public String textPrompt(){return RgPlatform.chinese()?"选择快捷物品 · B取消":"Choose item · B cancel";}
   public boolean itemSelectable(Item i){return i.defaultAction()!=null;}
   public void onSelect(Item i){if(i!=null)QuickSlotButton.set(slot,i);}
  });
 }
 public static void forItem(Item item){
  boolean zh=RgPlatform.chinese();String[] opts=new String[QuickSlot.SIZE+1];opts[0]=zh?"取消":"Cancel";
  for(int n=0;n<QuickSlot.SIZE;n++)opts[n+1]=(zh?"格 ":"Slot ")+(n+1)+": "+(Dungeon.quickslot.getItem(n)==null?(zh?"空":"Empty"):Dungeon.quickslot.getItem(n).name());
  GameScene.show(new WndOptions(zh?"放入快捷栏":"Assign quickslot",item.name(),opts){@Override protected void onSelect(int n){if(n>0)QuickSlotButton.set(n-1,item);}});
 }
}
