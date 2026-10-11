// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.ui.*;
import com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene;
import com.watabou.noosa.TextInput;
import com.watabou.noosa.Game;
/** Small D-pad keyboard for optional seed/name/note fields. */
public final class RgKeyboard extends Window {
 private String value;
 private final TextInput target;
 private final RenderedTextBlock preview;
 public RgKeyboard(TextInput target) {
  this.target=target;value=target.getText();
  preview=PixelScene.renderTextBlock(value.isEmpty()?"输入字符":value,7);preview.maxWidth(194);preview.setPos(3,3);add(preview);
  String[] rows={"1234567890","QWERTYUIOP","ASDFGHJKL","ZXCVBNM- "};
  for(int row=0;row<rows.length;row++)for(int col=0;col<rows[row].length();col++) {
   final char character=rows[row].charAt(col);
   RedButton b=new RedButton(character==' '?"空格":String.valueOf(character),7){@Override protected void onClick(){value+=character;refresh();}};
   b.setRect(col*20,23+row*17,19,16);add(b);
  }
  RedButton delete=new RedButton("删除",7){@Override protected void onClick(){if(!value.isEmpty())value=value.substring(0,value.offsetByCodePoints(value.length(),-1));refresh();}};
  delete.setRect(0,92,64,18);add(delete);
  RedButton clear=new RedButton("清空",7){@Override protected void onClick(){value="";refresh();}};
  clear.setRect(67,92,64,18);add(clear);
  RedButton done=new RedButton("完成",7){@Override protected void onClick(){target.setText(value);hide();}};
  done.setRect(134,92,66,18);add(done);
  resize(200,111);
 }
 private void refresh(){preview.text(value.isEmpty()?"输入字符":value,194);}
 @Override public boolean onSignal(com.watabou.input.KeyEvent e){
  if(e.code==com.badlogic.gdx.Input.Keys.BUTTON_Y){if(e.pressed){target.setText(value);hide();}return true;}
  if(e.code==com.badlogic.gdx.Input.Keys.BUTTON_X){if(e.pressed && !value.isEmpty()){value=value.substring(0,value.offsetByCodePoints(value.length(),-1));refresh();}return true;}
  return super.onSignal(e);
 }
 @Override public void onBackPressed(){hide();}
}
