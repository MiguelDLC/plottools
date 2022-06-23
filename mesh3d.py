#%%
import os
import numpy as np
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
pi = np.pi
from scipy.spatial import ConvexHull as ch
mpl.rc("text", usetex=True)
mpl.rc("font", family="serif")
mpl.rc("text.latex", preamble=r"""
\usepackage{amsmath}
\usepackage{bm}
\DeclareMathOperator{\newdiff}{d} % use \dif instead
\newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
""")

import cmocean

def inset(xy, r=0.9):
    dr = (1-r)/2
    M = np.ones((3,3))*dr
    M += np.eye(3)*(r-dr)
    return M.dot(xy)
def loop(x):
    return np.array([*x, x[0]])

def isgood(xy, i):
    pi = xy[i]
    p1 = xy[(i+2)%3]
    p2 = xy[(i+1)%3]
    if (pi[0] >= max(p1[0], p2[0])) or (pi[0] <= min(p1[0], p2[0])):
        return True
    dy = p2 - p1
    return p1[1] + dy[1]/dy[0]*(pi[0] -p1[0]) >= pi[1]

def isgood2(xy, i):
    pi = xy[i]
    p1 = xy[(i+2)%3]
    p2 = xy[(i+1)%3]
    dy = p2 - p1
    return p1[1] + dy[1]/dy[0]*(pi[0] -p1[0]) <= pi[1]



# %%

def prismplot(xyl, z, behind=True, color="w", alpha=0.8):
    height = 0.5
    xyl = xyl + [[0, z]]
    xyt = np.vstack([xyl, xyl+[[0, -height]]])

    if behind:
        #vertical bars
        goods = [not isgood(xyl, i) for i in range(3)]
        for i in range(3):
            if not goods[i]:
                continue
            line = xyt[[i,i+3]]
            plt.plot(line[:,0], line[:,1], "-k")

        #lower loop
        goods = [not isgood2(xyl, i) for i in range(3)]
        for i in range(3):
            if not goods[i]:
                continue
            line = xyt[[(i+1)%3+3, (i+2)%3+3]]
            plt.plot(line[:,0], line[:,1],  ".-k")
    
    # solid
    hull = ch(xyt)
    xyh = xyt[hull.vertices]
    poly = mpl.patches.Polygon(xyh, fill=True, alpha=alpha, color=color, zorder=2) #ec="k", ls="-.")
    plt.gca().add_patch(poly)
    
    # upper loop
    plt.plot(loop(xyl[:,0]), loop(xyl[:,1]), ".-k")

    #vertical bars
    goods = [isgood(xyl, i) for i in range(3)]
    for i in range(3):
        if not goods[i]:
            continue
        line = xyt[[i,i+3]]
        plt.plot(line[:,0], line[:,1], "-k")

    #lower loop
    goods = [isgood2(xyl, i) for i in range(3)]
    for i in range(3):
        if not goods[i]:
            continue
        line = xyt[[(i+1)%3+3, (i+2)%3+3]]
        plt.plot(line[:,0], line[:,1],  ".-k")


# %%


ang = 0*pi/180
rtransf = np.array([
    [np.cos(ang),-np.sin(ang)],
    [np.sin(ang), np.cos(ang)]
])

sheer = 0.3
transtransf = np.array([
    [1, sheer],
    [0, 0.35]
])

trans = np.eye(2)
trans = transtransf @ rtransf

xy = np.array([
    [0.0, 0.0],
    [0.9, 0.1],
    [0.1, 0.9],
    [1.0, 1.0],
    [1.8, 0.1],
    [2.0, 1.1],
    [.95, 1.75],
])

triangles = np.array([
    [3, 6, 2],
    [5, 6, 3],
    [1, 3, 2],
    [4, 5, 3],
    [1, 4, 3],
    [0, 1, 2],
])

plt.triplot(xy[:,0], xy[:,1], triangles=triangles)
for i, tri in enumerate(triangles):
    mid = np.mean(xy[tri], axis = 0)
    plt.text(*mid, str(i), ha="center", va="center")
plt.gca().set_aspect(1)
plt.show()

xy = (trans @ xy.T).T

X = xy[:,0]
Y = xy[:,1]


colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']
for alay in range(7):
    plt.figure(figsize=(6, 9))
    nlayers = [6, 6, 4, 2, 2, 4]
    for i, tri in enumerate(triangles):
        mid = np.mean(xy[tri], axis = 0)
        # plt.text(*mid, str(i), ha="center", va="center")
        xyl = inset(xy[tri])
        for l in np.arange(6-1, -1, -1):
            z = -0.55*l
            if l == alay:
                prismplot(xyl, z, True, color=colors[1], alpha=0.97)
            else:
                prismplot(xyl, z, True, alpha=0.97)
    
    plt.gca().set_aspect(1)
    plt.axis('off')
    fname = "Figures/bloc_struct_l-%d.pdf" % alay
    plt.tight_layout()
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()

#%%
for part in range(2):
    plt.figure(figsize=(6, 9))
    nlayers = [6, 6, 4, 2, 2, 4]
    for i, tri in enumerate(triangles):
        mid = np.mean(xy[tri], axis = 0)
        # plt.text(*mid, str(i), ha="center", va="center")
        xyl = inset(xy[tri])
        for l in np.arange(6-1, -1, -1):
            z = -0.55*l
            if (l >= 3*part) and (l < 3*(part+1)):
                prismplot(xyl, z, True, color=colors[0], alpha=0.97)
            else:
                prismplot(xyl, z, True, alpha=0.97)
    
    plt.gca().set_aspect(1)
    plt.axis('off')
    fname = "Figures/bloc_struct_p-%d.pdf" % part
    plt.tight_layout()
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()

# %%
