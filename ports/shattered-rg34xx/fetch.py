#!/usr/bin/env python3
"""Fetch the pinned GPL game snapshot and checksum-pinned Maven dependencies."""
from pathlib import Path
import concurrent.futures, hashlib, json, shutil, subprocess, urllib.request
root=Path(__file__).resolve().parents[2]
build=root/'build/shattered-rg34xx'
source=build/'source'
commit='57a4e06a4caf162446d1c28caa7983f0493fecf0'
vendor=root/'vendor/shattered-pixel-dungeon'
if vendor.exists():
    manifest=json.loads((root/'vendor/upstream-manifest.json').read_text())
    if manifest['commit'] != commit:
        raise RuntimeError('Vendored revision mismatch')
    for name, digest in manifest['files'].items():
        if hashlib.sha256((vendor/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Vendored checksum mismatch: '+name)
    if not source.exists():
        shutil.copytree(vendor,source)
        (source/'.upstream-revision').write_text(commit+'\n')
if not source.exists():
    subprocess.run(['git','clone','https://github.com/00-Evan/shattered-pixel-dungeon.git',str(source)],check=True)
if (source/'.git').exists():
    if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=commit:
        subprocess.run(['git','-C',str(source),'checkout','--detach',commit],check=True)
elif (source/'.upstream-revision').read_text().strip()!=commit:
    raise RuntimeError('Build source revision mismatch; remove build/shattered-rg34xx/source')
lock=json.loads((Path(__file__).parent/'dependencies.json').read_text())
out=build/'deps';out.mkdir(parents=True,exist_ok=True)
def fetch(item):
    p=out/item['file']
    if not p.exists():
        temporary=p.with_suffix('.download')
        urllib.request.urlretrieve(item['url'],temporary)
        if hashlib.sha256(temporary.read_bytes()).hexdigest()!=item['sha256']:
            temporary.unlink();raise RuntimeError('Checksum mismatch: '+p.name)
        temporary.replace(p)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
        raise RuntimeError('Checksum mismatch: '+p.name)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    list(pool.map(fetch,lock))
print('Verified source revision and',len(lock),'dependencies')
