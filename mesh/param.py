import numpy as np
from osgeo import ogr
import os
    
#####################
# DOWNLOAD FORCINGS #
#####################
initial_time    = "2021-01-01 00:00:00"
final_time      = "2021-02-01 00:00:00"
shape_file     = "./Shape files/Danube_Black_wo_loops.shp" # shape file containing coast lines
sfile = shape_file.split("/")[-1].split('.')[0]
input_model   = "mercator"
merca = "BS"
nc_data_dir = "nc_Danube_Black-sea_entree_taguee_2nd_20210101_20210201_BS"
#nc_data_dir = "./nc_%s_%s_%s_%s"%(sfile,''.join(initial_time.split(' ')[0].split('-')),''.join(final_time.split(' ')[0].split('-')), merca)
lon_min, lon_max, lat_min, lat_max = 1000, -1000, 1000, -1000
mesh_proj = None

if os.path.isfile(shape_file):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    data = driver.Open(shape_file, 0)
    layer = data.GetLayer()
    for f in layer:
        xmin, xmax, ymin, ymax = f.geometry().GetEnvelope()
        lon_min =  min(lon_min, xmin)
        lon_max =  max(lon_max, xmax)
        lat_min =  min(lat_min, ymin)
        lat_max =  max(lat_max, ymax)
    mean_lon = .5*(lon_min+lon_max)
    mean_lat = .5*(lat_min+lat_max)
    utm_zone = int(np.ceil((mean_lon+180.)/6))
    hemisphere = " +south" if mean_lat < 0. else " +north"
    mesh_proj = "+proj=utm +ellps=WGS84 +zone="+str(utm_zone)+hemisphere
elif os.path.isfile(nc_data_dir+"/projection"):
    with open(nc_data_dir+"/projection","r") as f:
        mesh_proj = f.readline().rstrip()


# forcings that you want to download
forcing_names = [ "bathymetry", "tides", "wind", "currents", "temperature", "salinity" ]

# Rivers
data_path = "./Rivers" # A changer si tu fais des runs different avec les river discharge
streamflow_geo = "%s/streamflow_europe.csv" %(data_path)
streamflow_obs = "%s/discharge_issacea_20200710_20220111.csv" %(data_path)


########
# MESH #
########
reef_file      = None # shape file with reefs (or other feature of interest)
use_bath       = True # True if mesh resolution depends on bathymetry otherwise False
use_bath_grad  = True # True if mesh resolution depends on bathymetry gradient otherwise False
version        = "4.1" #"4.1" en slim4 ou "2" pour slim3
include_rivers = True

mesh_file      = "./meshes/test7_with_rivers_v4.msh"
mesh_file_v3   = "./meshes/test7_with_rivers_v2.msh"

interior_point = (30.079,44.416)
# --- mesh 3D --- #
nb_procs = 24 
dt_min = 10.
dx_min = 1000.
tol_haney = 5 # normally 1, 5 should still be ok
tol_mesh = 0.01 # stop if less than 1% of elements increase
nb_layers = 5
layers = [0, 0.1, 0.2, 0.3, 0.65, 1]
mesh_file_3D = mesh_file[:-4] + f"_3D_nz={nb_layers}_part{nb_procs}.msh"

##################
# PREPRO & HYDRO #
##################
open_tags       = [ "open"]
open_tags_rivers_geo = ["12056318","12053629","12052252","12054160"] #rivers for whish we impose geoglows data
open_tags_rivers_obs = ["12060032"] #rivers for which we impose observations data
closed_tags     = [ "coast", "coast2", "coast3", "riverbank" ] 
use_transport   = True
ramp            = 86400.
vec_prepro2D    = ["bathymetry", "coriolis", "wind", "currents", "bottom", "nudging" ]
vec_prepro2D_V3 = ["bathymetry"]
prepro_data_dir = "./prepro_%s_%s_%s_%s"%(sfile,''.join(initial_time.split(' ')[0].split('-')),''.join(final_time.split(' ')[0].split('-')), merca)
min_depth       = 3
bath_tiff_hr    = ["./bathy/E7_bathy.tif"] #nom des bathys plus precises, a mettre dans ordre de precision (plus precis en dernier)
buffer_distance = 2500
base_bulk       = 2.5e-3
hard_bulk       = 5e-2
base_manning    = 0.025
hard_manning    = 0.025 * 3.162278
output_directory      = "output_%s_%s_%s"%(sfile,''.join(initial_time.split(' ')[0].split('-')),''.join(final_time.split(' ')[0].split('-')))
full_output_directory = output_directory+"/full_export"
rho_mean            = 1e3
g                   = 9.81
dt                  = 900
export_dt           = 3600.
ratio_full_export   = int(86400/export_dt) #every day
checkpoint_dt       = 86400
restart             = False
surface_layer_depth = 12 # [m]
use_manning         = True

#################
# CECI CLUSTERS #
#################
#le nombre de procs est defini dans la partie Mesh/mesh 3D
cluster = "nicgw" # 'nicgw', 'lmgw' or 'zenobe'
user_id = "alaertsl"
institute = "elie" # 'inma' or 'elie'
simu_name = "test_3d_24_rivers"
requested_time = "04:30:00"
email = "lauranne.alaerts@uliege.be"
prepro_slim3 = "prepro2D_v3.py"
prepro_script_name = "prepro2D.py"
hydro_script_name = "run2d.py"
queue = 'large' # for Zenobe, 'large' or 'main' 

if cluster == "zenobe":
    scratch_dir  = f"/SCRATCH/ucl-{institute}/{user_id}/{simu_name}/"
    home_dir = f"/home/acad/ucl-{institute}/{user_id}/{simu_name}/"
    bash_content = f"""#!/bin/bash
# Submission script for Zenobe
#PBS -N {simu_name}
#PBS -q {queue}
#PBS -r y
#PBS -W group_list=slim
#PBS -l walltime={requested_time}
#PBS -l select={int(nb_procs/24)}:ncpus=24:mem=63000mb:mpiprocs=24:ompthreads=1
#PBS -M {email}
#PBS -m abe
"""
    bash_content += """exec > ${PBS_O_WORKDIR}/${PBS_JOBNAME}_${PBS_JOBID}.log
echo "------------------ Work dir --------------------"
cd ${PBS_O_WORKDIR} && echo ${PBS_O_WORKDIR}
echo "------------------ Job Info --------------------"
echo "jobid : $PBS_JOBID"
echo "jobname : $PBS_JOBNAME"
echo "job type : $PBS_ENVIRONMENT"
echo "submit dir : $PBS_O_WORKDIR"
echo "queue : $PBS_O_QUEUE"
echo "user : $PBS_O_LOGNAME"
echo "threads : $OMP_NUM_THREADS"

source /projects/acad/slim/slim-common/slim-env.sh
"""
    bash_content += f"""slim {prepro_slim3}
mpirun --bind-to none python3 {prepro_script_name}
mpirun --bind-to none python3 {hydro_script_name}

qstat -f $PBS_JOBID
"""
else:
    scratch_dir  = f"/scratch/ucl/{institute}/{user_id}/{simu_name}/"
    home_dir     = f"/home/ucl/{institute}/{user_id}/{simu_name}/"
    bash_content = f"""#!/bin/bash

#SBATCH --job-name={simu_name}
#SBATCH --time={requested_time}
#SBATCH --ntasks={nb_procs}
#SBATCH --mem-per-cpu=3500 # megabytes
#SBATCH --partition=batch
#SBATCH --mail-user={email}
#SBATCH --mail-type=ALL

slim {prepro_slim3}
mpirun --bind-to none python3 {prepro_script_name}
mpirun --bind-to none python3 {hydro_script_name}
"""

def write_submission_script():
    if (cluster == "zenobe") and (nb_procs % 24 > 0):
        raise Exception("nb_proc must be multiple of 24 of zenobe !")
    with open("submission.sh", "w") as f:
        f.write(bash_content)

localvars = locals().copy()

def write_new_param():
    required_variables = [ "prepro_data_dir", "nc_data_dir", "mesh_file", "mesh_proj", \
                            "initial_time", "final_time", "vec_prepro2D", "vec_prepro2D_V3", "bath_tiff_hr", \
                            "min_depth", "base_manning", "hard_manning", "base_bulk", \
                            "hard bulk", "ramp", "use_transport", "open_tags", "open_tags_rivers_geo", \
                            "open_tags_rivers_obs", "closed_tags","output_directory", "export_dt", "dt",  \
                            "full_output_directory","ratio_full_export", "rho_mean", "mesh_file_v3", "reef_file", \
                            "use_manning" , "buffer_distance", "include_rivers",\
                            "streamflow_geo","streamflow_obs"]
    with open("param_ceci.py","w") as fo :
        for name, value in localvars.items():
            if name not in required_variables:
                continue
            if name in ["prepro_data_dir","nc_data_dir", "output_directory"] :
                value = scratch_dir+os.path.split(value)[-1]
            if name in ["streamflow_geo","streamflow_obs"]:
                value = scratch_dir+value[2:]
            elif name in ["mesh_file", "mesh_file_v3"]:
                value = os.path.split(value)[-1]
            elif name == "bath_tiff_hr":
                value = [ scratch_dir+os.path.split(v)[-1] for v in value ]
            elif name == "reef_file" and value is not None:
                value = os.path.split(value)[-1]
            if name == "full_output_directory":
                value = "output_directory+'/full_export'"
            elif isinstance(value,str):
                value = f"\"{value}\""
            fo.write(f"{name:21s} = {value}\n")

def copy_to_cluster(prepro_made=False):
    write_submission_script()
    write_new_param()
    with open("create_directories.sh", "w") as f:
        f.write( f"mkdir {home_dir}\nmkdir {scratch_dir}")
    os.system(f"scp create_directories.sh {cluster}:~/")
    print("=====================================================")
    print("If target directories don't exist on clusters, please")
    print("connect to cluster and run create_directories.sh")
    print("=====================================================")
    directory = prepro_data_dir if prepro_made else nc_data_dir
    os.system( f"scp -r {directory} {' '.join(bath_tiff_hr)} {data_path} {cluster}:{scratch_dir}/./" )
    meshes = [ mesh_file, mesh_file_v3 ]
    mesh_str = " ".join(meshes)
    scripts = "prepro2D_v3.py prepro2D.py prepro_util.py run2d.py "
    reef_str = '' if reef_file is None else reef_file
    os.system( f"scp {mesh_str} submission.sh {scripts} {reef_str} {cluster}:{home_dir}")
    os.system( f"scp param_ceci.py {cluster}:{home_dir}/param.py")
