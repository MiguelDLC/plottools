#%%


import matplotlib
import cmocean
import matplotlib as mpl
mpl.rc("text", usetex=True)
mpl.rc("font", family="serif")
mpl.rc("text.latex", preamble=r"""
\usepackage{amsmath}
\usepackage{bm}
\DeclareMathOperator{\newdiff}{d} % use \dif instead
\newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
""")

cmap = matplotlib.cm.get_cmap('Spectral_r')
norm = matplotlib.colors.Normalize(vmin=-5, vmax=5)
cm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

slimcl.copy_from_device(solution,solngpu)
solution = np.ascontiguousarray(solution.reshape((9,-1)).T).reshape(-1,3,3)


plt.figure(figsize=(7.5,6))
ax = plt.gca()
x = mesh.x[:,:,0].ravel()
y = mesh.x[:,:,1].ravel()
eta = solution[:,:,0]
H = solution[:,:,0] + sol_0[:,:,0]
u, v = (solution[:,:,1]/H).ravel()*1000, (solution[:,:,2]/H).ravel()*1000


scs = plt.tricontourf([0, 0, 1], [0, 1, 0], [-5,5, 0], 256, cmap=cmap, vmin=-5, vmax=5)
cs = plt.tricontourf(x, y, eta.ravel()*1000, 6400, cmap=cmap, vmin=-5, vmax=5)
for c in cs.collections:
    c.set_rasterized(True)
cbar = plt.colorbar(scs, ticks=np.linspace(-5, 5, 11), aspect=20)

sub = len(x)//2000
scale = norm((u[0::sub]**2 + v[0::sub]**2)**0.5)
plt.quiver(x[0::sub], y[0::sub], u[0::sub], v[0::sub], scale, scale=150, cmap=cmap)
ax.set_aspect(1)
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.xlabel(r"$\eta$ [mm] and $\bm{\bar{u}}$[mm/s]", fontsize=14)
plt.savefig("Figures/sol.pdf")

os.system("pdfcrop %s %s" % ("Figures/sol.pdf", "Figures/sol.pdf"))
# %%


plt.figure(figsize=(7.5,6))
ax = plt.gca()
cmap = cmocean.cm.deep

eta = plt.tricontourf([0, 0, 1], [0, 1, 0], [200, 1000, 200], 256, cmap=cmap, vmin=200, vmax=1000)
cs = plt.tricontourf(x, y, hm.ravel(), 2**15, cmap=cmap, vmin=200, vmax=1000)
for c in cs.collections:
    c.set_rasterized(True)
cbar = plt.colorbar(eta, ticks=np.linspace(200, 1000, 9), aspect=20)


ax.set_aspect(1)
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.xlabel(r"Bathymetry [m]", fontsize=14)
plt.savefig("Figures/bath.pdf")

os.system("pdfcrop %s %s" % ("Figures/bath.pdf", "Figures/bath.pdf"))
# %%



