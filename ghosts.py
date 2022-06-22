#%%
import slim4
from slim4 import slim2d
from slim4 import slimcl
from slim4.slimcl import d2
import os
import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.rc("text", usetex=True)
#matplotlib.rc("font", family="serif")
# matplotlib.rc("text.latex", preamble=r"""
# \usepackage{amsmath}
# \usepackage{bm}
# \DeclareMathOperator{\newdiff}{d} % use \dif instead
# \newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
# """)

import cmocean

from stommel_ref import UVEtaAnalytic as analytic
from line_profiler import LineProfiler

tic = time.time()
scalar = np.float32
#%%

colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728', u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']
############# Mesh initialization #############
comm_rank = slim4.mpi_rank()
comm_size = slim4.mpi_size()
node_rank = slimcl.get_node_rank()
node_size = slimcl.get_node_size()
if comm_size > 1 :
    partname = slim2d.partition_mesh("square.msh")
    mesh = slim2d.Mesh(partname, None)
else :
    fpath = os.path.dirname(os.path.realpath(__file__))
    mesh = slim2d.Mesh(fpath + "/square.msh",None)


if  mesh.n_triangles_p < 500 * 0:
    neighbours = mesh.neighbours
    centroids = mesh.x.mean(axis=1)
    #plt.plot(centroids[:mesh.n_intern,0], centroids[:mesh.n_intern,1], alpha=0.5)
    #plt.plot(centroids[mesh.n_intern:,0], centroids[mesh.n_intern:,1], alpha=0.5)
    #plt.plot(centroids[mesh.boundary_edges[:,0] ,0], centroids[mesh.boundary_edges[:,0] ,1])
    plt.gca().set_aspect(1)
    lab = True
    for i in range(mesh.n_triangles):
        x, y = mesh.x[i].T
        if lab:
            plt.fill(x, y, c=colors[0], alpha=0.5, label="Normal triangles")
            lab = False
        else:
            plt.fill(x, y, c=colors[0], alpha=0.5)

    lab = True
    for i in range(mesh.n_triangles, mesh.n_triangles_p):
        x, y = mesh.x[i].T
        if lab:
            plt.fill(x, y, c=colors[3], alpha=0.5, label="Ghost triangles")
            lab = False
        else:
            plt.fill(x, y, c=colors[3], alpha=0.5)
    
    plt.triplot(mesh.xnodes[:, 0], mesh.xnodes[:, 1], mesh.triangles[:mesh.n_triangles_p], color="k", lw=0.5)
    for el, _, cl, _ in mesh.ghost_edges:
        nodes = [cl, (cl+1)%3]
        n0, n1 = mesh.triangles[el][nodes]
        x, y = mesh.xnodes[[n0,n1]].T
        plt.plot(x, y, "k", lw=1.3)
    
    plt.xlim([-5e5*1.001, 5e5*1.001])
    plt.ylim([-5e5*1.001, 5e5*1.001])
    plt.axis("off")
    
    if comm_rank == 1:
        plt.legend(loc="upper left")
    
    fname = "Figures/meshghost-%d.pdf" % comm_rank
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()
    
# %%


if  mesh.n_triangles_p < 500:
    neighbours = mesh.neighbours
    centroids = mesh.x.mean(axis=1)
    #plt.plot(centroids[:mesh.n_intern,0], centroids[:mesh.n_intern,1], alpha=0.5)
    #plt.plot(centroids[mesh.n_intern:,0], centroids[mesh.n_intern:,1], alpha=0.5)
    #plt.plot(centroids[mesh.boundary_edges[:,0] ,0], centroids[mesh.boundary_edges[:,0] ,1])
    plt.gca().set_aspect(1)
    lab = True
    for i in range(mesh.n_intern):
        x, y = mesh.x[i].T
        if lab:
            plt.fill(x, y, c=colors[0], alpha=0.5, label="Internal triangles")
            lab = False
        else:
            plt.fill(x, y, c=colors[0], alpha=0.5)

    lab = True
    for i in range(mesh.n_intern, mesh.n_triangles):
        x, y = mesh.x[i].T
        if lab:
            plt.fill(x, y, c="goldenrod", alpha=0.5, label="Boundary triangles")
            lab = False
        else:
            plt.fill(x, y, c="goldenrod", alpha=0.5)

    lab = True
    for i in range(mesh.n_triangles, mesh.n_triangles_p):
        x, y = mesh.x[i].T
        if lab:
            plt.fill(x, y, c=colors[3], alpha=0.5, label="Ghost triangles")
            lab = False
        else:
            plt.fill(x, y, c=colors[3], alpha=0.5)
    
    plt.triplot(mesh.xnodes[:, 0], mesh.xnodes[:, 1], mesh.triangles[:mesh.n_triangles_p], color="k", lw=0.5)
    for el, _, cl, _ in mesh.ghost_edges:
        nodes = [cl, (cl+1)%3]
        n0, n1 = mesh.triangles[el][nodes]
        x, y = mesh.xnodes[[n0,n1]].T
        plt.plot(x, y, "k", lw=1.3)
    
    plt.xlim([-5e5*1.001, 5e5*1.001])
    plt.ylim([-5e5*1.001, 5e5*1.001])
    plt.axis("off")
    
    if comm_rank == 1:
        plt.legend(loc="upper left")
    
    fname = "Figures/meshghostv2-%d.pdf" % comm_rank
    plt.savefig(fname)
    os.system("pdfcrop %s %s" % (fname, fname))
    plt.show()
    
# %%
