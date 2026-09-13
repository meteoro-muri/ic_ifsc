import pandas as pd
import geopandas as gpd
import sys
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import matplotlib.colors as cls 
import numpy as np

# Define color dictionary for clusters
color_dict = {'0': 'orange', '1': 'purple', '-1': 'blue'}  
# Add more colours as needed


unicos = pd.read_csv("casos_primeiros.csv")
municipios = gpd.read_file("/home/sifapsc/scripts/matheus/dados_dengue/shapefiles/SC_Municipios_2022.shp")

br = "BR/BR_UF_2022.shp"
semana_epidemio = "2024-10-20"

##### MANIPULANDO TABELAS DE REVISÃO ####
tabela0_pivot = pd.read_csv('https://raw.githubusercontent.com/matheusf30/operacional_dengue/refs/heads/main/dados_operacao/casos_dive_total.csv')
tabela0_pivot_trans = tabela0_pivot.T
print(tabela0_pivot)
sys.exit()
tabela0_pivot = tabela0_pivot.drop(columns = ["index", "Semana"], index = {3, 4, 5})
print(tabela0_pivot)
sys.exit()
tabela0_pivot_trans = tabela0_pivot.T
print(tabela0_pivot_trans)
tabela0_pivot_trans = tabela0_pivot_trans.reset_index()
tabela0_pivot_trans = tabela0_pivot_trans.rename(columns = {"index": "Município", 0 : "S0", 1 : "S1", 2:"S2"})
print(tabela0_pivot_trans)

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
resultado = pd.DataFrame()
resultado["Município"] = tabela0_pivot_trans["Município"]
resultado["S1"] = tabela0_pivot_trans["S1"] - tabela0_pivot_trans["S0"]
resultado["S2"] = tabela0_pivot_trans["S2"] - tabela0_pivot_trans["S1"]

print(resultado)



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
#### CARTOGRAFIA ####

#SC_Coroplético
xy = municipios.copy()
xy.drop(columns = ["CD_MUN", "SIGLA_UF", "AREA_KM2"], inplace = True)
xy = xy.rename(columns = {"NM_MUN" : "Município"})
xy["Município"] = xy["Município"].str.upper() 
resultado_melt_poli = pd.merge(resultado, xy, on = "Município", how = "left")
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


bounds = [-1,0,1]
resultado_melt_poligeo.plot(column = "color", legend=True, cmap = "RdYlGn_r")



plt.show()





