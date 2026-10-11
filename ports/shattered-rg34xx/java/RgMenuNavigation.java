// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.SPDAction;
import com.shatteredpixel.shatteredpixeldungeon.ui.ControllerNavigator;
import com.watabou.input.*;
import com.watabou.noosa.*;
import com.watabou.utils.Signal;
/** Scene-level navigation, with modal windows taking priority in the listener stack. */
public final class RgMenuNavigation implements Signal.Listener<KeyEvent> {
 private final Group root;
 private boolean covered;
 private final ControllerNavigator navigator=new ControllerNavigator();
 public RgMenuNavigation(Group root){this(root,false);}
 public RgMenuNavigation(Group root,boolean focus){this.root=root;KeyEvent.addKeyListener(this);if(focus)navigator.ensureFocus(root);}
 @Override public boolean onSignal(KeyEvent event){
  GameAction action=KeyBindings.getActionForKey(event);
  if(System.getProperty("nextui.commands")!=null && event.pressed)System.err.println("Menu key="+event.code+" action="+action.name());
  if(action==SPDAction.ACCEPT){
   if(navigator.ensureFocus(root))navigator.accept(event.pressed);
   return true;
  }
  return event.pressed && navigator.move(root,action);
 }
 public void update(){boolean now=com.shatteredpixel.shatteredpixeldungeon.ui.Window.rgTop()!=null;if(covered && !now)navigator.revealFocus();covered=now;}
 public void close(){KeyEvent.removeKeyListener(this);navigator.destroy();}
}
