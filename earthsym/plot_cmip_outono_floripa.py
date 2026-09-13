import sys
import glob
import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Coordenadas de Florianópolis
LAT_FLORIPA = -27.59
LON_FLORIPA = -48.54
LON_FLORIPA_360 = 360 + LON_FLORIPA


def temp_floripa(path_file):
    ds = xr.open_dataset(path_file)
    nome_do_arquivo = Path(path_file).stem

    lon_target = LON_FLORIPA_360 if ds.lon.max() > 180 else LON_FLORIPA

    # Selecionar ponto mais próximo
    ds_floripa = ds.sel(lat=LAT_FLORIPA, lon=lon_target, method='nearest')
    
    ds_floripa['ano'] = ds_floripa.time.dt.year
    ds_floripa['mes'] = ds_floripa.time.dt.month

    df_ponto = ds_floripa.to_dataframe().reset_index()
    
    # Filtrar meses de Outono (Março=3, Abril=4, Maio=5)
    df_ponto = df_ponto[df_ponto['mes'].isin([3, 4, 5])]
    
    # Identificar nome da variável de temperatura no dataset
    var_temp = 'tasmax' if 'tasmax' in df_ponto.columns else ('ts' if 'ts' in df_ponto.columns else 'temp')

    # Conversão de Kelvin para Celsius se necessário
    if df_ponto[var_temp].mean() > 100:
        df_ponto[var_temp] = df_ponto[var_temp] - 273.15

    # MÁXIMA do outono para o ponto de Florianópolis (.max())
    max_outono_floripa = df_ponto.groupby('ano')[var_temp].max().reset_index()
    max_outono_floripa = max_outono_floripa.rename(columns={var_temp: f"{nome_do_arquivo}"})

    return max_outono_floripa


def prec_floripa(path_file):
    ds = xr.open_dataset(path_file)
    nome_do_arquivo = Path(path_file).stem

    lon_target = LON_FLORIPA_360 if ds.lon.max() > 180 else LON_FLORIPA

    ds_floripa = ds.sel(lat=LAT_FLORIPA, lon=lon_target, method='nearest')
    
    ds_floripa['ano'] = ds_floripa.time.dt.year
    ds_floripa['mes'] = ds_floripa.time.dt.month
    ds_floripa['dias_no_mes'] = ds_floripa.time.dt.days_in_month

    df_ponto = ds_floripa.to_dataframe().reset_index()

    df_ponto = df_ponto[df_ponto['mes'].isin([3, 4, 5])]

    # Conversão de kg/m²/s para mm acumulado no mês
    df_ponto['pr_mm_mes'] = df_ponto['pr'] * 86400 * df_ponto['dias_no_mes']

    # Média mensal da estação de Outono (MAM) -> alterado para .mean()
    chuva_outono_floripa = df_ponto.groupby('ano')['pr_mm_mes'].mean().reset_index()
    chuva_outono_floripa = chuva_outono_floripa.rename(columns={'pr_mm_mes': f"{nome_do_arquivo}"})

    return chuva_outono_floripa


def plot(df):
    estilos_modelos = {
        # TEMPERATURA MÁXIMA
        'temp_Amon_TaiESM1_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'TaiESM1 (SSP1-2.6)'},
        'temp_Amon_TaiESM1_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'TaiESM1 (SSP2-4.5)'},
        'temp_Amon_TaiESM1_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'TaiESM1 (SSP5-8.5)'},
        'temp_gfdl_esm4_ssp1_2_6':     {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP1-2.6)'},
        'temp_gfdl_esm4_ssp2_4_5':     {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP2-4.5)'},
        'temp_gfdl_esm4_ssp5_8_5':     {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'GFDL-ESM4 (SSP5-8.5)'},
        'temp_samet':                  {'color': 'black',   'linestyle': 'solid',  'linewidth': 1.5, 'label': 'SAMeT (Avg. Max. Observed)'},

        # PRECIPITAÇÃO
        'prec_ec_earth3_veg_lr_ssp1_2_6': {'color': '#2ca02c', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP1-2.6)'},
        'prec_ec_earth3_veg_lr_ssp2_4_5': {'color': '#ff7f0e', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP2-4.5)'},
        'prec_ec_earth3_veg_lr_ssp5_8_5': {'color': '#d62728', 'linestyle': '-', 'linewidth': 1.2, 'label': 'EC-Earth3-Veg-LR (SSP5-8.5)'},
        'prec_access_cm2_ssp1_2_6':       {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP1-2.6)'},
        'prec_access_cm2_ssp2_4_5':       {'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP2-4.5)'},
        'prec_access_cm2_ssp5_8_5':       {'color': '#d62728', 'linestyle': '--', 'linewidth': 1.2, 'label': 'ACCESS-CM2 (SSP5-8.5)'},
        'prec_merge':                     {'color': 'black',   'linestyle': 'solid',  'linewidth': 1.5, 'label': 'MERGE (Observed)'}
    }

    fig, (ax_temp, ax_prec) = plt.subplots(nrows=2, ncols=1, figsize=(11, 8), sharex=True)

    # Identificar o período observado para aplicar a faixa amarela nos dois gráficos
    anos_obs = df.dropna(subset=['temp_samet'])['ano'] if 'temp_samet' in df.columns else df.dropna(subset=['prec_merge'])['ano']
    ano_inicio_obs = anos_obs.min()
    ano_fim_obs = anos_obs.max()

    # Plotar as linhas
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

    # Subplot 1: Temperatura Máxima no Outono
    ax_temp.set_title("IPCC Projections - Florianópolis/SC: Monthly Average Temperature on Autumn (MAM)", fontsize=12, fontweight='bold', pad=10)
    ax_temp.set_ylabel("Maximum Temperature (°C)", fontsize=10, fontweight='bold')
    ax_temp.grid(True, linestyle=':', alpha=0.6)
    ax_temp.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
    temp_min_destaque, temp_max_destaque = 24.0, 27.0
    ax_temp.axhspan(
        temp_min_destaque, temp_max_destaque, 
        color='yellow', alpha=0.3, zorder=0, 
        label='Critical Threshold (24-27°C)'
    )
    ax_temp.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)

    # Subplot 2: Média Mensal de Precipitação no Outono
    ax_prec.set_title("IPCC Projections - Florianópolis/SC: Monthly Average Precipitation on Autumn (MAM)", fontsize=12, fontweight='bold', pad=10)
    ax_prec.set_xlabel("Year", fontsize=10, fontweight='bold')
    ax_prec.set_ylabel("Average Precipitation (mm/month)", fontsize=10, fontweight='bold')
    ax_prec.grid(True, linestyle=':', alpha=0.6)
    ax_prec.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
    prec_min_destaque, prec_max_destaque = 0, 200
    ax_prec.axhspan(
        prec_min_destaque, prec_max_destaque, 
        color='yellow', alpha=0.3, zorder=0, 
        label='Critical Threshold (0-200mm)'
    )
    ax_prec.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)

    plt.tight_layout()
    plt.savefig("projecoes_climaticas_outono_max_florianopolis.png", dpi=300, bbox_inches='tight')
    plt.show()


# =========================================================
# PROCESSAMENTO DOS ARQUIVOS
# =========================================================
path_file = Path("/dados4/pesquisa/meteoromuri/earthsym/")

chuva = pd.DataFrame()
for arquivo in path_file.rglob('prec_*.nc'):
    df = prec_floripa(arquivo)
    nome_do_arquivo = Path(arquivo).stem
    if "ano" not in chuva.columns:
        chuva = pd.concat([chuva, df], ignore_index=True)
    else:
        df = df.drop('ano', axis=1)
        chuva[f"{nome_do_arquivo}"] = df

temperaturas = pd.DataFrame()
for arquivo in path_file.rglob('temp_*.nc'):
    df = temp_floripa(arquivo)
    nome_do_arquivo = Path(arquivo).stem
    if "ano" not in temperaturas.columns:
        temperaturas = pd.concat([temperaturas, df], ignore_index=True)
    else:
        df = df.drop('ano', axis=1)
        temperaturas[f"{nome_do_arquivo}"] = df

# 1. Cruzamento das projeções CMIP6 para Florianópolis
df_floripa = pd.merge(temperaturas, chuva, on='ano')

# 2. Carregar e unificar com os dados observados históricos
caminho_obs = "serie_historica_outono_merge_samet_floripa.csv"
df_obs = pd.read_csv(caminho_obs)

# Garantir que a série do MERGE observada também reflita a média mensal (se o arquivo CSV original contiver o acumulado da estação)
# Caso a prec_merge no CSV original seja o acumulado total de 3 meses, dividimos por 3:
if 'prec_merge' in df_obs.columns and df_obs['prec_merge'].mean() > 200:
    df_obs['prec_merge'] = df_obs['prec_merge'] / 3.0

df_floripa = pd.merge(df_floripa, df_obs[['ano', 'prec_merge', 'temp_samet']], on='ano', how='left')

# 3. Salvar o CSV final
df_floripa.to_csv("geral_proj_outono_max_florianopolis.csv", index=False)

# 4. Exibir o gráfico
plot(df_floripa)
