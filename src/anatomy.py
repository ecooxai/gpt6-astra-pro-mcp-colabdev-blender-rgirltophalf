"""Shared analytical anatomy for a continuous face and inset eyes."""
from common import *
from face import face_y as base_y
CX=.355;CZ=4.50;RX=.222;HU=.113;HL=.073

def opening(s,a,expand=0):
    c=cos(a);sn=sin(a);h=HU if sn>=0 else HL
    ray=sqrt((RX*c)**2+(h*sn+s*.018*c)**2)
    r=1+expand/max(.001,ray)
    return s*CX+RX*r*c,CZ+h*r*sn+s*.018*r*c

def eye_y(x,z,s):
    return -.40-sqrt(max(.0008,.30**2-(x-s*.33)**2-(z-CZ)**2))

def eye_coord(x,z,s):
    dx=x-s*CX;u=dx/RX;dz=z-CZ-s*.018*u;h=HU if dz>=0 else HL
    v=dz/h;r=sqrt(u*u+v*v);a=math.atan2(v,u)
    ray=sqrt((RX*cos(a))**2+(h*sin(a)+s*.018*cos(a))**2)
    return r,a,(r-1)*ray

def orbital_y(x,z):
    base=base_y(x,z);delta=0
    for s in [-1,1]:
        r,a,dist=eye_coord(x,z,s)
        if 0<=dist<.145:
            t=clamp(dist/.145);ix,iz=opening(s,a);b=smooth(t)
            yy=(eye_y(ix,iz,s)-.0025)*(1-b)+base*b-.075*t*t*(1-t)*(1-t)
            if sin(a)>0:yy+=.0045*exp(-((t-.41)/.075)**2)*sin(a)**.6
            else:yy-=.0015*exp(-((t-.33)/.22)**2)*abs(sin(a))
            delta+=yy-base
    return base+delta

def nostril_coord(x,z,s):
    u=(s*x-.105)/.035;v=(z-3.984-.005*u)/.013
    return sqrt(u*u+v*v)

def nostril_border(s,a):
    return s*(.105+.035*cos(a)),3.984+.013*sin(a)+.005*cos(a)

def mouth_info(x,z):
    q=x/.252
    if abs(q)>=1.08:return 0,0,0,rgba('#c88c89')
    fade=max(0,1-q*q)**.64
    seam=3.747+.003*cos(q*pi)-.005*exp(-(x/.075)**2)
    upper=z>=seam
    thick=(.062+.018*exp(-((abs(x)-.066)/.050)**2)-.004*exp(-(x/.027)**2))*fade if upper else .098*fade
    t=abs(z-seam)/max(.0001,thick)
    if t>=1.28:return 0,0,0,rgba('#c88c89')
    strength=(1-smooth((t-.87)/.36))*(1-smooth((abs(q)-.88)/.20))
    disp=-(.022*(1-smooth(t))+.022*sin(pi*clamp(t))**1.1)*fade
    disp+=.00045*sin(x*560+sin(t*14))*sin(pi*clamp(t))**2*fade
    col=rgba('#b87574') if upper else rgba('#cb8b88')
    return disp,strength,t,col

def front_y(x,z):
    return orbital_y(x,z)+mouth_info(x,z)[0]

def face_color(x,y,z):
    c=skin_color(x,y,z)
    # Broad, soft blood-color variation is part of the mesh, not an image texture.
    rosy=.14*(gauss(x,z,-.53,4.14,.23,.24)+gauss(x,z,.53,4.14,.23,.24))
    rosy+=.11*gauss(x,z,0,4.04,.19,.14)
    c=mix(c,rgba('#d9978b'),clamp(rosy))
    for s in [-1,1]:
        r,a,dist=eye_coord(x,z,s)
        if 0<=dist<.145:
            t=dist/.145;warm=.24*(1-t)**2
            if sin(a)>0:warm+=.12*exp(-((t-.41)/.08)**2)*sin(a)
            c=mix(c,rgba('#ba887e'),warm)
    disp,strength,t,lipcolor=mouth_info(x,z)
    c=mix(c,lipcolor,strength*.90)
    return c
