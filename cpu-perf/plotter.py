#%%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime

def tconv(x):
    if isinstance(x, str):
        return datetime.strptime(x, "%b-%Y")
    else:
        return -1


colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']

df = pd.read_csv("data.csv")
df["HW Avail"] = df["HW Avail"].apply(tconv)
good = df["HW Avail"] != -1
df = df[good]


# %%
plt.figure(figsize=(10,10))
plt.plot(df["HW Avail"], df["Result"], ".")
plt.semilogy([0, 1000])

# %%
