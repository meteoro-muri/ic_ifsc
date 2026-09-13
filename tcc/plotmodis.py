import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas as pd
import sys
import geopandas as gpd


brazil_states = gpd.read_file("/home/sifapsc/shapefiles/BR_UF_2024.shp")



f = pd.read_csv('/home/sifapsc/scripts/meteoromuri/TCC/fire_archive_M-C61_725417.csv')

filtrado = f.loc[f['confidence'] > 80].loc[f['acq_date'] == '2024-09-01']

print(filtrado.info())
#sys.exit()


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

im = ax.scatter(filtrado['longitude'], filtrado['latitude'], filtrado['brightness'], c = 'Red', marker = '.', linewidths = 0.2)



ax.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=0.6, transform=ccrs.PlateCarree())
#fig.colorbar(im,  ax=ax, orientation="vertical",shrink= 1.0)

ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)
ax.add_feature(cfeature.BORDERS, edgecolor = 'black')

brazil_states.plot(
ax=ax, 
edgecolor='black', 
linewidth=1, 
alpha=0.5, 
facecolor='none',
transform=ccrs.PlateCarree()  # Ensure correct transform
)


ax.add_feature(cfeature.LAND, facecolor = 'white')
ax.add_feature(cfeature.OCEAN, facecolor = 'white')
gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 8}
gl.ylabel_style = {'size': 8}
fig.suptitle(f"FIREEEEEEEEEEEEEEEEEE")
plt.show()
