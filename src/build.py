"""Rebuild original geometry, render with Eevee, and export a browser model."""
import bpy, os, sys, math, json, time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
FAST='--fast' in ARGS
STEM='gpt6_astra_pro_mcp_colabdev_blender_rgirltophalf'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials):bpy.data.materials.remove(d)
from common import *
from clothing import make_clothing
from face import make_face
from hair import make_hair
make_clothing()
old=set(bpy.data.objects)
make_face()
headparts=set(bpy.data.objects)-old
before_hair=set(bpy.data.objects)
make_hair()
hairparts=set(bpy.data.objects)-before_hair
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,3.08));pivot=bpy.context.object;pivot.name='Portrait pose · head tilt and turn';pivot['export_web']=True
for o in headparts:
    world=o.matrix_world.copy();o.parent=pivot;o.matrix_world=world
pivot.rotation_euler=(math.radians(-1),math.radians(5.8),math.radians(1.5))
pivot.scale.x=1.04
# Hair follows the head at its roots, but the chest lengths retain a natural gravity-led drape.
rot=pivot.rotation_euler.to_matrix();origin=Vector((0,0,3.08))
for ob in hairparts:
    if ob.type=='MESH':
        for vert in ob.data.vertices:
            p=vert.co.copy();weight=smooth((p.z-2.35)/1.15);vert.co=p.lerp(origin+rot@(p-origin),weight)
            if vert.co.z<2.70:
                from clothing import W,D
                w=interp(W,vert.co.z)+.035;d=interp(D,vert.co.z)+.035
                q=sqrt((vert.co.x/w)**2+((vert.co.y-.06)/d)**2)
                if .03<q<1:vert.co.x/=q;vert.co.y=.06+(vert.co.y-.06)/q


scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16 if FAST else 64
scene.render.resolution_x=720 if FAST else 1200;scene.render.resolution_y=1080 if FAST else 1800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
scene.world.color=(.055,.055,.055);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.09,.105,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.28
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0

def area(name,loc,power,color,size,target=(0,0,3.8),shape='DISK',size_y=None):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape=shape;o.data.size=size
    if size_y is not None and shape=='RECTANGLE':o.data.size_y=size_y
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['export_web']=False
area('Key · large warm portrait softbox',(-3.8,-5.2,6.5),680,(1,.90,.83),4.2,shape='RECTANGLE',size_y=5.5)
area('Fill · cool bounce',(3.3,-4.1,4.7),300,(.85,.89,1),3.5)
area('Rim · hair separation',(2.4,2.2,6.6),220,(1,.85,.77),3.0)
area('Left hair rim',(-3.0,1.4,5.1),160,(.86,.91,1),2.4)
area('Eye softbox',(-.5,-4.0,5.4),45,(1,.98,.92),1.5,shape='RECTANGLE',size_y=.8)
backmat=mat('Studio backdrop · warm charcoal','#29242b',.91)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.055));floor=bpy.context.object;floor.name='Studio floor';floor.data.materials.append(backmat);floor['export_web']=False
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,4,40),rotation=(math.pi/2,0,0));wall=bpy.context.object;wall.name='Studio backdrop';wall.data.materials.append(backmat);wall['export_web']=False
bpy.ops.object.camera_add(location=(0,-12,3.2));cam=bpy.context.object;cam.name='Portrait camera';cam.data.type='ORTHO';cam.data.ortho_scale=6.10;cam.data.lens=85;cam['export_web']=False
cam.rotation_euler=(Vector((0,0,3.225))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
bpy.context.view_layer.update()
build=ROOT/'build';build.mkdir(exist_ok=True)
blend=build/(STEM+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
print('BLEND saved',blend,flush=True)
scene.render.filepath=str(build/'portrait.next.png');bpy.ops.render.render(write_still=True);os.replace(build/'portrait.next.png',build/'portrait.png')
print('RENDER portrait complete',flush=True)
if '--export' in ARGS:
    bpy.ops.object.select_all(action='DESELECT');selected=[]
    for o in list(bpy.data.objects):
        if o.get('export_web',False) and o.type in {'MESH','EMPTY'}:o.select_set(True);selected.append(o)
    bpy.ops.export_scene.gltf(filepath=str(build/(STEM+'.next.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False,export_extras=True,export_materials='EXPORT')
    os.replace(build/(STEM+'.next.glb'),build/(STEM+'.glb'))
    print('GLB exported',len(selected),'objects',flush=True)
print('BUILD completed',flush=True)
