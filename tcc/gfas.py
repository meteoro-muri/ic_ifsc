import xarray as xr
import cf_xarray as cfxr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas as pd
import sys
from shapely.geometry import Point
from shapely.geometry import box
from datetime import datetime
import rasterio
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def converter_dataset_longitude(ds):
    """
    Converte as longitudes do dataset de 0-360 para -180 a 180
    """
    # Verificar se longitude está no formato 0-360
    if ds.longitude.max() > 180:
        # Criar nova coordenada de longitude convertida
        lon_convertida = ds.longitude.values.copy()
        lon_convertida[lon_convertida > 180] = lon_convertida[lon_convertida > 180] - 360
        
        # Ordenar por longitude (importante para o HYSPLIT)
        idx_sort = np.argsort(lon_convertida)
        
        # Reordenar o dataset
        ds_convertido = ds.isel(longitude=idx_sort)
        ds_convertido = ds_convertido.assign_coords(longitude=lon_convertida[idx_sort])
        
        #print(f"Longitude convertida: {ds_convertido.longitude.min():.1f}° a {ds_convertido.longitude.max():.1f}°")
        
        return ds_convertido
    else:
        print("Dataset já está no formato -180 a 180")
        return ds


def calculo_area(ds):
    # Parâmetros do GFAS
    res_lat = 0.1  # graus (1800 pontos de -90 a 90)
    res_lon = 0.1  # graus (3600 pontos de 0 a 360)
    R = 6371000  # Raio da Terra em metros

    # Converter resolução para radianos
    dlat_rad = np.radians(res_lat)
    dlon_rad = np.radians(res_lon)

    # Extrair latitudes
    latitudes = ds.latitude.values

    # Calcular área para cada latitude (área varia com o coseno da latitude)
    lat_rad = np.radians(latitudes)
    area_por_latitude_m2 = R**2 * dlat_rad * dlon_rad * np.cos(lat_rad)

    # Criar array 2D com áreas para cada célula (1800 x 3600)
    nlon = len(ds.longitude)
    area_grid_2d = np.tile(area_por_latitude_m2[:, np.newaxis], (1, nlon))

    # Criar DataArray com as áreas (para facilitar cálculos futuros)
    areas = xr.DataArray(
        area_grid_2d,
        dims=['latitude', 'longitude'],
        coords={'latitude': latitudes, 'longitude': ds.longitude.values},
        attrs={
            'units': 'm^2',
            'long_name': 'Grid cell area',
            'description': f'GFAS grid cell area at {res_lat}° resolution'
        }
    )

    return areas

def emission_rate(ds):
    fire_vars = [var for var in ds.data_vars if var.endswith('fire')]
    emission_rate = xr.Dataset()
    for var in fire_vars:
        rate_hourly = ds[var] * ds['cell_area'] * 3600
        rate_hourly.attrs.update({
            'units': 'kg h**-1',
            'long_name': f'Emission rate of {var}',
            'description': f'GFAS {var} emission rate in kg per hour'})
        ds[f"{var}_rate"] = rate_hourly
    return ds 


def plot(var):
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    var.plot(ax=ax, transform=ccrs.PlateCarree(),cmap = "Reds")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.OCEAN, alpha=0.3)
    ax.add_feature(cfeature.LAND, alpha=0.1)
    plt.title(var.name)
    plt.show()
    return 0

def encontrar_maximo(var):
    """
    Encontra o valor máximo e suas coordenadas - Versão robusta
    """
    # Converter para numpy array
    data = var.values
    
    # Encontrar o valor máximo
    max_val = np.max(data)
    
    # Encontrar a posição do máximo
    # Usar np.where para encontrar todas as ocorrências
    posicoes = np.where(data == max_val)
    
    if len(posicoes[0]) == 0:
        print("Nenhum máximo encontrado!")
        return None
    
    # Pegar a primeira ocorrência
    indices = [p[0] for p in posicoes]
    
    print(f"\n=== MÁXIMO DE {var.name} ===")
    print(f"Shape do array: {data.shape}")
    print(f"Dimensões: {var.dims}")
    print(f"Valor máximo: {max_val:.4f} {var.attrs.get('units', '')}")
    
    # Construir resultado baseado nas dimensões
    resultado = {'valor': float(max_val), 'unidades': var.attrs.get('units', '')}
    
    for i, dim in enumerate(var.dims):
        if i < len(indices):
            idx = indices[i]
            
            if dim == 'latitude':
                lat = var.latitude.values[idx]
                resultado['latitude'] = float(lat)
                print(f"Latitude: {lat:.4f}°")
                
            elif dim == 'longitude':
                lon = var.longitude.values[idx]
                resultado['longitude'] = float(lon)
                print(f"Longitude: {lon:.4f}°")
                
            elif dim == 'time':
                tempo = var.time.values[idx]
                resultado['tempo'] = tempo
                print(f"Tempo: {pd.to_datetime(tempo)}")
            
            else:
                if dim in var.coords:
                    valor_coord = var[dim].values[idx]
                    resultado[dim] = valor_coord
                    print(f"{dim}: {valor_coord}")
                else:
                    resultado[f'{dim}_idx'] = idx
                    print(f"Índice {dim}: {idx}")
    
    return resultado
    
    
def criar_emitimes(ds, poluente='bcfire_rate', n_fontes=10, altura_inicial=500, 
                   duracao_horas=24, area_base=None, arquivo_saida='EMITIMES'):
    """
    Cria arquivo EMITIMES com as N fontes de maior taxa de emissão
    
    Parâmetros:
    -----------
    ds : xarray.Dataset
        Dataset com as variáveis de taxa de emissão (já processadas)
    poluente : str
        Nome da variável de taxa de emissão (ex: 'bcfire_rate', 'pm2p5fire_rate')
    n_fontes : int
        Número de fontes a serem selecionadas (top N)
    altura_inicial : float
        Altura inicial da fonte em metros (será usada se 'injh' não estiver disponível)
    duracao_horas : int
        Duração da emissão em horas
    area_base : xarray.DataArray ou None
        Área da célula para converter fluxo para taxa total (se None, usa ds['cell_area'])
    arquivo_saida : str
        Nome do arquivo EMITIMES a ser gerado
    
    Retorna:
    --------
    pandas.DataFrame : DataFrame com as fontes selecionadas
    """
    
    print(f"\n{'='*60}")
    print(f"📋 CRIANDO EMITIMES PARA {poluente}")
    print(f"{'='*60}")
    
    # Verificar se a variável existe
    if poluente not in ds.data_vars:
        print(f"ERRO: Variável {poluente} não encontrada no dataset!")
        print(f"Variáveis disponíveis: {list(ds.data_vars.keys())}")
        return None
    
    # Obter os dados de taxa de emissão
    taxa = ds[poluente].copy()
    
    # Verificar se tem tempo
    if 'time' in taxa.dims:
        # Se tiver múltiplos tempos, processar apenas o primeiro
        print(f"📅 Processando primeiro tempo: {pd.to_datetime(taxa.time.values[0])}")
        data_inicio = pd.to_datetime(taxa.time.values[0])
        taxa = taxa.isel(time=0)
    else:
        # Usar data atual se não tiver time
        data_inicio = pd.Timestamp.now().floor('D')
        print(f"AVISO: Usando data atual: {data_inicio}")
    
    # Obter área da célula
    if area_base is None:
        if 'cell_area' in ds.data_vars:
            area = ds['cell_area']
        else:
            print("AVISO: cell_area não encontrada! Usando área de 100 km²")
            # Criar área aproximada (100 km² para resolução de 0.1°)
            lon_size = 111000 * 0.1 * np.cos(np.radians(taxa.latitude.values))
            lat_size = 111000 * 0.1
            area = xr.DataArray(
                np.ones((len(taxa.latitude), len(taxa.longitude))) * lon_size * lat_size,
                dims=['latitude', 'longitude'],
                coords={'latitude': taxa.latitude.values, 'longitude': taxa.longitude.values}
            )
            print(f"Área aproximada: {area.values[0,0]:.2f} m²")
    else:
        area = area_base
    
    # Filtrar apenas valores positivos (ignorar zeros e NaN)
    mask = (taxa > 0) & (~np.isnan(taxa))
    taxa_filtrado = taxa.where(mask, drop=False)
    
    # Verificar se há dados positivos
    if taxa_filtrado.max() <= 0:
        print("ERRO: Nenhum valor positivo encontrado!")
        return None
    
    # Criar lista de pontos com seus valores
    latitudes = taxa.latitude.values
    longitudes = taxa.longitude.values
    
    print(f"🔍 Buscando top {n_fontes} fontes entre {len(latitudes)}x{len(longitudes)} pixels...")
    
    # Encontrar os N maiores valores
    values_flat = taxa_filtrado.values.flatten()
    
    # Ordenar índices por valor (decrescente)
    idx_sorted = np.argsort(values_flat)[::-1]
    
    # Filtrar apenas valores > 0
    idx_sorted = idx_sorted[values_flat[idx_sorted] > 0]
    
    # Pegar os N maiores (ou todos se tiver menos)
    n_selecionados = min(n_fontes, len(idx_sorted))
    
    print(f"✅ Encontrados {len(values_flat[values_flat > 0])} pixels com emissão > 0")
    print(f"✅ Selecionando os {n_selecionados} maiores...")
    print()
    
    # Construir lista de fontes
    fontes = []
    
    for i in range(n_selecionados):
        idx = idx_sorted[i]
        # Converter índice linear para 2D
        lat_idx = idx // len(longitudes)
        lon_idx = idx % len(longitudes)
        
        lat = latitudes[lat_idx]
        lon = longitudes[lon_idx]
        valor_taxa = values_flat[idx]
        
        # Calcular taxa total (kg/h) a partir do fluxo (kg m⁻² s⁻¹) * área (m²) * 3600
        if 'rate' not in poluente:
            area_pixel = area.isel(latitude=lat_idx, longitude=lon_idx).values
            taxa_total = valor_taxa * area_pixel * 3600
        else:
            taxa_total = valor_taxa
        
        # Obter altura de injeção (se disponível)
        altura = altura_inicial
        if 'injh' in ds.data_vars:
            try:
                altura = ds['injh'].isel(latitude=lat_idx, longitude=lon_idx).values
                if np.isnan(altura) or altura <= 0:
                    altura = altura_inicial
            except:
                altura = altura_inicial
        
        # Calcular heat release (FRP * área)
        heat_release = 0
        if 'frpfire' in ds.data_vars:
            try:
                frp = ds['frpfire'].isel(latitude=lat_idx, longitude=lon_idx).values
                if not np.isnan(frp) and frp > 0:
                    area_pixel = area.isel(latitude=lat_idx, longitude=lon_idx).values
                    heat_release = frp * area_pixel
            except:
                heat_release = 0
        
        fonte = {
            'indice': i + 1,
            'latitude': lat,
            'longitude': lon,
            'taxa_fluxo': float(valor_taxa),
            'taxa_total_kg_h': float(taxa_total),
            'altura_m': float(altura),
            'heat_release_W': float(heat_release)
        }
        fontes.append(fonte)
    
    # Criar DataFrame com as fontes
    df_fontes = pd.DataFrame(fontes)
    
    # ================================================
    # 📋 GERAR TABELA PARA PREENCHER A GUI
    # ================================================
    
    print(f"{'='*60}")
    print(f"📋 INFORMAÇÕES PARA PREENCHER A GUI DO HYSPLIT")
    print(f"{'='*60}")
    print()
    
    # Extrair data e hora do data_inicio
    ano = data_inicio.year
    mes = data_inicio.month
    dia = data_inicio.day
    hora = data_inicio.hour
    minuto = data_inicio.minute
    
    # Duração em formato HHMM (4 dígitos)
    duracao_str = f"{duracao_horas:02d}{minuto:02d}"
    
    print("📌 CONFIGURAÇÕES GERAIS:")
    print(f"   Release start time (YYYY MM DD HH mm): {ano:04d} {mes:02d} {dia:02d} {hora:02d} {minuto:02d}")
    print(f"   Release duration (HHMM): {duracao_str}")
    print(f"   Número de fontes: {n_selecionados}")
    print()
    
    print("📌 LISTA DE FONTES (para preencher na GUI):")
    print("="*100)
    print(f"{'Fonte':<6} {'Latitude':<10} {'Longitude':<12} {'Altura(m)':<10} {'Taxa(kg/h)':<12} {'Área(m²)':<10} {'Heat(W)':<12}")
    print("-"*100)
    
    for i, fonte in enumerate(fontes, 1):
        print(f"{i:<6} {fonte['latitude']:<10.4f} {fonte['longitude']:<12.4f} {fonte['altura_m']:<10.1f} {fonte['taxa_total_kg_h']:<12.2f} 1.0{'':<8} {fonte['heat_release_W']:<12.0f}")
    
    print("="*100)
    print()
    
    # ================================================
    # 📝 GERAR ARQUIVO EMITIMES
    # ================================================
    
    print(f"📝 Gerando arquivo {arquivo_saida}...")
    
    # Escrever arquivo EMITIMES
    with open(arquivo_saida, 'w') as f:
        # Escrever cabeçalho do ciclo
        # Formato: YYYY MM DD HH DURACAO(hhhh) N_RECORDS
        f.write(f"{ano:04d} {mes:02d} {dia:02d} {hora:02d} {duracao_str} {n_selecionados}\n")
        
        # Para cada fonte, escrever um registro de emissão
        for fonte in fontes:
            lat = fonte['latitude']
            lon = fonte['longitude']
            altura = fonte['altura_m']
            taxa = fonte['taxa_total_kg_h']
            area_emit = 1.0  # Área padrão para fonte pontual
            heat = fonte['heat_release_W']
            
            # Formato: YYYY MM DD HH MM DURATION LAT LON HGT RATE AREA HEAT
            duracao_fonte = f"{duracao_horas:02d}{minuto:02d}"
            f.write(f"{ano:04d} {mes:02d} {dia:02d} {hora:02d} {minuto:02d} {duracao_fonte} {lat:.4f} {lon:.4f} {altura:.1f} {taxa:.2f} {area_emit:.1f} {heat:.0f}\n")
    
    print(f"✅ Arquivo {arquivo_saida} criado com sucesso!")
    print(f"✅ Total de {len(fontes)} fontes escritas")
    print(f"✅ Coordenadas no formato -180 a 180 (longitude)")
    print()
    
    # ================================================
    # 📋 RESUMO PARA PREENCHIMENTO MANUAL
    # ================================================
    
    print(f"{'='*60}")
    print(f"📋 RESUMO PARA PREENCHER A GUI DO HYSPLIT")
    print(f"{'='*60}")
    print()
    print("1. Vá em 'Advanced / File Edit / Emissions File'")
    print(f"2. Número de fontes: {n_selecionados}")
    print("3. Clique em 'Configure Locations'")
    print("4. Preencha cada fonte com:")
    print()
    print("   Para cada fonte (Location 1, 2, ...):")
    print(f"   - Release start time: {ano:04d} {mes:02d} {dia:02d} {hora:02d} {minuto:02d}")
    print(f"   - Release duration (hhmm): {duracao_str}")
    print("   - Release location (Lat Lon Hgt-agl): [ver tabela abaixo]")
    print("   - Emission rate (mass/hour): [ver tabela abaixo]")
    print("   - Emission area (sq meters): 1.0")
    print("   - Heat release for plume rise (watts): [ver tabela abaixo]")
    print()
    print("5. Clique em 'Save to File' para salvar como 'EMITIMES'")
    print("6. Vá em 'Advanced / Concentration Setup / Configuration'")
    print("7. Opção 6: 'Define EMISSION CYCLING or input file'")
    print("8. Selecione 'Default Name' para usar 'EMITIMES'")
    print()
    print("9. No 'Concentration Setup', defina:")
    print(f"   - Release Rate: 0.0")
    print(f"   - Emission Duration: 0")
    print()
    print(f"{'='*60}")
    
    # Criar arquivo de configuração para o HYSPLIT
    criar_arquivo_controle(df_fontes, data_inicio, duracao_horas, poluente)
    
    # ================================================
    # 📊 SALVAR TABELA EM CSV
    # ================================================
    
    csv_saida = arquivo_saida.replace('EMITIMES', 'fontes')
    df_fontes.to_csv(f"{csv_saida}.csv", index=False)
    print(f"✅ Tabela de fontes salva em: {csv_saida}.csv")
    print()
    
    return df_fontes


def criar_arquivo_controle(df_fontes, data_inicio, duracao_horas, poluente):
    """
    Cria arquivo CONTROL básico para usar com o EMITIMES
    """
    
    print(f"{'='*60}")
    print(f"📋 CRIANDO ARQUIVO CONTROL")
    print(f"{'='*60}")
    
    # Mapear poluente para número de espécie do HYSPLIT
    especie_map = {
        'bcfire_rate': 'BC',
        'pm2p5fire_rate': 'PM25',
        'tpmfire_rate': 'TPM',
        'cofire_rate': 'CO',
        'co2fire_rate': 'CO2'
    }
    
    especie = especie_map.get(poluente, 'XX')
    n_fontes = len(df_fontes)
    
    with open('CONTROL', 'w') as f:
        # Linha 1: Número de fontes
        f.write(f"{n_fontes:3d}\n")
        
        # Linhas 2 até (n_fontes+1): Localização das fontes
        for i, fonte in df_fontes.iterrows():
            lat = fonte['latitude']
            lon = fonte['longitude']
            # Mantém longitude no formato -180 a 180
            f.write(f"{lat:.2f} {lon:.2f} 0.0\n")
        
        # Próximas linhas do CONTROL (formato fixo)
        f.write("0.0\n")          # Altura de partida (não usada)
        f.write("10000\n")        # Número de partículas
        f.write(f"{duracao_horas:3d}\n")  # Duração total
        f.write("0.0 0.0 0.0\n")  # Posição da fonte (não usada)
        f.write(f"{especie}\n")   # Nome do poluente
        f.write("0.0\n")          # Taxa de emissão (0 - usando EMITIMES)
        
        # Data de início
        data_str = data_inicio.strftime('%Y%m%d%H')
        f.write(f"{data_str}\n")
        
        f.write("0\n")            # Duração da emissão (0 - usando EMITIMES)
        f.write("0.0 0.0 0.0\n")  # Posição inicial (não usada)
        f.write("1\n")            # Nível vertical
        f.write("0.0 0.0 1.0 1.0\n")  # Grid (será sobrescrito pela GUI)
        f.write("1 1 1\n")        # Dimensões do grid (será sobrescrito)
        f.write("0.0 100.0 500.0 1000.0 5000.0\n")  # Níveis de altura
        f.write("./\n")           # Diretório de saída
        f.write("cdump\n")        # Nome do arquivo de saída
        f.write("1\n")
        f.write("1 1 1 1 1 1 1 1 1 1 1 1 1 1\n")
        f.write("0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        f.write("0.0 0.0 0.0 0.0 0.0\n")
        f.write("0 0 0 0 0\n")
        for _ in range(15):
            f.write("0\n")
    
    print("✅ Arquivo CONTROL criado com sucesso!")
    print(f"✅ Coordenadas no formato -180 a 180 (longitude)")
    print(f"✅ ATENÇÃO: Configure o arquivo SETUP.CFG com 'efile = EMITIMES'")
    print(f"✅ ATENÇÃO: O arquivo CONTROL é básico. Ajuste na GUI conforme necessário.")
    print()


# Exemplo de uso
if __name__ == "__main__":
    # Seu código existente
    data = datetime(2024, 9, 9) 
    
    ds = xr.open_dataset('/dados4/pesquisa/meteoromuri/gfas_hysplit_novo.grib', engine='cfgrib')
    
    ds["cell_area"] = calculo_area(ds)
    ds = ds.sel(time=data, latitude=slice(20, -40), longitude=slice(279, 325))
    ds = converter_dataset_longitude(ds)
    ds = emission_rate(ds)
    
    # Criar EMITIMES para Black Carbon com as 10 maiores fontes
    df_fontes_bc = criar_emitimes(
        ds, 
        poluente='bcfire_rate', 
        n_fontes=10,
        altura_inicial=500,
        duracao_horas=24,
        arquivo_saida='EMITIMES_BC_20240909'
    )

def criar_arquivo_controle(df_fontes, data_inicio, duracao_horas, poluente):
    """
    Cria arquivo CONTROL básico para usar com o EMITIMES
    """
    
    print("\n=== CRIANDO ARQUIVO CONTROL ===")
    
    # Mapear poluente para número de espécie do HYSPLIT
    especie_map = {
        'bcfire_rate': 'BC',
        'pm2p5fire_rate': 'PM25',
        'tpmfire_rate': 'TPM',
        'cofire_rate': 'CO',
        'co2fire_rate': 'CO2'
    }
    
    especie = especie_map.get(poluente, 'XX')
    n_fontes = len(df_fontes)
    
    with open('CONTROL', 'w') as f:
        # Linha 1: Número de fontes
        f.write(f"{n_fontes:3d}\n")
        
        # Linhas 2 até (n_fontes+1): Localização das fontes
        for i, fonte in df_fontes.iterrows():
            lat = fonte['latitude']
            lon = fonte['longitude']
            # 🔧 MODIFICAÇÃO: Mantém longitude no formato -180 a 180
            # (NÃO converte para 0-360)
            # Altura 0 porque será usada do EMITIMES
            f.write(f"{lat:.2f} {lon:.2f} 0.0\n")
        
        # Próximas linhas do CONTROL (formato fixo)
        f.write("0.0\n")          # Altura de partida (não usada)
        f.write("10000\n")        # Número de partículas
        f.write(f"{duracao_horas:3d}\n")  # Duração total
        f.write("0.0 0.0 0.0\n")  # Posição da fonte (não usada)
        f.write(f"{especie}\n")   # Nome do poluente
        f.write("0.0\n")          # Taxa de emissão (0 - usando EMITIMES)
        
        # Data de início
        data_str = data_inicio.strftime('%Y%m%d%H')
        f.write(f"{data_str}\n")
        
        f.write("0\n")            # Duração da emissão (0 - usando EMITIMES)
        f.write("0.0 0.0 0.0\n")  # Posição inicial (não usada)
        f.write("1\n")            # Nível vertical
        f.write("0.0 0.0 1.0 1.0\n")  # Grid (será sobrescrito pela GUI)
        f.write("1 1 1\n")        # Dimensões do grid (será sobrescrito)
        f.write("0.0 100.0 500.0 1000.0 5000.0\n")  # Níveis de altura
        f.write("./\n")           # Diretório de saída
        f.write("cdump\n")        # Nome do arquivo de saída
        f.write("1\n")
        f.write("1 1 1 1 1 1 1 1 1 1 1 1 1 1\n")
        f.write("0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        f.write("0.0 0.0 0.0 0.0 0.0\n")
        f.write("0 0 0 0 0\n")
        for _ in range(15):
            f.write("0\n")
    
    print("Arquivo CONTROL criado com sucesso!")
    print(f"Coordenadas no formato -180 a 180 (longitude)")
    print(f"ATENÇÃO: Configure o arquivo SETUP.CFG com 'efile = {arquivo_saida}'")
    print(f"ATENÇÃO: O arquivo CONTROL é básico. Ajuste na GUI conforme necessário.")


# Exemplo de uso
if __name__ == "__main__":
    # Seu código existente
    data = datetime(2024, 9, 9) 
    
    ds = xr.open_dataset('/dados4/pesquisa/meteoromuri/gfas_hysplit_novo.grib', engine='cfgrib')
    
    ds["cell_area"] = calculo_area(ds)
    ds = ds.sel(time=data, latitude=slice(20, -40), longitude=slice(279, 325))
    ds = converter_dataset_longitude(ds)  # 🔧 Isso converte para -180 a 180
    ds = emission_rate(ds)
    
    # Criar EMITIMES para Black Carbon com as 10 maiores fontes
    df_fontes_bc = criar_emitimes(
        ds, 
        poluente='bcfire_rate', 
        n_fontes=10,
        altura_inicial=500,
        duracao_horas=24,
        arquivo_saida='EMITIMES_BC_20240909'
    )
    
    print("\n=== VERIFICAÇÃO DAS COORDENADAS ===")
    print(df_fontes_bc[['latitude', 'longitude', 'taxa_total_kg_h']].head(10))
