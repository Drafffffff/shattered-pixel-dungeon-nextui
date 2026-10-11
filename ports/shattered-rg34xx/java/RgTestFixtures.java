// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.shatteredpixel.shatteredpixeldungeon.*;
import com.shatteredpixel.shatteredpixeldungeon.scenes.*;
import com.shatteredpixel.shatteredpixeldungeon.ui.*;
import com.shatteredpixel.shatteredpixeldungeon.windows.*;
/** Only called by the explicitly enabled local test command channel. */
public final class RgTestFixtures {
 private static WndTextInput lastText;
 public static String textValue(){
  if(lastText==null || lastText.parent==null)return "";
  try{java.lang.reflect.Field f=WndTextInput.class.getDeclaredField("textBox");f.setAccessible(true);return ((com.watabou.noosa.TextInput)f.get(lastText)).getText();}
  catch(Exception e){throw new RuntimeException(e);}
 }
 public static void run(String name){
  if(System.getProperty("nextui.commands")==null)throw new IllegalStateException("Test mode required");
  switch(name){
   case "buff":com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Buff.affect(Dungeon.hero,com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Bless.class,20f);break;
   case "loot":Dungeon.level.drop(new com.shatteredpixel.shatteredpixeldungeon.items.Gold(17),Dungeon.hero.pos);break;
   case "rat":{
    com.shatteredpixel.shatteredpixeldungeon.actors.mobs.Rat rat=new com.shatteredpixel.shatteredpixeldungeon.actors.mobs.Rat();
    for(int offset:com.watabou.utils.PathFinder.NEIGHBOURS8){int pos=Dungeon.hero.pos+offset;if(Dungeon.level.passable[pos] && com.shatteredpixel.shatteredpixeldungeon.actors.Actor.findChar(pos)==null){rat.pos=pos;break;}}
    rat.state=rat.PASSIVE;GameScene.add(rat);Dungeon.level.heroFOV[rat.pos]=true;Dungeon.hero.checkVisibleMobs();break;
   }
   case "journal":GameScene.show(new WndJournal());break;
   case "hero":GameScene.show(new WndHero());break;
   case "radial":GameScene.show(new RadialMenu("Test","",new String[]{"First","Second","Third"},new com.watabou.noosa.Image[]{Icons.INFO.get(),Icons.INFO.get(),Icons.INFO.get()}){public void onSelect(int i,boolean alt){System.err.println("Radial selected "+i+" "+alt);}});break;
   case "text":lastText=new WndTextInput("Test",null,"ORIGINAL",20,false,"OK","Cancel");GameScene.show(lastText);break;
   case "upgrade":GameScene.show(new WndUpgrade(new com.shatteredpixel.shatteredpixeldungeon.items.scrolls.ScrollOfUpgrade(),Dungeon.hero.belongings.weapon(),false));break;
   case "descend":InterlevelScene.curTransition=Dungeon.level.getTransition(com.shatteredpixel.shatteredpixeldungeon.levels.features.LevelTransition.Type.REGULAR_EXIT);InterlevelScene.mode=InterlevelScene.Mode.DESCEND;ShatteredPixelDungeon.switchNoFade(InterlevelScene.class);break;
   case "reload":try{Dungeon.saveAll();InterlevelScene.mode=InterlevelScene.Mode.CONTINUE;ShatteredPixelDungeon.switchNoFade(InterlevelScene.class);}catch(Exception e){throw new RuntimeException(e);}break;
   case "alchemy":ShatteredPixelDungeon.switchNoFade(AlchemyScene.class);break;
   default:throw new IllegalArgumentException(name);
  }
 }
}
