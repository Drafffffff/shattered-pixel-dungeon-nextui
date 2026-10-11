// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.badlogic.gdx.Input.Keys;
import com.shatteredpixel.shatteredpixeldungeon.Dungeon;
import com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene;
import com.watabou.noosa.Game;
/** Hardware dispatch owns explicit modes before any hidden HUD key listeners. */
public final class RgInteraction {
 public static boolean handle(int key,boolean down){
  if(System.getProperty("nextui.commands")!=null && key==Keys.BUTTON_A && down)System.err.println("Interact dispatch: scene="+Game.scene().getClass().getSimpleName()+" window="+GameScene.showingWindow()+" selecting="+GameScene.selectingCell());
  if(RgMap.input(key,down))return true;
  if(!(Game.scene() instanceof GameScene) || GameScene.showingWindow() || Dungeon.hero==null || !Dungeon.hero.isAlive())return false;
  if(GameScene.selectingCell()){
   if(key==Keys.BUTTON_A || key==Keys.BUTTON_Y){if(down)GameScene.rgConfirmTarget();return true;}
   if(key==Keys.BUTTON_L1 || key==Keys.BUTTON_R1){if(down)GameScene.rgCycleTarget(key==Keys.BUTTON_L1?-1:1);return true;}
   if(key==Keys.BUTTON_START && down)GameScene.cancel();
  }else if(key==Keys.BUTTON_A){if(down && Dungeon.hero.ready)GameScene.rgInteract();return true;}
  if(key==Keys.BUTTON_THUMBL){if(down && Dungeon.hero.ready)Dungeon.hero.rest(false);return true;}
  if(key==Keys.BUTTON_Y && down && !Dungeon.hero.ready)return true;
  return false;
 }
}
