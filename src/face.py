from common import *
WIDTH=[(3.24,.04),(3.31,.20),(3.42,.37),(3.60,.55),(3.85,.70),(4.10,.80),(4.38,.84),(4.65,.85),(4.95,.83),(5.25,.78),(5.52,.64),(5.75,.43),(5.89,.05)]
DEPTH=[(3.24,.14),(3.31,.25),(3.42,.35),(3.60,.46),(3.85,.56),(4.10,.65),(4.38,.68),(4.65,.69),(4.95,.70),(5.25,.70),(5.52,.61),(5.75,.41),(5.89,.04)]

def face_y(x,z):
    w=max(.01,interp(WIDTH,z));d=interp(DEPTH,z); q=clamp(x/w,-.9999,.9999)
    cy=.055+.035*smooth((z-4.4)/1.1)
    y=cy-d*sqrt(max(.001,1-q*q))
    # Brow, orbit, cheek, nose bridge, alae, muzzle and chin are one continuous sculpted surface.
    y-=.042*(gauss(x,z,-.37,4.92,.31,.14)+gauss(x,z,.37,4.92,.31,.14))
    y+=.075*(gauss(x,z,-.37,4.64,.30,.17)+gauss(x,z,.37,4.64,.30,.17))
    y-=.065*(gauss(x,z,-.53,4.23,.26,.32)+gauss(x,z,.53,4.23,.26,.32))
    y-=.088*gauss(x,z,0,4.48,.125,.43)
    y-=.115*gauss(x,z,0,4.20,.105,.28)
    y-=.245*gauss(x,z,0,4.065,.142,.145)
    y-=.094*(gauss(x,z,-.142,4.005,.069,.088)+gauss(x,z,.142,4.005,.069,.088))
    y+=.018*gauss(x,z,0,3.865,.034,.085)
    y-=.090*gauss(x,z,0,3.72,.33,.23)
    y-=.068*gauss(x,z,0,3.38,.26,.13)
    return y

def opening(s,a,expand=0):
    rx=.255+expand; u=cos(a); h=(.112 if sin(a)>=0 else .083)+expand*.68
    x=s*.365+rx*u;z=4.64+h*sin(a)+s*.025*u
    return x,z

def eye_y(x,z,s):
    dx=x-s*.365;dz=z-4.64
    return min(-.43-sqrt(max(.011,.282**2-dx*dx-dz*dz)),face_y(x,z)-.009)

def is_eye(x,z):
    for s in [-1,1]:
        dx=(x-s*.365)/.255;dz=z-4.64-s*.025*dx;h=.112 if dz>0 else .083
        if dx*dx+(dz/h)**2<1.03:return True
    return False

def head():
    v=[];f=[];N=288;M=215
    for j in range(M):
        z=3.245+(5.885-3.245)*j/(M-1);w=interp(WIDTH,z);d=interp(DEPTH,z)
        for i in range(N):
            t=2*pi*i/N;x=w*sin(t);y=face_y(x,z) if cos(t)>=0 else .06-d*cos(t)
            v.append((x,y,z))
    for j in range(M-1):
        for i in range(N):
            a=j*N+i;b=j*N+(i+1)%N;inds=(a,b,b+N,a+N);cx=sum(v[q][0] for q in inds)/4;cz=sum(v[q][2] for q in inds)/4
            if cos(2*pi*(i+.5)/N)>0 and is_eye(cx,cz):continue
            f.append(inds)
    f.extend([tuple(reversed(range(N))),tuple((M-1)*N+i for i in range(N))])
    mesh('Face · continuous original facial topology',v,f,SKIN)

def eyes():
    lashes=Tubes('Individually tapered eyelashes',LASH,4)
    folds=Tubes('Upper eyelid crease',CREASE,5)
    wet=Tubes('Rose waterline',mat('Waterline · peach rose','#c38b7e',.32),5)
    lashroot=Tubes('Upper lash root',LASH,5)
    for s in [-1,1]:
        # An actual convex almond mesh, not a flat eye decal.
        v=[];f=[];nr=20;nt=128
        for j in range(nr+1):
            rr=j/nr
            for i in range(nt):
                a=i*2*pi/nt;ex,ez=opening(s,a);x=s*.365+(ex-s*.365)*rr;z=4.64+(ez-4.64)*rr
                v.append((x,eye_y(x,z,s),z))
        for j in range(nr):
            for i in range(nt):a=j*nt+i;b=j*nt+(i+1)%nt;f.append((a,b,b+nt,a+nt))
        mesh(('Left' if s<0 else 'Right')+' · convex sclera',v,f,SCLERA)
        # Eyelid skin is blended into the face along a broad smooth ring.
        v=[];f=[];colors=[];nr=12
        for j in range(nr+1):
            t=j/nr;blend=smooth(t)
            for i in range(nt):
                a=2*pi*i/nt;ix,iz=opening(s,a);ox,oz=opening(s,a,.092)
                x=ix*(1-t)+ox*t;z=iz*(1-t)+oz*t
                y=eye_y(ix,iz,s)*(1-blend)+face_y(x,z)*blend-.014*sin(pi*t)-.003
                v.append((x,y,z));colors.append(mix(skin_color(x,y,z),rgba('#cf9a87'),.18*(1-t)**3))
        for j in range(nr):
            for i in range(nt):a=j*nt+i;b=j*nt+(i+1)%nt;f.append((a,b,b+nt,a+nt))
        mesh(('Left' if s<0 else 'Right')+' · sculpted eyelids',v,f,SKIN,colors)
        for upper in [True,False]:
            points=[]
            for k in range(65):
                a=(pi*k/64) if upper else pi+pi*k/64;x,z=opening(s,a)
                points.append((x,eye_y(x,z,s)-.004,z))
            wet.add(points,.0032,False)
            if upper:lashroot.add(points,.004,False)
        cp=[]
        for k in range(45):
            a=.2+(pi-.4)*k/44;x,z=opening(s,a,.039)
            cp.append((x,face_y(x,z)-.013,z+.014))
        folds.add(cp,.0025,True)
        for upper,num in [(True,36),(False,16)]:
            for k in range(num):
                a=(.13+(pi-.26)*(k+.3)/num)+(0 if upper else pi);x,z=opening(s,a)
                yy=eye_y(x,z,s)-.006;ln=RNG.uniform(.026,.064)*(1 if upper else .56);dx=cos(a)*.025
                pts=[(x,yy,z),(x+dx*.30,yy-.010,z+(.5 if upper else -.4)*ln),(x+dx,yy-.040,z+(1 if upper else -.7)*ln)]
                lashes.add(spline(pts,7),RNG.uniform(.0012,.0022),True)
        # Radial, colored iris fibers; all colors are analytically generated.
        irismat=mat(('Left' if s<0 else 'Right')+' iris · brown radial fibers','#614234',.22)
        n=irismat.node_tree.nodes;l=irismat.node_tree.links;p=n.get('Principled BSDF');attr=n.new('ShaderNodeVertexColor');attr.layer_name='Color';l.new(attr.outputs['Color'],p.inputs['Base Color']);p.inputs['Coat Weight'].default_value=.7;p.inputs['Coat Roughness'].default_value=.11
        v=[];f=[];cs=[];rings=22;segs=192;cx=s*.365;cz=4.648;rad=.100
        for j in range(rings+1):
            rr=j/rings;r=rad*rr
            for k in range(segs):
                a=2*pi*k/segs;x=cx+r*cos(a);z=cz+r*sin(a);y=eye_y(x,z,s)-.004
                fibers=.5+.28*sin(83*a+1.3*sin(rr*18))+.14*sin(157*a+rr*6)+.08*cos(43*a-rr*12)
                c=mix(rgba('#34251e'),rgba('#936a47'),clamp(fibers)*.75)
                if rr>.84:c=mix(c,rgba('#261c1b'),smooth((rr-.84)/.16)*.9)
                if rr<.47:c=mix(c,rgba('#3b2519'),.35)
                v.append((x,y,z));cs.append(c)
        for j in range(rings):
            for k in range(segs):a=j*segs+k;b=j*segs+(k+1)%segs;f.append((a,b,b+segs,a+segs))
        mesh(('Left' if s<0 else 'Right')+' iris · geometric radial filaments',v,f,irismat,cs)
        v=[(cx,eye_y(cx,cz,s)-.007,cz)];f=[]
        for k in range(96):
            a=2*pi*k/96;x=cx+.041*cos(a);z=cz+.041*sin(a);v.append((x,eye_y(x,z,s)-.007,z))
        for k in range(96):f.append((0,k+1,(k+1)%96+1))
        mesh(('Left' if s<0 else 'Right')+' pupil',v,f,PUPIL)
        sphere('Lacrimal caruncle', (s*.117,face_y(s*.117,4.616)-.013,4.616),(.023,.012,.015),mat('Tear corner '+str(s),'#bc8478',.4))
    for b in [lashes,folds,wet,lashroot]:b.finish()

def nose_mouth():
    # Subtle nostril openings sit below the integrated nasal wings.
    nost=Tubes('Nostril openings · small inset curves',mat('Nostril warm shadow','#7c4e41',.8),6)
    for s in [-1,1]:
        pts=[]
        for i in range(26):
            t=pi*.05+pi*.86*i/25;x=s*(.107+.041*cos(t));z=3.993+.014*sin(t)
            pts.append((x,face_y(x,z)-.004,z))
        nost.add(pts,.0058,True)
    nost.finish()
    # Two smoothly cambered lip surfaces, feathered into the surrounding skin.
    def seam(x):return 3.699+.004*cos(x/.27*pi)-.012*exp(-(x/.085)**2)
    for upper in [True,False]:
        v=[];f=[];colors=[];nx=101;ny=13
        for j in range(ny):
            t=j/(ny-1)
            for i in range(nx):
                x=-.27+.54*i/(nx-1);q=x/.27;fade=max(0,1-q*q)**.7;mid=seam(x)
                if upper:
                    thick=(.063+.026*exp(-((abs(x)-.072)/.055)**2)-.009*exp(-(x/.030)**2))*fade
                    z=mid+t*thick
                else:z=mid-t*.090*fade
                y=face_y(x,z)-.004-(.019+.024*sin(pi*t))*fade*(1-t*.6)
                v.append((x,y,z));lipc=mix(rgba('#ae6569') if upper else rgba('#ce8988'),skin_color(x,y,z),smooth((t-.66)/.34)*.75)
                colors.append(lipc)
        for j in range(ny-1):
            for i in range(nx-1):a=j*nx+i;f.append((a,a+1,a+1+nx,a+nx))
        lipmat=LIP.copy();lipmat.name='Upper lip vermilion' if upper else 'Lower lip vermilion';n=lipmat.node_tree.nodes;attr=n.new('ShaderNodeVertexColor');attr.layer_name='Color';lipmat.node_tree.links.new(attr.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
        mesh('Upper sculpted lip' if upper else 'Lower sculpted lip',v,f,lipmat,colors)
    pts=[]
    for i in range(80):
        x=-.27+.54*i/79;z=seam(x);pts.append((x,face_y(x,z)-.026*max(0,1-(x/.27)**2)-.004,z))
    b=Tubes('Relaxed mouth line',MOUTH,6);b.add(pts,.0037,True);b.finish()

def eyebrows():
    hairs=Tubes('Eyebrows · individual swept hairs',LASH,4)
    for s in [-1,1]:
        for k in range(190):
            t=RNG.random();x=s*(.16+.51*t);z=4.932+.057*sin(pi*t)-.035*t+RNG.uniform(-.022,.018)*(1-t*.65)
            length=RNG.uniform(.022,.055)*(1-t*.4);pts=[]
            for j in range(6):
                a=j/5;xx=x+s*(.018+.025*t)*a;zz=z+length*sin(a*pi*.63)
                pts.append((xx,face_y(xx,zz)-.010,zz))
            hairs.add(pts,RNG.uniform(.0011,.002),True)
    hairs.finish()

def ears():
    for s in [-1,1]:
        sphere('Auricle base '+str(s),(s*.837,.01,4.36),(.175,.145,.329),SKIN)
        sphere('Concha recessed bowl '+str(s),(s*.92,-.116,4.38),(.067,.018,.151),mat('Ear inner warm '+str(s),'#bd8273',.58))
        p=[(s*.852,-.092,4.06),(s*.967,-.083,4.15),(s*1.01,-.051,4.37),(s*.977,-.015,4.59),(s*.891,-.028,4.66),(s*.840,-.108,4.57)]
        line('Rolled helix '+str(s),p,.030,SKIN)
        p=[(s*.885,-.137,4.14),(s*.945,-.143,4.29),(s*.917,-.146,4.44),(s*.932,-.121,4.54)]
        line('Antihelix '+str(s),p,.018,SKIN)
        sphere('Tragus '+str(s),(s*.839,-.153,4.31),(.043,.039,.065),SKIN)

def make_face():
    head();eyes();nose_mouth();eyebrows();ears()
    print('FACE complete',flush=True)
