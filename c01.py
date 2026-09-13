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
import matplotlib.colors as colors
import matplotlib as mpl
import matplotlib
import matplotlib.pyplot as plt                 #Figure
from matplotlib import cm                       # Colormap handling utilities
import matplotlib.colors as cls
from matplotlib.colors import Normalize

import geopandas as gpd

# Lendo dados dos modelos .nc - AQUI VOCÊ COLOCA O SEU CAMINHO
data1 = xr.open_dataset('~/DADOS/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_MONTHLY_SB_2025.nc')
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
#regiao_br = data1
prec=regiao_br["prec"].mean(dim='time')
#prec=regiao_br["prec"]

print(prec.shape)
print(prec.min())
print(prec.max())

#sys.exit()

#prec = ((prec['M2TMNXFLX_5_12_4_PRECTOT'])*86400)*30 #convertendo para mm por dia e por mes

#=============================================================================
#convertendo os dados para numpyarray
#prec_annual_mean_np=np.array((prec*86400)*30)
prec_annual_mean_np = prec
lon=np.array(regiao_br['lon'])
lat=np.array(regiao_br['lat'])


print(lon)
print(lat)
#sys.exit()

# Encontrar o valor máximo da precipitacao na região selecionada
max_prec = prec_annual_mean_np.max().item()
int_max = int(max_prec)
print(f'Valor máximo da precipitação na região selecionada: {int_max} mm')
int_min = 0

data_min = int_min
data_max = int_max
interval = 1
levels = np.linspace(data_min, data_max, num=256)
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
class PiecewiseNorm(Normalize):
    def __init__(self, levels, clip=False):
        # input levels
        self._levels = np.sort(levels)
        # corresponding normalized values between 0 and 1
        self._normed = np.linspace(0, 1, len(levels))
        Normalize.__init__(self, None, None, clip)

    def __call__(self, value, clip=None):
        # linearly interpolate to get the normalized value
        return np.ma.masked_array(np.interp(value, self._levels, self._normed))

    def inverse(self, value):
        return 1.0 - self.__call__(value)
#=============================================================================   
from matplotlib import cm
from matplotlib.colors import ListedColormap, to_rgb, to_rgba

def pastelize_cmap(cmap_name='PuOr_r', alpha=1.0, pastel_factor=0.5):
    """
    Suaviza uma colormap para deixá-la em tons pastel.
    
    pastel_factor: 0 = original, 1 = completamente pastel (branco)
    """
    base = cm.get_cmap(cmap_name, 256)
    new_colors = []

    for i in range(base.N):
        r, g, b, a = base(i)
        r = r + (1 - r) * pastel_factor
        g = g + (1 - g) * pastel_factor
        b = b + (1 - b) * pastel_factor
        new_colors.append((r, g, b, alpha))

    return ListedColormap(new_colors, name=f'{cmap_name}_pastel')

# Exemplo de uso
#pastel_cmap = pastelize_cmap('jet_r', pastel_factor=0.3) 
pastel_cmap = pastelize_cmap('bwr_r', pastel_factor=0.3)  #=============================================================================      
fig = plt.figure(figsize=(12,6))
ax = plt.axes(projection=ccrs.PlateCarree())

#levels = [110,115,120,125,130,135,140,
#          150,155,160,165,170,180,185,190,195,200,210,
#          220,230]

#levels = [80,90,100,110,120,130,140,150,160,161,162,163,165,170,175,
 #         176,177,178,179,180]

cmap_data = [(1.0, 1.0, 1.0),
             (0.3137255012989044, 0.8156862854957581, 0.8156862854957581),
             (0.0, 1.0, 1.0),
             (0.0, 0.8784313797950745, 0.501960813999176),
             (0.0, 0.7529411911964417, 0.0),
             (0.501960813999176, 0.8784313797950745, 0.0),
             (1.0, 1.0, 0.0),
             (1.0, 0.6274510025978088, 0.0),
             (1.0, 0.0, 0.0),
             (1.0, 0.125490203499794, 0.501960813999176),
             (0.9411764740943909, 0.250980406999588, 1.0),
             (0.501960813999176, 0.125490203499794, 1.0),
             (0.250980406999588, 0.250980406999588, 1.0),
             (0.125490203499794, 0.125490203499794, 0.501960813999176),
             (0.125490203499794, 0.125490203499794, 0.125490203499794),
             (0.501960813999176, 0.501960813999176, 0.501960813999176),
             (0.8784313797950745, 0.8784313797950745, 0.8784313797950745),
             (0.9333333373069763, 0.8313725590705872, 0.7372549176216125),
             (0.8549019694328308, 0.6509804129600525, 0.47058823704719543),
             (0.6274510025978088, 0.42352941632270813, 0.23529411852359772),
             (0.4000000059604645, 0.20000000298023224, 0.0)]

#cmap = mcolors.ListedColormap(cmap_data, 'precipitation')
#norm = mcolors.BoundaryNorm(levels, cmap.N)
             
# Criar uma paleta de cores personalizada
colors = ["#b4f0f0", "#96d2fa", "#78b9fa", "#3c95f5", "#1e6deb", "#1463d2", 
          "#0fa00f", "#28be28", "#50f050", "#72f06e", "#b3faaa", "#fff9aa", 
          "#ffe978", "#ffc13c", "#ffa200", "#ff6200", "#ff3300", "#ff1500", 
          "#c00100", "#a50200", "#870000", "#653b32"]
cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#000000')
cmap.set_under('#ffffff')
data_min = int_min
data_max = int_max

interval = 1
levels = np.linspace(data_min, data_max, 23)

#im = ax.contourf(lon, lat, prec_annual_mean_np,cmap=cmap, norm=PiecewiseNorm(levels), levels=25,extend='both',)

im = ax.contourf(lon, lat, prec_annual_mean_np,norm=cls.Normalize(vmin=int_min, vmax=int_max),cmap=cmap, levels=levels, extend='max')


#ax.contour(lon, lat, prec_annual_mean_np,levels=levels,
 #       colors='k', linewidths=0.6, linestyles='dashed',
  #      transform=ccrs.PlateCarree())
  
#ax.add_feature(ocean, facecolor='white', edgecolor='white')
ax.add_feature(brazil_states, facecolor='none', edgecolor='grey')
ax.add_feature(COUNTIES, facecolor='none', edgecolor='black')
ax.add_feature(brazil_states, facecolor='none', edgecolor='darkblue')
#ax.add_feature(brazil_cidades, facecolor='none', edgecolor='darkblue')
#

a1 = ax.gridlines(draw_labels=True,
                  linewidth=2, color='none', alpha=0.5, linestyle='--')

#a1.bottom_labels=False 
a1.top_labels=False 
a1.right_labels=False

#======================================

cb=fig.colorbar(im, orientation="vertical",shrink= 1.0, pad=0.02)
cb.set_label('Precipitação (mm/mês)',size=13,rotation=90,labelpad=10)
cb.ax.tick_params(labelsize=10)
plt.show()

#======================================#======================================

#plotando média mensal

#convertendo os dados para numpyarray
prec_mon=regiao_br["prec"]
prec_mensal_mean_np=np.array(prec_mon)
lon=np.array(regiao_br['lon'])
lat=np.array(regiao_br['lat'])

# Encontrar o valor máximo da precipitacao na região selecionada
max_prec = prec_mensal_mean_np.max().item()
int_max = int(max_prec)
print(f'Valor máximo da precipitação na região selecionada: {int_max} mm')
int_min = 0

data_min = int_min
data_max = int_max
interval = 1
levels = np.linspace(data_min, data_max, 23)

fig, axes = plt.subplots(1,3,figsize=(23,25),subplot_kw={'projection': ccrs.PlateCarree()})

#v2 = np.linspace(-30, 30, 15, endpoint=True)

time = ('Julho','Agosto','Setembro')
#'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',)

numero = ('(a)','(b)','(c)')


#levels=np.linspace(0, 0.00006, 15)


i=0
for dat, ax in zip(prec_mensal_mean_np[6:9,:,:], axes.flat):
    im = ax.contourf(lon, lat, dat,norm=cls.Normalize(vmin=int_min, vmax=int_max),cmap=cmap, levels=levels, extend='max')
    ax.add_feature(brazil_states, facecolor='none', edgecolor='dimgrey')
    ax.add_feature(COUNTIES, facecolor='none', edgecolor='black')
    a1 = ax.gridlines(draw_labels=True,
                  linewidth=1, color='white', alpha=0.2, linestyle='--')
    a1.top_labels=False
    a1.right_labels=False
    ax.set_title(time[i], loc='center', fontsize=15)
    #ax.set_title(numero[i], loc='left', fontsize=10)

    i += 1

#for i in [5]:
 #   fig.delaxes(axes.flatten()[i])

cb=fig.colorbar(im, ax=axes.ravel().tolist(), orientation="horizontal",shrink= 1.0, pad=0.04, aspect=30)
cb.set_label('Precipitação (mm/mês)',size=15,rotation=0,labelpad=20)
cb.ax.tick_params(labelsize=15)
#cb.formatter.set_powerlimits((0, 0))
#fig.suptitle('Anomalia da precipitação (mm/dia) ABRIL2025 - CI:MAR2025',fontsize=15)
plt.savefig(f"plot_obs/prec_obs_jul-set25.png", dpi=300, bbox_inches="tight")
plt.show()

#======================================#======================================

#plotando anomalia

# Lendo dados dos modelos .nc
data2 = xr.open_dataset('~/DADOS/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_MONTHLY_ANOMALIA.nc')
regiao_br2 = data2.sel(lat = lat_bounds, lon = lon_bounds)
time=np.array(data2['time'])

print(time[297:300])

#sys.exit()
#convertendo os dados para numpyarray
anom_mon=regiao_br2["prec"]
anom_mensal_mean_np=np.array(anom_mon)
lon=np.array(regiao_br2['lon'])
lat=np.array(regiao_br2['lat'])


# Encontrar o valor máximo e mínimo da precipitacao na região selecionada
max_prec = anom_mensal_mean_np.max().item() 
int_max = int(max_prec) + 20
min_prec = anom_mensal_mean_np.min().item() 
int_min = int(min_prec) - 20
abs_value = max(abs(int_min),abs(int_max))
print(f'Valor máximo da precipitacao na região selecionada: {round(max_prec, 2)} mm')
print(f'Valor mínimo da precipitacao na região selecionada: {round(min_prec, 2)} mm')


fig, axes = plt.subplots(1,3,figsize=(23,25),subplot_kw={'projection': ccrs.PlateCarree()})

#v2 = np.linspace(-30, 30, 15, endpoint=True)

time = ('Julho','Agosto','Setembro')
#'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',)

numero = ('(a)','(b)','(c)')
data_min = int_min
data_max = int_max
interval = 1
#levels = np.linspace(data_min, data_max, 23)

colors = ["#a50026","#d73027","#f46d43","#fdae61","#fee090","#e0f3f8",
           "#abd9e9","#74add1","#4575b4","#313695"]
cmap = matplotlib.colors.ListedColormap(colors) 
cmap.set_under('#800026')
cmap.set_over('#040273')


#levels=np.linspace(0, 0.00006, 15)


i=0
for dat, ax in zip(anom_mensal_mean_np[298:301,:,:], axes.flat):
    im = ax.contourf(lon, lat, dat,norm=cls.Normalize(vmin=-150, vmax=150),cmap=pastel_cmap, levels=21, extend='both')
    ax.add_feature(brazil_states, facecolor='none', edgecolor='dimgrey')
    ax.add_feature(COUNTIES, facecolor='none', edgecolor='black')
    a1 = ax.gridlines(draw_labels=True,
                  linewidth=1, color='white', alpha=0.2, linestyle='--')
    a1.top_labels=False
    a1.right_labels=False
    ax.set_title(time[i], loc='center', fontsize=15)
    #ax.set_title(numero[i], loc='left', fontsize=10)

    i += 1

#for i in [5]:
 #   fig.delaxes(axes.flatten()[i])

cb=fig.colorbar(im, ax=axes.ravel().tolist(), orientation="horizontal",shrink= 1.0, pad=0.04, aspect=30)
cb.set_label('Anomalia de Precipitação (mm/mês)',size=15,rotation=0,labelpad=20)
cb.ax.tick_params(labelsize=15)
#cb.formatter.set_powerlimits((0, 0))
#fig.suptitle('Anomalia da precipitação (mm/dia) ABRIL2025 - CI:MAR2025',fontsize=15)
plt.savefig(f"plot_obs/anom_obs_jul-set25_v2.png", dpi=300, bbox_inches="tight")
plt.show()







