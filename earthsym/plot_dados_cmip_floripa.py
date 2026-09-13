import sys
import glob
import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Coordenadas centrais de Florianópolis
LAT_FLORIPA = -27.59
LON_FLORIPA = -48.54
LON_FLORIPA_360 = 360 + LON_FLORIPA


def temp(path_file):
    ds = xr.open_dataset(path_file)
    nome_do_arquivo = Path(path_file).stem

    # Identifica o formato da longitude (0 a 360 ou -180 a 180)
    lon_target = LON_FLORIPA_360 if ds.lon.max() > 180 else LON_FLORIPA

    # Seleciona o ponto mais próximo de Florianópolis
    ds_floripa = ds.sel(lat=LAT_FLORIPA, lon=lon_target, method='nearest')
    
    # Extrai o ano diretamente via xarray (suporta cftime/noleap nativamente)
    ds_floripa['ano'] = ds_floripa.time.dt.year

    df_floripa = ds_floripa.to_dataframe().reset_index()

    # Identificar a variável de temperatura (ts, tasmax, temp)
    var_temp = 'ts' if 'ts' in df_floripa.columns else ('tasmax' if 'tasmax' in df_floripa.columns else 'temp')

    # Conversão de Kelvin para Celsius (se necessário)
    if df_floripa[var_temp].mean() > 100:
        df_floripa[var_temp] = df_floripa[var_temp] - 273.15

    media_anual_floripa = df_floripa.groupby('ano')[var_temp].max().reset_index()
    media_anual_floripa = media_anual_floripa.rename(columns={var_temp: f"{nome_do_arquivo}"})

    return media_anual_floripa


def prec(path_file):
    ds = xr.open_dataset(path_file)
    nome_do_arquivo = Path(path_file).stem

    # Identifica o formato da longitude (0 a 360 ou -180 a 180)
    lon_target = LON_FLORIPA_360 if ds.lon.max() > 180 else LON_FLORIPA

    # Seleciona o ponto mais próximo de Florianópolis
    ds_floripa = ds.sel(lat=LAT_FLORIPA, lon=lon_target, method='nearest')
    
    # Extrai ano e número de dias no mês via xarray antes do dataframe
    ds_floripa['ano'] = ds_floripa.time.dt.year
    ds_floripa['dias_no_mes'] = ds_floripa.time.dt.days_in_month

    df_floripa = ds_floripa.to_dataframe().reset_index()

    # Conversão de unidades: kg/m²/s -> mm/mês
    df_floripa['pr_mm_mes'] = df_floripa['pr'] * 86400 * df_floripa['dias_no_mes']

    # Média mensal do ano para o ponto de Florianópolis
    media_anual_floripa = df_floripa.groupby('ano')['pr_mm_mes'].mean().reset_index()
    media_anual_floripa = media_anual_floripa.rename(columns={'pr_mm_mes': f"{nome_do_arquivo}"})

    return media_anual_floripa

def plot(df):
    # 1. Dicionário de Estilos
    estilos_modelos = {
        # TEMPERATURA
        'temp_Amon_TaiESM1_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'TaiESM1 (SSP1-2.6)'},
        'temp_Amon_TaiESM1_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'TaiESM1 (SSP2-4.5)'},
        'temp_Amon_TaiESM1_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'TaiESM1 (SSP5-8.5)'},
        'temp_gfdl_esm4_ssp1_2_6':     {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP1-2.6)'},
        'temp_gfdl_esm4_ssp2_4_5':     {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP2-4.5)'},
        'temp_gfdl_esm4_ssp5_8_5':     {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP5-8.5)'},
        'temp_samet':                  {'color': 'black',   'linestyle': 'solid', 'linewidth': 1.2, 'label': 'SAMeT (Avg. Max. Observed)'},

        # PRECIPITAÇÃO
        'prec_ec_earth3_veg_lr_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP1-2.6)'},
        'prec_ec_earth3_veg_lr_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP2-4.5)'},
        'prec_ec_earth3_veg_lr_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP5-8.5)'},
        'prec_access_cm2_ssp1_2_6':       {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP1-2.6)'},
        'prec_access_cm2_ssp2_4_5':       {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP2-4.5)'},
        'prec_access_cm2_ssp5_8_5':       {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP5-8.5)'},
        'prec_merge':                     {'color': 'black',   'linestyle': 'solid', 'linewidth': 1.2, 'label': 'MERGE (Observed)'}
    }

    # 2. Criar a figura com 2 subplots compartilhando o eixo X
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

    # 4. Subplot 1: Temperatura
    ax_temp.set_title("IPCC Projections - Florianópolis/SC:  Annual Average Temperature (°C)", fontsize=12, fontweight='bold', pad=10)
    ax_temp.set_ylabel("Temperature (°C)", fontsize=10, fontweight='bold')
    ax_temp.grid(True, linestyle=':', alpha=0.6)
    
    temp_min_destaque, temp_max_destaque = 24.0, 27.0
    ax_temp.axhspan(
        temp_min_destaque, temp_max_destaque, 
        color='yellow', alpha=0.3, zorder=0, 
        label='Critical Threshold (24-27°C)'
    )
    ax_temp.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)

    # 5. Subplot 2: Precipitação
    ax_prec.set_title("IPCC Projections - Florianópolis/SC: Annual Average Precipitation (mm/month)", fontsize=12, fontweight='bold', pad=10)
    ax_prec.set_xlabel("Year", fontsize=10, fontweight='bold')
    ax_prec.set_ylabel("Precipitation (mm/month)", fontsize=10, fontweight='bold')
    ax_prec.grid(True, linestyle=':', alpha=0.6)
    
    prec_min_destaque, prec_max_destaque = 0, 200
    ax_prec.axhspan(
        prec_min_destaque, prec_max_destaque, 
        color='yellow', alpha=0.3, zorder=0, 
        label='Critical Threshold (0-200 mm)'
    )
    ax_prec.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)

    plt.tight_layout()
    plt.savefig("projecoes_climaticas_florianopolis.png", dpi=300, bbox_inches='tight')
    plt.show()


# =========================================================
# EXECUÇÃO PRINCIPAL
# =========================================================
path_file = Path("/dados4/pesquisa/meteoromuri/earthsym/")

# Processar Precipitação
chuva = pd.DataFrame()
for arquivo in path_file.rglob('prec_*.nc'):
    df = prec(arquivo)
    nome_do_arquivo = Path(arquivo).stem
    if "ano" not in chuva.columns:
        chuva = pd.concat([chuva, df], ignore_index=True)
    else:
        df = df.drop('ano', axis=1)
        chuva[f"{nome_do_arquivo}"] = df

# Processar Temperatura
temperaturas = pd.DataFrame()
for arquivo in path_file.rglob('temp_*.nc'):
    df = temp(arquivo)
    nome_do_arquivo = Path(arquivo).stem
    if "ano" not in temperaturas.columns:
        temperaturas = pd.concat([temperaturas, df], ignore_index=True)
    else:
        df = df.drop('ano', axis=1)
        temperaturas[f"{nome_do_arquivo}"] = df

# Unir projeções
df_proj = pd.merge(temperaturas, chuva, on='ano')
df_proj.to_csv("geral_proj_florianopolis.csv", index=False)

# Carregar dados históricos e realizar o merge
df_obs = pd.read_csv("serie_historica_anual_merge_samet_floripa.csv")
df_obs = df_obs.loc[df_obs["ano"] >= 2015]

df_final = pd.merge(df_proj, df_obs[['ano', 'prec_merge', 'temp_samet']], on='ano', how='left')

# Gerar o gráfico
plot(df_final)
