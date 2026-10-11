#!/usr/bin/env python3
"""Verify selected slot survives actual floor transitions and save/load on a copy."""
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
 before=state('before');assert before['hotbar']==0,before
 send('key 102');send('key 102');selected=state('selected');assert selected['hotbar']!=0,selected;assert selected['quickslots'].split(';')[selected['hotbar']]=='empty',selected
 send('fixture-ux descend',1)
 deadline=time.monotonic()+20
 while True:
  descended=state('descended')
  if descended['scene']=='GameScene' and descended['depth']==selected['depth']+1:break
  assert time.monotonic()<deadline,descended
 assert descended['hotbar']==selected['hotbar'],(selected,descended)
 send('fixture-ux reload',1)
 deadline=time.monotonic()+20
 while True:
  restored=state('restored')
  if restored['scene']=='GameScene':break
  assert time.monotonic()<deadline,restored
 assert restored['hotbar']==selected['hotbar'],(selected,restored)
 send('exit');assert p.wait(timeout=15)==0,logpath.read_text()
 assert 'Exception in thread' not in logpath.read_text(),logpath.read_text()
 data=(home/'game1/game.dat').read_bytes();bundle=json.loads(gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data)
 assert bundle['nextui_selected_hotbar']==selected['hotbar'],bundle.get('nextui_selected_hotbar')
 print('PASS: legacy default 0, nonzero/empty selected slot, real descent, save/load; slot',selected['hotbar'],'flip',options.flip_toolbar)
 print('Screenshots and log:',home)
finally:
 if p.poll() is None:
  try:send('exit',0);p.wait(timeout=10)
  except Exception:p.terminate()
 log.close()
