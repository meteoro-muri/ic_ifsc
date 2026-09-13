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

    ds_sc = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    
    # Extrair 'ano' e 'mes' direto do Xarray via cftime
    ds_sc['ano'] = ds_sc.time.dt.year
    ds_sc['mes'] = ds_sc.time.dt.month

    # Converter para DataFrame
    df_sc = ds_sc.to_dataframe().reset_index()
    
    # Filtrar os meses de Outono (Março=3, Abril=4, Maio=5)
    df_sc = df_sc[df_sc['mes'].isin([3, 4, 5])]
    
    df_sc['lon_geo'] = df_sc['lon'].apply(lambda x: x - 360 if x > 180 else x)

    gdf_dados = gpd.GeoDataFrame(
        df_sc, 
        geometry=gpd.points_from_xy(df_sc['lon_geo'], df_sc['lat']),
        crs="EPSG:4326"
    )
    sh_brasil = gpd.read_file(caminho_shp)
    sh_sc = sh_brasil[sh_brasil["SIGLA_UF"] == "SC"]

    if sh_sc.crs is None:
        sh_sc = sh_sc.set_crs("EPSG:4326")
    elif sh_sc.crs != "EPSG:4326":
        sh_sc = sh_sc.to_crs("EPSG:4326")

    gdf_sc_final = gpd.sjoin(gdf_dados, sh_sc, predicate='within')
    
    gdf_sc_final["ts"] = gdf_sc_final["ts"] - 273.15  # Kelvin para Celsius

    # Média do outono por ponto e depois média espacial de SC
    temp_outono_por_ponto = gdf_sc_final.groupby(['ano', 'lat', 'lon_geo'])['ts'].mean().reset_index()
    media_outono_sc = temp_outono_por_ponto.groupby('ano')['ts'].mean().reset_index()
    
    media_outono_sc = media_outono_sc.rename(columns={'ts': f"{nome_do_arquivo}"})

    return media_outono_sc


def prec(path_file):
    ds = xr.open_dataset(path_file)
    nome_do_arquivo = Path(path_file).stem

    ds_sc = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    
    # Extrair 'ano', 'mes' e 'dias_no_mes' no Xarray
    ds_sc['ano'] = ds_sc.time.dt.year
    ds_sc['mes'] = ds_sc.time.dt.month
    ds_sc['dias_no_mes'] = ds_sc.time.dt.days_in_month

    # Converter para DataFrame
    df_sc = ds_sc.to_dataframe().reset_index()

    # Filtrar os meses de Outono (Março=3, Abril=4, Maio=5)
    df_sc = df_sc[df_sc['mes'].isin([3, 4, 5])]

    df_sc['lon_geo'] = df_sc['lon'].apply(lambda x: x - 360 if x > 180 else x)

    sh_brasil = gpd.read_file(caminho_shp)
    sh_sc = sh_brasil[sh_brasil["SIGLA_UF"] == "SC"]

    if sh_sc.crs is None:
        sh_sc = sh_sc.set_crs("EPSG:4326")
    elif sh_sc.crs != "EPSG:4326":
        sh_sc = sh_sc.to_crs("EPSG:4326")

    gdf_dados = gpd.GeoDataFrame(
        df_sc, 
        geometry=gpd.points_from_xy(df_sc['lon_geo'], df_sc['lat']),
        crs="EPSG:4326"
    )

    gdf_sc_final = gpd.sjoin(gdf_dados, sh_sc, predicate='within')
    
    # Conversão de kg/m²/s para mm no mês
    gdf_sc_final['pr_mm_mes'] = gdf_sc_final['pr'] * 86400 * gdf_sc_final['dias_no_mes']

    # Acumulado total da estação de Outono por ponto
    chuva_outono_por_ponto = gdf_sc_final.groupby(['ano', 'lat', 'lon_geo'])['pr_mm_mes'].mean().reset_index()

    # Média espacial de todos os pontos do estado para o outono
    media_outono_sc = chuva_outono_por_ponto.groupby('ano')['pr_mm_mes'].mean().reset_index()
    
    media_outono_sc = media_outono_sc.rename(columns={'pr_mm_mes': f"{nome_do_arquivo}"})

    return media_outono_sc


def plot(df):
    estilos_modelos = {
        # TEMPERATURA (MPI vs GFDL vs Observado)
        'temp_mpi_esm1_2_lr_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'MPI-ESM1-2-LR (SSP1-2.6)'},
        'temp_mpi_esm1_2_lr_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'MPI-ESM1-2-LR (SSP2-4.5)'},
        'temp_mpi_esm1_2_lr_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'MPI-ESM1-2-LR (SSP5-8.5)'},
        'temp_gfdl_esm4_ssp1_2_6':     {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP1-2.6)'},
        'temp_gfdl_esm4_ssp2_4_5':     {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP2-4.5)'},
        'temp_gfdl_esm4_ssp5_8_5':     {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP5-8.5)'},
        'temp_samet':                  {'color': 'black',   'linestyle': 'solid',  'linewidth': 1.5, 'label': 'SAMeT (Observado)'},

        # PRECIPITAÇÃO (EC-Earth3 vs ACCESS-CM2 vs Observado)
        'prec_ec_earth3_veg_lr_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP1-2.6)'},
        'prec_ec_earth3_veg_lr_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP2-4.5)'},
        'prec_ec_earth3_veg_lr_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP5-8.5)'},
        'prec_access_cm2_ssp1_2_6':       {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP1-2.6)'},
        'prec_access_cm2_ssp2_4_5':       {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP2-4.5)'},
        'prec_access_cm2_ssp5_8_5':       {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP5-8.5)'},
        'prec_merge':                     {'color': 'black',   'linestyle': 'solid',  'linewidth': 1.5, 'label': 'MERGE (Observado)'}
    }

    fig, (ax_temp, ax_prec) = plt.subplots(nrows=2, ncols=1, figsize=(11, 8), sharex=True)

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

    # Subplot 1: Temperatura Média no Outono
    ax_temp.set_title("Projeções Climáticas: Temperatura Média no Outono - MAM (°C)", fontsize=12, fontweight='bold', pad=10)
    ax_temp.set_ylabel("Temperatura (°C)", fontsize=10, fontweight='bold')
    ax_temp.grid(True, linestyle=':', alpha=0.6)
    ax_temp.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
    temp_min_destaque, temp_max_destaque = 24.0, 27.0
    ax_temp.axhspan(
        temp_min_destaque, temp_max_destaque, 
        color='yellow', alpha=0.15, zorder=0, 
        label='Limiar Crítico (18-20°C)'
    )

    # Subplot 2: Acumulado de Precipitação no Outono
    ax_prec.set_title("Projeções Climáticas: Precipitação Total no Outono - MAM (mm)", fontsize=12, fontweight='bold', pad=10)
    ax_prec.set_xlabel("Ano", fontsize=10, fontweight='bold')
    ax_prec.set_ylabel("Precipitação (mm/outono)", fontsize=10, fontweight='bold')
    ax_prec.grid(True, linestyle=':', alpha=0.6)
    ax_prec.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
    prec_min_destaque, prec_max_destaque = 0, 200
    ax_prec.axhspan(
        prec_min_destaque, prec_max_destaque, 
        color='yellow', alpha=0.15, zorder=0, 
        label='Faixa Normal (400-600mm)'
    )

    plt.tight_layout()
    plt.savefig("projecoes_climaticas_outono_MAM.png", dpi=300, bbox_inches='tight')
    plt.show()


# =========================================================
# PROCESSAMENTO DOS ARQUIVOS
# =========================================================
path_file = Path("/dados4/pesquisa/meteoromuri/earthsym/")

chuva = pd.DataFrame()
for arquivo in path_file.rglob('prec_*.nc'):
    df = prec(arquivo)
    nome_do_arquivo = Path(arquivo).stem
    if "ano" not in chuva.columns:
        chuva = pd.concat([chuva, df], ignore_index=True)
    else:
        df = df.drop('ano', axis=1)
        chuva[f"{nome_do_arquivo}"] = df

temperaturas = pd.DataFrame()
for arquivo in path_file.rglob('temp_*.nc'):
    df = temp(arquivo)
    nome_do_arquivo = Path(arquivo).stem
    if "ano" not in temperaturas.columns:
        temperaturas = pd.concat([temperaturas, df], ignore_index=True)
    else:
        df = df.drop('ano', axis=1)
        temperaturas[f"{nome_do_arquivo}"] = df

# 1. Cruzamento das projeções climáticas CMIP6
df_outono = pd.merge(temperaturas, chuva, on='ano')

# 2. Carregar e unificar com os dados observados (MERGE e SAMeT)
caminho_obs = "serie_historica_merge_samet_sc.csv"
df_obs = pd.read_csv(caminho_obs)

df_outono = pd.merge(df_outono, df_obs[['ano', 'prec_merge', 'temp_samet']], on='ano', how='left')

# 3. Preencher anos sem dados observados com 0.0
#df_outono['prec_merge'] = df_outono['prec_merge']
#df_outono['temp_samet'] = df_outono['temp_samet']

# 4. Salvar CSV compilado final
df_outono.to_csv("geral_proj_outono.csv", index=False)

# 5. Plotar o resultado contendo CMIP6 + MERGE + SAMeT
plot(df_outono)
