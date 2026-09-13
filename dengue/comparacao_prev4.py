import pandas as pd
import geopandas as gpd
import sys
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import matplotlib.colors as cls 
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

# Define color dictionary for clusters
color_dict = {'0': 'white', '1': 'red', '-1': 'green'}  
# Add more colours as needed


unicos = pd.read_csv("casos_primeiros.csv")
municipios = gpd.read_file("/home/sifapsc/scripts/matheus/dados_dengue/shapefiles/SC_Municipios_2022.shp")

br = "BR/BR_UF_2022.shp"
semana_epidemio = "2024-10-20"



#### CRIAÇÃO DE DATAFRAME ####
'''
xy = unicos.drop(columns = ["Semana", "Casos"])
print("xy: ",xy)
print("resultado: ", resultado)

resultado_xy = pd.merge(resultado, xy, on = ['Município'])

geometry = [Point(xy) for xy in zip(resultado_xy["longitude"], resultado_xy["latitude"])]
resultado_melt_geo = gpd.GeoDataFrame(resultado_xy, geometry = geometry, crs = "EPSG:4674")
resultado_melt_geo = resultado_melt_geo[["S1", "S2", "Município", "geometry"]]
print(resultado_melt_geo)
sys.exit()
'''



tabela0_pivot = pd.read_csv('https://raw.githubusercontent.com/matheusf30/operacional_dengue/refs/heads/main/modelagem/resultados/2025/202509/previsao_melt_total_v20250923_h0_r2.csv')
tabela0_pivot["Semana"] = pd.to_datetime(tabela0_pivot["Semana"])
print(tabela0_pivot)


## definindo variáveis para recortar o dataframe, é necessário apenas ajustar as datas nas próximas 3 linhas ##

data_s0 = '2025-09-14'
data_s1 =  '2025-09-21'
data_s2 = '2025-09-28'
data_s3 = '2025-10-05'



semana_0 = pd.DataFrame()
semana_0 = tabela0_pivot[tabela0_pivot["Semana"] == data_s0]
semana_0 = semana_0.drop(columns = ['Semana'])
semana_0 = semana_0.set_index('Município')
semana_0.rename(columns={"Casos" : data_s0 },inplace=True)


semana_1 = pd.DataFrame()
semana_1 = tabela0_pivot[tabela0_pivot["Semana"] == data_s1]
semana_1 = semana_1.drop(columns = ['Semana'])
semana_1 = semana_1.set_index('Município')
semana_1.rename(columns={"Casos" : data_s1},inplace=True)
#print(semana16)

semana_2 = pd.DataFrame()
semana_2 = tabela0_pivot[tabela0_pivot["Semana"] == data_s2]
semana_2 = semana_2.drop(columns = ['Semana'])
semana_2 = semana_2.set_index('Município')
semana_2.rename(columns={"Casos" : data_s2},inplace=True)
#print(semana23)

semana_3 = pd.DataFrame()
semana_3 = tabela0_pivot[tabela0_pivot["Semana"] == data_s3]
semana_3 = semana_3.drop(columns = ['Semana'])
semana_3 = semana_3.set_index('Município')
semana_3.rename(columns={"Casos" : data_s3},inplace=True)
#print(semana02)

resultado = pd.DataFrame()
resultado = pd.concat([semana_0, semana_1, semana_2, semana_3], axis=1)

resultado["S1"] = resultado[data_s1] - resultado[data_s0]
resultado["S2"] = resultado[data_s2] - resultado[data_s1]
resultado["S3"] = resultado[data_s3] - resultado[data_s2]







#### CARTOGRAFIA ####

#SC_Coroplético



xy = municipios.copy()
xy.drop(columns = ["CD_MUN", "SIGLA_UF", "AREA_KM2"], inplace = True)
xy = xy.rename(columns = {"NM_MUN" : "Município"})
xy["Município"] = xy["Município"].str.upper() 

#S1

resultado_melt_poli = pd.merge(resultado["S1"], xy, on = "Município", how = "left")
resultado_melt_poligeo = gpd.GeoDataFrame(resultado_melt_poli, geometry = "geometry", crs = "EPSG:4674")
color = resultado_melt_poligeo["S1"]
color = color.to_list()
#print(color)
for i in range(len(color)):
	if float(color[i]) > 0:
		color[i] = 1
	if float(color[i]) < 0:
		color[i] = -1
	if float(color[i]) == 0:
		color[i] = 0

color = pd.DataFrame(color, columns = ["cor"])
resultado_melt_poligeo["color"] = color

# Define discrete colormap
cmap = ListedColormap(['green', 'white', 'red'])

# Define boundaries (-1 to 0 = green, 0 to 1 = white, 1+ = red)
bounds = [-1, 0, 1, 2]  # You need one more than the number of colors
norm = BoundaryNorm(bounds, cmap.N)

# Plot the choropleth
base = resultado_melt_poligeo.plot(
    column="color",
    cmap=cmap,
    norm=norm,
    linewidth=0.1,
    edgecolor='black',
    legend=False,  # We’ll add custom legend
    ax=None
)

# Overlay other layer
xy.plot(ax=base, color="#FF000000", edgecolor="#636363", linewidth=0.1, )

# Add custom legend to include all bins (even if unused)
legend_elements = [
    Patch(facecolor='green', label='Negative'),
    Patch(facecolor='white', label='Neutral'),
    Patch(facecolor='red', label='Positive')
]

base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)

plt.legend(handles=legend_elements, title='Category', loc='lower left')
plt.title(f"Previsão de alteração nos casos \n semana {data_s0} à semana {data_s1}")

base.set_ylabel("Latitude")
base.set_xlabel("Longitude")

plt.tight_layout()


#S2
resultado_melt_poli = pd.merge(resultado["S2"], xy, on = "Município", how = "left")
resultado_melt_poligeo = gpd.GeoDataFrame(resultado_melt_poli, geometry = "geometry", crs = "EPSG:4674")
color = resultado_melt_poligeo["S2"]
color = color.to_list()
#print(color)
for i in range(len(color)):
	if float(color[i]) > 0:
		color[i] = 1
	if float(color[i]) < 0:
		color[i] = -1
	if float(color[i]) == 0:
		color[i] = 0

color = pd.DataFrame(color, columns = ["cor"])
resultado_melt_poligeo["color"] = color

# Define discrete colormap
cmap = ListedColormap(['green', 'white', 'red'])

# Define boundaries (-1 to 0 = green, 0 to 1 = white, 1+ = red)
bounds = [-1, 0, 1, 2]  # You need one more than the number of colors
norm = BoundaryNorm(bounds, cmap.N)

# Plot the choropleth
base = resultado_melt_poligeo.plot(
    column="color",
    cmap=cmap,
    norm=norm,
    linewidth=0.1,
    edgecolor='black',
    legend=False,  # We’ll add custom legend
    ax=None
)

# Overlay other layer
xy.plot(ax=base, color="#FF000000", edgecolor="#636363", linewidth=0.1)

# Add custom legend to include all bins (even if unused)
legend_elements = [
    Patch(facecolor='green', label='Negative'),
    Patch(facecolor='white', label='Neutral'),
    Patch(facecolor='red', label='Positive')
]
plt.legend(handles=legend_elements, title='Category', loc='lower left')
plt.title(f"Previsão de alteração nos casos \n semana {data_s1} para à semana {data_s2}")
base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)
base.set_ylabel("Latitude")
base.set_xlabel("Longitude")

plt.tight_layout()




#S3
resultado_melt_poli = pd.merge(resultado["S3"], xy, on = "Município", how = "left")
resultado_melt_poligeo = gpd.GeoDataFrame(resultado_melt_poli, geometry = "geometry", crs = "EPSG:4674")
color = resultado_melt_poligeo["S3"]
color = color.to_list()
#print(color)
for i in range(len(color)):
	if float(color[i]) > 0:
		color[i] = 1
	if float(color[i]) < 0:
		color[i] = -1
	if float(color[i]) == 0:
		color[i] = 0

color = pd.DataFrame(color, columns = ["cor"])
resultado_melt_poligeo["color"] = color

# Define discrete colormap
cmap = ListedColormap(['green', 'white', 'red'])

# Define boundaries (-1 to 0 = green, 0 to 1 = white, 1+ = red)
bounds = [-1, 0, 1, 2]  # You need one more than the number of colors
norm = BoundaryNorm(bounds, cmap.N)

# Plot the choropleth
base = resultado_melt_poligeo.plot(
    column="color",
    cmap=cmap,
    norm=norm,
    linewidth=0.1,
    edgecolor='black',
    legend=False,  # We’ll add custom legend
    ax=None
)

# Overlay other layer
xy.plot(ax=base, color="#FF000000", edgecolor="#636363", linewidth=0.1)

# Add custom legend to include all bins (even if unused)
legend_elements = [
    Patch(facecolor='green', label='Negative'),
    Patch(facecolor='white', label='Neutral'),
    Patch(facecolor='red', label='Positive')
]
plt.legend(handles=legend_elements, title='Category', loc='lower left')
plt.title(f"Previsão de alteração nos casos \n semana {data_s2} para semana {data_s3}")
base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)

plt.tight_layout()

base.set_ylabel("Latitude")
base.set_xlabel("Longitude")
plt.show()





