"""Build deterministic release archives from an explicit public-file allowlist."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from travel_kit import __version__
from travel_kit.demo import make_demo

STAMP=(2026,9,19,0,0,0)
EPOCH='1789776000'


def zip_files(path,files):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data,executable in sorted(files):
            info=zipfile.ZipInfo(name,STAMP);info.create_system=3;info.external_attr=(0o100755 if executable else 0o100644)<<16;info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def main():
    names=json.loads((ROOT/'release-files.json').read_text())
    if names!=sorted(set(names)):raise ValueError('Release file list must be sorted and unique.')
    files=[];hashes={}
    for name in names:
        path=ROOT/name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or not path.is_file():raise ValueError('Unsafe or missing allowlisted file: '+name)
        data=path.read_bytes();files.append((name,data,name.endswith('.command')));hashes[name]=hashlib.sha256(data).hexdigest()
    prefix='travel-planning-kit-'+__version__;destination=ROOT/'artifacts'/'release';destination.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='travel-release-') as folder:
        temporary=Path(folder);source=temporary/prefix;source.mkdir()
        for name,data,executable in files:
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);path.chmod(0o755 if executable else 0o644)
        out=temporary/'output';out.mkdir()
        zip_files(out/(prefix+'-source.zip'),[(prefix+'/'+name,data,mode) for name,data,mode in files])
        demo=temporary/'demo';make_demo(demo)
        zip_files(out/(prefix+'-demo.zip'),[('travel-planning-kit-demo/'+p.name,p.read_bytes(),False) for p in demo.iterdir()])
        env=dict(os.environ,SOURCE_DATE_EPOCH=EPOCH,PYTHONHASHSEED='0')
        subprocess.run([sys.executable,'-m','build','--wheel','--no-isolation','--outdir',str(out)],cwd=source,env=env,check=True,stdout=subprocess.DEVNULL)
        provenance={'project':'Travel Planning Kit','version':__version__,'sourceFiles':hashes,'fixture':'Entirely invented Cedar Bay trip and generated property images','buildEpoch':EPOCH}
        (out/'release-provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
        checks=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(out.iterdir()))
        (out/'SHA256SUMS.txt').write_text(checks)
        for path in out.iterdir():shutil.copyfile(path,destination/path.name)
    print('Created reviewed-source candidates in '+str(destination))

if __name__=='__main__':main()
