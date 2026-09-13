# -*- coding: utf-8 -*-
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd
import xarray as xr

# ==========================================
# FUNÇÕES DE PROCESSAMENTO E CONVERSÃO
# ==========================================


def shapefile_para_path(gdf):
    """Converte as geometrias de um GeoDataFrame (Polígonos/MultiPolígonos)

    em um objeto Path do Matplotlib para ser usado como clipe.
    """
    paths = []
    geom_unida = gdf.unary_union

    geoms = (
        [geom_unida]
        if geom_unida.geom_type == "Polygon"
        else list(geom_unida.geoms)
    )

    for geom in geoms:
        coords = np.asarray(geom.exterior.coords)
        codes = (
            [Path.MOVETO]
            + [Path.LINETO] * (len(coords) - 2)
            + [Path.CLOSEPOLY]
        )
        paths.append(Path(coords, codes))

        for interior in geom.interiors:
            coords_int = np.asarray(interior.coords)
            codes_int = (
                [Path.MOVETO]
                + [Path.LINETO] * (len(coords_int) - 2)
                + [Path.CLOSEPOLY]
            )
            paths.append(Path(coords_int, codes_int))

    return Path.make_compound_path(*paths)


def carregar_e_processar_precipitacao_outono(
    caminho_nc, meses_outono=[3, 4, 5]
):
    """Carrega o NetCDF do MERGE, filtra os meses do outono (MAM),

    realiza o recorte espacial e padroniza as coordenadas.
    """
    ds = xr.open_dataset(caminho_nc)

    # Identifica a variável de precipitação no MERGE
    var_nc = None
    for possivel in ["prec", "precip", "p", "pr"]:
        if possivel in ds.data_vars:
            var_nc = possivel
            break

    if not var_nc:
        raise KeyError(
            f"Variável de precipitação não encontrada. Variáveis no NetCDF: {list(ds.data_vars)}"
        )

    # =========================================================
    # 🍁 FILTRO DO OUTONO (Março=3, Abril=4, Maio=5)
    # =========================================================
    if "time" in ds.coords or "time" in ds.dims:
        ds = ds.sel(time=ds["time"].dt.month.isin(meses_outono))
    else:
        print(
            "⚠️ Alerta: Coordenada 'time' não encontrada. Verifique o arquivo."
        )

    lats = ds.lat.values
    lons = ds.lon.values

    # Recorte Espacial ao redor de SC
    if lons.max() > 180:
        ds_box = ds.sel(
            lat=slice(-29.8, -25.5), lon=slice(360 - 54.2, 360 - 48.0)
        )
    else:
        lat_slice = (
            slice(-29.8, -25.5) if lats[0] < lats[-1] else slice(-25.5, -29.8)
        )
        ds_box = ds.sel(lat=lat_slice, lon=slice(-54.2, -48.0))

    df_grid = (
        ds_box[[var_nc]].to_dataframe().reset_index().dropna(subset=[var_nc])
    )
    df_grid["lon"] = df_grid["lon"].apply(lambda x: x - 360 if x > 180 else x)
    df_grid = df_grid.rename(columns={var_nc: "precipitacao"})

    return df_grid


def exportar_dados_csv(
    df_dados, caminho_csv_ponto=None, caminho_csv_medio=None, gdf_sc=None
):
    """Filtra os pontos dentro de SC e exporta a média do outono."""
    gdf_dados = gpd.GeoDataFrame(
        df_dados,
        geometry=gpd.points_from_xy(df_dados["lon"], df_dados["lat"]),
        crs="EPSG:4326",
    )

    gdf_sc_recortado = gpd.sjoin(gdf_dados, gdf_sc, predicate="within")

    # Climatologia média por ponto (Lat, Lon) considerando apenas o Outono
    df_clima_ponto = (
        gdf_sc_recortado.groupby(["lat", "lon"])["precipitacao"]
        .mean()
        .reset_index()
    )

    if caminho_csv_ponto:
        df_clima_ponto.to_csv(
            caminho_csv_ponto, index=False, float_format="%.2f"
        )
        print(f"📄 Dados do outono por ponto salvos em: {caminho_csv_ponto}")

    if caminho_csv_medio:
        media_estadual = df_clima_ponto["precipitacao"].mean()
        df_medio = pd.DataFrame(
            [{"estado": "SC", "media_precipitacao_outono_mm": media_estadual}]
        )
        df_medio.to_csv(caminho_csv_medio, index=False, float_format="%.2f")
        print(f"📄 Média estadual do outono salva em: {caminho_csv_medio}")

    return df_clima_ponto


def plotar_mapa_precipitacao_outono(
    df_dados,
    gdf_sc,
    titulo="Precipitação Média Mensal de Outono - SC",
    salvar_path=None,
):
    """Plota o mapa com contourf recortado de forma precisa para a precipitação."""
    df_clima = (
        df_dados.groupby(["lat", "lon"])["precipitacao"].mean().reset_index()
    )
    grid_pivot = df_clima.pivot(index="lat", columns="lon", values="precipitacao")

    lons = grid_pivot.columns.values
    lats = grid_pivot.index.values
    Z = grid_pivot.values
    X, Y = np.meshgrid(lons, lats)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Paleta de cores apropriada para chuva (Blues ou YlGnBu)
    contour = ax.contourf(X, Y, Z, levels=30, cmap="Blues", zorder=1)

    # Máscara recortando pelo contorno exato do Shapefile
    sc_path = shapefile_para_path(gdf_sc)
    patch = PathPatch(
        sc_path, transform=ax.transData, facecolor="none", edgecolor="none"
    )
    ax.add_patch(patch)

    for collection in contour.collections:
        collection.set_clip_path(patch)

    # Contorno do Estado de Santa Catarina
    gdf_sc.plot(
        ax=ax, facecolor="none", edgecolor="black", linewidth=1.2, zorder=3
    )

    minx, miny, maxx, maxy = gdf_sc.total_bounds
    ax.set_xlim(minx - 0.1, maxx + 0.1)
    ax.set_ylim(miny - 0.1, maxy + 0.1)

    # Barra de cores
    cbar = plt.colorbar(
        contour, ax=ax, orientation="horizontal", pad=0.07, shrink=0.7
    )
    cbar.set_label(
        "Precipitação Média Mensal (mm/mês)", fontsize=11, fontweight="bold"
    )

    ax.set_title(titulo, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Longitude (°)", fontsize=10)
    ax.set_ylabel("Latitude (°)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.3, color="gray", zorder=2)

    plt.tight_layout()
    if salvar_path:
        plt.savefig(salvar_path, dpi=300, bbox_inches="tight")
        print(f"🖼️ Mapa salvo em: {salvar_path}")

    plt.show()


# ==========================================
# EXECUÇÃO DO FLUXO PRINCIPAL
# ==========================================
if __name__ == "__main__":

    # Arquivos de entrada
    caminho_nc = "/media/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_MONTHLY_ACUMULADO.nc"
    caminho_shp = "/home/meteoro/scripts/scripts_python/BR_UF_2019.shp"

    # Arquivos de saída
    saida_png = "/home/meteoro/scripts/scripts_muri/earthsym/climatologia_outono_precipitacao_sc.png"
    csv_pontos = "/home/meteoro/scripts/scripts_muri/earthsym/climatologia_outono_precipitacao_pontos_sc.csv"
    csv_medio = "/home/meteoro/scripts/scripts_muri/earthsym/climatologia_outono_precipitacao_sc.csv"

    # 1. Carregar MERGE e filtrar apenas o Outono (MAM)
    print(f"🔄 Processando arquivo de chuva (MERGE) para o Outono: {caminho_nc}")
    df_grid = carregar_e_processar_precipitacao_outono(
        caminho_nc, meses_outono=[3, 4, 5]
    )

    # 2. Carregar Shapefile
    gdf_brasil = gpd.read_file(caminho_shp)
    gdf_sc = gdf_brasil[gdf_brasil["SIGLA_UF"] == "SC"]

    if gdf_sc.crs is None:
        gdf_sc = gdf_sc.set_crs(epsg=4326)
    else:
        gdf_sc = gdf_sc.to_crs(epsg=4326)

    # 3. Exportar CSVs
    df_clima_sc = exportar_dados_csv(
        df_dados=df_grid,
        caminho_csv_ponto=csv_pontos,
        caminho_csv_medio=csv_medio,
        gdf_sc=gdf_sc,
    )

    # 4. Gerar o mapa recortado
    plotar_mapa_precipitacao_outono(
        df_dados=df_grid,
        gdf_sc=gdf_sc,
        titulo="Autumn (MAM) Average Monthly Precipitation - Santa Catarina (MERGE)",
        salvar_path=saida_png,
    )
