#%%
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import datetime
epoch = datetime.datetime.utcfromtimestamp(0)

import dateparser
here = os.path.dirname(__file__)
#%%
vendor = "amd"
with open(here + "/gpu-perf/" + vendor + "-gpu.csv", "r") as f:
    data = f.read()

gens = data.split("\n\n")

gplist = []

keys = ["Model", "Launch", "Double precision", "Single precision"]
for gen in gens:
    with open(here + "/gpu-perf/" + "tmp.csv", "w") as f:
        lines = gen.split("\n")
        #print(lines[2])
        factor = 1000 if "TFLOPS" in lines[0] else 1
        gen = "\n".join(lines[1:])
        f.write(gen)
    df = pd.read_csv(here + "/gpu-perf/" + "tmp.csv")
    if not (("Model" in df) and ("Single precision" in df)):
        continue
    
    hasdouble = "Double precision" in df
    for i, row in df.iterrows():
        model = row["Model"]
        try:
            date = dateparser.parse(row["Launch"])
            sp = str(row["Single precision"])
            sp = sp.split("-")[-1] if '-' in sp else sp
            fp32 = float(sp) * factor

            if hasdouble:
                dp = str(row["Double precision"])
                dp = dp.split("-")[-1] if '-' in dp else dp
                try:
                    fp64 = float(dp) * factor
                except:
                    fp64=np.nan
            else:
                fp64 = np.nan
            
        except Exception as e:
            continue

        if not np.isnan(fp32) and date is not None:
            deltat = (date - epoch)
            gplist.append([model, deltat, fp32, fp64])

# %%
gpudata = np.array(gplist, dtype=object)
order = np.argsort(gpudata[:,0])
gpudata = gpudata[order,:]

count = 1
gplist2 = [gpudata[0]]
for i in range(1, len(gpudata)):
    r = gpudata[i]
    if r[0] == gplist2[-1][0]:
        gplist2[-1][1:] += r[1:]
        count += 1
    else:
        gplist2[-1][1:] /= count
        gplist2.append(r)
        count = 1
gpudata = np.array(gplist2, dtype=object)
#%%




order = np.argsort(gpudata[:,1])
gpudata = gpudata[order,:]
name = gpudata[:,0]
time = gpudata[:,1] + epoch
fp32 = gpudata[:,2].astype(np.float64)
fp64 = gpudata[:,3].astype(np.float64)



# %%
plt.semilogy(time, fp32, '.')
#for (i, (t, fp, l)) in enumerate(zip(time, fp32, name)):
#    plt.text(t, fp, l, fontsize=6, rotation=45)

plt.grid()
plt.show()

plt.semilogy(time, fp64, '.')
#for (i, (t, fp, l)) in enumerate(zip(time, fp64, name)):
#    if not np.isnan(fp):
#        plt.text(t, fp, l, fontsize=6, rotation=45)
plt.grid()
plt.show()
# %%

with open(vendor+"-summary.csv", "w") as f:
    for row in gpudata:
        name, delta_t, f32, f64 = row
        date = epoch + delta_t
        strdate = date.strftime("%Y-%m-%d")
        f.write("%s,%s,%.18e,%.18e\n" % (name, strdate, f32, f64))
    

# %%
