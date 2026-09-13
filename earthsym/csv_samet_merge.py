# -*- coding: utf-8 -*-
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
from matplotlib.path import Path

def extrair_serie_temporal_sc_xarray(caminho_nc, caminho_shp, var_desejada, funcao_agregacao='mean'):
    '''
    Processa NetCDF usando Xarray nativo e mascara espacial por polígono (SC)
    sem estourar a memória RAM.
    '''
    # 1. Carregar o NetCDF
    ds = xr.open_dataset(caminho_nc)

    # Identificar nome da variável
    var_nc = None
    for nome in [var_desejada, 'prec', 'precip', 'tmed', 'temp', 't2m']:
        if nome in ds.data_vars:
            var_nc = nome
            break
            
    if not var_nc:
        raise KeyError(f"Variável {var_desejada} não encontrada no arquivo {caminho_nc}")

    da = ds[var_nc]

    # Ajustar unidades de temperatura (K -> °C) se necessário
    if ('tmed' in var_desejada or 'temp' in var_desejada) and float(da.mean()) > 100:
        da = da - 273.15

    # Identificar nomes das coordenadas de Lat/Lon
    lat_name = 'lat' if 'lat' in da.coords else ('latitude' if 'latitude' in da.coords else None)
    lon_name = 'lon' if 'lon' in da.coords else ('longitude' if 'longitude' in da.coords else None)

    # Ajustar Longitude se estiver em formato 0-360
    if da[lon_name].max() > 180:
        da = da.assign_coords({lon_name: (((da[lon_name] + 180) % 360) - 180)})
        da = da.sortby(lon_name)

    # 2. Carregar o Shapefile de SC
    gdf_brasil = gpd.read_file(caminho_shp)
    gdf_sc = gdf_brasil[gdf_brasil['SIGLA_UF'] == 'SC']
    if gdf_sc.crs is None or gdf_sc.crs != "EPSG:4326":
        gdf_sc = gdf_sc.to_crs(epsg=4326)

    # 3. Recorte Bounding Box no Xarray (Reduz o volume de dados imediatamente)
    minx, miny, maxx, maxy = gdf_sc.total_bounds
    
    # Garantir que a seleção de latitude funcione independente da ordem (crescente/decrescente)
    lat_slice = slice(miny, maxy) if da[lat_name][0] < da[lat_name][-1] else slice(maxy, miny)
    da_crop = da.sel({lon_name: slice(minx, maxx), lat_name: lat_slice})

    # 4. Criar Máscara Espacial Nao-Retangular (Estreita o limite ao polígono exato de SC)
    lon_grid, lat_grid = np.meshgrid(da_crop[lon_name].values, da_crop[lat_name].values)
    points = np.vstack((lon_grid.flatten(), lat_grid.flatten())).T

    # Combinar geometrias caso haja ilhas/multipolígonos
    geom_sc = gdf_sc.geometry.unary_union
    
    mask = np.zeros(len(points), dtype=bool)
    if geom_sc.geom_type == 'Polygon':
        polys = [geom_sc]
    else:
        polys = list(geom_sc.geoms)

    for poly in polys:
        path = Path(np.array(poly.exterior.coords))
        mask |= path.contains_points(points)

    mask_2d = mask.reshape(lon_grid.shape)
    
    # Criar DataArray com a máscara
    xr_mask = xr.DataArray(mask_2d, coords={lat_name: da_crop[lat_name], lon_name: da_crop[lon_name]}, dims=[lat_name, lon_name])

    # 5. Aplicar Máscara e Calcular a Média Espacial para cada passo de tempo
    da_sc = da_crop.where(xr_mask)
    serie_temporal_espacial = da_sc.mean(dim=[lat_name, lon_name], skipna=True)

    # 6. Agregação Temporal por Ano no Pandas
    df_temp = serie_temporal_espacial.to_dataframe().reset_index()
    time_name = 'time' if 'time' in df_temp.columns else 'date'
    df_temp['ano'] = pd.to_datetime(df_temp[time_name]).dt.year

    if funcao_agregacao == 'sum':
        # Para Precipitação (MERGE): Soma acumulada do ano
        serie_anual = df_temp.groupby('ano')[var_nc].sum()
    else:
        # Para Temperatura (SAMET): Média anual
        serie_anual = df_temp.groupby('ano')[var_nc].mean()

    return serie_anual


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == '__main__':

    caminho_shp = "/home/meteoro/scripts/scripts_python/BR_UF_2019.shp"
    
    nc_merge = "/media/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_MONTHLY_ACUMULADO.nc"
    nc_samet = "/media/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMED_MEAN_ACUMULADO_SC.nc"
    
    csv_saida = "/home/meteoro/scripts/scripts_muri/earthsym/serie_historica_merge_samet_sc.csv"

    print("🔄 Processando dados do MERGE (Precipitação)...")
    serie_prec = extrair_serie_temporal_sc_xarray(nc_merge, caminho_shp, var_desejada='prec', funcao_agregacao='mean')

    print("🔄 Processando dados do SAMET (Temperatura Média)...")
    serie_tmed = extrair_serie_temporal_sc_xarray(nc_samet, caminho_shp, var_desejada='tmed', funcao_agregacao='mean')

    # Unir as duas séries temporais pelo Ano
    df_resultado = pd.DataFrame({
        'prec_merge': serie_prec,
        'temp_samet': serie_tmed
    }).reset_index()

    # Exportar CSV no formato padrão
    df_resultado.to_csv(csv_saida, index=True, float_format='%.5f')
    
    print(f"\n✅ Concluído com sucesso! Arquivo gerado em: {csv_saida}")
    print("\nPrévia das 10 primeiras linhas:")
    print(df_resultado.head(10))
