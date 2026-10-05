"""Original continuous rear hair volume, under independent fine filaments."""
from common import *

def back_shell():
    N=201;M=105;v=[];f=[]
    for j in range(M):
        t=j/(M-1)
        zbase=interp([(0,5.62),(.12,5.20),(.30,4.34),(.52,3.2),(.73,2.03),(.90,.96),(1,.42)],t)
        rx=interp([(0,.77),(.12,.94),(.30,1.03),(.52,1.08),(.73,1.13),(.90,1.13),(1,1.015)],t)
        ry=interp([(0,.67),(.12,.80),(.30,.85),(.52,.77),(.73,.71),(.90,.68),(1,.67)],t)
        for i in range(N):
            a=1.16+(2*pi-2.32)*i/(N-1)
            wave=.013*sin(7*a+2.2*zbase)+.007*sin(19*a-zbase*2.4)
            x=(rx+wave)*sin(a)+.018*sin(zbase*2.7+a*4)*sin(pi*t)
            y=.14-(ry+wave)*cos(a)
            z=zbase+smooth((t-.82)/.18)*(.19*abs(sin(a))**1.6+.023*sin(43*a)+.013*sin(91*a))
            v.append((x,y,z))
    for j in range(M-1):
        for i in range(N-1):a=j*N+i;f.append((a+N,a+N+1,a+1,a))
    m=mat('Hair · continuous rear underlayer','#281c1e',.55)
    o=mesh('Rear hair · continuous softly waved underlayer',v,f,m)
    sol=o.modifiers.new('Hair volume thickness','SOLIDIFY');sol.thickness=.018
    return o
