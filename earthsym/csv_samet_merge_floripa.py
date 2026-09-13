# -*- coding: utf-8 -*-
import xarray as xr
import pandas as pd
import numpy as np

# Coordenadas centrais de Florianópolis
LAT_FLORIPA = -27.59
LON_FLORIPA = -48.54

def extrair_serie_temporal_floripa_outono(caminho_nc, var_desejada, funcao_agregacao='mean'):
    '''
    Extrai a série temporal da estação de Outono (MAM) do ponto mais próximo 
    de Florianópolis/SC.
    '''
    # 1. Carregar o NetCDF
    ds = xr.open_dataset(caminho_nc)

    # Identificar nome da variável
    var_nc = None
    for nome in [var_desejada, 'prec', 'precip', 'tmed', 'temp', 't2m', 'tasmax', 'tmax']:
        if nome in ds.data_vars:
            var_nc = nome
            break
            
    if not var_nc:
        raise KeyError(f"Variável {var_desejada} não encontrada no arquivo {caminho_nc}")

    da = ds[var_nc]

    # Identificar nomes das coordenadas de Lat/Lon
    lat_name = 'lat' if 'lat' in da.coords else ('latitude' if 'latitude' in da.coords else None)
    lon_name = 'lon' if 'lon' in da.coords else ('longitude' if 'longitude' in da.coords else None)

    # Identificar se o dataset usa longitude de 0 a 360 ou -180 a 180
    lon_target = (360 + LON_FLORIPA) if da[lon_name].max() > 180 else LON_FLORIPA

    # 2. Seleção do Ponto Mais Próximo de Florianópolis
    da_floripa = da.sel({lat_name: LAT_FLORIPA, lon_name: lon_target}, method='nearest')

    # Ajustar unidades de temperatura (K -> °C) se necessário
    if ('tmed' in var_desejada or 'temp' in var_desejada or 'tmax' in var_desejada) and float(da_floripa.mean()) > 100:
        da_floripa = da_floripa - 273.15

    # 3. Converter para DataFrame
    df_temp = da_floripa.to_dataframe().reset_index()
    time_name = 'time' if 'time' in df_temp.columns else ('date' if 'date' in df_temp.columns else df_temp.columns[0])
    
    # Extração de ano e mês
    df_temp['dt'] = pd.to_datetime(df_temp[time_name])
    df_temp['ano'] = df_temp['dt'].dt.year
    df_temp['mes'] = df_temp['dt'].dt.month


    # Agregação por Ano (Média mensal do outono para prec e temp)
    if funcao_agregacao == 'max':
        serie_anual = df_temp.groupby('ano')[var_nc].max()
    else:
        # 'mean': Média mensal dos meses de outono
        serie_anual = df_temp.groupby('ano')[var_nc].mean()

    return serie_anual


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == '__main__':
    
    nc_merge = "/media/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_MONTHLY_ACUMULADO.nc"
    nc_samet = "/media/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMED_MEAN_ACUMULADO_SC.nc"
    
    csv_saida = "/home/meteoro/scripts/scripts_muri/earthsym/serie_historica_anual_merge_samet_floripa.csv"

    print("🔄 Processando dados do MERGE (Precipitação Média)...")
    # Agora usamos 'mean' em vez de 'sum'
    serie_prec = extrair_serie_temporal_floripa_outono(nc_merge, var_desejada='prec', funcao_agregacao='mean')

    print("🔄 Processando dados do SAMET (Temperatura Média)...")
    serie_tmed = extrair_serie_temporal_floripa_outono(nc_samet, var_desejada='tmed', funcao_agregacao='max')

    # Unir as duas séries temporais pelo Ano
    df_resultado = pd.DataFrame({
        'prec_merge': serie_prec,
        'temp_samet': serie_tmed
    }).reset_index()

    # Exportar CSV
    df_resultado.to_csv(csv_saida, index=False, float_format='%.5f')
    
    print(f"\n✅ Concluído com sucesso! Arquivo gerado em: {csv_saida}")
    print("\nPrévia das 10 primeiras linhas:")
    print(df_resultado.head(10))
