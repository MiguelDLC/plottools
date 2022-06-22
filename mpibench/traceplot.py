#%%
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatch
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import sqlite3

import cmocean
import os
matplotlib.rc("text", usetex=True)
matplotlib.rc("font", family="serif")

matplotlib.rc("text.latex", preamble=r"""
\usepackage{amsmath}
\usepackage{bm}
\DeclareMathOperator{\newdiff}{d} % use \dif instead
\newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
""")
colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']

# %%
def slabel(t):
    if t < 1e3:
        return "%.2f" % t
    if t < 1e6:
        return "%.2f K" % (t*1e-3)
    if t < 1e9:
        return "%.2f M" % (t*1e-6)
    if t < 1e12:
        return "%.2f G" % (t*1e-9)


arrowprop = {
    "linewidth" : 2.3,
    "arrowstyle" : '<|-|>',
    "mutation_scale" : 15,
    "joinstyle" : 'miter',
    "fill" : True,
    "color" : "k"
}

def addrec(x0, x1, cy, h, **kwargs):
    w = x1 - x0
    lly = cy - h/2
    rect = mpatch.Rectangle((x0, lly), w, h, **kwargs)
    plt.gca().add_patch(rect)

def addtxt(x0, x1, cy, s, **kwargs):
    cx = (x0+x1)/2
    ang = np.deg2rad(kwargs.get("rotation", 0))
    dx =  np.sin(ang) * 0.03
    dy = -np.cos(ang) * 0.03
    if 'fontsize' not in kwargs:
        kwargs['fontsize'] = 10
    plt.text(cx+dx, cy+dy, s, ha='center', va='center', **kwargs)

def harrow(x0, x1, y, direct=True, txt=None, txtargs={}, **kwarks):
    options = {}
    options.update(arrowprop)
    options.update(kwarks)
    dx = x1 - x0
    if direct:
        options["arrowstyle"] = '-|>'
        x0 = x0 + 0.03*np.sign(dx)
        dx = x1 - x0

    arrow = mpatch.FancyArrowPatch((x0, y), (x1, y), **options)
    plt.gca().add_patch(arrow)
    if txt is not None:
        cx = (x0+x1)/2
        f = txtargs.pop("under", 1)
        txtargs["fontsize"] = 10
        addtxt(cx, y+f*0.27, txt, **txtargs)


def getval(s):
    s = s.replace(" ", "")
    s = s.replace("s", "")
    s = s.replace("m", "e-3")
    s = s.replace("μ", "e-6")
    s = s.replace("n", "e-8")
    return float(s)

def getstream(s):
    if len(s) > 7:
        return int(s[7:])
    return None

def getstgpu(s):
    if len(s) > 4:
        return int(s[4:])
    return None

evfiles = ["00-0.csv", "00-1.csv"]

def getev(evfiles):
    dfs = [pd.read_csv(evfile) for evfile in evfiles]
    for i, df in enumerate(dfs):
        df["process"] = i
    for df in dfs:
        df["Start"] = np.array(df["Start"].apply(getval))
        df["Duration"] = np.array(df["Duration"].apply(getval))
    return pd.concat(dfs, ignore_index=True,axis=0)

def load(fname, tmin=0, tmax=1e500):
    con = sqlite3.connect(fname)
    cur = con.cursor().execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    labels = np.array(pd.read_sql_query("SELECT * from StringIds", con)["value"])
    def relabel(iid):
        if not np.isnan(iid):
            return labels[int(iid)]
        return None
    
    if ("NVTX_EVENTS",) in tables:
        nvtx = pd.read_sql_query("SELECT * from NVTX_EVENTS", con)
        nvtx["textId"] = nvtx["textId"].apply(relabel)
        iids = np.unique(nvtx["globalTid"])
        corr = {iids[0] : 0, iids[1] : 1}
        nvtx["rank"] = nvtx["globalTid"].apply(lambda n : corr[n])
        nvtx = nvtx[["start", "end", "textId", "rank", "text"]]
        nvtx.rename(columns = {"textId" : "name"}, inplace = True)
        index = nvtx["text"].apply(lambda s : (type(s) == str) and ('MPI Rank' in s))
        print(nvtx.loc[index])
        nvtx["stream"] = np.array([1e500/1e800]).astype(int)[0]
        nvtx = nvtx[["start", "end", "name", "rank", "stream"]]
    else:
        nvtx = pd.DataFrame(columns=["start", "end", "name", "rank", "stream"])

    kernels = pd.read_sql_query("SELECT * from CUPTI_ACTIVITY_KIND_KERNEL", con)
    kernels["demangledName"] = kernels["demangledName"].apply(relabel)
    kernels["shortName"] = kernels["shortName"].apply(relabel)
    kernels["mangledName"] = kernels["mangledName"].apply(relabel)
    kernels = kernels[["start", "end", "shortName", "deviceId", "streamId"]]
    kernels.rename(columns = {"shortName" : "name", "deviceId" : "rank", "streamId" : "stream"}, inplace = True)


    copyKind = np.array(["other", "Host to Device", "Device to Host"])
    memcpy = pd.read_sql_query("SELECT * from CUPTI_ACTIVITY_KIND_MEMCPY", con)
    memcpy["copyKind"] = copyKind[memcpy["copyKind"]]
    memcpy = memcpy[["start", "end", "copyKind", "deviceId", "streamId"]]
    memcpy.rename(columns = {"copyKind" : "name", "deviceId" : "rank", "streamId" : "stream"}, inplace = True)

    cur.close()
    con.close()

    start = max(np.min(kernels["start"]), tmin*1e9)
    stop  = min(np.max(kernels["end"]),   tmax*1e9)

    kernels = kernels[kernels["start"] >= start]
    kernels = kernels[kernels["end"] <=  stop]
    nvtx = nvtx[nvtx["start"] >= start]
    nvtx = nvtx[nvtx["end"] <=  stop]
    memcpy = memcpy[memcpy["start"] >= start]
    memcpy = memcpy[memcpy["end"] <=  stop]
    start = np.min(kernels["start"])

    kernels["start"] =  kernels["start"] * 1e-3 - start*1e-3
    kernels["end"]   =  kernels["end"]   * 1e-3 - start*1e-3
    memcpy["start"]  =  memcpy["start"]  * 1e-3 - start*1e-3
    memcpy["end"]    =  memcpy["end"]    * 1e-3 - start*1e-3
    nvtx["start"]    =  nvtx["start"]    * 1e-3 - start*1e-3
    nvtx["end"]      =  nvtx["end"]      * 1e-3 - start*1e-3
    return kernels, memcpy, nvtx



#%%
def getc(name):
    if name == 'dudt': return colors[0]
    if name == 'dudt_intern': return colors[0]
    if name == 'dudt_bnd': return colors[0]
    if name == 'vec_sum': return colors[1]
    if name == 'vec_sum_in_place': return colors[1]
    if name == 'gather_to_host': return colors[2]
    if name == 'scatter_to_ghost': return colors[2]
    if name == 'Device to Host': return colors[3]
    if name == 'Host to Device': return colors[3]
    if name == 'MPI_Irecv': return "gray"
    if name == 'MPI_Waitall': return "gray"
    if name == 'MPI_Isend': return "gray"
    print("undefined op :", name)
    return "black"

def addlegend(ax, color, label):
    ax.bar([-1000, -1000, -10001], [0, 1, 0], color=color, edgecolor="k", lw=0.5, label=label, alpha=0.8)

def plotev(df, i, y, axes, xxmax, **kwargs):
    start, end, name, rank, stream = df.iloc[i]
    xxmax = max(xxmax, end)
    color = getc(name)
    plt.sca(axes[0])
    h = kwargs.get("h", 0.85)
    mult = kwargs.get("mult", 2)
    y += 1-mult*rank
    addrec(start, end, y, h, linewidth=0.2, edgecolor='k', facecolor=color, alpha=0.8)
    txt = kwargs.get("txt", "dudt")
    if end - start > 50 or txt != "dudt":
        addtxt(start, end, y, r"\texttt{%s}" % txt)
    return xxmax




# %%

def plot_mpi_1stream(dbname, fname, tmin, tmax=1e500):
    xxmax = 0
    kernels, memcpy, nvtx = load(dbname, tmin, tmax)
    fig, axes = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(8,3))
    axes = [axes]
    addlegend(axes[0], colors[1], label="Vector sum")
    addlegend(axes[0], colors[2], label="Gather/scatter")
    addlegend(axes[0], colors[3], label="Memcopy")

    for i in range(10):
        xxmax = plotev(kernels, i, 0.5, axes, xxmax)
    for i in range(4):
        xxmax = plotev(memcpy, i, 0.5, axes, xxmax)
    for i in range(6):
        xxmax = plotev(nvtx, i, -0.5, axes, xxmax)



    plt.xlim([-3, xxmax-30])
    plt.ylim([-2, 2])
    plt.yticks([])
    for ax in axes:
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(color='k', alpha=0.1, axis='x')
        ax.grid(which='minor', ls=":", color='k', alpha=0.1, axis='x')
        ax.legend(loc="lower right")
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        #ax.axis('off')

    axes[0].set_xlabel("Time $[\mu s]$")
    xmax = xxmax - 30 + 3
    plt.axhline(0, color="k", lw=0.7)
    plt.text(-xmax/6,  1, r"\textbf{Rank 0}", ha="center", va="center", fontsize=12, rotation=90)
    plt.text(-5,  1.5, "Kernels", ha="right", va="center", fontsize=12, rotation=0)
    plt.text(-5,  0.5, "MPI calls", ha="right", va="center", fontsize=12, rotation=0)

    plt.text(-xmax/6, -1, r"\textbf{Rank 1}", ha="center", va="center", fontsize=12, rotation=90)
    plt.text(-5,  -0.5, "Kernels", ha="right", va="center", fontsize=12, rotation=0)
    plt.text(-5,  -1.5, "MPI calls", ha="right", va="center", fontsize=12, rotation=0)

    plt.tight_layout()
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()

plot_mpi_1stream("profile00.sqlite", "../Figures/mpi-0.pdf", 4.427220, 4.4283)
#%%
plot_mpi_1stream("profile01.sqlite", "../Figures/mpi-1.pdf", 15.261736, 15.261736+180e-5)

#%%

def plot_base():
    xxmax = 0
    kernels, _, _ = load("../benchmarks/profile05.sqlite", 2.19367718, 2.22)
    fig, axes = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(8,1.25))
    axes = [axes]
    addlegend(axes[0], colors[1], label="Vector sum")

    for i in range(4):
        xxmax = plotev(kernels, i, 0.5, axes, xxmax)

    plt.xlim([-3, xxmax+3])
    plt.ylim([1, 2])
    plt.yticks([])
    for ax in axes:
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(color='k', alpha=0.1, axis='x')
        ax.grid(which='minor', ls=":", color='k', alpha=0.1, axis='x')
        ax.legend(loc="lower right")
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        #ax.axis('off')

    axes[0].set_xlabel("Time $[\mu s]$")
    plt.text(-5,  1.5, "Kernels", ha="right", va="center", fontsize=12, rotation=0)

    plt.tight_layout()
    fname = "../Figures/no-mpi.pdf"
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()

plot_base()
# %%

def plot_mpi_2_stream(dbname, fname, tmin, tmax=1e500):
    xxmax = 0
    kernels, memcpy, nvtx = load(dbname, tmin, tmax)
    fig, axes = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(8,4))
    axes = [axes]
    addlegend(axes[0], colors[1], label="Vector sum")
    addlegend(axes[0], colors[2], label="Gather/scatter")
    addlegend(axes[0], colors[3], label="Memcopy")

    for i in range(12):
        start, end, name, rank, stream = kernels.iloc[i]
        sp = stream/7-1
        if start > 135 : name = "dudt..   "
        txt = name if "dudt" in name else ""
        xxmax = plotev(kernels, i, 1.5-sp+rank, axes, xxmax, mult=4, txt=txt)
    for i in range(4):
        start, end, name, rank, stream = memcpy.iloc[i]
        xxmax = plotev(memcpy, i, 0.5+rank, axes, xxmax, mult=4)
    for i in range(6):
        start, end, name, rank, stream = nvtx.iloc[i]
        xxmax = plotev(nvtx, i, -0.5+rank, axes, xxmax, mult=4)



    plt.xlim([-3, xxmax-5])
    plt.ylim([-3, 3])
    plt.yticks([])
    for ax in axes:
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.grid(color='k', alpha=0.1, axis='x')
        ax.grid(which='minor', ls=":", color='k', alpha=0.1, axis='x')
        ax.legend(loc="lower right")
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        #ax.axis('off')

    axes[0].set_xlabel("Time $[\mu s]$")
    xmax = xxmax - 30 + 3
    plt.axhline(0, color="k", lw=0.7)
    plt.text(-xmax/5,  1.5, r"\textbf{Rank 0}", ha="center", va="center", fontsize=12, rotation=90)
    plt.text(-5,  2.5, "Default\nStream", ha="right", va="center", fontsize=12, rotation=0)
    plt.text(-5,  1.5, "Comm\nStream", ha="right", va="center", fontsize=12, rotation=0)
    plt.text(-5,  0.5, "MPI calls", ha="right", va="center", fontsize=12, rotation=0)

    plt.text(-xmax/5, -1.5, r"\textbf{Rank 1}", ha="center", va="center", fontsize=12, rotation=90)
    plt.text(-5,  -0.5, "Default\nStream", ha="right", va="center", fontsize=12, rotation=0)
    plt.text(-5,  -1.5, "Comm\nStream", ha="right", va="center", fontsize=12, rotation=0)
    plt.text(-5,  -2.5, "MPI calls", ha="right", va="center", fontsize=12, rotation=0)

    plt.tight_layout()
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()

plot_mpi_2_stream("profile02.sqlite", "../Figures/mpi-2.pdf", 15.376288, 15.376525)

#%%