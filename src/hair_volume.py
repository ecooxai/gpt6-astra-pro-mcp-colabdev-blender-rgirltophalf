"""Continuous rear hair surface and its matching fiber guides, all original geometry."""
from common import *

def back_point(u,t):
    tt=clamp(t)
    z=interp([(0,5.62),(.12,5.20),(.30,4.34),(.52,3.2),(.73,2.03),(.90,.96),(1,.42)],tt)
    rx=interp([(0,.675),(.12,.94),(.30,1.03),(.52,1.08),(.73,1.13),(.90,1.13),(1,1.015)],tt)
    ry=interp([(0,.585),(.12,.80),(.30,.85),(.52,.77),(.73,.71),(.90,.68),(1,.67)],tt)
    edge=1.16+(pi/2-1.16)*smooth((tt-.30)/.32)
    a=edge+(2*pi-2*edge)*u
    wave=.013*sin(7*a+2.2*z)+.007*sin(19*a-z*2.4)
    x=(rx+wave)*sin(a)+.018*sin(z*2.7+a*4)*sin(pi*tt)
    y=.14-(ry+wave)*cos(a)
    z+=smooth((tt-.82)/.18)*(.19*abs(sin(a))**1.6+.023*sin(43*a)+.013*sin(91*a))
    if t>1:z-=(t-1)*2.0
    return Vector((x,y,z)),a

def back_shell():
    N=201;M=105;v=[];f=[]
    for j in range(M):
        for i in range(N):v.append(tuple(back_point(i/(N-1),j/(M-1))[0]))
    for j in range(M-1):
        for i in range(N-1):a=j*N+i;f.append((a+N,a+N+1,a+1,a))
    o=mesh('Rear hair · continuous softly waved underlayer',v,f,mat('Hair · rear matte density','#261c1e',.64))
    sol=o.modifiers.new('Hair volume thickness','SOLIDIFY');sol.thickness=.012
    return o

def back_fibers(studio):
    for k in range(4500):
        u0=(k+.5)/4500;phase=RNG.random()*2*pi;last=RNG.uniform(.985,1.07);pts=[]
        for j in range(49):
            t=last*j/48;u=clamp(u0+.009*sin(7*t+phase)*sin(pi*min(t,1)))
            p,a=back_point(u,t)
            p+=Vector((sin(a),-cos(a),0))*(.006+RNG.uniform(0,.0015))
            if p.z>5.0:
                target=max(.001,1.007**2-((p.z-4.8)/1.283)**2)
                current=(p.x/.956)**2+((p.y-.12)/.827)**2
                if current<target:
                    scale=sqrt(target/max(.001,current));p.x*=scale;p.y=.12+(p.y-.12)*scale
            pts.append(p)
        studio.strand(pts,RNG.uniform(.00095,.0015),RNG.choices(range(5),[19,43,27,10,1])[0],k%6==0,True)
