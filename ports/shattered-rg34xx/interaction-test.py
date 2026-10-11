#!/usr/bin/env python3
"""Run the real SDL/GLES backend on ARM64 Mesa; this is not hardware validation."""
from pathlib import Path
import subprocess,time,sys,tempfile,json,gzip,shutil,argparse,struct,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[2]
b=root/'build/shattered-rg34xx'
home=Path(tempfile.mkdtemp(prefix='smoke-',dir=b))
parser=argparse.ArgumentParser()
parser.add_argument('--resume-from',type=Path)
parser.add_argument('--death-test',action='store_true',help='Exercise game-over cursor and actions on a local save copy')
parser.add_argument('--menu-test',action='store_true',help='Exercise pause/help/title navigation on a local save copy')
parser.add_argument('--delete-test',action='store_true',help='Delete only the test copy of the supplied save')
parser.add_argument('--flip-toolbar',action='store_true',help='Test spatial shoulder direction with flipped toolbar')
options=parser.parse_args()
if options.resume_from:shutil.copytree(options.resume_from,home,dirs_exist_ok=True)
if options.flip_toolbar:
 pref=home/'settings.xml';tree=ET.parse(pref)
 for element in list(tree.getroot()):
  if element.get('key')=='flipped_ui':tree.getroot().remove(element)
 ET.SubElement(tree.getroot(),'entry',key='flipped_ui').text='true'
 pref.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">\n'+ET.tostring(tree.getroot(),encoding='unicode'))
settingsFile=home/'hardware-settings'
hardware=[1,5,20,4,10,0,0,0,0,0,0,0,0,100,100,100]
settingsFile.write_bytes(struct.pack('<16i',*hardware))
command=home/'commands'; logpath=home/'run.log'
# Mount under /test so this script does not depend on host path spelling.
relative=home.relative_to(b).as_posix()
log=logpath.open('w')
args=['docker','run','--rm','--init','-v',f'{b}:/test','-w','/test/dist','-e',f'SPD_SAVE_DIR=/test/{relative}','shattered-rg34xx-smoke:local','xvfb-run','-a','-s','-screen 0 720x480x24','java','-Xms32m','-Xmx192m','-Xss512k','-XX:+UseSerialGC','-XX:MaxDirectMemorySize=64m','-XX:ActiveProcessorCount=2','-Djava.library.path=/test/dist/lib','-Dorg.lwjgl.opengles.libname=libGLESv2.so.2','-Dnextui.smokeSeconds=180',f'-Dnextui.commands=/test/{relative}/commands','-cp','shattered-rg34xx.jar:lib/*','org.nextui.shattered.RgLauncher']
args.insert(args.index('-cp'),f'-Dnextui.settingsFile=/test/{relative}/hardware-settings')
p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
def wait_for(needle,timeout=30):
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  if needle in logpath.read_text():return
  if p.poll() is not None:break
  time.sleep(.1)
 raise RuntimeError('Missing '+needle+'\n'+logpath.read_text())
def send(cmd,delay=.22):
 t=command.with_suffix('.tmp');t.write_text(cmd+'\n');t.replace(command)
 deadline=time.monotonic()+5
 while command.exists():
  if time.monotonic()>deadline:raise RuntimeError('Command not consumed: '+cmd)
  time.sleep(.03)
 time.sleep(delay)
def wait_for_home():
 deadline=time.monotonic()+30
 continued=False;welcome_since=None
 while time.monotonic()<deadline:
  text=logpath.read_text()
  if 'Scene: RgHome' in text:return
  if not continued and 'Scene: WelcomeScene' in text:
   if welcome_since is None:welcome_since=time.monotonic()
   # Welcome.create may automatically advance an unfinished legacy intro.
   if time.monotonic()-welcome_since>.6:
    shot('version-upgrade');send('key 96');continued=True
  if p.poll() is not None:break
  time.sleep(.1)
 raise RuntimeError('Upgrade did not reach the home screen\n'+logpath.read_text())
def shot(name):send(f'shot /test/{relative}/{name}.png')
def state(name):
 send(f'state /test/{relative}/{name}.json')
 raw=json.loads((home/f'{name}.json').read_text())
 return {k:v['value'] if isinstance(v,dict) and 'value' in v else v for k,v in raw.items()}

try:
 if options.resume_from:
  wait_for_home();shot('home-restored')
  send('key 96');wait_for('Scene: StartScene')
  send('key 1020');send('key 1020');send('key 96');send('key 96');wait_for('Scene: GameScene');time.sleep(2)
 else:
  wait_for('Scene: WelcomeScene')
  for key in [96,96,96,1020,1020,1020,96]:send(f'key {key}')
  wait_for('Scene: InterlevelScene');time.sleep(1);transition=state('transition-no-cursor');assert transition['scene']=='InterlevelScene' and not transition['cursor'],transition;shot('transition-no-cursor');send('key 96');wait_for('Scene: GameScene')
  send('fixture-guide');send('key 108');send('key 1020');send('key 96');send('key 96')
  shot('intro-reader');assert state('intro-reader-state')['intro']
  send('key 97');send('key 97');time.sleep(2)
  assert not state('intro-finished')['intro']
 before=state('explore')
 assert before['windowCount']==0 and not before['intro'],before
 # Verify primary pickup before other windows can affect the state.
 send('fixture-ux rat');send('fixture-ux loot');loot=state('initial-loot-before');send('key 96');picked=state('initial-loot-after');assert picked['gold']==loot['gold']+17,(loot,picked)
 before=state('explore-after-pickup')
 # Scroll viewport must follow the window's final position, including lower rows.
 send('key 108');pause=state('pause-aligned');shot('pause-aligned')
 assert pause['windowLeft']<pause['focusScreenX']<pause['windowRight'] and pause['windowTop']<pause['focusScreenY']<pause['windowBottom'],pause
 for _ in range(6):send('key 1020')
 pause=state('pause-scrolled');shot('pause-scrolled')
 assert pause['windowLeft']<pause['focusScreenX']<pause['windowRight'] and pause['windowTop']<pause['focusScreenY']<pause['windowBottom'],pause
 send('key 97')
 # Both confirmation buttons inspect; browsing does not advance a turn.
 send('key 97');send('key 100');detail=state('y-examine');assert detail['windowCount']>0 and not detail['cursor'],detail
 shot('examine-border');send('key 97');assert state('inspect-return')['turn']==before['turn']
 # Long B searches exactly once; it must never enter examine targeting.
 origin=state('search-before');send('down 97',.8);searched=state('search-while-held')
 assert searched['turn']>origin['turn'] and not searched['targeting'],(origin,searched)
 time.sleep(.7);assert state('search-still-held')['turn']==searched['turn']
 send('up 97',.8);assert state('search-after-release')['turn']==searched['turn']
 assert searched['turn']>origin['turn'] and searched['windowCount']==0 and not searched['targeting'],(origin,searched)
 stable=state('search-stable');assert stable['turn']==searched['turn']
 # B pressed in a menu is only Back, even if held.
 send('key 108');origin=state('menu-back-before');send('down 97',.8);send('up 97');returned=state('menu-back-after');assert returned['windowCount']==0 and returned['turn']==origin['turn']
 # An explore gesture interrupted by a new window cannot cancel that window.
 send('down 97');send('key 108');send('up 97');assert state('interrupted-b')['windowCount']==1;send('key 97')
 before=state('after-search')
 # Full-screen camera mode owns all input, including the quickslot button.
 send('down 109',.65);m=state('map-while-held');assert m['mapMode'] and not m['uiVisible'],m
 time.sleep(.7);assert state('map-still-held')['mapMode']
 send('up 109');assert state('map-after-release')['mapMode']
 assert m['cameraX']<=0 and m['cameraY']<=0 and m['cameraX']+m['cameraWorldWidth']>=m['mapWidth'] and m['cameraY']+m['cameraWorldHeight']>=m['mapHeight'],m;shot('map-overview')
 send('key 1022');pan=state('map-pan');assert pan['cameraX']!=m['cameraX'] and pan['pos']==before['pos'],pan
 send('key 100');assert state('map-y')['windowCount']==0
 send('key 105');assert state('map-zoom')['cameraZoom']>m['cameraZoom'];send('key 104');assert abs(state('map-zoom-out')['cameraZoom']-m['cameraZoom'])<.001;send('key 96');assert state('map-center')['mapMode']
 shot('map-fullscreen');send('key 97');m=state('map-closed');assert not m['mapMode'] and m['uiVisible'] and m['turn']==before['turn'] and m['cameraZoom']==before['cameraZoom'],m
 # Long Select can also close the map before release, without opening hero info.
 send('down 109',.7);assert state('map-reopen-held')['mapMode'];send('up 109')
 send('down 109',.7);closed=state('map-close-held');assert not closed['mapMode'] and closed['windowCount']==0
 send('up 109');assert state('map-close-release')['windowCount']==0
 # Item targeting can be cancelled without consuming the quickslot.
 targetBefore=state('throw-before');send('key 100');assert state('throw-target')['targeting'];send('key 97');assert state('throw-cancel')['turn']==targetBefore['turn']
 # Buff rows are independently focusable and open their original effect window.
 send('fixture-ux buff');send('key 109');send('key 103');send('key 103');buff=state('buff-tab');assert buff['heroTab']==2 and 'BuffSlot' in buff['focusType'],buff
 shot('buff-list');send('key 96');assert 'WndInfoBuff' in state('buff-details')['windows'];shot('buff-details');send('key 97');assert 'BuffSlot' in state('buff-restored')['focusType'];send('key 97')
 # Catalog navigation goes below categories, and survives closing/reopening.
 send('fixture-ux journal');j=state('journal-guide');assert j['journalTab']==1,j
 send('key 103');send('key 103');send('key 1020');j=state('catalog-grid');assert 'GridItem' in j['focusType'] or 'WndJournal$' in j['focusType'],j
 shot('catalog-grid');send('key 96');assert state('catalog-details')['windowCount']==2;shot('catalog-details');send('key 97');returned=state('catalog-return');assert returned['focusType']==j['focusType'] and returned['focusY']==j['focusY'],(j,returned)
 send('key 97');send('fixture-ux journal');assert state('journal-reopen')['journalTab']==3;send('key 97')
 # Replacing or clearing a quickslot is explicit; cancelled picker preserves it.
 slots=state('slots-before')['quickslots'];send('down 100',.9);send('up 100');assert state('slot-menu')['windowCount']==1;shot('quickslot-manage')
 send('key 1020');send('key 96');assert 'WndBag' in state('slot-picker')['windows'];send('key 97');assert state('slot-cancel')['quickslots']==slots
 send('down 100',.9);send('up 100');send('key 1020');send('key 1020');send('key 96');assert state('slot-clear')['quickslots'].split(';')[0]=='empty'
 send('key 100');assert 'WndBag' in state('slot-empty-picker')['windows'];send('key 96');assert state('slot-assigned')['quickslots'].split(';')[0]!='empty'
 # Child item actions take focus immediately; back restores the inventory item.
 send('key 99');bag=state('bag-focused');send('key 96');item=state('item-focused');assert 'WndUseItem' in item['windows'] and not item['cursor'] and item['focusType'],item
 shot('item-focused');send('key 97');assert state('bag-return')['focusType']==bag['focusType'];send('key 1020');send('key 100');assert state('bag-assign')['windowCount']==2;send('key 97');send('key 97')
 # Pickup remains available with a nearby enemy, at original turn cost.
 send('fixture-ux rat');send('fixture-ux loot');loot=state('loot-before');send('key 96');picked=state('loot-after');assert picked['gold']==loot['gold']+17 and picked['turn']>loot['turn'],(loot,picked)
 shot('combat-pickup')
 # Pointer-only radial menus now have ordinary reachable rows.
 send('fixture-ux radial');send('key 1020');send('key 96');wait_for('Radial selected 1 false');assert state('radial-closed')['windowCount']==0
 # Upgrade preview does not consume resources before confirmation.
 send('fixture-ux upgrade');shot('upgrade-preview');send('key 97');assert 'WndBag' in state('upgrade-return')['windows'];send('key 97')
 # Keyboard works on a private draft, with explicit commit and cancellation.
 send('fixture-ux text');send('key 99');send('key 96');send('key 97');assert state('keyboard-cancel')['inputText']=='ORIGINAL'
 send('key 99');send('key 96');send('key 100');assert state('keyboard-done')['inputText']=='ORIGINAL1';send('key 97')
 # System modifiers never cause world actions or modal changes.
 origin=state('system-before');send('down 106');send('key 20001');hardware[1]=6;settingsFile.write_bytes(struct.pack('<16i',*hardware));send('up 106');osd=state('brightness');assert osd['turn']==origin['turn'] and osd['windowCount']==0 and '6 / 10' in osd['overlay'];shot('system-osd')
 send('down 109');send('key 20001');hardware[2]=21;settingsFile.write_bytes(struct.pack('<16i',*hardware));time.sleep(.8);assert not state('color-held')['mapMode'];send('up 109');assert state('color')['windowCount']==0
 # Shoulder order follows actual screen coordinates, including flipped layout.
 hot=state('hotbar-order');positions={int(k):float(v) for k,v in (entry.split(':') for entry in hot['hotbarPositions'].strip(',').split(','))};order=sorted(positions,key=positions.get);idx=order.index(hot['hotbar']);send('key 102');assert state('left-slot')['hotbar']==order[(idx-1)%len(order)];send('key 103');assert state('return-slot')['hotbar']==hot['hotbar']
 # The full crafting scene preserves material selection and cancellation.
 send('fixture-ux alchemy',1);assert state('alchemy')['scene']=='AlchemyScene';shot('alchemy')
 send('key 99');assert 'WndBag' in state('alchemy-material')['windows'];send('key 97');send('key 97',1);assert state('alchemy-return')['scene']=='GameScene'
 # Selected quickslot survives a real floor transition and a saved-game reload.
 send('key 102');send('key 102');selected=state('hotbar-before-descent');assert selected['hotbar']!=0
 send('fixture-ux descend',1)
 deadline=time.monotonic()+20
 while True:
  descended=state('hotbar-after-descent')
  if descended['scene']=='GameScene' and descended['depth']==selected['depth']+1:break
  assert time.monotonic()<deadline,descended
 assert descended['hotbar']==selected['hotbar'],(selected,descended)
 send('fixture-ux reload',1)
 deadline=time.monotonic()+20
 while True:
  restored=state('hotbar-after-reload')
  if restored['scene']=='GameScene':break
  assert time.monotonic()<deadline,restored
 assert restored['hotbar']==selected['hotbar'],(selected,restored)
 # A true modal interruption must not lose the game-over action cursor.
 send('fixture-death');time.sleep(2);assert state('death')['cursor'];send('key 1020');send('key 96');assert 'WndGame' in state('death-menu')['windows'];send('key 97');assert state('death-back')['cursor'];send('key 1019');send('key 96');assert state('death-restart')['scene']=='HeroSelectScene'

 send('exit');assert p.wait(timeout=15)==0,logpath.read_text()
 assert 'Exception in thread' not in logpath.read_text(),logpath.read_text()
 print('PASS: inspect A/Y, fullscreen map isolation, Buff details, catalog grid/return/tab memory, quickslot replace/cancel/clear/assign, nested focus, combat pickup, list menu, upgrade preview.')
 print('Screenshots and log:',home)
finally:
 if p.poll() is None:
  try:send('exit',0);p.wait(timeout=10)
  except Exception:p.terminate()
 log.close()
