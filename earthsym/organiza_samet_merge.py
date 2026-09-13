# -*- coding: utf-8 -*-
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from pathlib import Path as SysPath

# ==========================================
# FUNÇÕES DE PROCESSAMENTO E CONVERSÃO
# ==========================================

def shapefile_para_path(gdf):
    '''
    Converte as geometrias de um GeoDataFrame (Polígonos/MultiPolígonos)
    em um objeto Path do Matplotlib para ser usado como clipe.
    '''
    paths = []
    geom_unida = gdf.unary_union
    
    geoms = [geom_unida] if geom_unida.geom_type == 'Polygon' else list(geom_unida.geoms)
    
    for geom in geoms:
        coords = np.asarray(geom.exterior.coords)
        codes = [Path.MOVETO] + [Path.LINETO] * (len(coords) - 2) + [Path.CLOSEPOLY]
        paths.append(Path(coords, codes))
        
        for interior in geom.interiors:
            coords_int = np.asarray(interior.coords)
            codes_int = [Path.MOVETO] + [Path.LINETO] * (len(coords_int) - 2) + [Path.CLOSEPOLY]
            paths.append(Path(coords_int, codes_int))

    return Path.make_compound_path(*paths)


def carregar_e_processar_grid_observacao(caminho_nc, variavel_desejada='prec'):
    '''
    Carrega o arquivo NetCDF do MERGE ou SAMET, faz a seleção espacial estendida
    para evitar bordas vazias e trata convenções de coordenadas/unidades.
    '''
    ds = xr.open_dataset(caminho_nc)

    var_nc = None
    for possivel_nome in [variavel_desejada, 'prec', 'precip', 'tmed', 'temp', 't2m', 'tmax']:
        if possivel_nome in ds.data_vars:
            var_nc = possivel_nome
            break
            
    if not var_nc:
        raise KeyError(f"Nenhuma variável correspondente a '{variavel_desejada}' foi encontrada no NetCDF.")

    lats = ds.lat.values
    lons = ds.lon.values
    
    if lons.max() > 180:
        ds_box = ds.sel(lat=slice(-29.8, -25.5), lon=slice(360 - 54.2, 360 - 48.0))
    else:
        lat_slice = slice(-29.8, -25.5) if lats[0] < lats[-1] else slice(-25.5, -29.8)
        ds_box = ds.sel(lat=lat_slice, lon=slice(-54.2, -48.0))

    df_grid = ds_box.to_dataframe().reset_index().dropna(subset=[var_nc])
    df_grid['lon'] = df_grid['lon'].apply(lambda x: x - 360 if x > 180 else x)

    if variavel_desejada in ['tmed', 'temp', 'tmax'] and df_grid[var_nc].mean() > 100:
        df_grid[var_nc] = df_grid[var_nc] - 273.15

    df_grid = df_grid.rename(columns={var_nc: variavel_desejada})
    
    return df_grid


def exportar_dados_csv(df_dados, gdf_sc, variavel='prec', caminho_csv_ponto=None, caminho_csv_medio=None):
    '''
    Filtra os pontos estritamente dentro de SC e exporta:
    1. A climatologia por ponto de grade (lat, lon, valor).
    2. A média espacial/climatológica única do estado (opcional).
    '''
    # Garantir que só exportamos pontos DENTRO do estado (Spatial Join)
    gdf_dados = gpd.GeoDataFrame(
        df_dados, 
        geometry=gpd.points_from_xy(df_dados['lon'], df_dados['lat']),
        crs="EPSG:4326"
    )
    
    gdf_sc_recortado = gpd.sjoin(gdf_dados, gdf_sc, predicate='within')

    # 1. temperaturas máximas por ponto (Lat, Lon)
    df_clima_ponto = gdf_sc_recortado.groupby(['lat', 'lon'])[variavel].max().reset_index()

    if caminho_csv_ponto:
        df_clima_ponto.to_csv(caminho_csv_ponto, index=False, float_format='%.4f')
        print(f"📄 Dados por ponto salvos em: {caminho_csv_ponto}")

    # 2. Média climatológica espacial de todo o estado
    if caminho_csv_medio:
        media_estadual = df_clima_ponto[variavel].mean()
        df_medio = pd.DataFrame([{ 'estado': 'SC', f'media_{variavel}': media_estadual }])
        df_medio.to_csv(caminho_csv_medio, index=False, float_format='%.4f')
        print(f"📄 Média estadual salva em: {caminho_csv_medio}")

    return df_clima_ponto


def plotar_climatologia_sc_precisa(df_dados, gdf_sc, variavel='prec', titulo="Climatologic Average Temperature - SC", salvar_path=None):
    '''
    Plota o mapa com contourf recortado de forma precisa pelo limite do Shapefile de SC.
    '''
    df_clima = df_dados.groupby(['lat', 'lon'])[variavel].max().reset_index()
    grid_pivot = df_clima.pivot(index='lat', columns='lon', values=variavel)
    
    lons = grid_pivot.columns.values
    lats = grid_pivot.index.values
    Z = grid_pivot.values
    X, Y = np.meshgrid(lons, lats)

    is_temp = variavel in ['tmed', 'temp', 'tmax']
    cmap = 'YlOrRd' if is_temp else 'Blues'
    label_colorbar = ' Average Temperature (°C)' if is_temp else 'Precipitation (mm/month)'

    fig, ax = plt.subplots(figsize=(10, 8))

    contour = ax.contourf(X, Y, Z, levels=30, cmap=cmap, zorder=1)

    sc_path = shapefile_para_path(gdf_sc)
    patch = PathPatch(sc_path, transform=ax.transData, facecolor='none', edgecolor='none')
    ax.add_patch(patch)

    for collection in contour.collections:
        collection.set_clip_path(patch)

    gdf_sc.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.2, zorder=3)

    minx, miny, maxx, maxy = gdf_sc.total_bounds
    ax.set_xlim(minx - 0.1, maxx + 0.1)
    ax.set_ylim(miny - 0.1, maxy + 0.1)

    cbar = plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.07, shrink=0.7)
    cbar.set_label(label_colorbar, fontsize=11, fontweight='bold')

    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Longitude (°)", fontsize=10)
    ax.set_ylabel("Latitude (°)", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.3, color='gray', zorder=2)

    plt.tight_layout()
    if salvar_path:
        plt.savefig(salvar_path, dpi=300, bbox_inches='tight')
        print(f"🖼️ Mapa salvo em: {salvar_path}")
    
    plt.show()


# ==========================================
# EXECUÇÃO DO FLUXO PRINCIPAL
# ==========================================
if __name__ == '__main__':

    # Configuração de arquivos de entrada e saída
    variavel_estudo = 'tmed'
    caminho_nc = "/media/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_MONTHLY_TMED_MEAN_ACUMULADO_SC.nc"
    caminho_shp = "/home/meteoro/scripts/scripts_python/BR_UF_2019.shp"
    
    # Caminhos para exportar as figuras e tabelas CSV
    saida_png = "/home/meteoro/scripts/scripts_muri/earthsym/climathology_temp_med_sc.png"
    csv_pontos = "/home/meteoro/scripts/scripts_muri/earthsym/climathologia_temp_med_max_pontos_sc.csv"
    csv_medio = "/home/meteoro/scripts/scripts_muri/earthsym/climathologia_temp_med_max_sc.csv"

    # 1. Carregar e filtrar dados do grid
    print(f"🔄 Processando arquivo: {caminho_nc}")
    df_grid = carregar_e_processar_grid_observacao(caminho_nc, variavel_desejada=variavel_estudo)

    # 2. Carregar Shapefile
    gdf_brasil = gpd.read_file(caminho_shp)
    gdf_sc = gdf_brasil[gdf_brasil['SIGLA_UF'] == 'SC']

    if gdf_sc.crs is None:
        gdf_sc = gdf_sc.set_crs(epsg=4326)
    else:
        gdf_sc = gdf_sc.to_crs(epsg=4326)

    # 3. EXPORTAR OS DADOS PARA CSV
    df_clima_sc = exportar_dados_csv(
        df_dados=df_grid, 
        gdf_sc=gdf_sc, 
        variavel=variavel_estudo, 
        caminho_csv_ponto=csv_pontos,
        caminho_csv_medio=csv_medio
    )

    # 4. Gerar o gráfico espacial com corte preciso
    plotar_climatologia_sc_precisa(
        df_dados=df_grid, 
        gdf_sc=gdf_sc, 
        variavel=variavel_estudo, 
        titulo="Average Temperature - Santa Catarina (SAMeT)",
        salvar_path=saida_png
    )
