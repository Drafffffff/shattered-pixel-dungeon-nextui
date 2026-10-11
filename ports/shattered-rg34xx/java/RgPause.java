// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.scenes.*;
import com.shatteredpixel.shatteredpixeldungeon.ui.*;
import com.shatteredpixel.shatteredpixeldungeon.windows.*;
import com.watabou.noosa.Game;
import com.watabou.noosa.ui.Component;
public final class RgPause {
 private RgPause(){}
 public static void fill(Window window){
  boolean zh=RgPlatform.chinese();int y=0;Component content=new Component();
  y=button(content,zh?"游戏设置":"Settings",y,()->{window.hide();GameScene.show(new WndSettings());});
  y=button(content,RgPlatform.menuLabel("journal"),y,()->{window.hide();GameScene.show(new WndJournal());});
  if(Dungeon.hero!=null && Dungeon.hero.isAlive()){
   y=button(content,RgPlatform.menuLabel("search"),y,()->{window.hide();if(Dungeon.hero.ready)Dungeon.hero.search(true);});
   y=button(content,zh?"浏览地图":"Browse map",y,()->{window.hide();RgMap.open();});
   y=button(content,zh?"休息至恢复":"Rest until healed",y,()->{
    window.hide();if(Dungeon.hero.ready){
     if(Dungeon.hero.visibleEnemies()>0)com.shatteredpixel.shatteredpixeldungeon.utils.GLog.w(zh?"附近有敌人，无法安全休息":"Enemies nearby: cannot rest safely");
     else Dungeon.hero.rest(true);
    }
   });
  }else y=button(content,zh?"开始新冒险":"New adventure",y,()->{GamesInProgress.curSlot=GamesInProgress.firstEmpty();GamesInProgress.selectedClass=null;ShatteredPixelDungeon.switchNoFade(HeroSelectScene.class);});
  y=button(content,zh?"按键说明":"Controls",y,()->{window.hide();GameScene.show(new RgControls());});
  if(Dungeon.challenges>0)y=button(content,zh?"本局挑战":"Challenges",y,()->{window.hide();GameScene.show(new WndChallenges(Dungeon.challenges,false));});
  y=button(content,zh?"保存并回到首页":"Save and title",y,()->{
   try{Dungeon.saveAll();}catch(java.io.IOException e){ShatteredPixelDungeon.reportException(e);return;}Game.switchScene(TitleScene.class);
  });
  y=button(content,RgPlatform.menuLabel("exit"),y,()->Game.instance.finish());
  content.setSize(172,y-2);int height=Math.min(y-2,116);window.resize(172,height);ScrollPane pane=new ScrollPane(content);window.add(pane);pane.setRect(0,0,172,height);
 }
 private static int button(Component root,String text,int y,Runnable action){
  StyledButton b=new StyledButton(Chrome.Type.GREY_BUTTON,text,7){protected void onClick(){action.run();}};
  b.setRect(0,y,172,18);root.add(b);return y+20;
 }
}
