// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.SPDAction;
import com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene;
import com.shatteredpixel.shatteredpixeldungeon.ui.*;
import com.watabou.input.*;
import com.watabou.noosa.ui.Component;

/** One concise, scrollable reference shared by title and pause menus. */
public final class RgControls extends Window {
 private final ScrollPane pane;
 public RgControls() {
  resize(204,130);
  RenderedTextBlock title=PixelScene.renderTextBlock(RgPlatform.chinese()?"按键说明":"Controls",8);
  title.hardlight(TITLE_COLOR);title.setPos(3,2);add(title);
  Component content=new Component();
  RenderedTextBlock text=PixelScene.renderTextBlock(RgPlatform.chinese()?
   "十字键：移动、菜单选择、选格\nA：确定、互动、确认目标\nB：查看目标／取消／返回\n长按B：搜索周围（消耗回合）\nX：背包    Y：使用快捷栏\nL1／R1：向左／右切换快捷栏或分页\nL2／R2：缩小／放大地图\nSelect：英雄、天赋与状态\n长按Select：全屏地图浏览\n地图：方向选区，A放大\n地图B：先全览，再退出\nStart：游戏菜单\nMenu：等待一回合\n音量键：音量    Menu＋音量：亮度\nSelect＋音量：色温\nSelect＋Start：保存并返回NextUI\n\n查看目标不会消耗回合。\n搜索周围：长按B，或Start菜单。\n长按Y：更换或清空快捷格。\n背包Y：将物品放入指定快捷格。\n查看/瞄准：A或Y确认，L1/R1换目标。\n力量靠力量药剂增长，升级不会加力量。"
   :"D-pad: move, navigate, aim\nA: confirm, interact, select target\nB: examine / cancel / back\nHold B: search nearby (costs a turn)\nX: inventory   Y: use hotbar\nL1/R1: left/right hotbar or tabs\nL2/R2: zoom out/in\nSelect: hero, talents, status\nStart: pause menu\nMenu: wait one turn\nVolume keys: volume\nMenu + Volume: brightness\nSelect + Volume: color temperature\nSelect + Start: save and quit\n\nExamine costs no turns.\nHold B or use Start menu to search.\nHold Y: replace/clear quickslot.\nHold Select: full-screen map.\nMap: D-pad cursor, A zoom region.\nMap B: overview, then exit.\nInventory Y: assign item to a slot.\nAim: A/Y confirm, L1/R1 targets.",6);
  text.maxWidth(192);content.add(text);content.setSize(192,text.height()+2);
  pane=new ScrollPane(content);add(pane);pane.setRect(4,18,196,94);
  RenderedTextBlock footer=PixelScene.renderTextBlock(RgPlatform.chinese()?"↑↓滚动 · B返回":"Up/Down scroll · B back",6);
  footer.setPos(4,119);add(footer);
 }
 @Override public boolean onSignal(KeyEvent event) {
  GameAction action=KeyBindings.getActionForKey(event);
  if(action==SPDAction.N || action==SPDAction.S) {
   if(event.pressed)pane.scrollTo(0,pane.content().camera.scroll.y+(action==SPDAction.N?-16:16));
   return true;
  }
  return super.onSignal(event);
 }
}
