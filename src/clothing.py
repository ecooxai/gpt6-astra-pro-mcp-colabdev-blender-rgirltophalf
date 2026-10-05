from common import *

def neck():
    v=[];f=[];N=96;M=50
    for j in range(M):
        t=j/(M-1);z=2.16+1.44*t
        w=interp([(2.16,.56),(2.55,.43),(3.05,.32),(3.38,.34),(3.6,.40)],z)
        d=interp([(2.16,.36),(2.55,.35),(3.05,.31),(3.38,.29),(3.6,.34)],z)
        for i in range(N):
            a=2*pi*i/N;x=w*sin(a);y=.10-d*cos(a)
            if cos(a)>0:y-=.013*(exp(-((x-.19)/.05)**2)+exp(-((x+.19)/.05)**2))*sin(pi*t)
            v.append((x,y,z))
    for j in range(M-1):
        for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
    mesh('Neck · tapered continuous surface',v,f,SKIN)

W=[(.03,1.36),(.6,1.34),(1.25,1.38),(1.85,1.42),(2.20,1.40),(2.38,1.36),(2.55,1.03),(2.74,.59),(2.94,.405)]
D=[(.03,.68),(.7,.68),(1.4,.73),(1.95,.70),(2.25,.57),(2.55,.46),(2.74,.37),(2.94,.325)]
def cloth_y(x,z):
    w=interp(W,z);d=interp(D,z);y=.06-d*sqrt(max(.02,1-(x/w)**2))
    folds=.013*sin(17*x+3.0*z)+.012*sin(24*z+8*x)*exp(-((abs(x)-.36)/.24)**2)
    return y+folds

def shirt():
    v=[];f=[];N=160;M=115
    for j in range(M):
        basez=.03+2.91*j/(M-1);w=interp(W,basez);d=interp(D,basez)
        for i in range(N):
            a=2*pi*i/N;c=cos(a);x=w*sin(a);y=.06-d*c
            z=basez-.71*(max(0,c)**3)*smooth((basez-2.24)/.7)
            wave=.012*sin(18*x+3*z)+.014*sin(24*z+8*x)*exp(-((abs(x)-.36)/.24)**2)
            if c>0:y+=wave*c
            else:y+=.010*sin(14*x+1.3*z)*(-c)
            y-=.016*sin(28*z-14*abs(x))*exp(-((z-1.80)/.24)**2)*max(0,c)
            v.append((x,y,z))
    for j in range(M-1):
        for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
    f.append(tuple(reversed(range(N))))
    o=mesh('Shirt · tailored torso with open neckline',v,f,SHIRT)
    sol=o.modifiers.new('Poplin thickness','SOLIDIFY');sol.thickness=.012
    for s in [-1,1]:
        pts=spline([(s*1.19,.065,2.34),(s*1.48,.055,2.15),(s*1.66,.04,1.60),(s*1.72,.015,.85),(s*1.72,.01,.03)],64)
        v=[];f=[];N=72
        for j,p in enumerate(pts):
            t=j/(len(pts)-1);r=.37+.09*sin(pi*t*.87);tangent=(pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)]).normalized();u=tangent.cross(Vector((0,1,0))).normalized();vv=tangent.cross(u).normalized()
            for i in range(N):
                a=2*pi*i/N;wrinkle=.014*sin(36*t+3*cos(a))+.007*sin(70*t+2*sin(a));rr=r+wrinkle
                v.append(tuple(p+u*cos(a)*rr+vv*sin(a)*rr*.90))
        for j in range(len(pts)-1):
            for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
        f.extend([tuple(reversed(range(N))),tuple((len(pts)-1)*N+i for i in range(N))])
        mesh('Cotton sleeve '+str(s),v,f,SHIRT)
        line('Shoulder seam '+str(s),[(s*.62,.05,2.73),(s*.98,-.13,2.56),(s*1.25,-.30,2.33),(s*1.43,-.34,2.07)],.004,SEAM)
        line('Sleeve outer seam '+str(s),[(s*1.71,-.19,1.95),(s*1.95,-.23,1.27),(s*2.04,-.22,.38),(s*2.02,-.19,.05)],.0038,SEAM)
    grid=[]
    for j in range(7):
        t=j/6;row=[]
        for i in range(90):
            a=.60+(2*pi-1.2)*i/89;x=(.42+.027*t)*sin(a);y=.10-(.355+.025*t)*cos(a);z=2.76+.21*t
            row.append((x,y,z))
        grid.append(row)
    panel('Standing collar band',grid,SHIRT,.012)
    for s in [-1,1]:
        A=Vector((s*.39,-.265,2.98));B=Vector((s*.68,-.395,2.71));C=Vector((s*.66,-.695,2.16));E=Vector((s*.105,-.575,2.235))
        grid=[]
        for j in range(28):
            v=j/27;row=[]
            for i in range(28):
                u=i/27;p=(1-v)*((1-u)*A+u*B)+v*((1-u)*E+u*C)
                p.y-=.065*sin(pi*u)*sin(pi*v);p.z+=.035*sin(pi*u)*sin(pi*v)
                row.append(tuple(p))
            grid.append(row)
        panel('Folded pointed collar '+str(s),grid,SHIRT,.016)
        for label,points in [('outer',[tuple(B),tuple(C)]),('edge',[tuple(C),tuple(E)])]:
            a,b=[Vector(p) for p in points];line('Collar topstitch '+label+str(s),[tuple(a*.98+b*.02+Vector((0,-.012,0))),tuple(a*.5+b*.5+Vector((0,-.012,0))),tuple(a*.02+b*.98+Vector((0,-.012,0)))],.0028,SEAM,24)
    grid=[]
    for j in range(90):
        z=.035+2.19*j/89;xc=.035+.055*cos(z*1.45);row=[]
        for i in range(9):
            u=i/8;x=xc+(u-.5)*.155;y=cloth_y(x,z)-.019-.006*sin(pi*u);row.append((x,y,z))
        grid.append(row)
    panel('Raised curved button placket',grid,SHIRT,.010)
    for s in [-1,1]:
        pts=[]
        for i in range(80):
            z=.045+2.12*i/79;x=.035+.055*cos(z*1.45)+s*.064;pts.append((x,cloth_y(x,z)-.03,z))
        line('Placket stitch '+str(s),pts,.0025,SEAM,80)
    for z in [.40,1.07,1.74]:
        x=.035+.055*cos(z*1.45);make_button(x,cloth_y(x,z)-.047,z,.045)
    make_button(.337,-.483,2.615,.039)

def make_button(x,y,z,r):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=.018,location=(x,y,z),rotation=(pi/2,0,0))
    ob=bpy.context.object;ob.name='Nacre shirt button';ob.data.materials.append(BUTTON);ob['export_web']=True
    mod=ob.modifiers.new('Rounded button rim','BEVEL');mod.width=.009;mod.segments=3
    for p in ob.data.polygons:p.use_smooth=True
    dark=mat('Button hole shadow','#9e9b95',.7)
    for dx in [-.011,.011]:
        for dz in [-.011,.011]:sphere('Recessed sewing hole',(x+dx,y-.012,z+dz),(.006,.003,.006),dark,16,8)
    line('Cotton button thread',[(x-.011,y-.016,z-.011),(x,y-.019,z),(x+.011,y-.016,z+.011)],.003,SHIRT,12)
    line('Cotton button thread',[(x+.011,y-.016,z-.011),(x,y-.020,z),(x-.011,y-.016,z+.011)],.003,SHIRT,12)

def make_clothing():
    neck();shirt();print('CLOTHING complete',flush=True)
