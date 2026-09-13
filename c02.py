import xarray as xr
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib
import matplotlib.pyplot as plt                 #Figure
from matplotlib import cm                       # Colormap handling utilities
import matplotlib.colors as cls
from matplotlib.colors import Normalize
import matplotlib.colors as mcolors
import geopandas as gpd
import matplotlib.colors as colors

#sys.exit()

# Lendo dados dos modelos .nc
data1 = xr.open_dataset('~/DADOS/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMAX_MEAN_ANOMALIA_SB.nc')
#print(data1)

#=============================================================================
#definindo a região

#lat_bounds = slice(-40, -10)  
#lon_bounds = slice(-63, -40)

lat_bounds = slice(-34, -26.2)  
lon_bounds = slice(-58, -49)

#lat_bounds = slice(-29, -28) 
#lon_bounds = slice(-53.75, -52.5)


#lat_bounds = slice(-35, -4) 
#lon_bounds = slice(-74, -33)

regiao_br = data1.sel(lat = lat_bounds, lon = lon_bounds)

#sys.exit()

#=============================================================================
#lendo shapefile dos paises
reader = shpreader.Reader('/media/dados/shapefiles/BR/BR_UF_2022.shp')
counties = list(reader.geometries())
COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

#lendo shapefile estados brasileiros
reader2 = shpreader.Reader('/media/dados/shapefiles/BR/BR_UF_2022.shp')
states = list(reader2.geometries())
brazil_states = cfeature.ShapelyFeature(states, ccrs.PlateCarree())

#lendo shapefile estados brasileiros
#reader3 = shpreader.Reader('testeando_shape/shape_lat_lon_v2.shp')
#shape = list(reader3.geometries())
#brazil_shape= cfeature.ShapelyFeature(shape, ccrs.PlateCarree())

#lendo shapefile estados brasileiros
#reader4 = shpreader.Reader('RS_Municipios_2024/RS_Municipios_2024.shp')
#cidades = list(reader4.geometries())
#brazil_cidades = cfeature.ShapelyFeature(cidades, ccrs.PlateCarree())

#=============================================================================   
#=============================================================================      

#convertendo os dados para numpyarray
anom_mon=regiao_br["tmax"]
anom_mensal_mean_np=np.array(anom_mon)
lon=np.array(regiao_br['lon'])
lat=np.array(regiao_br['lat'])


# Encontrar o valor máximo da temperatura máxima e mínimo da temperatura mínima na região selecionada
max_tmax = anom_mon.max().item()
int_max = int(max_tmax)
min_tmin = anom_mon.min().item()
int_min = int(min_tmin)
abs_value = max(abs(int_min),abs(int_max))
print(f'Valor máximo da temperatura na região selecionada: {round(max_tmax, 2)} °C')
print(f'Valor mínimo da temperatura na região selecionada: {round(min_tmin, 2)} °C')

fig, axes = plt.subplots(1,3,figsize=(23,25),subplot_kw={'projection': ccrs.PlateCarree()})

#v2 = np.linspace(-30, 30, 15, endpoint=True)

time = ('Julho','Agosto','Setembro')
#'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',)

numero = ('(a)','(b)','(c)')
data_min = int_min
data_max = int_max
#interval = 1
# Cria níveis simétricos com 11 faixas, centrado no zero
levels = np.linspace(data_min, data_max, 9)

#colors = ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#fee090", 
#		  "#fdae61", "#f46d43", "#d73027", "#a50026"]
#cmap = matplotlib.colors.ListedColormap(colors)
#cmap.set_over('#800026')
#cmap.set_under('#040273')#07101C')
#norm = mcolors.BoundaryNorm(ncolors=cmap.N)
v2 = np.linspace(-5, 5, 21, endpoint=True)

vmin = -5
vmax = 5
norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)



#levels=np.linspace(0, 0.00006, 15)

i=0
for dat, ax in zip(anom_mensal_mean_np[306:309,:,:], axes.flat):
    im = ax.contourf(lon, lat, dat, v2, cmap=plt.cm.bwr, vmin=vmin, vmax=vmax, norm=norm, extend='both') 
    ax.add_feature(brazil_states, facecolor='none', edgecolor='black')
    ax.add_feature(COUNTIES, facecolor='none', edgecolor='black')
    a1 = ax.gridlines(draw_labels=True,
                  linewidth=1, color='black', alpha=0.0, linestyle='--')  
    # declare text size
    #XTEXT_SIZE = 20
    #YTEXT_SIZE = 20
    # to facilitate text rotation at bottom edge, ...
    # text justification: 'ha':'right' is used to avoid clashing with map's boundary
    # default of 'ha' is center, often causes trouble when text rotation is not zero
    #a1.xlabel_style = {'size': XTEXT_SIZE}
    #a1.ylabel_style = {'size':YTEXT_SIZE}
    a1.top_labels=False
    a1.right_labels=False
    ax.set_title(time[i], loc='center', fontsize=15)
    #ax.set_title(number[i], loc='left', fontsize=25)
    #localizando santa maria
    #mypt = (-53.8, -29.69)
    #ax.plot(mypt[0], mypt[1], 'wD', ms=5)
    i += 1

cb=fig.colorbar(im, ax=axes.ravel().tolist(), orientation="horizontal",shrink= 1.0, pad=0.04, aspect=30)
cb.set_label('Anomalia de Temperatura Máxima (ºC/mês)',size=15,rotation=0,labelpad=15)
cb.ax.tick_params(labelsize=15)
#cb.formatter.set_powerlimits((0, 0))
#fig.suptitle('Anomalia da precipitação (mm/dia) ABRIL2025 - CI:MAR2025',fontsize=15)
plt.savefig(f"plot_obs/anom_tempMAX_obs_jul-set25_2.png", dpi=300, bbox_inches="tight")
plt.show()

#sys.exit()

#======================================#======================================
#======================================#======================================

#plotando anomalia

# Lendo dados dos modelos .nc
data2 = xr.open_dataset('~/DADOS/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMIN_MEAN_ANOMALIA_SB.nc')
regiao_br2 = data2.sel(lat = lat_bounds, lon = lon_bounds)
#print(data1)


#convertendo os dados para numpyarray
anom_mon=regiao_br2["tmin"]
anom_mensal_mean_np=np.array(anom_mon)
lon=np.array(regiao_br2['lon'])
lat=np.array(regiao_br2['lat'])


# Encontrar o valor máximo da temperatura máxima e mínimo da temperatura mínima na região selecionada
max_tmax = anom_mon.max().item()
int_max = int(max_tmax)
min_tmin = anom_mon.min().item()
int_min = int(min_tmin)
abs_value = max(abs(int_min),abs(int_max))
print(f'Valor máximo da temperatura na região selecionada: {round(max_tmax, 2)} °C')
print(f'Valor mínimo da temperatura na região selecionada: {round(min_tmin, 2)} °C')

fig, axes = plt.subplots(1,3,figsize=(23,25),subplot_kw={'projection': ccrs.PlateCarree()})

#v2 = np.linspace(-30, 30, 15, endpoint=True)

time = ('Julho','Agosto','Setembro')
#'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',)

numero = ('(a)','(b)','(c)')
v2 = np.linspace(-5, 5, 21, endpoint=True)

vmin = -5
vmax = 5
norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)



i=0
for dat, ax in zip(anom_mensal_mean_np[306:309,:,:], axes.flat):
    im = ax.contourf(lon, lat, dat, v2, cmap=plt.cm.bwr, vmin=vmin, vmax=vmax, norm=norm, extend='both') 
    ax.add_feature(brazil_states, facecolor='none', edgecolor='black')
    ax.add_feature(COUNTIES, facecolor='none', edgecolor='black')
    a1 = ax.gridlines(draw_labels=True,
                  linewidth=1, color='black', alpha=0.0, linestyle='--')  
    # declare text size
    #XTEXT_SIZE = 20
    #YTEXT_SIZE = 20
    # to facilitate text rotation at bottom edge, ...
    # text justification: 'ha':'right' is used to avoid clashing with map's boundary
    # default of 'ha' is center, often causes trouble when text rotation is not zero
    #a1.xlabel_style = {'size': XTEXT_SIZE}
    #a1.ylabel_style = {'size':YTEXT_SIZE}
    a1.top_labels=False
    a1.right_labels=False
    ax.set_title(time[i], loc='center', fontsize=15)
    #ax.set_title(number[i], loc='left', fontsize=25)
    #localizando santa maria
    #mypt = (-53.8, -29.69)
    #ax.plot(mypt[0], mypt[1], 'wD', ms=5)
    i += 1

cb=fig.colorbar(im, ax=axes.ravel().tolist(), orientation="horizontal",shrink= 1.0, pad=0.04, aspect=30)
cb.set_label('Anomalia de Temperatura Mínima (ºC/mês)',size=15,rotation=0,labelpad=20)
cb.ax.tick_params(labelsize=15)
#cb.formatter.set_powerlimits((0, 0))
#fig.suptitle('Anomalia da precipitação (mm/dia) ABRIL2025 - CI:MAR2025',fontsize=15)
plt.savefig(f"plot_obs/anom_tempMIN_obs_jul-set25.png", dpi=300, bbox_inches="tight")
plt.show()





