#%%
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rc("text", usetex=True)
matplotlib.rc("font", family="serif")
matplotlib.rc("text.latex", preamble=r"""
\usepackage{amsmath}
\usepackage{bm}
\DeclareMathOperator{\newdiff}{d} % use \dif instead
\newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
""")
import pandas as pd
from datetime import datetime
import os
tconv = lambda x : datetime.strptime(x, "%Y-%m-%d")
colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']

df = pd.read_csv("filtered.csv")
df["launch"] = df["launch"].apply(tconv)
amd = df[df["vendor"] == "amd"]
nvi = df[df["vendor"] == "nvidia"]

nvi64 = nvi[np.maximum.accumulate(nvi["fp64"]) <= nvi["fp64"]]; nvi64 = nvi64[nvi64["fp64"] > 0]
nvi32 = nvi[np.maximum.accumulate(nvi["fp32"]) <= nvi["fp32"]]; nvi32 = nvi32[nvi32["fp32"] > 0]
amd64 = amd[np.maximum.accumulate(amd["fp64"]) <= amd["fp64"]]; amd64 = amd64[amd64["fp64"] > 0]
amd32 = amd[np.maximum.accumulate(amd["fp32"]) <= amd["fp32"]]; amd32 = amd32[amd32["fp32"] > 0]

def get_prefix(n):
    if n < 2**10:
        return "%.3g " % (n / 1)
    if n < 2**20:
        return "%.3g K" % (n / 2**10)
    if n < 2**30:
        return "%.3g M" % (n / 2**20)
    if n < 2**40:
        return "%.3g G" % (n / 2**30)
    if n < 2**50:
        return "%.3g T" % (n / 2**40)
    return "%.3g P" % (n / 2**50)

# %%

plt.figure(figsize=(5,5))
plt.semilogy(nvi32["launch"], nvi32["fp32"], ".-", c=colors[2], label=r"NVIDIA \texttt{FP32}")
plt.semilogy(nvi64["launch"], nvi64["fp64"], ".:", c=colors[2], label=r"NVIDIA \texttt{FP64}")
plt.semilogy(amd32["launch"], amd32["fp32"], ".-", c=colors[3], label=r"AMD \texttt{FP32}")
plt.semilogy(amd64["launch"], amd64["fp64"], ".:", c=colors[3], label=r"AMD \texttt{FP64}")
plt.yticks(2**np.arange(8, 17), 2**np.arange(8, 17))
plt.yticks(2**np.arange(8, 17), labels=[get_prefix(p)+"Flops" for p in 2.0**(np.arange(8, 17) + 30)])
plt.minorticks_off()
plt.xticks(rotation=45)
plt.legend()
#plt.xlabel("Launch date", fontsize=14)
# plt.ylabel("Peak performance", fontsize=14)
plt.tight_layout()
plt.grid(which='major')
plt.savefig("gpuperf3.pdf")
os.system("pdfcrop gpuperf3.pdf gpuperf3.pdf")
plt.show()
# %%
