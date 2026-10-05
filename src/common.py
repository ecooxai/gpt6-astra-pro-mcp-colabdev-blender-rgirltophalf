"""Original geometric utilities. No image sampling or imported model assets."""
import bpy, math, random
from mathutils import Vector
from math import sin, cos, pi, exp, sqrt
RNG=random.Random(20261005)

def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def rgba(h):
    h=h.lstrip('#'); return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
def mix(a,b,t): return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def clamp(x,a=0,b=1): return max(a,min(b,x))
def smooth(t): t=clamp(t); return t*t*(3-2*t)
def gauss(x,z,cx,cz,sx,sz): return exp(-((x-cx)/sx)**2-((z-cz)/sz)**2)
def interp(table,t):
    if t<=table[0][0]: return table[0][1]
    if t>=table[-1][0]: return table[-1][1]
    i=next(i for i in range(len(table)-1) if table[i][0]<=t<=table[i+1][0])
    x1,y1=table[i]; x2,y2=table[i+1]; u=(t-x1)/(x2-x1)
    p0=table[max(0,i-1)]; p3=table[min(len(table)-1,i+2)]
    m1=(y2-p0[1])/(x2-p0[0]); m2=(p3[1]-y1)/(p3[0]-x1)
    return (2*u**3-3*u*u+1)*y1+(u**3-2*u*u+u)*m1*(x2-x1)+(-2*u**3+3*u*u)*y2+(u**3-u*u)*m2*(x2-x1)
def spline(points,n=50):
    p=[Vector(v) for v in points]; out=[]
    for k in range(n):
        q=(len(p)-1)*k/(n-1); i=min(len(p)-2,int(q)); t=q-i
        a,b,c,d=p[max(0,i-1)],p[i],p[i+1],p[min(len(p)-1,i+2)]
        out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return out

def mat(name,color,rough=.45,metal=0,skin=False,cloth=False):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=rgba(color)
    n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=rgba(color); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    p.inputs['Specular IOR Level'].default_value=.32
    if skin:
        p.inputs['Subsurface Weight'].default_value=.095; p.inputs['Subsurface Radius'].default_value=(1,.45,.30); p.inputs['Subsurface Scale'].default_value=.12
        a=n.new('ShaderNodeVertexColor'); a.layer_name='SkinTone'; l.new(a.outputs['Color'],p.inputs['Base Color'])
        lipmask=n.new('ShaderNodeVertexColor'); lipmask.layer_name='LipMask'
        rough=n.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.46;rough.inputs['To Max'].default_value=.33;l.new(lipmask.outputs['Color'],rough.inputs['Value']);l.new(rough.outputs['Result'],p.inputs['Roughness'])
        tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=185; tex.inputs['Detail'].default_value=2.5; tex.inputs['Roughness'].default_value=.68
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15; bump.inputs['Distance'].default_value=.006; l.new(tex.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],p.inputs['Normal'])
    if cloth:
        p.inputs['Sheen Weight'].default_value=.25; p.inputs['Sheen Roughness'].default_value=.7
        tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=230; tex.inputs['Detail'].default_value=1
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.18; bump.inputs['Distance'].default_value=.004; l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m
SKIN=mat('Skin · peach ivory / procedural pores','#e7bba8',.44,skin=True)
SKIN_BASE=rgba('#e6b6a6'); BLUSH=rgba('#dba092'); EYEWARM=rgba('#bb897d')
LIP=mat('Lips · muted rose satin','#b86f73',.38)
LIP.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.15
SCLERA=mat('Sclera · warm ivory','#e4dcd5',.23)
SCLERA.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.65
PUPIL=mat('Pupil · deep brown-black','#100b09',.16)
LASH=mat('Eyelashes · umber','#30201e',.47)
CREASE=mat('Soft facial creases','#97675c',.65)
MOUTH=mat('Mouth opening','#693c3c',.65)
SHIRT=mat('Shirt · cotton poplin / procedural weave','#f2f2f6',.60,cloth=True)
SEAM=mat('Shirt · stitched edge','#d1d2dd',.70)
BUTTON=mat('Buttons · warm nacre','#eee9dd',.30)
HAIRS=[]
for h in ['#24191a','#302022','#392629','#453033','#503836']:
    m=mat('Hair · chestnut '+h,h,.44)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Anisotropic'].default_value=.35;p.inputs['Coat Weight'].default_value=.015
    HAIRS.append(m)

def skin_color(x,y,z):
    cheek=max(gauss(x,z,-.53,4.08,.28,.30),gauss(x,z,.53,4.08,.28,.30))*.24
    shade=max(gauss(x,z,-.37,4.34,.30,.10),gauss(x,z,.37,4.34,.30,.10))*.09
    nose=gauss(x,z,0,4.03,.20,.18)*.10
    c=mix(SKIN_BASE,BLUSH,clamp(cheek+nose)); return mix(c,EYEWARM,shade)

def mesh(name,verts,faces,material,colors=None,subdiv=0,export=True):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    if material: me.materials.append(material)
    for p in me.polygons:p.use_smooth=True
    if material==SKIN or colors is not None:
        a=me.color_attributes.new(name='SkinTone' if material==SKIN else 'Color',type='FLOAT_COLOR',domain='POINT')
        cs=colors if colors is not None else [skin_color(*v) for v in verts]
        a.data.foreach_set('color',[c for col in cs for c in col])
    if subdiv:
        m=ob.modifiers.new('Surface refinement','SUBSURF');m.levels=subdiv;m.render_levels=subdiv
    ob['export_web']=export;return ob

def sphere(name,loc,scale,material,segments=48,rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    if material==SKIN:
        a=o.data.color_attributes.new(name='SkinTone',type='FLOAT_COLOR',domain='POINT')
        for v,d in zip(o.data.vertices,a.data):d.color=skin_color(*(v.co+o.location))
    o['export_web']=True;return o

class Tubes:
    def __init__(self,name,material,sides=5,export=True):self.name=name;self.material=material;self.sides=sides;self.v=[];self.f=[];self.export=export
    def add(self,pts,r=.003,taper=True,aspect=1,radii=None):
        pts=[Vector(p) for p in pts]; base=len(self.v); S=self.sides
        for j,p in enumerate(pts):
            t=j/(len(pts)-1); tangent=(pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)]).normalized()
            ref=Vector((0,1,0)); u=tangent.cross(ref)
            if u.length<.05:u=tangent.cross(Vector((1,0,0)))
            u.normalize();v=tangent.cross(u).normalized()
            rad=radii[j] if radii else r*((.70+.30*sin(pi*t))*(1-t**3)**.45 if taper else 1)
            rad=max(.00012,rad)
            for k in range(S):
                a=2*pi*k/S; self.v.append(tuple(p+rad*cos(a)*u+rad*aspect*sin(a)*v))
        for j in range(len(pts)-1):
            for k in range(S):a=base+j*S+k;b=base+j*S+(k+1)%S;self.f.append((a,b,b+S,a+S))
        self.f.append(tuple(base+k for k in reversed(range(S))));end=base+(len(pts)-1)*S;self.f.append(tuple(end+k for k in range(S)))
    def finish(self):
        if not self.v:return None
        return mesh(self.name,self.v,self.f,self.material,export=self.export)

def line(name,pts,r,material,steps=40):
    b=Tubes(name,material,6);b.add(spline(pts,steps),r,False);return b.finish()

def panel(name,grid,material,solid=.015):
    rows=len(grid);cols=len(grid[0]); v=[p for row in grid for p in row];f=[]
    for i in range(rows-1):
        for j in range(cols-1):a=i*cols+j;f.append((a,a+1,a+1+cols,a+cols))
    o=mesh(name,v,f,material)
    if solid:
        m=o.modifiers.new('True cloth thickness','SOLIDIFY');m.thickness=solid
        b=o.modifiers.new('Soft finished edge','BEVEL');b.width=.009;b.segments=2
    return o
