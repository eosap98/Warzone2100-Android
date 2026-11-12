#!/usr/bin/env python3
"""Extract portable game assets (never Debian executable code) and create integrity manifest."""
import hashlib, json, pathlib, shutil, subprocess, tarfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEB=ROOT.parent/'warzone2100_ubuntu24.04_amd64.deb'
ASSETS=ROOT/'build/assets'
DATA=ASSETS/'data'
DATA.mkdir(parents=True,exist_ok=True)
version=subprocess.check_output(['dpkg-deb','-f',str(DEB),'Version'],text=True).strip()
if version != '4.7.0': raise SystemExit('Expected Warzone 2100 data version 4.7.0; found '+version)
print('Extracting 4.7.0 game data',flush=True)
p=subprocess.Popen(['dpkg-deb','--fsys-tarfile',str(DEB)],stdout=subprocess.PIPE)
with tarfile.open(fileobj=p.stdout, mode='r|') as archive:
 for member in archive:
  prefix='./usr/share/warzone2100/'
  locale_prefix='./usr/share/locale/'
  if not member.isfile(): continue
  if member.name.startswith(prefix):
   relative=pathlib.PurePosixPath(member.name[len(prefix):])
  elif member.name.startswith(locale_prefix) and member.name.endswith(('/warzone2100.mo','/warzone2100_guide.mo')):
   relative=pathlib.PurePosixPath('locale')/member.name[len(locale_prefix):]
  else: continue
  if relative.is_absolute() or '..' in relative.parts: raise ValueError(member.name)
  target=DATA/relative; target.parent.mkdir(parents=True,exist_ok=True)
  with archive.extractfile(member) as src, target.open('wb') as out: shutil.copyfileobj(src,out,1024*1024)
if p.wait()!=0: raise SystemExit('Debian data extraction failed')
for name in ('base.wz','mp.wz','fonts/DejaVuSans.ttf','locale/id/LC_MESSAGES/warzone2100.mo','locale/id/LC_MESSAGES/warzone2100_guide.mo'):
 if not (DATA/name).is_file(): raise SystemExit('Missing data: '+name)
licenses=ASSETS/'licenses';licenses.mkdir(exist_ok=True)
for name in ('COPYING','COPYING.NONGPL','COPYING.README','AUTHORS'):
 shutil.copy2(ROOT.parent/'warzone2100'/name,licenses/name)
shutil.copy2(ROOT.parent/'warzone2100/pkg/licenses/COPYING.gpl3',licenses/'COPYING.gpl3')
shutil.copy2(ROOT.parent/'warzone2100/icons/warzone2100.png',ROOT/'app/res/drawable/icon.png')
files=[]
for path in sorted(DATA.rglob('*')):
 if path.is_file():
  files.append({'path':path.relative_to(DATA).as_posix(),'size':path.stat().st_size,'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()})
(ASSETS/'data-manifest.json').write_text(json.dumps({'version':version,'files':files},indent=2)+'\n')
print('Packaged data:',len(files),'files;',sum(f['size'] for f in files)//1048576,'MiB',flush=True)
