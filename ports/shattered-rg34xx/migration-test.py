#!/usr/bin/env python3
"""Verify real 3.3.8 save upgrade plus 4.0 vault rendering and D-pad interactions."""
from pathlib import Path
import subprocess,time,sys,tempfile,json,gzip,shutil,argparse,struct,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[2]
b=root/'build/shattered-rg34xx'
home=Path(tempfile.mkdtemp(prefix='smoke-',dir=b))
parser=argparse.ArgumentParser()
parser.add_argument('--resume-from',type=Path,required=True)
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
 original=json.loads(gzip.decompress((options.resume_from/'game1/game.dat').read_bytes()))
 assert original['version']==896, 'This migration regression requires a 3.3.8 fixture'
 wait_for_home();homeState=state('upgraded-home');assert homeState['gameVersion']=='4.0.2' and homeState['settingsVersion']==922,homeState
 shot('upgraded-home');send('key 96');wait_for('Scene: StartScene')
 send('key 1020');send('key 1020');send('key 96');send('key 96');wait_for('Scene: GameScene');time.sleep(2)
 restored=state('legacy-restored');shot('legacy-restored')
 assert restored['depth']==original['depth'] and restored['heroClass']==original['hero']['class'] and restored['heroLevel']==original['hero']['lvl'] and restored['gold']==original['gold'],restored
 assert not restored['intro'] and restored['toolbar'] and restored['status'],restored
 # Generate the official 4.0 vault through the normal transition loader.
 send('fixture-ux vault',1)
 deadline=time.monotonic()+30
 while True:
  vault=state('vault-generated')
  if vault['scene']=='GameScene' and vault['levelType']=='VaultLevel':break
  assert time.monotonic()<deadline,vault
  time.sleep(.2)
 assert vault['branch']==1 and vault['depth']==17 and not vault['cursor'],vault
 shot('vault-generated')
 send('down 109',.65);send('up 109');m=state('vault-map');shot('vault-map')
 assert m['mapMode'] and not m['uiVisible'] and m['cameraX']+m['cameraWorldWidth']>=m['mapWidth'] and m['cameraY']+m['cameraWorldHeight']>=m['mapHeight'],m
 send('key 105');assert state('vault-zoom')['cameraZoom']>m['cameraZoom'];send('key 97');assert state('vault-map-overview')['mapOverview'];send('key 97')
 # Reach the new mirror's long dialog by physically walking into the NPC.
 send('fixture-ux vault-mirror');send('key '+str(state('mirror-placed')['fixtureDirection']))
 mirror=state('mirror-dialog');shot('mirror-dialog');assert 'WndOptions' in mirror['windows'] and mirror['focusType'] and not mirror['cursor'],mirror
 assert mirror['windowLeft']<mirror['focusScreenX']<mirror['windowRight'] and mirror['windowTop']<mirror['focusScreenY']<mirror['windowBottom'],mirror
 send('key 96');accepted=state('mirror-accepted');assert accepted['mirrorUsed'] and 'WndTitledMessage' in accepted['windows'],accepted
 send('key 97');assert state('mirror-closed')['windowCount']==0
 # Token door: cancel preserves the door; confirm opens it using the original action.
 send('fixture-ux vault-door');direction=state('door-placed')['fixtureDirection'];send('key '+str(direction))
 door=state('door-dialog');shot('door-dialog');assert 'WndOptions' in door['windows'] and door['focusType'],door
 send('key 97');assert state('door-cancel')['fixtureNpcPresent'];send('key '+str(direction));send('key 96');assert not state('door-opened')['fixtureNpcPresent']
 # Escape crystal remains reachable and cancellable without leaving the quest.
 send('fixture-ux vault-exit');escape=state('vault-exit-dialog');shot('vault-exit-dialog');assert 'WndOptions' in escape['windows'] and escape['focusType'],escape
 send('key 97');assert state('vault-exit-cancel')['branch']==1
 send('fixture-ux vault-exit');send('key 96');picker=state('vault-reward-picker');assert 'WndBag' in picker['windows'] and picker['focusType'],picker
 send('key 96');confirmation=state('vault-reward-confirm');shot('vault-reward-confirm');assert 'WndOptions' in confirmation['windows'] and confirmation['focusType'],confirmation
 send('key 97');assert state('vault-reward-cancel')['branch']==1
 send('fixture-ux reload',1)
 deadline=time.monotonic()+20
 while True:
  loaded=state('vault-reloaded')
  if loaded['scene']=='GameScene':break
  assert time.monotonic()<deadline,loaded
 assert loaded['levelType']=='VaultLevel' and loaded['branch']==1 and loaded['mirrorUsed'],loaded
 send('exit');assert p.wait(timeout=15)==0,logpath.read_text()
 saved=json.loads(gzip.decompress((home/'game1/game.dat').read_bytes()));assert saved['version']==922,saved['version']
 assert 'Exception in thread' not in logpath.read_text() and 'JSONException' not in logpath.read_text(),logpath.read_text()
 print('PASS: legacy 3.3.8 hero retained; settings/save upgraded to 4.0.2; official vault generation/map, mirror reward, token door cancel/confirm, escape cancel and vault save/reload.')
 print('Screenshots and log:',home)
finally:
 if p.poll() is None:
  try:send('exit',0);p.wait(timeout=10)
  except Exception:p.terminate()
 log.close()
