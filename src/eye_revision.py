from common import *
from face import face_y
from anatomy import CX,CZ,RX,HU,HL,opening,eye_y,orbital_y

def eyes():
    lashes=Tubes('Individually tapered eyelashes',LASH,4);folds=Tubes('Upper eyelid crease',mat('Soft eyelid fold','#b78273',.65),5)
    wet=Tubes('Rose waterline',mat('Waterline · peach rose','#bd857b',.35),5);lashroot=Tubes('Upper lash root',LASH,5)
    eyemat=mat('Eyes · analytic vertex-color irises','#ccc4bf',.21)
    p=eyemat.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.07;p.inputs['Specular IOR Level'].default_value=.18;p.inputs['Coat Roughness'].default_value=.16
    a=eyemat.node_tree.nodes.new('ShaderNodeVertexColor');a.layer_name='Color';eyemat.node_tree.links.new(a.outputs['Color'],p.inputs['Base Color'])
    for s in [-1,1]:
        v=[];f=[];cs=[];nx=181;ny=65
        for j in range(ny):
            t=j/(ny-1)
            for i in range(nx):
                u=-1+2*i/(nx-1);x=s*CX+RX*u;arch=sqrt(max(.00001,1-u*u));z=CZ+(-HL+(HL+HU)*t)*arch+s*.018*u
                y=eye_y(x,z,s);r=sqrt((x-s*CX)**2+(z-(CZ+.023))**2);ang=math.atan2(z-(CZ+.023),x-s*CX);q=r/.103
                sclera=mix(rgba('#d4cdc8'),rgba('#cfaaa1'),smooth((abs(u)-.63)/.37)*.22)
                fiber=clamp(.50+.25*sin(103*ang+1.4*sin(q*23))+.13*sin(169*ang+q*9)+.1*sin(49*ang-q*15))
                iris=mix(rgba('#30231d'),rgba('#735038'),fiber*.72)
                iris=mix(iris,rgba('#241b17'),smooth((q-.84)/.16)*.85)
                c=mix(iris,sclera,smooth((r-.101)/.005))
                c=mix(rgba('#100c0a'),c,smooth((r-.039)/.006))
                v.append((x,y,z));cs.append(c)
        for j in range(ny-1):
            for i in range(nx-1):a=j*nx+i;f.append((a,a+1,a+1+nx,a+nx))
        mesh(('Left' if s<0 else 'Right')+' eye · convex continuous iris and sclera',v,f,eyemat,cs)
        for upper in [True,False]:
            points=[]
            for k in range(70):
                a=pi*k/69+(0 if upper else pi);x,z=opening(s,a);points.append((x,eye_y(x,z,s)-.003,z))
            wet.add(points,.0028,False)
            if upper:lashroot.add(points,.0055,False)
        for upper,num in [(True,37),(False,15)]:
            for k in range(num):
                a=.15+(pi-.3)*(k+.3)/num+(0 if upper else pi);x,z=opening(s,a);yy=eye_y(x,z,s)-.005;ln=RNG.uniform(.025,.052)*(1 if upper else .48);dx=cos(a)*.024
                pts=[(x,yy,z),(x+dx*.30,yy-.012,z+(.5 if upper else -.4)*ln),(x+dx,yy-.035,z+(1 if upper else -.7)*ln)]
                lashes.add(spline(pts,7),RNG.uniform(.0011,.0019),True)
        x=s*(CX-RX+.012);z=CZ-.015
        sphere('Small tear caruncle '+str(s),(x,eye_y(x,z,s)-.002,z),(.014,.008,.010),mat('Tear corner '+str(s),'#ad766e',.45),24,16)
    for b in [lashes,folds,wet,lashroot]:b.finish()
