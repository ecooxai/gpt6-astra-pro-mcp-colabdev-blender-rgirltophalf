"""Parted chestnut hairstyle built from original clumps and thousands of filaments."""
from common import *

class HairStudio:
    def __init__(self):
        self.base=[]
        for i,m in enumerate(HAIRS[:3]):
            under=m.copy();under.name='Hair underlayer '+str(i);bs=under.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.62;bs.inputs['Specular IOR Level'].default_value=.12;bs.inputs['Anisotropic'].default_value=0;bs.inputs['Coat Weight'].default_value=0
            self.base.append(Tubes('Hair volume · layer '+str(i),under,10))
        self.fine=[Tubes('Fine hair · render layer '+str(i),m,3,False) for i,m in enumerate(HAIRS)]
        self.web=[Tubes('Hair filaments · web layer '+str(i),m,3,True) for i,m in enumerate(HAIRS)]
        self.rear_fine=[Tubes('Back hair fibers · render '+str(i),m,3,False) for i,m in enumerate(HAIRS)]
        self.rear_web=[Tubes('Back hair fibers · web '+str(i),m,3,True) for i,m in enumerate(HAIRS)]
        self.count=0;self.locks=0
    def strand(self,pts,r=.0014,index=1,web=False,back=False):
        b=(self.rear_web[index] if web else self.rear_fine[index]) if back else (self.web[index] if web else self.fine[index]);b.add(pts,r,True);self.count+=1
    def lock(self,controls,width=.075,depth=.04,num=95,layer=1,solid=True):
        pts=spline(controls,56);rr=[]
        for j in range(len(pts)):
            t=j/(len(pts)-1);rr.append(width*(.47+.53*sin(pi*min(t*2,1)/2))*(1-.985*smooth((t-.68)/.32)))
        if solid:self.base[layer%3].add(pts,width,False,depth/width,radii=rr)
        self.locks+=1
        for k in range(num):
            angle=2*pi*(k+.25)/num+RNG.uniform(-.06,.06);phase=RNG.random()*2*pi
            c=cos(angle);d=sin(angle);out=[];last=RNG.uniform(.90,1)
            for j in range(39):
                t=last*j/38;f=t*(len(pts)-1);a=min(int(f),len(pts)-2);q=f-a;p=pts[a].lerp(pts[a+1],q)
                tangent=(pts[min(a+2,len(pts)-1)]-pts[max(0,a-1)]).normalized();u=tangent.cross(Vector((0,1,0)))
                if u.length<.05:u=tangent.cross(Vector((1,0,0)))
                u.normalize();v=tangent.cross(u).normalized();rad=rr[a]*(1-q)+rr[a+1]*q
                wave=.004*sin(t*18+phase)*sin(pi*t)+.0015*sin(t*41+phase*.7)
                p+=u*(rad*c+wave)+v*((rad*depth/width+.0022)*d+.001*sin(t*25+phase))
                if not solid and p.y<-.38 and 3.50<p.z<5.80:
                    from face import WIDTH
                    from anatomy import front_y
                    ratio=abs(p.x)/interp(WIDTH,p.z)
                    contact=(1-smooth((ratio-.82)/.14))*smooth((5.8-p.z)/.5)*smooth((p.z-3.5)/.25)
                    p.y=p.y*(1-contact)+(front_y(p.x,p.z)-.045-.006*sin(pi*t))*contact
                out.append(p)
            color=RNG.choices(range(5),[17,42,29,10,2])[0]
            self.strand(out,RNG.uniform(.00095,.0017),color,k%5==0)
    def finish(self):
        for b in self.base+self.fine+self.web+self.rear_fine+self.rear_web:b.finish()
        print('HAIR',self.locks,'clumps',self.count,'original strands',flush=True)

def make_hair():
    H=HairStudio();v=[];f=[];N=180;M=70
    for j in range(M):
        for i in range(N):
            th=2*pi*i/N;end=1.083+1.39*((1-cos(th))/2)**.67+.007*sin(th*27);ph=.006+(end-.006)*j/(M-1)
            v.append((.947*sin(ph)*sin(th),.12-.817*sin(ph)*cos(th),4.80+1.274*cos(ph)))
    for j in range(M-1):
        for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
    scalpmat=mat('Hair scalp · matte root density','#251b1d',.69)
    mesh('Hair scalp · asymmetrical forehead opening',v,[tuple(reversed(q)) for q in f],scalpmat)
    from hair_volume import back_shell,back_fibers
    back_shell();back_fibers(H)
    for k in range(12):
        t=k/11;dx=(t-.5)*.45;dep=(t-.5)*.115
        pts=[(.12-.14*t,-.01+.40*t,6.025-.06*t),(-.30-.08*t,-.43+.33*t,5.92-.04*t),(-.69-.09*t,-.58+.30*t,5.48),(-.90+dx*.23,-.24+.14*t,4.91),(-.946+dx*.30,.075+dep,4.38),(-.90+dx*.50,-.02+dep,3.66),(-.98+dx,-.38+dep,2.91),(-1.07+dx,-.64+dep,2.12),(-1.50+dx,-.72+dep,1.40),(-1.56+dx,-.66+dep,.92),(-1.31+dx,-.66+dep,.52),(-.95+dx*.55,-.65+dep,.25+.22*t)]
        pts=[(x+.035*sin(j*1.5+k*.85)*j/10,y+.02*sin(j+k*.7),z+(.13*sin(k*.8) if j>7 else 0)) for j,(x,y,z) in enumerate(pts)]
        H.lock(pts,.084,.030,135,k%3)
    for k in range(16):
        t=k/15;dx=(t-.5)*.45;dep=(t-.5)*.15
        pts=[(.15+.10*t,.045+.35*t,6.035-.035*t),(.54+.07*t,-.35+.28*t,5.86),(.84+dx*.35,-.40+dep,5.38),(1.00+dx*.38,-.26+dep,4.81),(.96+dx*.40,-.40+dep,4.08),(.88+dx*.72,-.59+dep,3.36),(.98+dx,-.71+dep,2.60),(1.24+dx,-.79+dep,2.00),(1.57+dx,-.72+dep,1.34),(1.49+dx,-.67+dep,.80),(1.17+dx*.70,-.66+dep,.48),(.80+dx*.55,-.66+dep,.24+.20*t)]
        pts=[(x+.048*sin(j*1.5+k*.65)*j/10,y+.025*sin(j*.8+k*.7),z+(.14*sin(k*.8) if j>7 else 0)) for j,(x,y,z) in enumerate(pts)]
        H.lock(pts,.09,.030,140,k%3)
    H.lock([(.10,-.12,6.03),(-.11,-.61,5.63),(-.42,-.745,5.17),(-.63,-.73,4.62),(-.70,-.63,4.12),(-.75,-.47,3.64),(-.62,-.39,3.20)],.026,.012,95,1,False)
    H.lock([(.14,-.15,6.035),(-.055,-.60,5.62),(-.27,-.75,5.20),(-.39,-.78,4.84)],.023,.009,65,1,False)
    for k in range(6):
        t=k/5;rootx=.16+.055*t
        H.lock([(rootx,-.085,6.043),(.22+.025*t,-.58,5.65),(.19+.045*t,-.75,5.22),(.095+.062*t,-.797,4.68+.14*t)],.020+.004*sin(t*pi),.006,29,1,False)
    for s in [-1,1]:
        for k in range(660):
            y0=RNG.uniform(-.47,.64);x0=.142+RNG.uniform(-.008,.008)
            z0=4.80+1.282*sqrt(max(.02,1-(x0/.956)**2-((y0-.12)/.823)**2))
            start=Vector((x0/.956,(y0-.12)/.823,(z0-4.80)/1.282)).normalized()
            a=s*(1.15+1.15*smooth((y0+.47)/1.11));ph=1.12+.44*RNG.random()
            end=Vector((sin(ph)*sin(a),-sin(ph)*cos(a),cos(ph))).normalized();angle=start.angle(end);pts=[]
            for j in range(39):
                t=j/38;q=(start*sin((1-t)*angle)+end*sin(t*angle))/max(.001,sin(angle))
                q.normalize();off=.004+RNG.uniform(0,.001)
                pts.append((q.x*(.956+off),.12+q.y*(.825+off),4.8+q.z*(1.281+off)))
            H.strand(pts,RNG.uniform(.001,.0017),RNG.choices(range(5),[15,42,30,11,2])[0],k%6==0)
    # Fine leading-edge fibers fully cover the previously exposed forehead cap.
    for side in [-1,1]:
        for k in range(1200):
            theta=side*(.015+1.86*(k+.35)/1200)
            phend=1.10+1.39*((1-cos(theta))/2)**.67
            y0=-.48+.82*(abs(theta)/1.88)**1.25+RNG.uniform(-.045,.045)
            x0=.141+RNG.uniform(-.014,.014)
            z0=4.8+1.282*sqrt(max(.01,1-(x0/.956)**2-((y0-.12)/.826)**2))
            start=Vector((x0/.956,(y0-.12)/.826,(z0-4.8)/1.282)).normalized()
            end=Vector((sin(phend)*sin(theta),-sin(phend)*cos(theta),cos(phend))).normalized()
            ang=start.angle(end);pts=[]
            for j in range(42):
                t=j/41;q=(start*sin((1-t)*ang)+end*sin(t*ang))/max(.001,sin(ang));q.normalize()
                off=.007+.002*sin(pi*t)+RNG.uniform(0,.001)
                pts.append((q.x*(.954+off),.12+q.y*(.824+off),4.8+q.z*(1.280+off)))
            H.strand(pts,RNG.uniform(.0010,.0016),RNG.choices(range(5),[17,43,28,10,2])[0],k%5==0)
    for s in [-1,1]:
        for k in range(65):
            t=RNG.random();rootz=5.0+.8*t;x=s*(.84+.09*(1-t));yy=RNG.uniform(-.4,.3);length=RNG.uniform(.3,1.3)
            pts=spline([(x,yy,rootz),(x+s*.075,yy-.03,rootz-.25),(x+s*.08,yy-.02,rootz-length*.65),(x+s*.03,yy+.02,rootz-length)],30)
            H.strand(pts,.00085,2,False)
    part=[]
    for k in range(35):
        y=-.39+.88*k/34;x=.14;z=4.8+1.272*sqrt(max(.02,1-(x/.947)**2-((y-.12)/.817)**2));part.append((x,y,z+.002))
    line('Fine visible side part',part,.005,mat('Scalp part · muted warm','#85665a',.62),35)
    H.finish()
