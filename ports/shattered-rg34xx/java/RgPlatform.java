// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.desktop.DesktopPlatformSupport;
public final class RgPlatform extends DesktopPlatformSupport {
 public static boolean chinese() {
  return com.shatteredpixel.shatteredpixeldungeon.SPDSettings.language()==com.shatteredpixel.shatteredpixeldungeon.messages.Languages.CHI_SMPL
   || com.shatteredpixel.shatteredpixeldungeon.SPDSettings.language()==com.shatteredpixel.shatteredpixeldungeon.messages.Languages.CHI_TRAD;
 }
 @Override public void updateDisplaySize() {}
 @Override public void updateSystemUI() {}
 @Override public boolean supportsFullScreen() { return false; }
 @Override public boolean connectedToUnmeteredNetwork() { return false; }
 @Override public boolean supportsVibration() { return false; }
 public static String menuLabel(String key) {
  boolean zh=com.shatteredpixel.shatteredpixeldungeon.SPDSettings.language()==com.shatteredpixel.shatteredpixeldungeon.messages.Languages.CHI_SMPL
   || com.shatteredpixel.shatteredpixeldungeon.SPDSettings.language()==com.shatteredpixel.shatteredpixeldungeon.messages.Languages.CHI_TRAD;
  if(key.equals("journal"))return zh?"日志与图鉴":"Journal and catalog";
  if(key.equals("search"))return zh?"搜索周围":"Search";
  return zh?"保存并退出":"Save and exit";
 }
 public static String controllerHelp(String key) {
  boolean chinese=com.shatteredpixel.shatteredpixeldungeon.SPDSettings.language()==com.shatteredpixel.shatteredpixeldungeon.messages.Languages.CHI_SMPL
   || com.shatteredpixel.shatteredpixeldungeon.SPDSettings.language()==com.shatteredpixel.shatteredpixeldungeon.messages.Languages.CHI_TRAD;
  if(key.equals("title"))return chinese?"RG34XX 按键":"RG34XX controls";
  if(key.equals("okay"))return chinese?"开始":"Ready";
  return chinese?"十字键移动、选择和瞄准。A确定，B查看目标／取消，长按B搜索周围，X背包，Y使用快捷栏。\n\nL1向左、R1向右，L2/R2缩放。Menu等待，Start菜单，Select英雄状态。\n\n更多操作：Start → 按键说明。\nSelect＋Start保存退出。":"D-pad moves, navigates and aims. A confirms, B examines/cancels, hold B searches nearby, X opens inventory, Y uses the hotbar.\n\nL1 left, R1 right. L2/R2 zoom. Menu waits. Start pauses, Select shows hero info.\n\nMore: Start → Controls.\nSelect + Start saves and exits.";
 }
}
