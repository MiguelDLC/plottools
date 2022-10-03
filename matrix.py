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
# %%

def getmatb(n):
    A = np.zeros((n*6, n*6))
    for i in range(n):
        mi = max(0, 6*(i-1))
        ma = min(n*6, 6*(i+2))
        A[6*i:6*i+3, mi:6*i+6] = 1
        A[6*i+3:6*i+6, 6*i:ma] = 1
    return A

def getmatc(n):
    A = np.zeros((n*6, n*6))
    for i in range(n):
        A[6*i:6*i+6, 6*i:6*i+6] = 1
    return A

def getband(n):
    A = np.ones((n*6, n*6))
    i, j = np.meshgrid(np.arange(n*6), np.arange(n*6), indexing='ij')
    A[i > j+8] = 0
    A[j > i+8] = 0
    return A


n = 5

Abad = getband(n) - getmatb(n)
Ahor = getmatb(n) - getmatc(n)
Aloc = getmatc(n)

plt.figure(figsize=(8,8))
plt.spy(Abad, marker="s", ms=11, color="red")
plt.spy(Ahor + Aloc, marker="s", ms=11)
# plt.spy(Aloc, marker="s", ms=11, color="orange")
plt.axis("off")
#plt.plot([18+8.5, 18+8.5, 12-8.5, 12-8.5, 18+8.5], [17.5, 11.5, 11.5, 17.5, 17.5], "k", zorder=5)
#for i in range(10):
#    plt.axhline(6*i-0.5+0.02, color="k", lw=1,  zorder=-1)

plt.ylim([ 20, 9])
plt.xlim([ 1, 6*n-2])
rect = mpl.patches.Rectangle((-1, -1), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)
rect = mpl.patches.Rectangle((9, 17.5), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)

fname = "Figures/banded.pdf"
plt.savefig(fname)
os.system("pdfcrop %s %s" % (fname, fname))
plt.show()
# %%

i, j = np.meshgrid(np.arange(n*6), np.arange(n*6), indexing='ij')
p0 = (Ahor+Aloc) * (i >= 12) * (i < 15)

plt.figure(figsize=(8,8))
plt.spy(Abad, marker=".", ms=5, color="k")
plt.spy(Ahor + Aloc - p0, marker="s", ms=11)
plt.spy(p0, marker="s", ms=11, color="orange")
plt.axis("off")
#plt.plot([18+8.5, 18+8.5, 12-8.5, 12-8.5, 18+8.5], [17.5, 11.5, 11.5, 17.5, 17.5], "k", zorder=5)
#for i in range(10):
#    plt.axhline(6*i-0.5+0.02, color="k", lw=1,  zorder=-1)

plt.ylim([ 20, 9])
plt.xlim([ 1, 6*n-2])
rect = mpl.patches.Rectangle((-1, -1), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)
rect = mpl.patches.Rectangle((9, 17.5), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)

fname = "Figures/matopt-0.pdf"
plt.savefig(fname)
os.system("pdfcrop %s %s" % (fname, fname))
plt.show()
# %%


i, j = np.meshgrid(np.arange(n*6), np.arange(n*6), indexing='ij')
p1 = (Ahor+Aloc) * (i >= 15) * (i < 18)

plt.figure(figsize=(8,8))
plt.spy(Abad, marker=".", ms=5, color="k")
plt.spy(Ahor + Aloc - p1, marker="s", ms=11)
plt.spy(p1, marker="s", ms=11, color="orange")
plt.axis("off")
#plt.plot([18+8.5, 18+8.5, 12-8.5, 12-8.5, 18+8.5], [17.5, 11.5, 11.5, 17.5, 17.5], "k", zorder=5)
#for i in range(10):
#    plt.axhline(6*i-0.5+0.02, color="k", lw=1,  zorder=-1)

plt.ylim([ 20, 9])
plt.xlim([ 1, 6*n-2])
rect = mpl.patches.Rectangle((-1, -1), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)
rect = mpl.patches.Rectangle((9, 17.5), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)

fname = "Figures/matopt-1.pdf"
plt.savefig(fname)
os.system("pdfcrop %s %s" % (fname, fname))
plt.show()
# %%


i, j = np.meshgrid(np.arange(n*6), np.arange(n*6), indexing='ij')
p2 = (Ahor+Aloc) * (j >= 12) * (j < 18) * (i >= 12) * (i < 18)

plt.figure(figsize=(8,8))
plt.spy(Abad, marker=".", ms=5, color="k")
plt.spy(Ahor + Aloc - p2, marker="s", ms=11)
plt.spy(p2, marker="s", ms=11, color="orange")
plt.axis("off")
#plt.plot([18+8.5, 18+8.5, 12-8.5, 12-8.5, 18+8.5], [17.5, 11.5, 11.5, 17.5, 17.5], "k", zorder=5)
#for i in range(10):
#    plt.axhline(6*i-0.5+0.02, color="k", lw=1,  zorder=-1)

plt.ylim([ 20, 9])
plt.xlim([ 1, 6*n-2])
rect = mpl.patches.Rectangle((-1, -1), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)
rect = mpl.patches.Rectangle((9, 17.5), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)

fname = "Figures/matopt-2.pdf"
plt.savefig(fname)
os.system("pdfcrop %s %s" % (fname, fname))
plt.show()
# %%

i, j = np.meshgrid(np.arange(n*6), np.arange(n*6), indexing='ij')

plt.figure(figsize=(8,8))
plt.spy(Abad, marker=".", ms=5, color="k")
plt.spy(Ahor + Aloc, marker="s", ms=11)
plt.axis("off")
#plt.plot([18+8.5, 18+8.5, 12-8.5, 12-8.5, 18+8.5], [17.5, 11.5, 11.5, 17.5, 17.5], "k", zorder=5)
#for i in range(10):
#    plt.axhline(6*i-0.5+0.02, color="k", lw=1,  zorder=-1)

plt.ylim([ 20, 9])
plt.xlim([ 1, 6*n-2])
rect = mpl.patches.Rectangle((-1, -1), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)
rect = mpl.patches.Rectangle((9, 17.5), 36, 12.5, zorder=10, alpha=0.8, color=u"#f0f0f0")
plt.gca().add_patch(rect)

fname = "Figures/matopt-3.pdf"
plt.savefig(fname)
os.system("pdfcrop %s %s" % (fname, fname))
plt.show()
# %%
