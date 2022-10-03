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
        return "%.3gs" % t
    if 1e-3 <= t and t < 1e0:
        return "%.3gms" % (t*1e3)
    if 1e-6 <= t and t < 1e-3:
        return r"%.3g$\mathrm{\mu}$s" % (t*1e6)
    


# %%

# files = ["cpu.txt", "cpu-mpi.txt", "out00-fp64.txt", "out00.txt"]
# names = ["Single process", "8 processes MPI", "64 bit GPU", "GPU"]
files = ["cpu.txt", "ava-cpu.txt", "cpu-mpi.txt", "ava-cpu-omp.txt", "ava-cpu-mpi.txt","ava-igpu.txt", "ava-2060m.txt", "ava-2080.txt"]
names = ["Base\nsingle", "AVA\nsingle", "Base\n$8\\times$ MPI", "AVA\n$8\\times$ OMP", "AVA\n$8\\times$ MPI", "AVA-hip\nRX Vega 7", "AVA-cuda\nRTX2060M", "AVA-cuda\nRTX2080"]

periter = np.array([gettime(fname) for fname in files])

plt.figure(figsize=(12,6))
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e3*periter, 0.5)
plt.gca().set_yscale('log')
plt.ylabel("Time per iteration [ms]")
plt.ylim([0.2, None])
plt.xticks(fontsize=14)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")

for i, t in enumerate(periter[:-1]):
    h1 = 1000*t
    h2 = periter[i+1]*1000
    arrow = mpatch.FancyArrowPatch(path=mpath.Path([(i+0.3,0.97*h1),(i+0.6,(0.8*h1+0.2*h2)*1.6),(i+0.77,h2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
    plt.gca().add_patch(arrow)
    plt.text(i+0.7, (0.8*h1+0.2*h2)*1.3 , "$\div%.2f$" % (h1/h2), ha="center", fontsize=14)


for i, t in enumerate(periter):
    plt.text(i, 0.25 , "%s" % tlabel(t), ha="center", fontsize=14)

figname = "../Figures/final_speed_log.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()
# %%


files = ["out00.txt", "out01.txt", "out02.txt", "out03.txt", "out04.txt", "out05.txt", "ava-2080.txt"]
names = ["Baseline", "Reordering", "Literals", r"\texttt{printf}", "Shared\nmemory", "Coalescence", "fastmath"]
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

reftime = gettime("cpu.txt")
files = ["out00.txt", "out01.txt", "out02.txt", "out03.txt", "out04.txt", "out05.txt", "ava-2080.txt"]
names = ["Baseline", "Reordering", "Literals", r"\texttt{printf}", "Shared\nmemory", "Coalescence", "fastmath"]
periter = np.array([gettime(fname) for fname in files])

plt.figure(figsize=(8,4))
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.plot(names, reftime/periter, 'o-')
plt.plot(names, 1e6*periter, 'o-')

# plt.bar(names, 57*periter**0, 0.5, label="Vector sums")
plt.ylabel("Speedup over 1 CPU core")
plt.ylim([100., 800])

ax2 = plt.gca().twinx()
plt.ylabel("Time per iteration $[\mu s]$")
plt.ylim([100., 800])
plt.xticks(fontsize=12, rotation=0)


#plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
#plt.text(1.72, 12 , r"$\div 8.61$", fontsize=14)
#plt.text(2.7, 2, r"$\div 6.18$", fontsize=14)

for i, t in enumerate(periter):
    if i != 2:
        plt.text(i, (reftime/(t)) , "$%s%d$\n\n" % (r"\times", np.ceil(reftime/t)), ha="center", va="center", fontsize=12, rotation=0)
    else:
        plt.text(i, (reftime/(t)) , "\n\n$%s%d$" % (r"\times", np.ceil(reftime/t)), ha="center", va="center", fontsize=12, rotation=0)


for i, t in enumerate(periter):
    if i < 3:
        plt.text(i, 1e6*t , "%s\n\n" % (tlabel(t)), ha="center", va="center", fontsize=12, rotation=0)
    else:
        plt.text(i, 1e6*t , "\n\n%s" % (tlabel(t)), ha="center", va="center", fontsize=12, rotation=0)

figname = "../Figures/final_speed-fact.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()

# %%

files = ["cpu.txt", "ava-cpu.txt", "cpu-mpi.txt", "ava-cpu-omp.txt", "ava-cpu-mpi.txt","ava-igpu.txt", "ava-2060m.txt", "ava-2080.txt"]
names = ["Base\nsingle", "AVA\nsingle", "Base\n$8\\times$ MPI", "AVA\n$8\\times$ OMP", "AVA\n$8\\times$ MPI", "AVA-hip\nRX Vega 7", "AVA-cuda\nRTX2060M", "AVA-cuda\nRTX2080"]
periter = np.array([gettime(fname) for fname in files])

fig, ax = plt.subplots(1, 1, figsize=(12,6), gridspec_kw={'width_ratios': [4.4]})
plt.sca(ax)
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e3*periter, 0.5)
plt.ylabel("Time per iteration [ms]", fontsize=14)
plt.ylim([0., 199])
plt.xlim([-0.5, None])
plt.xticks(fontsize=14)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")

#plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
#plt.text(1.5, 29 , r"$\div 8.61$", fontsize=14)
#plt.text(2.25, 115 , r"$\div 270$", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, 5 , "%s" % tlabel(t), ha="center", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, 183 , "$\\bm{%.2f}$" % (periter[0]/t), ha="center", fontsize=14)

for i, t in enumerate(periter[:-1]):
    h1 = 1000*t
    h2 = periter[i+1]*1000
    arrow = mpatch.FancyArrowPatch(path=mpath.Path([(i+0.3,0.97*h1),(i+0.6,0.8*h1+0.2*h2+20),(i+0.77,h2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
    plt.gca().add_patch(arrow)
    plt.text(i+0.6, 0.8*h1+0.2*h2+12 , "$\div%.2f$" % (h1/h2), ha="center", fontsize=14)


plt.title("\\textbf{Speed comparison of different SLIM versions}")
plt.tight_layout()
figname = "../Figures/speed_linear.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()

# %%

files = ["ava-igpu.txt", "ava-2060m.txt", "ava-2080.txt"]
names = ["AVA-hip\nRX Vega 7", "AVA-cuda\nRTX2060M", "AVA-cuda\nRTX2080"]
periter = np.array([gettime(fname) for fname in files])

fig, ax = plt.subplots(1, 1, figsize=(8,6), gridspec_kw={'width_ratios': [4.4]})
plt.sca(ax)
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e3*periter, 0.5)
plt.ylabel("Time per iteration [ms]", fontsize=14)
plt.ylim([0., 3.3])
plt.xlim([-0.5, None])
plt.xticks(fontsize=14)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")

for i, t in enumerate(periter):
    plt.text(i, 0.07 , "%s" % tlabel(t), ha="center", fontsize=14)

tref = gettime("ava-cpu-mpi.txt")
for i, t in enumerate(periter):
    plt.text(i, 3.1 , "$\\bm{%.2f}$" % (tref/t), ha="center", fontsize=14)

for i, t in enumerate(periter[:-1]):
    h1 = 1000*t
    h2 = periter[i+1]*1000
    arrow = mpatch.FancyArrowPatch(path=mpath.Path([(i+0.3,0.97*h1),(i+0.6,0.8*h1+0.2*h2+0.5),(i+0.77,h2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
    plt.gca().add_patch(arrow)
    plt.text(i+0.6, 0.8*h1+0.2*h2+0.3 , "$\div%.2f$" % (h1/h2), ha="center", fontsize=14)


plt.title("\\textbf{GPUs compared to the best CPU+MPI version}")
plt.tight_layout()
figname = "../Figures/gpu_speed_linear.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()

# %%
# %%

files = ["cpu-mpi.txt", "ava-cpu-omp.txt", "ava-cpu-mpi.txt","ava-igpu.txt", "ava-2060m.txt", "ava-2080.txt"]
names = ["Old version\n$8\\times$ MPI", "New (CPU)\n$8\\times$ OMP", "New (CPU)\n$8\\times$ MPI", "New (AMD)\nRX Vega 7", "New (NVIDIA)\nRTX2060M", "New (NVIDIA)\nRTX2080"]
periter = np.array([gettime(fname) for fname in files])

fig, ax = plt.subplots(1, 1, figsize=(12,5), gridspec_kw={'width_ratios': [4.4]})
plt.sca(ax)
plt.grid(color='k', alpha=0.1, axis='y')
plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='y')
plt.bar(names, 1e3*periter, 0.5)
plt.ylabel("Time per iteration [ms]", fontsize=14)
plt.ylim([0., 45])
plt.xlim([-0.5, None])
plt.xticks(fontsize=14)

style = "simple,tail_width=0.3,head_width=5,head_length=6"
kw = dict(arrowstyle=style,color="k")

#plt.text(0.7, 120, r"$\div 5.05$", fontsize=14)
#plt.text(1.5, 29 , r"$\div 8.61$", fontsize=14)
#plt.text(2.25, 115 , r"$\div 270$", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, 1 , "%s" % tlabel(t), ha="center", fontsize=14)

for i, t in enumerate(periter):
    plt.text(i, 42 , "$\\bm{%.2f}$" % (periter[2]/t), ha="center", fontsize=14)

for i, t in enumerate(periter[:-1]):
    h1 = 1000*t
    h2 = periter[i+1]*1000
    arrow = mpatch.FancyArrowPatch(path=mpath.Path([(i+0.3,0.97*h1),(i+0.6,0.8*h1+0.2*h2+3),(i+0.77,h2)],[mpath.Path.MOVETO,mpath.Path.CURVE3,mpath.Path.CURVE3]),**kw)
    plt.gca().add_patch(arrow)
    plt.text(i+0.6, 0.8*h1+0.2*h2+2 , "$\div%.2f$" % (h1/h2), ha="center", fontsize=14)


plt.title("\\textbf{Speed comparison of different SLIM versions}")
plt.tight_layout()
figname = "../Figures/new_speed_linear_nosingle.pdf"
plt.savefig(figname)
os.system("pdfcrop %s %s" % (figname, figname))

plt.show()
# %%
