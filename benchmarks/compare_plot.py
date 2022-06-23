#%%
from cProfile import label
from ctypes import c_int
import os
from tkinter import font
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatch
import cmocean
matplotlib.rc("text", usetex=True)
matplotlib.rc("font", family="serif")

matplotlib.rc("text.latex", preamble=r"""
\usepackage{amsmath}
\usepackage{bm}
\DeclareMathOperator{\newdiff}{d} % use \dif instead
\newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
""")
#%%
def gettime(fname):
    with open(fname, 'r') as f:
        s = f.read()
    s = s.split('\n')[:-1]
    l = s[-1].split(",")
    p = [k for k in l if '/iter' in k][0].strip()
    if "us/iter" in p:
        fact = 1e6
    elif "ms/iter" in p:
        fact = 1e3
    else:
        print("beep beep boop error")
    
    periter = float(p.split(" ")[0])/fact
    return periter

def tlabel(t):
    if 1e0 <= t and t < 1e3:
        return "%.3g s" % t
    if 1e-3 <= t and t < 1e0:
        return "%.3g ms" % (t*1e3)
    if 1e-6 <= t and t < 1e-3:
        return r"%.3g $\mu$s" % (t*1e6)
    


# %%

files = ["cpu.txt", "cpu-mpi.txt", "out00-fp64.txt", "out00.txt"]
names = ["Single process", "8 processes MPI", "64 bit GPU", "GPU"]
periter = np.array([gettime(fname) for fname in files])

plt.figure(figsize=(7,4))
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e3*periter, 0.5)
plt.gca().set_yscale('log')
plt.ylabel("Time per iteration [ms]")
plt.ylim([0.2, None])
plt.xticks(fontsize=14)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")
arrow1 = mpatch.FancyArrowPatch(path=mpath.Path([(0.3,166),(0.7,150),(0.85,36)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrow1)
arrow2 = mpatch.FancyArrowPatch(path=mpath.Path([(1.3,30),(1.7,20),(1.85,4.2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrow2)
arrow3 = mpatch.FancyArrowPatch(path=mpath.Path([(2.3,3.6),(2.7,2.8),(2.85,0.68)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrow3)

plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
plt.text(1.72, 12 , r"$\div 8.61$", fontsize=14)
plt.text(2.7, 2, r"$\div 6.18$", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, 0.25 , "%s" % tlabel(t), ha="center", fontsize=14)

figname = "../Figures/initial_speed.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()
# %%


files = ["out00.txt", "out01.txt", "out02.txt", "out03.txt", "out04.txt", "out05.txt"]
names = ["Baseline", "Reordering", "Literals", r"\texttt{printf}", "Shared\nmemory", "Coalescence"]
periter = np.array([gettime(fname) for fname in files])

plt.figure(figsize=(8,4))
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e6*periter, 0.5)
plt.bar(names, 57*periter**0, 0.5, label="Vector sums")
plt.ylabel(r"Time per iteration $[\mu s]$")
plt.ylim([0., None])
plt.xticks(fontsize=12, rotation=0)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")
arrow1 = mpatch.FancyArrowPatch(path=mpath.Path([(0.3,166),(0.7,150),(0.85,36)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
#plt.gca().add_patch(arrow1)
arrow2 = mpatch.FancyArrowPatch(path=mpath.Path([(1.3,30),(1.7,20),(1.85,4.2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
#plt.gca().add_patch(arrow2)
arrow3 = mpatch.FancyArrowPatch(path=mpath.Path([(2.3,3.6),(2.7,2.8),(2.85,0.68)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
#plt.gca().add_patch(arrow3)

#plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
#plt.text(1.72, 12 , r"$\div 8.61$", fontsize=14)
#plt.text(2.7, 2, r"$\div 6.18$", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, (57+1e6*t)/2 , "%s" % tlabel(t-57e-6), ha="center", va="center", fontsize=12, rotation=0)
    plt.text(i, 57/2 , "%s" % tlabel(57e-6), ha="center", va="center", fontsize=12, rotation=0)

figname = "../Figures/final_speed.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()

# %%

files = ["cpu.txt", "cpu-mpi.txt", "out00-fp64.txt", "out00.txt"]
names = ["Single\nprocess", "8 processes\nwith MPI", "GPU (FP64)", "GPU"]
periter = np.array([gettime(fname) for fname in files])

fig, ax = plt.subplots(1, 1, figsize=(8,4), gridspec_kw={'width_ratios': [4.4]})
plt.sca(ax)
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e3*periter, 0.5)
plt.ylabel("Time per iteration [ms]", fontsize=14)
plt.ylim([0., None])
plt.xlim([-0.5, 3.5])
plt.xticks(fontsize=14)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")
arrow1 = mpatch.FancyArrowPatch(path=mpath.Path([(0.35,166),(0.7,150),(0.85,36)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrow1)
arrow2 = mpatch.FancyArrowPatch(path=mpath.Path([(1.35,28),(1.7,25),(1.85,6)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrow2)
arrowc = mpatch.FancyArrowPatch(path=mpath.Path([(0.35,169),(2.5,166),(2.85,2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrowc)

plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
plt.text(1.5, 29 , r"$\div 8.61$", fontsize=14)
plt.text(2.25, 115 , r"$\div 270$", fontsize=14)

for i, t in enumerate(periter[0:2]):
    plt.text(i, 5 , "%s" % tlabel(t), ha="center", fontsize=14)

plt.text(2.08, 7 , "%s" % tlabel(periter[2]), ha="center", fontsize=14)
plt.text(3.08, 4 , "%s" % tlabel(periter[3]), ha="center", fontsize=14)


"""plt.sca(axes[1])
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names[2:], 1e3*periter[2:], 0.6)
plt.ylabel("Time per iteration [ms]")
plt.ylim([0., None])
plt.xlim([-0.5, 1.5])
plt.xticks(fontsize=14)


arrow3 = mpatch.FancyArrowPatch(path=mpath.Path([(0.35,3.8),(0.7,3.3),(0.85,0.68)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
plt.gca().add_patch(arrow3)"""

plt.tight_layout()
figname = "../Figures/initial_speed_linear.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()
# %%

reftime = gettime("cpu.txt")
files = ["out00.txt", "out01.txt", "out02.txt", "out03.txt", "out04.txt", "out05.txt"]
names = ["Baseline", "Reordering", "Literals", r"\texttt{printf}", "Shared\nmemory", "Coalescence"]
periter = np.array([gettime(fname) for fname in files])

plt.figure(figsize=(8,4))
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, reftime/periter, 0.6)
# plt.bar(names, 57*periter**0, 0.5, label="Vector sums")
plt.ylabel("Speedup over CPU with 1 process")
plt.ylim([0., None])
plt.xticks(fontsize=12, rotation=0)


#plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
#plt.text(1.72, 12 , r"$\div 8.61$", fontsize=14)
#plt.text(2.7, 2, r"$\div 6.18$", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, (reftime/(t))/2 , "%s\n\n$%s%d$" % (tlabel(t), r"\times", np.ceil(reftime/t)), ha="center", va="center", fontsize=12, rotation=0)

figname = "../Figures/final_speed-fact.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()

# %%
