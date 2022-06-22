#%%
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatch
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator

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

def addrec(cx, cy, w, h, **kwargs):
    llx = cx - w/2
    lly = cy - h/2
    rect = mpatch.Rectangle((llx, lly), w, h, **kwargs)
    plt.gca().add_patch(rect)

def addtxt(cx, cy, s, **kwargs):
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

#%%

def warpstate(kernel, outfname):
    metrics = np.array([
    float(kernel["smsp__average_warps_issue_stalled_barrier_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_branch_resolving_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_dispatch_stall_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_drain_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_imc_miss_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_lg_throttle_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_long_scoreboard_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_math_pipe_throttle_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_membar_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_mio_throttle_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_misc_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_no_instruction_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_not_selected_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_selected_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_short_scoreboard_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_sleeping_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_tex_throttle_per_issue_active.ratio"]),
    float(kernel["smsp__average_warps_issue_stalled_wait_per_issue_active.ratio"])])

    names = np.array(["Stall Barrier", "Stalled Branch Resolving", "Stall Dispach Stall",
    "Stall Drain", "Stall IMC Miss", "Stall LG Throttle", "Stall Long Scoreboard",
    "Stall Math Pipe Throttle", "Stall Membar", "Stall MIO Throttle", "Stall Misc",
    "Stall No Instruction", "Stall Not Selected", "Selected", "Stall Short Scoreboard",
    "Stall Sleeping", "Stall Tex Throttle", "Stall Wait"])
    order = np.argsort(metrics)[9:]
    names = names[order]
    metrics = metrics[order]

    plt.figure(figsize=(7,3))
    plt.barh(names, metrics)
    plt.gca().xaxis.set_minor_locator(MultipleLocator(0.1))

    plt.grid(color='k', alpha=0.1, axis='x')
    plt.grid(which='minor', ls=":", color='k', alpha=0.1, axis='x')
    plt.xlabel("Cycles per issued instruction")
    plt.tight_layout()
    plt.savefig(outfname)
    os.system("pdfcrop %s %s" % (outfname, outfname))
    plt.show()

num = "03"
figname = "../Figures/warpstate%s.pdf" % num
df = pd.read_csv("profile%s.csv" % num)
dudt = df.iloc[13]
warpstate(dudt, figname)

# %%
