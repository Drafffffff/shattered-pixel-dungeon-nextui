// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;

import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.scenes.*;
import com.shatteredpixel.shatteredpixeldungeon.ui.*;
import com.shatteredpixel.shatteredpixeldungeon.windows.WndOptions;
import com.shatteredpixel.shatteredpixeldungeon.utils.DungeonSeed;
import com.watabou.noosa.Game;

/** Keep both run actions inside the 240x160 handheld viewport. */
public final class RgRunDetails extends Window {
 public RgRunDetails(int slot) {
  resize(196,126);
  GamesInProgress.Info info=GamesInProgress.check(slot);
  boolean zh=RgPlatform.chinese();
  RenderedTextBlock title=PixelScene.renderTextBlock((zh?"存档 ":"Save ")+slot+" · "+info.heroClass.title(),8);
  title.hardlight(TITLE_COLOR);title.maxWidth(190);title.setPos(3,2);add(title);
  String details=zh?"等级 "+info.level+"   最深层数 "+info.maxDepth+"\n生命 "+info.hp+" / "+info.ht+"\n种子 "+DungeonSeed.convertToCode(info.seed)
   :"Level "+info.level+"   Deepest floor "+info.maxDepth+"\nHP "+info.hp+" / "+info.ht+"\nSeed "+DungeonSeed.convertToCode(info.seed);
  RenderedTextBlock body=PixelScene.renderTextBlock(details,6);
  body.maxWidth(190);body.setPos(3,title.bottom()+5);add(body);
  StyledButton cont=new StyledButton(Chrome.Type.GREY_BUTTON,zh?"继续游戏":"Continue",7) {
   @Override protected void onClick() {
    GamesInProgress.curSlot=slot;Dungeon.hero=null;Dungeon.daily=Dungeon.dailyReplay=false;
    ActionIndicator.clearAction();InterlevelScene.mode=InterlevelScene.Mode.CONTINUE;
    ShatteredPixelDungeon.switchScene(InterlevelScene.class);
   }
  };
  cont.setRect(2,71,192,22);add(cont);
  RedButton erase=new RedButton(zh?"删除此存档…":"Delete this save…",7) {
   @Override protected void onClick() {
    Game.scene().addToFront(new WndOptions(Icons.get(Icons.WARNING),zh?"删除存档 "+slot:"Delete save "+slot,
     zh?"删除此角色与地牢进度后无法恢复。其他存档不受影响。":"This hero and dungeon progress cannot be recovered. Other saves are kept.",
     zh?"取消，保留存档":"Cancel, keep save",zh?"确认删除":"Delete save") {
      @Override protected void onSelect(int index) {
       if(index==1) {Dungeon.deleteGame(slot,true);ShatteredPixelDungeon.switchNoFade(StartScene.class);}
      }
     });
   }
  };
  erase.setRect(2,98,192,22);add(erase);
 }
}
