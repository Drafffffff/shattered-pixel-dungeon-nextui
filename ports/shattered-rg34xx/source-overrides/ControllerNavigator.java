/*
 * Shattered Pixel Dungeon, Copyright (C) 2014-2026 Evan Debenham.
 * D-pad navigation derived from the GPL Shattered Pixel Dungeon D-pad fork.
 * Modified for NextUI RG34XX. SPDX-License-Identifier: GPL-3.0-or-later
 */
package com.shatteredpixel.shatteredpixeldungeon.ui;
import com.shatteredpixel.shatteredpixeldungeon.SPDAction;
import com.watabou.input.*;
import com.watabou.noosa.*;
import com.watabou.noosa.ui.Component;
import com.watabou.utils.*;
import java.util.ArrayList;
/** Spatial focus for buttons, grids, delegated rows and custom clickable controls. */
public class ControllerNavigator {
 private Component focused;
 private boolean down;
 private Component accepted;
 private final ColorBlock[] edges=new ColorBlock[4];
 public Component focused(){return focused;}
 public void focus(Component component){clear();focused=component;if(component!=null)movePointer(component);}
 public void cycle(Group root,int direction){ArrayList<Component> controls=new ArrayList<>();collect(root,controls);if(!controls.isEmpty())focus(controls.get(Math.floorMod(controls.indexOf(focused)+direction,controls.size())));}
 public void clear(){focused=null;down=false;accepted=null;}
 public void destroy(){clear();for(ColorBlock edge:edges)if(edge!=null)edge.destroy();}
 public boolean ensureFocus(Group root){
  ArrayList<Component> controls=new ArrayList<>();collect(root,controls);
  if(controls.isEmpty()){focused=null;return false;}
  if(!controls.contains(focused)){focused=controls.get(0);for(Component c:controls)if(c instanceof StyledButton && ((StyledButton)c).text().matches("(?i)取消|cancel|否|no")){focused=c;break;}movePointer(focused);}
  return true;
 }
 public void accept(boolean pressed){
  if(focused==null || focused instanceof OptionSlider)return;
  // A release belonging to a parent window must not click a new child window.
  if(pressed){movePointer(focused);down=true;accepted=focused;if(accepted instanceof Button)((Button)accepted).rgAccept(true);else Game.inputHandler.emulateTouch(ControllerHandler.CONTROLLER_POINTER_ID,PointerEvent.LEFT,true);}
  else if(down){down=false;Component target=accepted;accepted=null;if(target instanceof Button)((Button)target).rgAccept(false);else Game.inputHandler.emulateTouch(ControllerHandler.CONTROLLER_POINTER_ID,PointerEvent.LEFT,false);}
 }
 public boolean move(Group root,GameAction action){
  int dx=action==SPDAction.W?-1:action==SPDAction.E?1:0;
  int dy=action==SPDAction.N?-1:action==SPDAction.S?1:0;
  if(dx==0 && dy==0)return false;
  if(focused==null){if(ensureFocus(root))return true;return scrollText(root,dy);}
  if(!ensureFocus(root))return scrollText(root,dy);
  if(dx!=0 && focused instanceof OptionSlider){((OptionSlider)focused).controllerAdjust(dx);movePointer(focused);return true;}
  Point origin=screenCenter(focused);Component next=null;float best=Float.MAX_VALUE;
  ArrayList<Component> controls=new ArrayList<>();collect(root,controls);
  for(Component c:controls){
   if(c==focused)continue;
   Point point=screenCenter(c);float primary=dx!=0?(point.x-origin.x)*dx:(point.y-origin.y)*dy;
   if(primary<=0)continue;
   float perpendicular=dx!=0?Math.abs(point.y-origin.y):Math.abs(point.x-origin.x);
   float score=primary+perpendicular*3;
   if(score<best){best=score;next=c;}
  }
  if(next!=null)focused=next;
  else if(dy!=0 && scrollText(root,dy))return true;
  movePointer(focused);return true;
 }
 public static boolean scrollText(Group root,int dy){
  if(dy==0)return false;
  for(Gizmo g:root.members()){
   if(g==null || !g.isVisible() || !g.isActive())continue;
   if(g instanceof ScrollPane){ScrollPane p=(ScrollPane)g;p.scrollTo(p.content().camera.scroll.x,p.content().camera.scroll.y+dy*16);return true;}
   if(g instanceof Group && scrollText((Group)g,dy))return true;
  }return false;
 }
 private void collect(Group root,ArrayList<Component> controls){
  for(Gizmo g:root.members()){
   if(g==null || !g.isActive() || !g.isVisible())continue;
   if(g instanceof Component){
    Component c=(Component)g;
    boolean clickable=c instanceof Button || c instanceof OptionSlider || c instanceof ScrollingListPane.ListItem || c instanceof ScrollingGridPane.GridItem || c instanceof org.nextui.shattered.RgFocusable;
    if(!clickable && !(c instanceof ScrollPane))for(Gizmo child:c.members())if(child instanceof PointerArea && child.isActive()){clickable=true;break;}
    if(clickable && c.width()>0 && c.height()>0){controls.add(c);continue;}
   }
   if(g instanceof Group)collect((Group)g,controls);
  }
 }
 private Point screenCenter(Component c){return c.camera().cameraToScreen(c.centerX(),c.centerY());}
 private void movePointer(Component c){
  for(Group parent=c.parent;parent!=null;parent=parent.parent)if(parent instanceof ScrollPane){
   ScrollPane pane=(ScrollPane)parent;Camera camera=pane.content().camera;float y=camera.scroll.y;
   if(c.top()<y)y=c.top();else if(c.bottom()>y+pane.height())y=c.bottom()-pane.height();
   pane.scrollTo(camera.scroll.x,y);
  }
  Point point=screenCenter(c);ControllerHandler.setControllerPointer(true);
  ControllerHandler.updateControllerPointer(new PointF(point.x,point.y),false);
  ControllerHandler.updateControllerPointer(new PointF(point.x,point.y),true);
 }
 public void revealFocus(){if(focused!=null)movePointer(focused);}
 public int index(Group root){ArrayList<Component> c=new ArrayList<>();collect(root,c);return c.indexOf(focused);}
 public void restore(Group root,int index){ArrayList<Component> c=new ArrayList<>();collect(root,c);if(!c.isEmpty()){focused=c.get(Math.max(0,Math.min(index,c.size()-1)));movePointer(focused);}}
 public void draw(){
  if(focused==null || !focused.isVisible())return;
  Camera c=focused.camera();float x=focused.left(),y=focused.top(),w=focused.width(),h=focused.height();
  for(int i=0;i<4;i++){
   if(edges[i]==null)edges[i]=new ColorBlock(1,1,0xFFE6D47A);
   ColorBlock e=edges[i];e.camera=c;e.x=x+(i==3?w-1:0);e.y=y+(i==1?h-1:0);
   e.size(i<2?w:1,i<2?1:h);e.draw();
  }
 }
}
