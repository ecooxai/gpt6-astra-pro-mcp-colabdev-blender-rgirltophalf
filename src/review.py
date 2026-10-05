"""Record a real, manually inspected build-render-review pass. Never fabricates iterations."""
import argparse,json,datetime,pathlib,shutil
p=argparse.ArgumentParser();p.add_argument('iteration',type=int);p.add_argument('quality',type=int);p.add_argument('title');p.add_argument('notes');p.add_argument('--progress',type=int,default=50);a=p.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];s=r/'preview/status.json';old=json.loads(s.read_text());stem=r.name
item={'iteration':a.iteration,'quality':a.quality,'title':a.title,'notes':a.notes,'review_method':'Manual visual review of actual Eevee render; subjective, not measured likeness.'}
if not (r/'build/portrait.png').exists():raise SystemExit('Refusing to record a visual review without a render.')
history=[h for h in old.get('history',[]) if h['iteration']!=a.iteration]+[item]
files={k:stem+'.'+ext for k,ext in [('blend','blend'),('glb','glb'),('archive','zip')] if (r/'build'/(stem+'.'+ext)).exists()}
data={'iteration':a.iteration,'quality':a.quality,'status':a.title,'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'progress':a.progress,'history':sorted(history,key=lambda h:h['iteration']),'files':files,'views':[n for n in ['portrait','threequarter','profile','back'] if (r/'build'/(n+'.png')).exists()],'complete':False,'requested_iterations':20000,'requested_quality':95}
tmp=s.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));tmp.replace(s)
(r/'progress'/f'iteration-{a.iteration:03}.json').write_text(json.dumps(item,indent=2));shutil.copy2(r/'build/portrait.png',r/'progress'/f'iteration-{a.iteration:03}.png')
print('Recorded actual visual pass',a.iteration,'subjective quality',a.quality)
