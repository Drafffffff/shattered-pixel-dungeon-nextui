#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Package a committed source tree, SD-card installation, and dependency sources."""
from pathlib import Path
import concurrent.futures, hashlib, json, subprocess, sys, tarfile, urllib.request, zipfile
root=Path(__file__).resolve().parents[2]
version=sys.argv[1] if len(sys.argv)>1 else 'v4.0.2-nextui.5'
if not version or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_' for c in version):
    raise SystemExit('Invalid version')
build=root/'build/shattered-rg34xx';dist=build/'dist';out=build/'release'/version
if not (dist/'.build-ok').exists(): raise SystemExit('Build first')
if subprocess.check_output(['git','status','--porcelain'],cwd=root): raise SystemExit('Commit source changes first')
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
out.mkdir(parents=True,exist_ok=True)
prefix='Shattered-Pixel-Dungeon-'+version
binary=out/(prefix+'-RG34XX.zip')
with zipfile.ZipFile(binary,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    z.write(root/'ports/shattered-rg34xx/launch.sh','Roms/Ports (PORTS)/Shattered Pixel Dungeon.sh')
    target='Roms/Ports (PORTS)/.ports/shattered-rg34xx/'
    for p in sorted(dist.rglob('*')):
        relative=p.relative_to(dist)
        # These are regenerated below; dist may contain a previous release staging copy.
        if p.is_file() and relative.parts[0] not in ('BUILD-INFO.json','THIRD_PARTY_NOTICES.md','licenses'):
            z.write(p,target+str(relative))
    z.write(root/'README.md','INSTALL.md')
    z.write(root/'THIRD_PARTY_NOTICES.md',target+'THIRD_PARTY_NOTICES.md')
    for p in (root/'licenses').rglob('*'):
        if p.is_file(): z.write(p,target+'licenses/'+str(p.relative_to(root/'licenses')))
    z.writestr(target+'BUILD-INFO.json',json.dumps({'version':version,'source_commit':commit,'upstream_commit':'57a4e06a4caf162446d1c28caa7983f0493fecf0','target':'RG34XX H700 NextUI 720x480','source_repository':'https://github.com/Drafffffff/shattered-pixel-dungeon-nextui'},indent=2)+'\n')
source=out/(prefix+'-source.tar.gz')
subprocess.run(['git','archive','--format=tar.gz','--prefix='+prefix+'/', '-o',str(source),'HEAD'],cwd=root,check=True)
cache=build/'third-party-sources';cache.mkdir(parents=True,exist_ok=True)
items=json.loads((root/'third-party/sources-lock.json').read_text())
def fetch(i):
    p=cache/i['file']
    if not p.exists():
        tmp=p.with_suffix('.download');urllib.request.urlretrieve(i['url'],tmp);tmp.replace(p)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=i['sha256']: raise RuntimeError('Source checksum mismatch: '+p.name)
    return p
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: files=list(pool.map(fetch,items))
third=out/(prefix+'-third-party-sources.tar.gz')
with tarfile.open(third,'w:gz') as t:
    for p in files: t.add(p,arcname='third-party-sources/'+p.name)
    t.add(root/'third-party/sources-lock.json',arcname='third-party-sources/sources-lock.json')
    t.add(root/'THIRD_PARTY_NOTICES.md',arcname='third-party-sources/THIRD_PARTY_NOTICES.md')
checks=out/'SHA256SUMS'
checks.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in [binary,source,third]))
print(out)
