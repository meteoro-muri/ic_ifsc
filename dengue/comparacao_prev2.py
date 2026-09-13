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

##### MANIPULANDO TABELAS DE REVISÃO ####
#tabela0_pivot = pd.read_csv('https://raw.githubusercontent.com/matheusf30/operacional_dengue/refs/heads/main/dados_operacao/casos_dive_pivot_total.csv')
#print(tabela0_pivot)
#tabela0_pivot = tabela0_pivot.drop(columns = 'Semana')
#tabela0_pivot_trans = tabela0_pivot.T
#print(tabela0_pivot_trans)
#tabela0_pivot_trans = tabela0_pivot_trans.reset_index()
#tabela0_pivot_trans = tabela0_pivot_trans.rename(columns = {"index": "Município"})
#resultado = pd.DataFrame()
#resultado["Município"] = tabela0_pivot_trans["Município"]
#resultado["S1"] = tabela0_pivot_trans[20] - tabela0_pivot_trans[19]
#resultado["S2"] = tabela0_pivot_trans[21] - tabela0_pivot_trans[20]
#print(resultado)




#tabela0_pivot_trans_melt = tabela0_pivot_trans.melt()
#print(tabela0_pivot_trans_melt)

#sys.exit()
#S0 = tabela0_pivot[tabela0_pivot['index'] == 'S0']
#S1 = tabela0_pivot[tabela0_pivot['index'] == 'S1']
#S2 = tabela0_pivot[tabela0_pivot['index'] == 'S2']
#S0 = S0.T
#S1 = S1.T
#S2 = S2.T

#S1 = S1.drop(labels = ["index","Semana"])
#print(S1)
#S1 = S1.melt(id_vars = S1.index, var_name = "Município")
#S1["Munícipio"] = S1
#sys.exit()
#S0 = S0.drop(labels = ["index","Semana"])
#print(S1)
#print(S0.index)
#sys.exit()



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



tabela0_pivot = pd.read_csv('https://raw.githubusercontent.com/matheusf30/operacional_dengue/refs/heads/main/modelagem/resultados/dados_previstos/previsao_melt_total_v20250216_h0_r2.csv')
tabela0_pivot["Semana"] = pd.to_datetime(tabela0_pivot["Semana"])
print(tabela0_pivot)


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

base.tick_params(axis='both', labelsize=5)
for spine in base.spines.values():
    spine.set_linewidth(0.5)

plt.tight_layout()

base.set_ylabel("Latitude")
base.set_xlabel("Longitude")
plt.show()





