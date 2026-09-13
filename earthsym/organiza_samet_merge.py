import xarray as xr
import geopandas as gpd
from pathlib import Path
import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt


caminho_shp = "/home/sifapsc/shapefiles/BR_UF_2024.shp"

lat_min, lat_max = -29.35, -25.96
lon_min, lon_max = 306.16, 311.68



def prec(path_file):
	ds = xr.open_dataset(path_file)
	print(ds)
	sys.exit()
	nome_do_arquivo = Path(path_file).stem
	
	ds_sc = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
	df_sc = ds_sc.to_dataframe().reset_index()
	df_sc['lon_geo'] = df_sc['lon'].apply(lambda x: x - 360 if x > 180 else x)

	gdf_dados = gpd.GeoDataFrame(
		df_sc, 
		geometry=gpd.points_from_xy(df_sc['lon_geo'], df_sc['lat']),
		crs="EPSG:4326"
	)
	sh_sc = gpd.read_file(caminho_shp)

	if sh_sc.crs != "EPSG:4326":
		sh_sc = sh_sc.to_crs("EPSG:4326")
		
		
	gdf_sc_final = gpd.sjoin(gdf_dados, sh_sc, predicate='within')
	gdf_sc_final = gdf_sc_final.loc[gdf_sc_final["SIGLA_UF"] == "SC"]
	gdf_sc_final["pr"] = gdf_sc_final["pr"] * 3600

	gdf_sc_final['time'] = gpd.pd.to_datetime(gdf_sc_final['time'].astype(str))
	#gdf_sc_final['ano_mes'] = gdf_sc_final['time'].dt.strftime('%Y-%m')
	gdf_sc_final['ano'] = gdf_sc_final['time'].dt.year
	media_mensal_sc = gdf_sc_final.groupby('ano')['pr'].sum().reset_index()
	media_mensal_sc = media_mensal_sc.rename(columns={'pr': f"{nome_do_arquivo}"})


	return(media_mensal_sc)
	
path_file = Path("meteoro@172.16.0.110:/media/dados/operacao/merge/hourly/2010/01/01/MERGE_CPTEC_2010010100.grib2")
prec(path_file)
