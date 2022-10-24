#%%
import slim4
from slim4 import slim2d
from matplotlib import pyplot as plt

partname = slim2d.partition_mesh("mesh_Danube_Black_Sea.msh")
mesh = slim2d.Mesh(partname, None)

# %%
plt.triplot(mesh.xnodes[:,0], mesh.xnodes[:,1], triangles = mesh.triangles, c="k", lw=0.5)
plt.gca().set_aspect(1)
plt.show()
# %%
