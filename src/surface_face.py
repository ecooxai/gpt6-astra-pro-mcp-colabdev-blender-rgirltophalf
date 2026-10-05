"""Constrained, continuous facial topology with exact eye holes and integrated lips."""
from common import *
from face import WIDTH,DEPTH,center_y
from anatomy import *
from mathutils.geometry import delaunay_2d_cdt

def in_eye(x,z):
    return any(eye_coord(x,z,s)[0]<.9999 for s in [-1,1])

def head():
    points=[];edges=[];NZ=221;NT=211;zmin=3.325;zmax=5.885
    def add(t,z):points.append(Vector((t,z)));return len(points)-1
    # Exact outer hemisphere seam.
    outer=[]
    for j in range(NZ):outer.append(add(-pi/2,zmin+(zmax-zmin)*j/(NZ-1)))
    for i in range(1,NT):outer.append(add(-pi/2+pi*i/(NT-1),zmax))
    for j in range(NZ-2,-1,-1):outer.append(add(pi/2,zmin+(zmax-zmin)*j/(NZ-1)))
    for i in range(NT-2,0,-1):outer.append(add(-pi/2+pi*i/(NT-1),zmin))
    edges.extend((outer[i],outer[(i+1)%len(outer)]) for i in range(len(outer)))
    for j in range(1,NZ-1):
        z=zmin+(zmax-zmin)*j/(NZ-1);w=interp(WIDTH,z)
        for i in range(1,NT-1):
            th=-pi/2+pi*i/(NT-1);x=w*sin(th)
            if any(eye_coord(x,z,s)[2]<.151 for s in [-1,1]):continue
            add(th,z)
    # Dense, explicitly constrained loops give the lids and the face shared vertices.
    for s in [-1,1]:
        for j in range(20):
            dist=.154*j/19;ring=[]
            for k in range(144):
                x,z=opening(s,2*pi*k/144,dist);th=math.asin(clamp(x/interp(WIDTH,z),-1,1));ring.append(add(th,z))
            edges.extend((ring[k],ring[(k+1)%144]) for k in range(144))
    # Higher sampling around the nasal alae and vermilion border.
    for j in range(95):
        z=3.59+.64*j/94;w=interp(WIDTH,z)
        for i in range(79):
            x=-.335+.67*i/78;add(math.asin(clamp(x/w,-.999,.999)),z)
    uv,ed,tri,*_=delaunay_2d_cdt(points,edges,[],0,.00002,False)
    v=[];colors=[];mask=[]
    for th,z in uv:
        x=interp(WIDTH,z)*sin(th);y=front_y(x,z);v.append((x,y,z));colors.append(face_color(x,y,z));mask.append(mouth_info(x,z)[1])
    f=[]
    for face in tri:
        x=sum(v[i][0] for i in face)/len(face);z=sum(v[i][2] for i in face)/len(face)
        if not in_eye(x,z):f.append(tuple(face))
    # Back hemisphere meets the same outline, preserving genuine side/back anatomy.
    start=len(v);NB=145
    for j in range(NZ):
        z=zmin+(zmax-zmin)*j/(NZ-1);w=interp(WIDTH,z);d=interp(DEPTH,z);cy=center_y(z)
        for i in range(NB):
            a=pi/2+pi*i/(NB-1);x=w*sin(a);y=cy-d*cos(a);v.append((x,y,z));colors.append(skin_color(x,y,z));mask.append(0)
    for j in range(NZ-1):
        for i in range(NB-1):a=start+j*NB+i;f.append((a,a+1,a+1+NB,a+NB))
    ob=mesh('Face · unified eyes, nose and lips',v,f,SKIN,colors)
    attr=ob.data.color_attributes.new(name='LipMask',type='FLOAT_COLOR',domain='POINT')
    attr.data.foreach_set('color',[c for val in mask for c in (val,val,val,1)])
    # Weld only coincident front/back outline vertices, never the eye holes.
    import bmesh
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00015);
    for level in [zmin,zmax]:
        boundary=[e for e in bm.edges if e.is_boundary and all(abs(q.co.z-level)<.0002 for q in e.verts)]
        if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    for poly in ob.data.polygons:poly.use_smooth=True
    print('UNIFIED FACE',len(ob.data.vertices),'vertices',len(ob.data.polygons),'faces',flush=True)

def details():
    # The closed lip contact is a sub-millimeter dark curve over the unified surface.
    b=Tubes('Natural closed mouth contact',mat('Lip contact · rose brown','#86534f',.7),5)
    pts=[]
    for k in range(100):
        x=-.267+.534*k/99;q=x/.274;z=3.747+.003*cos(q*pi)-.005*exp(-(x/.075)**2)
        pts.append((x,front_y(x,z)-.0018,z))
    b.add(pts,.0023,True);b.finish()
