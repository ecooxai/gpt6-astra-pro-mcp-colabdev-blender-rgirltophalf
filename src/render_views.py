import bpy,sys,math,json,datetime
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
views=args[0].split(',') if args else ['threequarter','profile','back']
size=int(args[1]) if len(args)>1 else 720;samples=int(args[2]) if len(args)>2 else 20
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build'/(ROOT.name+'.blend')))
scene=bpy.context.scene;cam=scene.camera;scene.eevee.taa_render_samples=samples
scene.render.resolution_x=size;scene.render.resolution_y=int(size*1.5)
for name in views:
    a={'portrait':0,'threequarter':math.radians(35),'profile':math.radians(90),'back':math.pi}[name]
    d=Vector((math.sin(a),-math.cos(a),0));target=Vector((0,0,3.10));cam.location=target+d*12+Vector((0,0,.10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.35
    wall=bpy.data.objects.get('Studio backdrop');wall.location=target-d*4;wall.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    scene.render.filepath=str(ROOT/'build'/(name+'.png'));bpy.ops.render.render(write_still=True)
    print('VIEW COMPLETE',name,flush=True)
print('VIEW SET COMPLETE',flush=True)
