import os
import cdsapi
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from shapely.geometry import box

# ==========================================
# 1. ARQUIVO DE ENTRADA E SHAPEFILE
# ==========================================
output_grib = "/home/sifapsc/scripts/meteoromuri/TCC/cams_september_2003_2023.grib"

ds = xr.open_dataset(output_grib, engine="cfgrib")
brazil_states = gpd.read_file("/home/sifapsc/shapefiles/BR_UF_2024.shp")

# Coordenadas focadas em Santa Catarina
sc_lon_bounds = [-54.2, -47.8]
sc_lat_bounds = [-29.8, -25.6]
base_export_path = "/home/sifapsc/scripts/meteoromuri/TCC/figs"

# ==========================================
# 2. FUNÇÃO DE CLIMATOLOGIA
# ==========================================
def fig_climatologia_regiao(ds, var, brazil_states, lon_bounds=None, lat_bounds=None, output_base_dir="./figs"):
    # Identifica a dimensão temporal ('time' ou 'valid_time') e calcula a média
    time_dim = 'time' if 'time' in ds.dims else 'valid_time'
    clima = ds[var].mean(dim=time_dim, keep_attrs=True)

    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Define o recorte espacial
    if lon_bounds and lat_bounds:
        ax.set_extent([lon_bounds[0], lon_bounds[1], lat_bounds[0], lat_bounds[1]], crs=ccrs.PlateCarree())
                    
    vmin = float(clima.min())
    vmax = float(clima.max())
    
    # Plota o campo médio
    clima.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap='hot',
        vmin=vmin,
        vmax=vmax,
        add_colorbar=True,
        add_labels=False
    )
    
    # Elementos geográficos
    ax.add_feature(cfeature.COASTLINE, edgecolor='lightgray', linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, edgecolor='lightgray')
    
    # Divisão estadual
    if lon_bounds and lat_bounds:
        bbox = box(lon_bounds[0], lat_bounds[0], lon_bounds[1], lat_bounds[1])
        states_in_view = brazil_states[brazil_states.intersects(bbox)]
        states_in_view.boundary.plot(
            ax=ax,
            edgecolor='darkgray',
            linewidth=0.3,
            transform=ccrs.PlateCarree()
        )
    else:
        brazil_states.boundary.plot(
            ax=ax,
            edgecolor='darkgray',
            linewidth=0.3,
            transform=ccrs.PlateCarree()
        )
        
    # Linhas de grade
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 8}
    gl.ylabel_style = {'size': 8}
    
    # Título e salvamento
    long_name = clima.attrs.get('long_name', var)
    fig.suptitle(f"Climatologia (Média Temporal) - {long_name}")
    
    out_dir = os.path.join(output_base_dir, var, "climatologia")
    os.makedirs(out_dir, exist_ok=True)
    
    file_path = os.path.join(out_dir, f"{var}_climatologia_regiao.png")
    plt.savefig(file_path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Figura salva com sucesso: {file_path}")
    return 0

# ==========================================
# 3. EXECUÇÃO
# ==========================================
for var_name in ds.data_vars:
    fig_climatologia_regiao(
        ds=ds,
        var=var_name,
        brazil_states=brazil_states,
        lon_bounds=sc_lon_bounds,
        lat_bounds=sc_lat_bounds,
        output_base_dir=base_export_path
    )
