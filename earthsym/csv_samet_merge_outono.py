# -*- coding: utf-8 -*-
import xarray as xr
import pandas as pd
import numpy as np

# Coordenadas centrais de Florianópolis
LAT_FLORIPA = -27.59
LON_FLORIPA = -48.54

def extrair_serie_temporal_floripa_outono(caminho_nc, var_desejada, funcao_agregacao):
    '''
    Extrai a série temporal da estação de Outono (MAM: Março, Abril, Maio)
    do ponto mais próximo de Florianópolis/SC.
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

    # 3. Extrair ano e mês diretamente pelo Xarray (evita erros com cftime/datetime)
    da_floripa['ano'] = da_floripa.time.dt.year
    da_floripa['mes'] = da_floripa.time.dt.month

    # 4. Converter para DataFrame
    df_temp = da_floripa.to_dataframe().reset_index()

    # 5. Filtrar apenas os meses do Outono (Março = 3, Abril = 4, Maio = 5)
    df_outono = df_temp[df_temp['mes'].isin([3, 4, 5])]

    # 6. Agregação por Ano
    if funcao_agregacao == 'max':
        serie_anual = df_outono.groupby('ano')[var_nc].max()
    else:
        # 'mean': Média dos meses de outono
        serie_anual = df_outono.groupby('ano')[var_nc].mean()

    return serie_anual


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == '__main__':
    
    nc_merge = "/media/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_MONTHLY_ACUMULADO.nc"
    nc_samet = "/media/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMED_MEAN_ACUMULADO_SC.nc"
    
    csv_saida = "/home/meteoro/scripts/scripts_muri/earthsym/serie_historica_outono_merge_samet_floripa.csv"

    print("🔄 Processando dados do MERGE (Precipitação Média do Outono)...")
    serie_prec = extrair_serie_temporal_floripa_outono(nc_merge, var_desejada='prec', funcao_agregacao='mean')

    print("🔄 Processando dados do SAMET (Temperatura Máxima do Outono)...")
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
