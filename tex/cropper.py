#%%
import os
fnames = os.listdir()
for name in fnames:
    os.system("pdfcrop %s %s " % (name, name))
# %%
