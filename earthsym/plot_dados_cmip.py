import sys
import glob
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt

caminho_shp = "/home/sifapsc/shapefiles/BR_UF_2024.shp"
lat_min, lat_max = -29.35, -25.96
lon_min, lon_max = 306.16, 311.68


def temp(path_file):
	ds = xr.open_dataset(path_file)
	nome_do_arquivo = Path(path_file).stem
	#print(nome_do_arquivo)

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
	gdf_sc_final["ts"] = gdf_sc_final["ts"] - 273

	gdf_sc_final['time'] = gpd.pd.to_datetime(gdf_sc_final['time'].astype(str))
	#gdf_sc_final['ano_mes'] = gdf_sc_final['time'].dt.strftime('%Y-%m')
	gdf_sc_final['ano'] = gdf_sc_final['time'].dt.year
	media_mensal_sc = gdf_sc_final.groupby('ano')['ts'].mean().reset_index()
	media_mensal_sc = media_mensal_sc.rename(columns={'ts': f"{nome_do_arquivo}"})


	return(media_mensal_sc)

def prec(path_file):
    ds = xr.open_dataset(path_file)
    nome_do_arquivo = Path(path_file).stem

    # 1. Recorte da caixa delimitadora no Xarray
    ds_sc = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    df_sc = ds_sc.to_dataframe().reset_index()

    # Converter longitude para o intervalo [-180, 180] (graus oeste)
    df_sc['lon_geo'] = df_sc['lon'].apply(lambda x: x - 360 if x > 180 else x)

    # 2. Leitura e preparação do Shapefile do SC
    sh_brasil = gpd.read_file(caminho_shp)
    sh_sc = sh_brasil[sh_brasil["SIGLA_UF"] == "SC"]

    if sh_sc.crs is None:
        sh_sc = sh_sc.set_crs("EPSG:4326")
    elif sh_sc.crs != "EPSG:4326":
        sh_sc = sh_sc.to_crs("EPSG:4326")

    # 3. Transforma a grade em GeoDataFrame
    gdf_dados = gpd.GeoDataFrame(
        df_sc, 
        geometry=gpd.points_from_xy(df_sc['lon_geo'], df_sc['lat']),
        crs="EPSG:4326"
    )

    # 4. Spatial Join (recorta apenas os pontos dentro de SC)
    gdf_sc_final = gpd.sjoin(gdf_dados, sh_sc, predicate='within')
    
    # 5. Formatação das datas
    gdf_sc_final['time'] = pd.to_datetime(gdf_sc_final['time'])
    gdf_sc_final['ano'] = gdf_sc_final['time'].dt.year

    # =========================================================
    # OPÇÃO B: CONVERSÃO DE UNIDADES (kg/m²/s -> mm/mês)
    # =========================================================
    # 86400 (segundos/dia) * dias_no_mês do registro correspondente
    gdf_sc_final['dias_no_mes'] = gdf_sc_final['time'].dt.days_in_month
    gdf_sc_final['pr_mm_mes'] = gdf_sc_final['pr'] * 86400 * gdf_sc_final['dias_no_mes']

    # =========================================================
    # AGREGAÇÃO ANUAL (Pontos do grid -> Média do Estado)
    # =========================================================
    # Passo A: média dos 12 meses do ano para cada ponto individual do grid (lat, lon)
    chuva_anual_por_ponto = gdf_sc_final.groupby(['ano', 'lat', 'lon_geo'])['pr_mm_mes'].mean().reset_index()

    # Passo B: Média de todos os pontos do estado para cada ano
    media_anual_sc = chuva_anual_por_ponto.groupby('ano')['pr_mm_mes'].mean().reset_index()
    
    # Renomeia a coluna com o nome do arquivo/modelo
    media_anual_sc = media_anual_sc.rename(columns={'pr_mm_mes': f"{nome_do_arquivo}"})

    return media_anual_sc	
def plot(df):
	# 1. Dicionário de Estilos
	estilos_modelos = {
		# TEMPERATURA (MPI vs GFDL)
		'temp_mpi_esm1_2_lr_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'MPI-ESM1-2-LR (SSP1-2.6)'},
		'temp_mpi_esm1_2_lr_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'MPI-ESM1-2-LR (SSP2-4.5)'},
		'temp_mpi_esm1_2_lr_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'MPI-ESM1-2-LR (SSP5-8.5)'},
		'temp_gfdl_esm4_ssp1_2_6':     {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP1-2.6)'},
		'temp_gfdl_esm4_ssp2_4_5':     {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP2-4.5)'},
		'temp_gfdl_esm4_ssp5_8_5':     {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP5-8.5)'},
		'temp_samet':                  {'color': 'black',   'linestyle': 'solid', 'linewidth': 1.2, 'label': 'SAMeT'},
		

		# PRECIPITAÇÃO (EC-Earth3 vs ACCESS-CM2)
		'prec_ec_earth3_veg_lr_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP1-2.6)'},
		'prec_ec_earth3_veg_lr_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP2-4.5)'},
		'prec_ec_earth3_veg_lr_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP5-8.5)'},
		'prec_access_cm2_ssp1_2_6':       {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP1-2.6)'},
		'prec_access_cm2_ssp2_4_5':       {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP2-4.5)'},
		'prec_access_cm2_ssp5_8_5':       {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP5-8.5)'},
		'prec_merge':                     {'color': 'black',   'linestyle': 'solid', 'linewidth': 1.2, 'label': 'MERGE'}
	}

	# 2. Criar a figura com 2 subplots (linhas=2, colunas=1) compartilhando o eixo X
	fig, (ax_temp, ax_prec) = plt.subplots(nrows=2, ncols=1, figsize=(11, 8), sharex=True)

	# 3. Iterar e plotar nos subplots correspondentes
	for coluna, estilo in estilos_modelos.items():
		if coluna in df.columns:
		    if coluna.startswith('temp_'):
		        ax_temp.plot(
		            df['ano'], df[coluna],
		            color=estilo['color'],
		            linestyle=estilo['linestyle'],
		            linewidth=estilo['linewidth'],
		            label=estilo['label']
		        )
		    elif coluna.startswith('prec_'):
		        ax_prec.plot(
		            df['ano'], df[coluna],
		            color=estilo['color'],
		            linestyle=estilo['linestyle'],
		            linewidth=estilo['linewidth'],
		            label=estilo['label']
		        )

	# 4. Ajustes do Subplot 1: Temperatura
	ax_temp.set_title("Projeções Climáticas: Temperatura (°C)", fontsize=12, fontweight='bold', pad=10)
	ax_temp.set_ylabel("Temperatura (°C)", fontsize=10, fontweight='bold')
	ax_temp.grid(True, linestyle=':', alpha=0.6)
	ax_temp.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
	temp_min_destaque, temp_max_destaque = 24.0, 27.0
	ax_temp.axhspan(
		temp_min_destaque, temp_max_destaque, 
		color='yellow', alpha=0.15, zorder=0, 
		label='Limiar Crítico (18-20°C)')

	# 5. Ajustes do Subplot 2: Precipitação
	ax_prec.set_title("Projeções Climáticas: Precipitação (mm/mês)", fontsize=12, fontweight='bold', pad=10)
	ax_prec.set_xlabel("Ano", fontsize=10, fontweight='bold')
	ax_prec.set_ylabel("Precipitação (mm)", fontsize=10, fontweight='bold')
	ax_prec.grid(True, linestyle=':', alpha=0.6)
	ax_prec.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
	prec_min_destaque, prec_max_destaque = 0, 200
	ax_prec.axhspan(
		prec_min_destaque, prec_max_destaque, 
		color='yellow', alpha=0.15, zorder=0, 
		label='Faixa Normal (400-600mm)')

	# 6. Ajustar o layout para não cortar as legendas laterais
	plt.tight_layout()

	# Salvar ou exibir
	plt.savefig("projecoes_climaticas_subplots.png", dpi=300, bbox_inches='tight')
	plt.show()

'''
path_file = Path("/dados4/pesquisa/meteoromuri/earthsym/")
chuva = pd.DataFrame()
for arquivo in path_file.rglob(f'prec_*.nc'):
	df = prec(arquivo)
	nome_do_arquivo = Path(arquivo).stem
	if "ano" not in chuva.columns:
		chuva = pd.concat([chuva, df], ignore_index=True)
	else:
		df = df.drop('ano', axis=1)
		chuva[f"{nome_do_arquivo}"] = df

		
temperaturas = pd.DataFrame()
for arquivo in path_file.rglob(f'temp_*.nc'):
	df = temp(arquivo)
	nome_do_arquivo = Path(arquivo).stem
	if "ano" not in temperaturas.columns:
		#print(temperaturas)
		temperaturas = pd.concat([temperaturas, df], ignore_index=True)
		#print(temperaturas)
	else:
		df = df.drop('ano', axis=1)
		#print(df)
		temperaturas[f"{nome_do_arquivo}"] = df
df = pd.merge(temperaturas,chuva)
df.to_csv("geral_proj.csv")
'''
df = pd.read_csv("geral_proj.csv")
print(df)
df2 = pd.read_csv("serie_historica_merge_samet_sc.csv")
df2 = df2.loc[df2["ano"]>=2015]
df = pd.merge(df, df2[['ano', 'prec_merge', 'temp_samet']],on='ano', how = 'left')
plot(df)






