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


