#%%
from ctypes import c_int
import slim4
from slim4 import slim2d
import os
import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt
import cmocean

from slim4.slimcl import cu as launcher
from stommel_ref import UVEtaAnalytic as analytic
from line_profiler import LineProfiler

#%%
tic = time.time()
scalar = np.float32
cc = "gcc"
############# Mesh initialization #############
comm_rank = slim4.mpi_rank()
comm_size = slim4.mpi_size()
node_rank = launcher.get_node_rank()
node_size = launcher.get_node_size()
if comm_size > 1 :
    partname = slim2d.partition_mesh("square.msh")
    mesh = slim2d.Mesh(partname, None)
else :
    fpath = os.path.dirname(os.path.realpath(__file__))
    mesh = slim2d.Mesh(fpath + "/square.msh",None)

cmap = matplotlib.cm.get_cmap('brg')
nt = len(mesh.x)
color = cmap(np.linspace(0, 1, nt))

plt.figure(figsize=(6,6))
neighbours = mesh.neighbours
centroids = mesh.x.mean(axis=1)
plt.triplot(mesh.xnodes[:, 0], mesh.xnodes[:, 1], mesh.triangles[:mesh.n_triangles], color="k", lw=1, alpha=0.9)
for i in range(nt-1):
    plt.plot(centroids[i:i+2,0], centroids[i:i+2,1], '.-', lw=1, alpha=0.5, c=color[i])
plt.gca().set_aspect(1)
plt.gca().axis("off")
plt.savefig("Figures/order0.pdf")
os.system("pdfcrop %s %s" % ("Figures/order0.pdf", "Figures/order0.pdf"))
plt.show()

mesh.reorder_hilbert()
plt.figure(figsize=(6,6))
neighbours = mesh.neighbours
centroids = mesh.x.mean(axis=1)
plt.triplot(mesh.xnodes[:, 0], mesh.xnodes[:, 1], mesh.triangles[:mesh.n_triangles], color="k", lw=1, alpha=0.9)
for i in range(nt-1):
    plt.plot(centroids[i:i+2,0], centroids[i:i+2,1], '.-', lw=1, alpha=1, c=color[i])
plt.gca().set_aspect(1)
plt.gca().axis("off")
plt.savefig("Figures/orderh.pdf")
os.system("pdfcrop %s %s" % ("Figures/orderh.pdf", "Figures/orderh.pdf"))
plt.show()


# %%
