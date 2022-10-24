import seamsh
from seamsh.geometry import CurveType
import seamsh.geometry
import numpy as np
from osgeo import osr
import pyproj
import param
import gdal

###########################################
# VARIABLES OF PARAM.PY USED BY THIS SCRIPT
###########################################
#   * shape_file
#   * reef_file (if mesh size depends on distance to reef/structure/etc.)
#   * use_bath 
#   * use_bath_grad 
#   * mesh_file
#   * interior_point
# 
# WARNING: download_forcings must be run in order to use bathymetry (gradient)
###########################################

file_base = param.nc_data_dir[:-1] if param.nc_data_dir[-1] == "/" else param.nc_data_dir
path_to_bathy = file_base

# 1. Define projections and domain
domain_srs = osr.SpatialReference()
domain_srs.ImportFromProj4(param.mesh_proj)
lonlat_proj = osr.SpatialReference()
lonlat_proj.ImportFromProj4("+proj=latlong +ellps=WGS84 +unit=degrees")

domain = seamsh.geometry.Domain(domain_srs)
#domain_reefs = seamsh.geometry.Domain(domain_srs)

# 2. Add coastlines/features to domain
domain.add_boundary_curves_shp(param.shape_file, "physical", CurveType.POLYLINE)
#domain_reefs.add_interior_curves_shp(param.reef_file, "physical", CurveType.POLYLINE)

# 3. Define distances to features for mesh resolutions
dist_coast     = seamsh.field.Distance(domain, 100, ["coast"])
dist_coast2 = seamsh.field.Distance(domain, 100, ["coast2"])
dist_coast3 = seamsh.field.Distance(domain, 100, ["coast3"])
dist_river   = seamsh.field.Distance(domain, 100, ["riverbank"])
dist_open   = seamsh.field.Distance(domain, 100, ["open"])

# 4. Read bathymetry file and compute gradient if needed
if param.use_bath or param.use_bath_grad:
    bath_field = seamsh.field.Raster(path_to_bathy+"/bath.tiff")
if param.use_bath_grad:
    ll_proj = pyproj.Proj("+proj=latlong +ellps=WGS84 +unit=degrees")
    utm_proj = pyproj.Proj(param.mesh_proj)
    tif = gdal.Open(path_to_bathy+"/bath.tiff")
    geo_transform = tif.GetGeoTransform()
    ox, dx, _, oy, _, dy = geo_transform
    arr = tif.ReadAsArray()
    ny, nx = arr.shape
    lon, lat = ox + np.arange(nx)*dx, oy + np.arange(ny)*dy
    xmin, ymin = pyproj.transform(ll_proj, utm_proj, lon.min(), lat.min())
    xmax, ymax = pyproj.transform(ll_proj, utm_proj, lon.max(), lat.max())
    dx, dy = (xmax-xmin)/(nx-1), (ymax-ymin)/(ny-1)
    grad_x, grad_y = np.gradient(arr, dy, dx, axis=[1,0], edge_order=2)
    grad = np.hypot(grad_x, grad_y)
    tif = gdal.GetDriverByName("GTiff").Create(path_to_bathy+"/bath_grad.tiff", nx, ny, 1, gdal.GDT_Float32)
    tif.SetGeoTransform(geo_transform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    tif.SetProjection(srs.ExportToWkt())
    tif.GetRasterBand(1).WriteArray(grad)
    tif.FlushCache()
    tif = None 
    bath_grad_field = seamsh.field.Raster(path_to_bathy+"/bath_grad.tiff")

# 5. Define mesh element size function

def threshold(d, l0, l1, d0, d1):
    """
    if distance d < d0, return mesh size l0
    elif distance d > d1, return mesh size l1
    elif d0 <= distance d <= d1, return mesh size linearly interpolated between l0 and l1 
    """
    res = np.ones_like(d)*l1
    dd = d[d < d1]
    res[d < d1] = np.where(dd < d0, l0, (dd-d0)/(d1-d0)*l1 + (1-(dd-d0)/(d1-d0))*l0)
    return res

def mesh_size(x, projection):
    val = 1e9 * np.ones(x.shape[0])
    val = np.minimum( val, threshold(dist_coast(x, projection), 100, 10000, 0, 50000) )
    val = np.minimum( val, threshold(dist_coast2(x, projection), 1000, 10000, 0, 50000) )
    val = np.minimum( val, threshold(dist_coast3(x, projection), 4000, 10000, 0, 50000) )
    val = np.minimum( val, threshold(dist_river(x, projection), 50, 10000, 0, 10000) )
    if param.use_bath_grad or param.use_bath:
        bath = -bath_field(x,projection)
    if param.use_bath:
        size_bath = np.sqrt( np.clip(bath,100,4000) )*750
        idx = np.logical_and(
                  dist_coast3(x,projection) < 20000, dist_river(x,projection) < 1000
        )
        size_bath[idx] = np.maximum(4000,size_bath[idx]) 
        val = np.minimum(val, size_bath) #si a moins de 20km de coast3 et a moins de 1km de la riviere, cette iteration ne fera pas descendre la resolution sous 4km
    if param.use_bath_grad:
        bath_grad = bath_grad_field(x,projection)
        size_grad = np.ones_like(size_bath) * 10000
        idx = np.logical_and(
                  np.logical_and(
                      np.logical_and(bath_grad > 1e-5, dist_coast(x,projection) > 15000),
                  dist_coast2(x,projection) > 20000),
            dist_coast3(x,projection) > 100000
        )
        size_grad[idx] = np.maximum(1000, .5*bath[idx]/bath_grad[idx]) #il prend le maximum entre 1000 et .5*bath[idx]/bath_grad[idx] pour tous les elements qui satisfont les conditions plus haut
        val = np.minimum(val, size_grad)
    return val

# 6. Treat mesh boundaries
coarse = seamsh.geometry.coarsen_boundaries(domain, param.interior_point, lonlat_proj, mesh_size)

# 7. Start meshing
ver = float(param.version)
seamsh.gmsh.mesh(coarse, param.mesh_file, mesh_size, version=ver)
