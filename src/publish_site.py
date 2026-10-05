"""Assemble a self-contained GitHub Pages snapshot, never publishing private runtime logs."""
from pathlib import Path
import argparse,json,shutil
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--release-base',default='');args=parser.parse_args()
site=ROOT/'docs'
if site.exists():shutil.rmtree(site)
site.mkdir()
for name in ['index.html','app.js','style.css']:
    shutil.copy2(ROOT/'preview'/name,site/name)
shutil.copytree(ROOT/'preview/vendor',site/'vendor')
(site/'artifacts').mkdir();(site/'reference').mkdir();(site/'history').mkdir()
shutil.copy2(ROOT/'reference/reference.png',site/'reference/reference.png')
state=json.loads((ROOT/'preview/status.json').read_text())
for name in state.get('views',[]):
    source=ROOT/'build'/(name+'.png')
    if source.is_file():shutil.copy2(source,site/'artifacts'/source.name)
if state.get('files',{}).get('glb'):
    source=ROOT/'build'/state['files']['glb'];shutil.copy2(source,site/'artifacts'/source.name)
for item in state.get('history',[]):
    source=ROOT/'progress'/f"iteration-{int(item['iteration']):03}.png"
    if source.exists():shutil.copy2(source,site/'history'/source.name)
state['delivery']='snapshot';state['running']=False
state['source_url']='https://github.com/ecooxai/gpt6-astra-pro-mcp-colabdev-blender-rgirltophalf'
state['downloads']={}
for kind in ['blend','archive']:
    if kind not in state.get('files',{}):continue
    if args.release_base:state['downloads'][kind]=args.release_base.rstrip('/')+'/'+state['files'][kind]
    else:del state['files'][kind]
(site/'status.json').write_text(json.dumps(state,indent=2))
(site/'.nojekyll').write_text('')
print('Static checkpoint:',site,'iteration',state['iteration'])
print('Assets:',sum(p.stat().st_size for p in site.rglob('*') if p.is_file()),'bytes')
