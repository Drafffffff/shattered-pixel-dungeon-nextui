// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.badlogic.gdx.Input.Keys;
import com.shatteredpixel.shatteredpixeldungeon.Dungeon;
import com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene;
import com.watabou.input.KeyEvent;
import com.watabou.noosa.Game;
import com.watabou.noosa.Scene;
/** Explore-only B gesture; modal and targeting B keeps its immediate cancel behavior. */
public final class RgSearchShortcut {
 private static boolean pending;
 private static long pressedAt;
 private static Scene owner;
 private static boolean exploring(){return Game.scene() instanceof GameScene && !GameScene.showingWindow() && !GameScene.selectingCell() && !RgMap.active() && Dungeon.hero!=null && Dungeon.hero.isAlive() && Dungeon.hero.ready;}
 public static boolean input(int key,boolean down){
  if(key!=Keys.BUTTON_B)return false;
  if(down){
   if(pending)return true;
   if(!exploring())return false;
   pending=true;pressedAt=System.nanoTime();owner=Game.scene();return true;
  }
  if(!pending)return false;
  pending=false;
  // A gesture begun in exploration must never cancel a newly opened window.
  if(Game.scene()!=owner || !exploring()){owner=null;return true;}
  owner=null;
  if(System.nanoTime()-pressedAt>=550000000L)Dungeon.hero.search(true);
  else {KeyEvent.addKeyEvent(new KeyEvent(key,true));KeyEvent.addKeyEvent(new KeyEvent(key,false));}
  return true;
 }
}
