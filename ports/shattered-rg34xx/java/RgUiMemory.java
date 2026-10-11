// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Preferences;
import com.shatteredpixel.shatteredpixeldungeon.ui.ScrollPane;
import com.watabou.noosa.*;
/** Scroll positions are saved independently for each journal tab. */
public final class RgUiMemory {
 public static void save(Group root,String key){walk(root,key,false);}
 public static void restore(Group root,String key){walk(root,key,true);}
 private static void walk(Group root,String key,boolean restore){
  Preferences prefs=Gdx.app.getPreferences("rg-interaction");int index=0;
  for(Gizmo g:root.members()){
   String path=key+"-"+(index++);
   if(g==null || !g.isVisible() || !g.isActive())continue;
   if(g instanceof ScrollPane){ScrollPane pane=(ScrollPane)g;
    if(restore)pane.scrollTo(prefs.getFloat(path+"-x",0),prefs.getFloat(path+"-y",0));
    else if(pane.content().camera!=null){prefs.putFloat(path+"-x",pane.content().camera.scroll.x);prefs.putFloat(path+"-y",pane.content().camera.scroll.y);}
   }
   if(g instanceof Group)walk((Group)g,path,restore);
  }
 }
}
