#%%
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatch
import cmocean
import os
#matplotlib.rc("text", usetex=True)
#matplotlib.rc("font", family="serif")

# matplotlib.rc("text.latex", preamble=r"""
# \usepackage{amsmath}
# \usepackage{bm}
# \DeclareMathOperator{\newdiff}{d} % use \dif instead
# \newcommand{\dif}{\newdiff\!} %the correct way to do derivatives
# """)

def slabel(t):
    if t < 1e3:
        return "%.2f" % t
    if t < 1e6:
        return "%.2f K" % (t*1e-3)
    if t < 1e9:
        return "%.2f M" % (t*1e-6)
    if t < 1e12:
        return "%.2f G" % (t*1e-9)
    else:
        return "%.2f T" % (t*1e-12)


arrowprop = {
    "linewidth" : 2.3,
    "arrowstyle" : '<|-|>',
    "mutation_scale" : 15,
    "joinstyle" : 'miter',
    "fill" : True,
    "color" : "k"
}

def addrec(cx, cy, w, h, **kwargs):
    llx = cx - w/2
    lly = cy - h/2
    rect = mpatch.Rectangle((llx, lly), w, h, **kwargs)
    plt.gca().add_patch(rect)

def addtxt(cx, cy, s, **kwargs):
    ang = np.deg2rad(kwargs.get("rotation", 0))
    dx =  np.sin(ang) * 0.03
    dy = -np.cos(ang) * 0.03
    if 'fontsize' not in kwargs:
        kwargs['fontsize'] = 10
    plt.text(cx+dx, cy+dy, s, ha='center', va='center', **kwargs)

def harrow(x0, x1, y, direct=True, txt=None, txtargs={}, **kwarks):
    options = {}
    options.update(arrowprop)
    options.update(kwarks)
    dx = x1 - x0
    if direct:
        options["arrowstyle"] = '-|>'
        x0 = x0 + 0.03*np.sign(dx)
        dx = x1 - x0

    arrow = mpatch.FancyArrowPatch((x0, y), (x1, y), **options)
    plt.gca().add_patch(arrow)
    if txt is not None:
        cx = (x0+x1)/2
        f = txtargs.pop("under", 1)
        txtargs["fontsize"] = 10
        addtxt(cx, y+f*0.27, txt, **txtargs)



def get_L1_cache_hit_ratio(kernel):
    hits = (
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_local_op_ld_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_ld_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_ld_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_texture_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_st_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_local_op_st_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_st_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_red_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_red_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_atom_lookup_hit.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_atom_lookup_hit.sum"]) )

    misses = (
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_local_op_ld_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_ld_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_ld_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_texture_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_st_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_local_op_st_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_st_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_red_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_red_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_lsu_mem_global_op_atom_lookup_miss.sum"]) +
   float(kernel["l1tex__t_sectors_pipe_tex_mem_surface_op_atom_lookup_miss.sum"]) )

    return hits/(hits+misses)

# %%


def get_data(kernel):
    #kernel-L1-global
    kern_global_load_req = float(kernel["l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum"])
    kern_global_load_req_ratio = float(kernel["l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum.pct_of_peak_sustained_elapsed"])/100
    kern_global_stor_req = float(kernel["l1tex__t_requests_pipe_lsu_mem_global_op_st.sum"])
    kern_global_stor_req_ratio = float(kernel["l1tex__t_requests_pipe_lsu_mem_global_op_st.sum.pct_of_peak_sustained_elapsed"])/100

    kern_global_load_ins = float(kernel["sass__inst_executed_global_loads"])
    kern_global_stor_ins = float(kernel["sass__inst_executed_global_stores"])
    kern_global_inst = kern_global_load_ins + kern_global_stor_ins

    #kernelL1-local
    kern_local_load_req = float(kernel["l1tex__t_requests_pipe_lsu_mem_local_op_ld.sum"])
    kern_local_load_req_ratio = float(kernel["l1tex__t_requests_pipe_lsu_mem_local_op_ld.sum.pct_of_peak_sustained_elapsed"])/100
    kern_local_stor_req = float(kernel["l1tex__t_requests_pipe_lsu_mem_local_op_st.sum"])
    kern_local_stor_req_ratio = float(kernel["l1tex__t_requests_pipe_lsu_mem_local_op_st.sum.pct_of_peak_sustained_elapsed"])/100

    kern_lo_l_ins = float(kernel["sass__inst_executed_local_loads"])
    kern_lo_s_ins = float(kernel["sass__inst_executed_local_stores"])
    kern_lo_inst = kern_lo_l_ins + kern_lo_s_ins

    L1_cache_hit_ratio = get_L1_cache_hit_ratio(kernel)

    #kernel shared
    kern_shared_load_req_ratio = float(kernel["l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum.pct_of_peak_sustained_elapsed"])/100
    kern_shared_stor_req_ratio = float(kernel["l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum.pct_of_peak_sustained_elapsed"])/100

    kern_shared_load_req = float(kernel["sass__inst_executed_shared_loads"])
    kern_shared_stor_req = float(kernel["sass__inst_executed_shared_stores"])
    kern_shared_inst = kern_shared_load_req + kern_shared_stor_req

    # L1-L2
    l1_l2_read  = 32*float(kernel["lts__t_sectors_srcunit_tex_op_read.sum"])
    l1_l2_read_ratio = float(kernel["lts__t_sectors_srcunit_tex_op_read.avg.pct_of_peak_sustained_elapsed"])/100
    l1_l2_write = 32*float(kernel["lts__t_sectors_srcunit_tex_op_write.sum"])
    l1_l2_write_ratio = float(kernel["lts__t_sectors_srcunit_tex_op_write.avg.pct_of_peak_sustained_elapsed"])/100

    l2_hit = float(kernel["lts__t_sectors_lookup_hit.sum"])
    l2_miss = float(kernel["lts__t_sectors_lookup_miss.sum"])
    l2_hit_ratio = l2_hit / (l2_hit + l2_miss)

    # L2-global
    dram_read = float(kernel["dram__bytes_read.sum"])*1e6
    dram_read_ratio = float(kernel["dram__bytes_read.sum.pct_of_peak_sustained_elapsed"])/100
    dram_write = float(kernel["dram__bytes_write.sum"])*1e6
    dram_write_ratio = float(kernel["dram__bytes_write.sum.pct_of_peak_sustained_elapsed"])/100

    shared = [
        kern_shared_load_req_ratio,
        kern_shared_stor_req_ratio,
        kern_shared_load_req,
        kern_shared_stor_req,
        kern_shared_inst,
    ]

    all = [
        kern_global_load_req,
        kern_global_load_req_ratio,
        kern_global_stor_req,
        kern_global_stor_req_ratio,
        kern_global_inst,

        kern_local_load_req,
        kern_local_load_req_ratio,
        kern_local_stor_req,
        kern_local_stor_req_ratio,
        kern_lo_inst,

        L1_cache_hit_ratio,

        l1_l2_read,
        l1_l2_read_ratio,
        l1_l2_write,
        l1_l2_write_ratio,
        l2_hit_ratio,
        dram_read,
        dram_read_ratio,
        dram_write,
        dram_write_ratio,
        shared,
    ]
    return all

# %%

def doplot(all, outfname, cbar=True):
    [kern_global_load_req,
    kern_global_load_req_ratio,
    kern_global_stor_req,
    kern_global_stor_req_ratio,
    kern_global_inst,

    kern_local_load_req,
    kern_local_load_req_ratio,
    kern_local_stor_req,
    kern_local_stor_req_ratio,
    kern_lo_inst,

    L1_cache_hit_ratio,

    l1_l2_read,
    l1_l2_read_ratio,
    l1_l2_write,
    l1_l2_write_ratio,
    l2_hit_ratio,
    dram_read,
    dram_read_ratio,
    dram_write,
    dram_write_ratio, shared] = all


    cmap = matplotlib.cm.get_cmap('hot')



    txtargs={"under" : -1}

    txthsep = 0.15

    glspos = 2.9
    glsw = 0.7
    glsh = 0.5

    l1pos = 6.2
    l1w = 0.65

    l2pos = 9.4
    l2w = 0.65

    drampos = 12

    fig = plt.figure(figsize=(17,4))
    ax = plt.gca()
    #kernel
    addrec(0, 0, 0.5, 4, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(0, 0, "Kernel", rotation=90)

    #global
    addrec(glspos, (2-glsh), 2*glsw,2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, (2-glsh), "Global")
    harrow(0.25, glspos-glsw, (2-glsh), False, txt=slabel(kern_global_inst) + " Inst")
    harrow(l1pos-l1w, glspos+glsw, 2-glsh+txthsep, True, txt=slabel(kern_global_load_req) + " Req", color=cmap(kern_global_load_req_ratio))
    harrow(glspos+glsw, l1pos-l1w, 2-glsh-txthsep, True, txt=slabel(kern_global_stor_req) + " Req", txtargs={"under" : -1}, color=cmap(kern_global_stor_req_ratio))

    #local
    addrec(glspos, -(2-glsh), 2*glsw, 2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, -(2-glsh), "Local")
    harrow(0.25, glspos-glsw, -(2-glsh), False, txt=slabel(kern_lo_inst) + " Inst")
    harrow(l1pos-l1w, glspos+glsw, -(2-glsh)+txthsep, True, txt=slabel(kern_local_load_req) + " Req", color=cmap(kern_global_load_req_ratio))
    harrow(glspos+glsw, l1pos-l1w, -(2-glsh)-txthsep, True, txt=slabel(kern_local_stor_req) + " Req", txtargs={"under" : -1}, color=cmap(kern_global_stor_req_ratio))

    #L1
    addrec(l1pos, 0, 2*l1w, 4, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l1pos, 0, "L1/TEX\nCache\n\nHit rate:\n%.2f" % (L1_cache_hit_ratio*100) + "%", color="w")
    harrow(l2pos-l2w, l1pos+l1w,  txthsep, True, txt=slabel(l1_l2_read ) + "B", color=cmap(l1_l2_read_ratio))
    harrow(l1pos+l1w, l2pos-l2w, -txthsep, True, txt=slabel(l1_l2_write) + "B", txtargs={"under" : -1}, color=cmap(l1_l2_write_ratio))

    #L2
    addrec(l2pos, 0, 2*l2w, 4, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l2pos, 0, "L2 Cache\n\nHit rate:\n%.2f" % (l2_hit_ratio*100) + "%", color="w")
    harrow(drampos-0.25, l2pos+l2w, txthsep, True, txt=slabel(dram_read ) + "B", color=cmap(dram_read_ratio))
    harrow(l2pos+l2w, drampos-0.25, -txthsep, True, txt=slabel(dram_write) + "B", txtargs={"under" : -1}, color=cmap(dram_write_ratio))

    #dram
    addrec(drampos, 0, 0.5, 4, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(drampos, 0, "Device memory", rotation=90, color="w")
    loopx = np.array([ 0,  1, 1, 0])*0.1 + drampos - 0.25
    loopy = np.array([-3, -2.5, 2.5, 3])*0.14

    plt.fill(loopx, loopy, color=cmap(dram_read_ratio + dram_write_ratio))



    plt.xlim([-1, 17])
    plt.ylim([-3, 3])
    plt.gca().axis("off")

    if cbar:
        dyp = 0.245
        axes = fig.add_axes([0.72, dyp+0.005, 0.007, 1-2*dyp])
        cbar = matplotlib.colorbar.ColorbarBase(axes, cmap=cmap, orientation='vertical', ticks=np.linspace(0, 1, 6))
        cbar.ax.set_yticklabels(["%2d" % (20*i) + "%" for i in range(6)], fontsize=9)
        axes.yaxis.set_label_position('left')
        cbar.ax.set_ylabel('% Peak', fontsize=9)

    plt.savefig(outfname)
    os.system("pdfcrop %s %s" % (outfname, outfname))

    plt.show()
 # %%


def doplot2(all, outfname, cbar=False):
    [kern_global_load_req,
    kern_global_load_req_ratio,
    kern_global_stor_req,
    kern_global_stor_req_ratio,
    kern_global_inst,

    kern_local_load_req,
    kern_local_load_req_ratio,
    kern_local_stor_req,
    kern_local_stor_req_ratio,
    kern_lo_inst,

    L1_cache_hit_ratio,

    l1_l2_read,
    l1_l2_read_ratio,
    l1_l2_write,
    l1_l2_write_ratio,
    l2_hit_ratio,
    dram_read,
    dram_read_ratio,
    dram_write,
    dram_write_ratio, shared] = all

    [kern_shared_load_req_ratio,
    kern_shared_stor_req_ratio,
    kern_shared_load_req,
    kern_shared_stor_req,
    kern_shared_inst ] = shared


    cmap = matplotlib.cm.get_cmap('hot')



    txtargs={"under" : -1}

    txthsep = 0.15

    glspos = 2.9
    glsw = 0.7
    glsh = 0.5
    glsph = 0.9

    l1pos = 6.2
    l1w = 0.65

    l2pos = 9.4
    l2w = 0.65

    drampos = 12

    kernh = 3.6

    fig = plt.figure(figsize=(17,4))
    ax = plt.gca()
    #kernel
    addrec(0, 0, 0.5, 2*kernh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(0, 0, "Kernel", rotation=90)

    #global
    addrec(glspos, (kernh-glsph), 2*glsw,2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, (kernh-glsph), "Global")
    harrow(0.25, glspos-glsw, (kernh-glsph), False, txt=slabel(kern_global_inst) + " Inst")
    harrow(l1pos-l1w, glspos+glsw, kernh-glsph+txthsep, True, txt=slabel(kern_global_load_req) + " Req", color=cmap(kern_global_load_req_ratio))
    harrow(glspos+glsw, l1pos-l1w, kernh-glsph-txthsep, True, txt=slabel(kern_global_stor_req) + " Req", txtargs={"under" : -1}, color=cmap(kern_global_stor_req_ratio))

    #local
    addrec(glspos, 0, 2*glsw, 2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, 0, "Local")
    harrow(0.25, glspos-glsw, 0, False, txt=slabel(kern_lo_inst) + " Inst")
    harrow(l1pos-l1w, glspos+glsw, +txthsep, True, txt=slabel(kern_local_load_req) + " Req", color=cmap(kern_global_load_req_ratio))
    harrow(glspos+glsw, l1pos-l1w, -txthsep, True, txt=slabel(kern_local_stor_req) + " Req", txtargs={"under" : -1}, color=cmap(kern_global_stor_req_ratio))

    #shared
    addrec(glspos, -(kernh-glsph), 2*glsw, 2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, -(kernh-glsph), "Shared")
    harrow(0.25, glspos-glsw, -(kernh-glsph), False, txt=slabel(kern_shared_inst) + " Inst")
    harrow(l1pos-l1w, glspos+glsw, -(kernh-glsph)+txthsep, True, txt=slabel(kern_shared_load_req) + " Req", color=cmap(kern_shared_load_req_ratio))
    harrow(glspos+glsw, l1pos-l1w, -(kernh-glsph)-txthsep, True, txt=slabel(kern_shared_stor_req) + " Req", txtargs={"under" : -1}, color=cmap(kern_shared_stor_req_ratio))

    #L1
    addrec(l1pos, kernh/2-glsph/2, 2*l1w, kernh+glsph, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l1pos, kernh/2-glsph/2, "L1/TEX\nCache\n\nHit rate:\n%.2f" % (L1_cache_hit_ratio*100) + "%", color="w")
    harrow(l2pos-l2w, l1pos+l1w, 1.5-glsh/2+txthsep, True, txt=slabel(l1_l2_read ) + "B", color=cmap(l1_l2_read_ratio))
    harrow(l1pos+l1w, l2pos-l2w, 1.5-glsh/2-txthsep, True, txt=slabel(l1_l2_write) + "B", txtargs={"under" : -1}, color=cmap(l1_l2_write_ratio))

    #shared (L1-level)
    addrec(l1pos, -(kernh-glsph), 2*l1w, 2*glsph, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l1pos, -(kernh-glsph), "Shared\nmemory", color="w")


    #L2
    addrec(l2pos, 0, 2*l2w, 2*kernh, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l2pos, 0, "L2 Cache\n\nHit rate:\n%.2f" % (l2_hit_ratio*100) + "%", color="w")
    harrow(drampos-0.25, l2pos+l2w, txthsep, True, txt=slabel(dram_read ) + "B", color=cmap(dram_read_ratio))
    harrow(l2pos+l2w, drampos-0.25, -txthsep, True, txt=slabel(dram_write) + "B", txtargs={"under" : -1}, color=cmap(dram_write_ratio))

    #dram
    addrec(drampos, 0, 0.5, 2*kernh, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(drampos, 0, "Device memory", rotation=90, color="w")
    loopx = np.array([ 0,  1, 1, 0])*0.1 + drampos - 0.25
    loopy = np.array([-3, -2.5, 2.5, 3])*0.14

    plt.fill(loopx, loopy, color=cmap(dram_read_ratio + dram_write_ratio))



    plt.xlim([-1, 17])
    plt.ylim([-4.2, 4.2])
    plt.gca().axis("off")

    if cbar:
        dyp = 0.175
        axes = fig.add_axes([0.72, dyp, 0.007, 1-2*dyp])
        cbar = matplotlib.colorbar.ColorbarBase(axes, cmap=cmap, orientation='vertical', ticks=np.linspace(0, 1, 6))
        cbar.ax.set_yticklabels(["%2d" % (20*i) + "%" for i in range(6)], fontsize=9)
        axes.yaxis.set_label_position('left')
        cbar.ax.set_ylabel('% Peak', fontsize=9)
    
    plt.savefig(outfname)
    os.system("pdfcrop %s %s" % (outfname, outfname))

    plt.show()

#%%
for i in range(4):
    num = "0" + str(i)
    df = pd.read_csv("profile%s.csv" % num)
    dudt = df.iloc[13]
    all = get_data(dudt)
    figname = "../Figures/memchart%s.pdf" % num
    doplot(all, figname, False)

for i in range(4,6):
    num = "0" + str(i)
    df = pd.read_csv("profile%s.csv" % num)
    dudt = df.iloc[13]
    all = get_data(dudt)
    figname = "../Figures/memchart%s.pdf" % num
    doplot2(all, figname, False)


# %%


def doplot3(outfname):
    cmap = matplotlib.cm.get_cmap('hot')



    txtargs={"under" : -1}

    glspos = 1.95
    glsw = 0.7
    glsh = 0.5
    glsph = 0.9

    l1pos = 4.3
    l1w = 0.65

    l2pos = 7
    l2w = 0.65

    drampos = 9.5

    kernh = 3.6

    fig = plt.figure(figsize=(10,4))
    ax = plt.gca()
    #kernel
    addrec(0, 0, 0.5, 2*kernh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(0, 0, "Kernel", rotation=90)

    #global
    addrec(glspos, (kernh-glsph), 2*glsw,2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, (kernh-glsph), "Global")
    harrow(0.25, glspos-glsw, (kernh-glsph), False)
    harrow(l1pos-l1w, glspos+glsw, kernh-glsph, False)

    #local
    addrec(glspos, 0, 2*glsw, 2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, 0, "Local")
    harrow(0.25, glspos-glsw, 0, False)
    harrow(l1pos-l1w, glspos+glsw, 0, False)

    #shared
    addrec(glspos, -(kernh-glsph), 2*glsw, 2*glsh, linewidth=1, edgecolor='k', facecolor='limegreen')
    addtxt(glspos, -(kernh-glsph), "Shared")
    harrow(0.25, glspos-glsw, -(kernh-glsph), False)
    harrow(l1pos-l1w, glspos+glsw, -(kernh-glsph), False)

    #L1
    addrec(l1pos, kernh/2-glsph/2, 2*l1w, kernh+glsph, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l1pos, kernh/2-glsph/2, "L1/TEX\nCache", color="w")
    harrow(l2pos-l2w, l1pos+l1w, 1.5-glsh/2, False, txt=slabel(1450e9) + "B/s", linewidth=6, txtargs={"under" : 2}, color=cmap(0.5))

    #shared (L1-level)
    addrec(l1pos, -(kernh-glsph), 2*l1w, 2*glsph, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l1pos, -(kernh-glsph), "Shared\nmemory", color="w")


    #L2
    addrec(l2pos, 0, 2*l2w, 2*kernh, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(l2pos, 0, "L2 Cache", color="w")
    harrow(drampos-0.25, l2pos+l2w, 0, False, txt="448.0 GB/s", linewidth=3, txtargs={"under" : 2}, color=cmap(0.5))

    #dram
    addrec(drampos, 0, 0.5, 2*kernh, linewidth=1, edgecolor='k', facecolor='darkblue')
    addtxt(drampos, 0, "Device memory", rotation=90, color="w")

    plt.xlim([-1, 10])
    plt.ylim([-4.2, 4.2])
    plt.gca().axis("off")
    
    plt.savefig(outfname)
    os.system("pdfcrop %s %s" % (outfname, outfname))

    plt.show()



figname = "../Figures/memchart-max.pdf"
doplot3(figname)

# %%
