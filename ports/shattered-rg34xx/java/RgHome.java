// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.scenes.*;
import com.shatteredpixel.shatteredpixeldungeon.ui.*;
import com.shatteredpixel.shatteredpixeldungeon.windows.WndSettings;
import com.watabou.noosa.ColorBlock;
import com.watabou.noosa.Game;

/** Main actions fit on one quiet 240x160 handheld screen. */
public final class RgHome extends PixelScene {
 @Override public void create() {
  super.create();
  Badges.loadGlobal();com.shatteredpixel.shatteredpixeldungeon.journal.Journal.loadGlobal();
  boolean zh=RgPlatform.chinese();
  TitleBackground bg=new TitleBackground(240,160);bg.camera=uiCamera;bg.setRect(0,0,240,160);add(bg);
  RenderedTextBlock title=renderTextBlock(zh?"破碎的像素地牢":"SHATTERED",14);
  title.hardlight(0xE5D5AA);title.setPos((240-title.width())/2f,18);add(title);
  RenderedTextBlock sub=renderTextBlock(zh?"回合制地牢冒险":"PIXEL DUNGEON",6);
  sub.hardlight(0x8D9B9C);sub.setPos((240-sub.width())/2f,40);add(sub);
  boolean saved=!GamesInProgress.checkAll().isEmpty();
  float y=saved?60:73;
  if(saved) {
   StyledButton cont=new StyledButton(Chrome.Type.GREY_BUTTON,zh?"继续游戏":"Continue",8) {
    @Override protected void onClick(){ShatteredPixelDungeon.switchNoFade(StartScene.class);}
   };
   cont.setRect(45,y,150,22);add(cont);y+=27;
  }
  StyledButton start=new StyledButton(Chrome.Type.GREY_BUTTON,zh?"开始新冒险":"New adventure",8) {
   @Override protected void onClick() {
    int slot=GamesInProgress.firstEmpty();
    if(slot<0){ShatteredPixelDungeon.switchNoFade(StartScene.class);return;}
    GamesInProgress.selectedClass=null;GamesInProgress.curSlot=slot;
    ShatteredPixelDungeon.switchNoFade(HeroSelectScene.class);
   }
  };
  start.setRect(45,y,150,22);add(start);y+=27;
  StyledButton settings=new StyledButton(Chrome.Type.GREY_BUTTON,zh?"设置与按键说明":"Settings and controls",7) {
   @Override protected void onClick(){RgHome.this.addToFront(new Preferences());}
  };
  settings.setRect(45,y,150,22);add(settings);
  RenderedTextBlock hint=renderTextBlock(zh?"十字键选择 · A确定 · B返回NextUI":"D-pad select · A confirm · B quit",6);
  hint.hardlight(0x8D9B9C);hint.setPos((240-hint.width())/2f,146);add(hint);
 }
 @Override protected void onBackPressed(){Game.instance.finish();}
 private static final class Preferences extends Window {
  Preferences() {
   resize(172,52);
   StyledButton settings=new StyledButton(Chrome.Type.GREY_BUTTON,RgPlatform.chinese()?"游戏设置":"Game settings",8) {
    @Override protected void onClick(){hide();Game.scene().addToFront(new WndSettings());}
   };
   settings.setRect(2,2,168,22);add(settings);
   StyledButton controls=new StyledButton(Chrome.Type.GREY_BUTTON,RgPlatform.chinese()?"按键说明":"Controls",8) {
    @Override protected void onClick(){hide();Game.scene().addToFront(new RgControls());}
   };
   controls.setRect(2,28,168,22);add(controls);
  }
 }
}
