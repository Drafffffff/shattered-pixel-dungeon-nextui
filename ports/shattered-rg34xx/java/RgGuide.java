// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;

import com.shatteredpixel.shatteredpixeldungeon.SPDAction;
import com.shatteredpixel.shatteredpixeldungeon.SPDSettings;
import com.shatteredpixel.shatteredpixeldungeon.journal.Document;
import com.shatteredpixel.shatteredpixeldungeon.messages.Languages;
import com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene;
import com.shatteredpixel.shatteredpixeldungeon.scenes.PixelScene;
import com.shatteredpixel.shatteredpixeldungeon.ui.RedButton;
import com.shatteredpixel.shatteredpixeldungeon.ui.RenderedTextBlock;
import com.shatteredpixel.shatteredpixeldungeon.ui.ScrollPane;
import com.shatteredpixel.shatteredpixeldungeon.ui.ScrollingListPane;
import com.shatteredpixel.shatteredpixeldungeon.ui.Window;
import com.shatteredpixel.shatteredpixeldungeon.windows.WndJournal;
import com.watabou.input.GameAction;
import com.watabou.input.KeyBindings;
import com.watabou.input.KeyEvent;
import com.watabou.noosa.ui.Component;

/** Controller-accessible found pages, with a bounded, scrollable reader. */
public final class RgGuide extends WndJournal {
 private static boolean chinese() {
  return SPDSettings.language()==Languages.CHI_SMPL || SPDSettings.language()==Languages.CHI_TRAD;
 }
 public RgGuide() { super(); }
 public static final class Page extends Window {
  private final ScrollPane body;
  private final boolean finishesIntro;
  private boolean closed;
  public Page(String page) {
   Document.ADVENTURERS_GUIDE.readPage(page);
   if(System.getProperty("nextui.commands")!=null)System.err.println("Guide page read: "+page);
   finishesIntro=SPDSettings.intro() && page.equals(Document.GUIDE_INTRO);
   resize(212,132);
   RenderedTextBlock title=PixelScene.renderTextBlock(Document.ADVENTURERS_GUIDE.pageTitle(page),8);
   title.maxWidth(204);title.hardlight(TITLE_COLOR);title.setPos(2,1);add(title);
   Component content=new Component();
   RenderedTextBlock text=PixelScene.renderTextBlock(Document.ADVENTURERS_GUIDE.pageBody(page),6);
   text.maxWidth(200);text.setPos(0,0);content.add(text);content.setSize(200,text.height()+2);
   float top=title.bottom()+4;
   body=new ScrollPane(content);add(body);body.setRect(4,top,200,118-top);
   RenderedTextBlock hint=PixelScene.renderTextBlock(chinese()?"↑↓滚动 · A/B返回":"Up/Down scroll · A/B back",6);
   hint.setPos(4,122);add(hint);
  }
  @Override public void hide() {
   if(closed)return;
   closed=true;
   super.hide();
   // Match the original flashing journal reader: finish only on closing Intro.
   if(finishesIntro && SPDSettings.intro()) {
    GameScene.endIntro();
    System.err.println("Tutorial completed: Intro reader closed");
   }
  }
  @Override public boolean onSignal(KeyEvent event) {
   GameAction action=KeyBindings.getActionForKey(event);
   if(action==SPDAction.N || action==SPDAction.S) {
    if(event.pressed)body.scrollTo(0,body.content().camera.scroll.y+(action==SPDAction.N?-16:16));
    return true;
   }
   if(action==SPDAction.ACCEPT || action==SPDAction.BACK) {
    if(event.pressed)onBackPressed();return true;
   }
   return super.onSignal(event);
  }
 }
}
