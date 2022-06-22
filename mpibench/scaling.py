
#%%
from turtle import pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import os
import pandas 
import parse
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator, LogLocator)
from scipy.optimize import root_scalar, minimize
import pandas as pd

matplotlib.rc("text", usetex=True)
matplotlib.rc("font", family="serif")
matplotlib.rc("text.latex", preamble=r"""
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{bm}
\usepackage{siunitx}
""")



fnames = ["../time.txt", "../time-1.txt"]

def getpred(N, x):
    a, b, c = x
    pred = np.maximum(a*N, b)
    pred = np.maximum(c*N**0.5, pred)
    return pred


def fit(N, t):
    a, b = np.polyfit(N, t, 1, w = N**(-0.5))
    b = 100 if b < 100 else b
    c = 1

    def error(x):
        pred = getpred(N, x)
        r = np.log(pred) - np.log(t)
        return (np.abs(r)).sum()

    sol = minimize(error, x0=[a, b, c], method="Nelder-Mead")
    a, b, c = sol.x
    return a, b, c


def addcurve(N, t, *args, **kwargs):
    #std = [np.std(t[N == n]) for n in N]
    a, b, c = fit(N, t)
    print(1/a)
    print(b)
    
    n = 2.0**np.linspace(np.log2(N.min()),np.log2(N.max()), 100)
    pred = np.maximum(a*n, b)
    pred = np.maximum(c*n**0.5, pred)
    getpred(n, [a, b, c])

    plt.loglog(n, pred, "k", lw=0.7, alpha=0.5)
    plt.loglog(N, t, *args, **kwargs)

#%%

plt.figure(figsize=(5.5,3))

df = pd.read_csv("../time.txt")
N = df["nelem"]
t = df["time"]
addcurve(N*2, t, ".", label="Multi-GPU")

df = pd.read_csv("../time-1.txt")
N = df["nelem"]
t = df["time"]
addcurve(N, t, "+", label="Single GPU")

# df = pd.read_csv("../time-cpu.txt")
# N = df["nelem"]
# t = df["time"]
# addcurve(N, t, "*", label="8 CPUs")

plt.legend(fontsize=12)
plt.xlabel("Total number of triangles $N$")
plt.ylabel("Time for 1 RK iteration $[\mu s]$")
plt.xlim([100, None])
plt.ylim([10, None])
#plt..set_minor_locator(AutoMinorLocator(2))
#plt.yaxis.set_minor_locator(AutoMinorLocator(5))
plt.grid(which='major', color='k', linestyle='-', linewidth=0.5, alpha=0.7)
plt.grid(which='minor', color='k', linestyle=':', linewidth=0.3, alpha=0.5)
sname = "../Figures/scaling-1" + ".pdf"
plt.tight_layout()
plt.savefig(sname)
os.system("pdfcrop %s %s" % (sname, sname))
plt.show()

# %%

#%%

plt.figure(figsize=(5.5,3))

df = pd.read_csv("../time-2.txt")
N = df["nelem"]
t = df["time"]
addcurve(N*2, t, ".", label="Multi-GPU")

df = pd.read_csv("../time-1.txt")
N = df["nelem"]
t = df["time"]
addcurve(N, t, "+", label="Single GPU")



# df = pd.read_csv("../time-cpu.txt")
# N = df["nelem"]
# t = df["time"]
# addcurve(N, t, "*", label="8 CPUs")

plt.legend(fontsize=12)
plt.xlabel("Total number of triangles $N$")
plt.ylabel("Time for 1 RK iteration $[\mu s]$")
plt.xlim([100, None])
plt.ylim([10, None])
#plt..set_minor_locator(AutoMinorLocator(2))
#plt.yaxis.set_minor_locator(AutoMinorLocator(5))
plt.grid(which='major', color='k', linestyle='-', linewidth=0.5, alpha=0.7)
plt.grid(which='minor', color='k', linestyle=':', linewidth=0.3, alpha=0.5)
sname = "../Figures/scaling-2" + ".pdf"
plt.tight_layout()
plt.savefig(sname)
os.system("pdfcrop %s %s" % (sname, sname))
plt.show()

# %%
