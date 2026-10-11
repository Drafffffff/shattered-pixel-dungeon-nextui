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
args=['docker','run','--rm','--init','-v',f'{b}:/test','-w','/test/dist','-e',f'SPD_SAVE_DIR=/test/{relative}','shattered-rg34xx-smoke:local','xvfb-run','-a','-s','-screen 0 720x480x24','java','-Xms32m','-Xmx192m','-Xss512k','-XX:+UseSerialGC','-XX:MaxDirectMemorySize=64m','-XX:ActiveProcessorCount=2','-Djava.library.path=/test/dist/lib','-Dorg.lwjgl.opengles.libname=libGLESv2.so.2','-Dnextui.smokeSeconds=70',f'-Dnextui.commands=/test/{relative}/commands','-cp','shattered-rg34xx.jar:lib/*','org.nextui.shattered.RgLauncher']
args.insert(args.index('-cp'),f'-Dnextui.settingsFile=/test/{relative}/hardware-settings')
p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
def wait_for(needle,timeout=30):
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  if needle in logpath.read_text():return
  if p.poll() is not None:break
  time.sleep(.1)
 raise RuntimeError('Missing '+needle+'\n'+logpath.read_text())
def send(cmd,delay=.45):
 t=command.with_suffix('.tmp');t.write_text(cmd+'\n');t.replace(command)
 deadline=time.monotonic()+5
 while command.exists():
  if time.monotonic()>deadline:raise RuntimeError('Command not consumed: '+cmd)
  time.sleep(.03)
 time.sleep(delay)
def shot(name):send(f'shot /test/{relative}/{name}.png')
def state(name):
 send(f'state /test/{relative}/{name}.json')
 raw=json.loads((home/f'{name}.json').read_text())
 return {k:v['value'] if isinstance(v,dict) and 'value' in v else v for k,v in raw.items()}
def checkUX():
 before=state('exploring')
 send('key 97');examining=state('examine-mode');shot('examine-mode')
 assert examining['targeting'] and examining['windowCount']==0 and not examining['targetPrompt'],examining
 send('key 97');cancelled=state('examine-cancelled')
 assert not cancelled['targeting'] and cancelled['windowCount']==0,cancelled
 assert cancelled['turn']==before['turn'],'Examine/cancel spent a turn'
 send('key 97');send('key 96');shot('examine-details')
 assert state('examine-details-state')['windowCount']>0,'A did not open target details'
 send('key 97')
 send('key 108');assert 'WndGame' in state('pause-open')['windows']
 send('key 108');assert state('pause-closed')['windowCount']==0,'Start did not toggle pause'
 before=state('hotbar-before')
 positions={int(k):float(v) for k,v in (entry.split(':') for entry in before['hotbarPositions'].strip(',').split(','))}
 order=sorted(positions,key=positions.get);index=order.index(before['hotbar'])
 send('key 102');left=state('hotbar-left');shot('hotbar-left')
 assert left['hotbar']==order[(index-1)%len(order)],(before,left)
 send('key 103');assert state('hotbar-return')['hotbar']==before['hotbar']
 send('key 103');right=state('hotbar-right');shot('hotbar-right')
 assert right['hotbar']==order[(index+1)%len(order)],(before,right)
 hardware[4]=11;settingsFile.write_bytes(struct.pack('<16i',*hardware));time.sleep(.2)
 assert '11 / 20' in state('volume-state')['overlay'];shot('volume')
 before=state('system-combo-before')
 send('down 106');send('key 20001');hardware[1]=6;settingsFile.write_bytes(struct.pack('<16i',*hardware));send('up 106')
 assert '6 / 10' in state('brightness-state')['overlay'];shot('brightness')
 after=state('system-combo-after');assert after['turn']==before['turn'],'Brightness combo spent a turn'
 send('down 109');send('key 20001');hardware[2]=21;settingsFile.write_bytes(struct.pack('<16i',*hardware));send('up 109')
 assert '21 / 40' in state('color-state')['overlay']
 assert state('system-combo-windows')['windowCount']==0,'System combo opened hero info'
 time.sleep(2.1);assert state('osd-hidden')['overlay']=='','OSD did not expire'
try:
 if options.resume_from:
  wait_for('Scene: RgHome');shot('home')
  send('key 96');wait_for('Scene: StartScene')
  # First direction focuses Back; second moves down to the saved hero.
  send('key 1020');send('key 1020')
  send('key 96');shot('resume-dialog')
  if options.delete_test:
   send('key 1020');send('key 1020');send('key 96');shot('delete-confirm')
   assert state('delete-confirm-state')['windowCount']==2
   send('key 96');assert (home/'game1/game.dat').exists(),'Default confirmation deleted the save'
   assert state('delete-cancel-state')['windowCount']==1
   send('key 96');send('key 1020');send('key 1020');send('key 96')
   shot('delete-after');deleted=state('delete-after-state')
   # Upstream overwrites game.dat with a one-byte tombstone, not unlink.
   time.sleep(.6);assert (home/'game1/game.dat').stat().st_size==1,'Confirmed deletion left a playable save'
   assert not list((home/'game1').glob('depth*.dat')),'Confirmed deletion left dungeon floors'
   assert deleted['windowCount']==0,deleted
   send('exit');assert p.wait(timeout=15)==0,logpath.read_text()
   print('PASS: compact run details, cancel-by-default and confirmed deletion of test copy only.')
   print('Screenshots and log:',home)
   sys.exit(0)
  send('key 96');wait_for('Scene: GameScene')
  time.sleep(2.5)
  recovered=state('resume-state')
  assert not recovered['intro'] and recovered['status'] and recovered['toolbar'],recovered
  assert recovered['hiddenDoors']==0 and not recovered['cursor'],recovered
  assert 'Tutorial recovered: previously read Intro on floor 1' in logpath.read_text()
  shot('resume-recovered')
  if options.menu_test:
   send('key 108')
   for _ in range(5):send('key 1020')
   send('key 96');assert 'RgControls' in state('pause-controls-state')['windows']
   shot('pause-controls')
   for _ in range(7):send('key 1020')
   shot('controls-scrolled');send('key 97')
   assert state('controls-closed')['windowCount']==0
   send('key 108')
   for _ in range(6):send('key 1020')
   send('key 96');wait_for('Scene: RgHome');shot('saved-title')
   assert state('saved-title-state')['scene']=='RgHome'
   data=(home/'game1/game.dat').read_bytes()
   json.loads(gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data)
   for _ in range(3):send('key 1020')
   shot('home-settings-focused');send('down 96');send('up 96');shot('home-settings-opened');assert 'Preferences' in state('home-preferences-state')['windows']
   shot('home-preferences')
   send('key 1020');send('key 1020');send('key 96')
   assert 'RgControls' in state('home-controls-state')['windows']
   shot('home-controls');send('key 97')
   assert state('home-controls-closed')['windowCount']==0
   send('exit');assert p.wait(timeout=15)==0,logpath.read_text()
   assert 'Exception in thread' not in logpath.read_text()
   print('PASS: pause help scrolling/back, save-to-title JSON, home preferences/help and modal navigation.')
   print('Screenshots and log:',home)
   sys.exit(0)
  checkUX()
  send('key 99');assert 'WndBag' in state('x-inventory-state')['windows'],'X lost inventory shortcut'
  shot('x-inventory');send('key 97')
  if options.death_test:
   send('fixture-death');time.sleep(2.5)
   dead=state('game-over-state');assert not dead['alive'] and dead['cursor'],dead
   shot('game-over')
   send('key 1020');shot('game-over-menu-focused');send('key 96')
   assert 'WndGame' in state('game-over-menu-open')['windows']
   shot('game-over-menu');send('key 97')
   assert state('game-over-menu-closed')['cursor']
   send('key 1019');send('key 96')
   assert state('game-over-restart')['scene']=='HeroSelectScene'
   shot('game-over-new-adventure')
  send('exit');assert p.wait(timeout=15)==0,logpath.read_text()
  assert 'Exception in thread' not in logpath.read_text()
  print('PASS: old save recovery, B examine/cancel without floating prompt, X inventory, Start toggle, spatial L/R and system OSD/combo isolation.')
  if options.death_test:print('PASS: game-over cursor, D-pad menu, B return and new-adventure action.')
  print('Screenshots and log:',home)
 else:
  wait_for('Scene: WelcomeScene')
  shot('help')
  for c in [96,96,96,1020,1020,1020,96]:send(f'key {c}')
  wait_for('Scene: InterlevelScene')
  time.sleep(1)
  send('key 96')
  wait_for('Scene: GameScene')
  for c in [1020,1020,1020]:send(f'key {c}')
  shot('dungeon')
  before=state('intro-before')
  assert before['intro'] and not before['status'] and not before['toolbar'],before
  assert not before['cursor'],before
  send('key 99');shot('inventory')
  # The first down gives initial focus; the next selects the thrown stones.
  for c in [1020,1020,96]:send(f'key {c}')
  shot('item')
  # First arrow initializes focus on Drop; second moves to Throw.
  send('key 1022');send('key 1022');send('key 96');shot('aim')
  assert state('aim-state')['cursor'],'Target cursor was hidden'
  send('key 1022');shot('aim-right')
  send('key 97')
  # A found guide page must be reachable through the real pause menu.
  send('fixture-guide')
  send('key 108')
  for c in [1020,1020,96]:send(f'key {c}')
  shot('guide-index')
  send('key 96');shot('guide-page')
  assert state('guide-state')['intro'],'Intro ended before closing its page'
  assert state('guide-cursor')['cursor'],'Reader cursor was hidden'
  send('key 1020');shot('guide-scrolled')
  send('key 97');send('key 97')
  time.sleep(2.2)
  after=state('intro-after')
  assert not after['intro'] and after['status'] and after['toolbar'],after
  assert after['hiddenDoors']==0,after
  assert not after['cursor'],after
  shot('tutorial-completed')
  checkUX()
  send('key 108');shot('pause')
  # Default focus is settings; A opens it and arrows can reach sliders.
  send('key 96');shot('settings')
  for c in [1020,1020,1022]:send(f'key {c}')
  shot('settings-adjusted')
  send('key 97')
  send('exit')
  code=p.wait(timeout=15)
  if code:raise RuntimeError(logpath.read_text())
  saves=list(home.glob('game*/game.dat'))
  assert saves,'No game save produced'
  for f in saves:
   data=f.read_bytes()
   if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
   json.loads(data)
  assert 'Exception in thread' not in logpath.read_text(),logpath.read_text()
  assert 'Guide page read:' in logpath.read_text(),'Guide page was not reachable by D-pad/A'
  assert 'Tutorial completed: Intro reader closed' in logpath.read_text()
  print(logpath.read_text())
  print('PASS: real render, D-pad play, tutorial completion/HUD/doors, contextual cursor, settings and save JSON.')
  print('Screenshots and log:',home)
finally:
 if p.poll() is None:
  try:send('exit',0);p.wait(timeout=10)
  except Exception:p.terminate()
 log.close()
