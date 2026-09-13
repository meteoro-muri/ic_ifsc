import pandas as pd
import geopandas as gpd
import sys
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import matplotlib.colors as cls 
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm, TwoSlopeNorm, LinearSegmentedColormap
from matplotlib.patches import Patch

# Define color dictionary for clusters
color_dict = {'0': 'white', '1': 'red', '-1': 'green'}  
# Add more colours as needed


unicos = pd.read_csv("casos_primeiros.csv")
municipios = gpd.read_file("/home/sifapsc/scripts/matheus/dados_dengue/shapefiles/SC_Municipios_2022.shp")

br = "BR/BR_UF_2022.shp"
semana_epidemio = "2024-10-20"

##### MANIPULANDO TABELAS DE REVISÃO ####
tabela0_pivot = pd.read_csv('https://raw.githubusercontent.com/matheusf30/operacional_dengue/refs/heads/main/modelagem/resultados/dados_previstos/previsao_melt_total_v20250216_h0_r2.csv')
tabela0_pivot["Semana"] = pd.to_datetime(tabela0_pivot["Semana"])
print(tabela0_pivot.dtypes)


semana09 = pd.DataFrame()
semana09 = tabela0_pivot[tabela0_pivot["Semana"] == '2025-02-09']

semana09 = semana09.drop(columns = ['Semana'])
semana09 = semana09.set_index('Município')
semana09.rename(columns={"Casos" : "2025-02-09"},inplace=True)
#print(semana09)

semana16 = pd.DataFrame()
semana16 = tabela0_pivot[tabela0_pivot["Semana"] == '2025-02-16']
semana16 = semana16.drop(columns = ['Semana'])
semana16 = semana16.set_index('Município')
semana16.rename(columns={"Casos" : "2025-02-16"},inplace=True)
#print(semana16)

semana23 = pd.DataFrame()
semana23 = tabela0_pivot[tabela0_pivot["Semana"] == '2025-02-23']
semana23 = semana23.drop(columns = ['Semana'])
semana23 = semana23.set_index('Município')
semana23.rename(columns={"Casos" : "2025-02-23"},inplace=True)
#print(semana23)

semana02 = pd.DataFrame()
semana02 = tabela0_pivot[tabela0_pivot["Semana"] == '2025-03-02']
semana02 = semana02.drop(columns = ['Semana'])
semana02 = semana02.set_index('Município')
semana02.rename(columns={"Casos" : "2025-03-02"},inplace=True)
#print(semana02)

resultado = pd.DataFrame()
resultado = pd.concat([semana09, semana16, semana23, semana02], axis=1)

resultado["S1"] = resultado['2025-02-16'] - resultado['2025-02-09']
resultado["S2"] = resultado['2025-02-23'] - resultado['2025-02-16']
resultado["S3"] = resultado['2025-03-02'] - resultado['2025-02-23']





#### CARTOGRAFIA ####

#SC_Coroplético


#S1
xy = municipios.copy()
xy.drop(columns = ["CD_MUN", "SIGLA_UF", "AREA_KM2"], inplace = True)
xy = xy.rename(columns = {"NM_MUN" : "Município"})
xy["Município"] = xy["Município"].str.upper() 
resultado_melt_poli = pd.merge(resultado["S1"], xy, on = "Município", how = "left")
resultado_melt_poligeo = gpd.GeoDataFrame(resultado_melt_poli, geometry = "geometry", crs = "EPSG:4674")
color = resultado_melt_poligeo["S1"]
color = color.to_list()
print(color)
color = pd.DataFrame(color, columns = ["cor"])
resultado_melt_poligeo["color"] = color

resultado_melt_poligeo["color"]
#sys.exit()


# Define a diverging colormap with white at 0
colors = ["green", "white", "red"]  # Negative = red, Zero = white, Positive = green
cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)

# Set normalization to center at zero
vmin = resultado_melt_poligeo["color"].min()
vmax = resultado_melt_poligeo["color"].max()

absmax = max(abs(vmin), abs(vmax))
norm = TwoSlopeNorm(vmin=-absmax, vcenter=0, vmax=absmax)

base =  resultado_melt_poligeo.plot(column = "color", legend=True, cmap = cmap, norm = norm, legend_kwds={'shrink': 0.6})
xy.plot(ax = base, color = "#FF000000", edgecolor = "#636363", linewidth=0.1)

base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)

#S2
xy = municipios.copy()
xy.drop(columns = ["CD_MUN", "SIGLA_UF", "AREA_KM2"], inplace = True)
xy = xy.rename(columns = {"NM_MUN" : "Município"})
xy["Município"] = xy["Município"].str.upper() 
resultado_melt_poli = pd.merge(resultado["S2"], xy, on = "Município", how = "left")
resultado_melt_poligeo = gpd.GeoDataFrame(resultado_melt_poli, geometry = "geometry", crs = "EPSG:4674")
color = resultado_melt_poligeo["S2"]
color = color.to_list()
print(color)
color = pd.DataFrame(color, columns = ["cor"])
resultado_melt_poligeo["color"] = color

resultado_melt_poligeo["color"]
#sys.exit()


# Define a diverging colormap with white at 0
colors = ["green", "white", "red"]  # Negative = red, Zero = white, Positive = green
cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)

# Set normalization to center at zero
vmin = resultado_melt_poligeo["color"].min()
vmax = resultado_melt_poligeo["color"].max()

absmax = max(abs(vmin), abs(vmax))
norm = TwoSlopeNorm(vmin=-absmax, vcenter=0, vmax=absmax)

base =  resultado_melt_poligeo.plot(column = "color", legend=True, cmap = cmap, norm = norm, legend_kwds={'shrink': 0.6})
xy.plot(ax = base, color = "#FF000000", edgecolor = "#636363", linewidth=0.1)

base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)

#S3
xy = municipios.copy()
xy.drop(columns = ["CD_MUN", "SIGLA_UF", "AREA_KM2"], inplace = True)
xy = xy.rename(columns = {"NM_MUN" : "Município"})
xy["Município"] = xy["Município"].str.upper() 
resultado_melt_poli = pd.merge(resultado["S3"], xy, on = "Município", how = "left")
resultado_melt_poligeo = gpd.GeoDataFrame(resultado_melt_poli, geometry = "geometry", crs = "EPSG:4674")
color = resultado_melt_poligeo["S3"]
color = color.to_list()
print(color)
color = pd.DataFrame(color, columns = ["cor"])
resultado_melt_poligeo["color"] = color

resultado_melt_poligeo["color"]
#sys.exit()


# Define a diverging colormap with white at 0
colors = ["green", "white", "red"]  # Negative = red, Zero = white, Positive = green
cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)

# Set normalization to center at zero
vmin = resultado_melt_poligeo["color"].min()
vmax = resultado_melt_poligeo["color"].max()

absmax = max(abs(vmin), abs(vmax))
norm = TwoSlopeNorm(vmin=-absmax, vcenter=0, vmax=absmax)

base =  resultado_melt_poligeo.plot(column = "color", legend=True, cmap = cmap, norm = norm, legend_kwds={'shrink': 0.6})
xy.plot(ax = base, color = "#FF000000", edgecolor = "#636363", linewidth=0.1)

base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)

plt.show()







