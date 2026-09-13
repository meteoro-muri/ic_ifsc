import pandas as pd
import numpy as np
import xarray as xr
import sys
import matplotlib.pyplot as plt
import subprocess
import geopandas as gpd
import seaborn as sns
from datetime import datetime, timedelta, date
from pathlib import Path
import glob
import calendar
from dateutil.relativedelta import relativedelta
from matplotlib.dates import DateFormatter, DayLocator

data_i = datetime(2026,5,24,00,00,00)
data_a = data_i - timedelta(days=7)
data_f = data_i + relativedelta(days = 14) #- timedelta(days=1)

fct1 = "f24"
fct2 = "f120"

mes = int(data_i.strftime('%m'))
#sys.exit()

municipios = [('chapeco',"Chapecó"), ('criciuma',"Criciúma"), ('florianopolis',"Florianópolis"), ('joinville',"Joinville")]


lat_chapeco = -27.06
lon_chapeco = -52.5
lat_criciuma = -28.6
lon_criciuma = -49.3
lat_florianopolis = -27.5
lon_florianopolis = -48.5
lat_joinville = -26.3
lon_joinville = -48.9


tempo_plot = pd.date_range(data_i, data_f, freq='h')
colunas = ['data', 'hora', 'longitude', 'latitude', 'valor']
path_dados  = Path('/home/sifapsc/scripts/climenv/dados/')
path_gfs = Path(f"/home/sifapsc/scripts/climenv/dados/gfs/")
path_samet_merge = Path(f"/home/sifapsc/scripts/climenv/dados/samet_merge")
path_save = Path('/home/sifapsc/scripts/climenv/img/')

def gfs(municipio):
    linhas_temp = []
    for arquivo in path_gfs.rglob(f'tmp2m_gfs_day_{municipio}_{fct1}_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    linhas_temp.append(linha)
    # Lê os dados
    df1 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_temp)),
    sep=r'\s+',  # separador é espaços em branco
    names=colunas,
    header=None)
    
    # Converte data para datetime
    df1['timestamp'] = pd.to_datetime(df1['data'])
    df1.set_index('timestamp', inplace = True)
    df1.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df1.rename(columns = {'valor' : 'tempGFS_07d'}, inplace = True)
    #print(df1)
    #sys.exit()
    
    linhas_prec = []
    for arquivo in path_gfs.rglob(f'prec_gfs_day_{municipio}_{fct1}_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    linhas_prec.append(linha)
    # Lê os dados
    df2 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_prec)), 
                     sep=r'\s+',  # separador é espaços em branco
                     names=colunas,
                     header=None)

    # Converte data para datetime
    df2['timestamp'] = pd.to_datetime(df2['data'])
    df2.set_index('timestamp', inplace = True)
    df2.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df2.rename(columns = {'valor' : 'precGFS_07d'}, inplace = True)

    df = pd.merge(df1, df2['precGFS_07d'], left_index=True, right_index=True, how='outer')
    #print(df)
    
    linhas_temp15 = []
    for arquivo in path_gfs.rglob(f'tmp2m_gfs_day_{municipio}_{fct2}_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    linhas_temp15.append(linha)
    # Lê os dados
    df3 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_temp15)),
    sep=r'\s+',  # separador é espaços em branco
    names=colunas,
    header=None)
    
    # Converte data para datetime
    df3['timestamp'] = pd.to_datetime(df3['data'])
    df3.set_index('timestamp', inplace = True)
    df3.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df3.rename(columns = {'valor' : 'tempGFS_15d'}, inplace = True)
    #print(df3)
    
    linhas_prec15 = []
    for arquivo in path_gfs.rglob(f'prec_gfs_day_{municipio}_{fct2}_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    linhas_prec15.append(linha)
    # Lê os dados
    df4 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_prec15)),
    sep=r'\s+',  # separador é espaços em branco
    names=colunas,
    header=None)
    
    
    # Converte data para datetime
    df4['timestamp'] = pd.to_datetime(df4['data'])
    df4.set_index('timestamp', inplace = True)
    df4.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df4.rename(columns = {'valor' : 'precGFS_15d'}, inplace = True)
    #print(df4)

    
    
    df = pd.merge(df1, df2, left_index=True, right_index=True, how='outer')
    df = pd.merge(df, df3, left_index=True, right_index=True, how='outer')
    df = pd.merge(df, df4, left_index=True, right_index=True, how='outer')
    #print(df2.index)
    #print(df4.index)
    #print(df)
    #sys.exit()
    return df
 

def merge(i):
    linhas_prec = []
    timestamps_vistos = set()  # Armazena combinação data+hora
    
    for arquivo in path_samet_merge.rglob(f'merge_prec_hor_{i}_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    
                    # Extrai data e hora da linha
                    partes = linha.strip().split()
                    if len(partes) >= 2:  # Verifica se tem pelo menos data e hora
                        data_hora = f"{partes[0]}_{partes[1]}"  # combina data e hora
                        
                        # Verifica se esta combinação data+hora já foi processada
                        if data_hora not in timestamps_vistos:
                            timestamps_vistos.add(data_hora)
                            linhas_prec.append(linha)
    
    # Lê os dados
    df2 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_prec)), 
                     sep=r'\s+',  # separador é espaços em branco
                     names=colunas,
                     header=None)
    
    # Converte data para datetime
    df2['timestamp'] = pd.to_datetime(df2['data'] + ' ' + df2['hora'])
    df2.set_index('timestamp', inplace=True)
    df2.drop(columns=['data', 'hora', 'latitude', 'longitude'], inplace=True)
    df2.rename(columns={'valor': 'precMERGE'}, inplace=True)
    df2 = df2.resample('D').sum()
    return df2

    
def samet(i):
    linhas_temp = []
    timestamps_vistos = set()  # Armazena combinação data+hora
    
    for arquivo in path_samet_merge.rglob(f'samet_tmp2m_hor_{i}_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    
                    partes = linha.strip().split()
                    if len(partes) >= 2:
                        data_hora = f"{partes[0]}_{partes[1]}"  # data_hora
                        
                        if data_hora not in timestamps_vistos:
                            timestamps_vistos.add(data_hora)
                            linhas_temp.append(linha)
    
    # Restante do código...
    df2 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_temp)), 
                     sep=r'\s+',
                     names=colunas,
                     header=None)

    df2['timestamp'] = pd.to_datetime(df2['data'] + ' ' + df2['hora'])
    df2.set_index('timestamp', inplace=True)
    df2.drop(columns=['data', 'hora', 'latitude', 'longitude'], inplace=True)
    df2.rename(columns={'valor': 'tempSAMET'}, inplace=True)
    df2 = df2.resample('D').mean()
    return df2
    
def estacao(arquivo):
    df = pd.read_csv(arquivo,
                   encoding="utf-8",
                   sep=",",
                   header=0,
                   index_col=False)
    df['Data'] = pd.to_datetime(df['Data'])
    # NÃO converter para string! Manter como Timestamp
    df = df.set_index('Data')
    df.index = df.index.tz_localize(None)
    df.index.name = 'time'
    df = df.add_suffix(f"_ifsc")
    df = df.iloc[::-1]  # Inverter ordem se necessário
    
    ##Isola apenas variável de interesse e converte pra dado diário##
    df = df [["Precipitação_ifsc","Temperatura_ifsc"]]
    prec = df["Precipitação_ifsc"].resample('D').sum()
    temp = df["Temperatura_ifsc"].resample('D').mean()
    df = pd.merge(prec,temp,left_index=True, right_index=True, how='outer')
    
    
    return(df)

def epagri(arquivo):
    df = pd.read_csv(arquivo,
                   encoding="latin1",
                   sep=",",
                   header=1,
                   index_col=False,
                   on_bad_lines='skip')
    df['Data Horario'] = pd.to_datetime(df['Data Horario'], 
                                        format='%d/%m/%Y %H:%M:%S',
                                        dayfirst=True)
    # NÃO converter para string! Manter como Timestamp
    
    df = df.set_index('Data Horario')
    df.index.name = 'time'
    df.index = df.index.tz_localize(None)
    df = df.add_suffix(f"_epagri")
    df = df.replace(9999.9, np.nan)
    
    ##Isola apenas variável de interesse e converte pra dado diário##
    df = df[["Precipitacao(mm)_epagri","TempArInst(C)_epagri"]] 
    prec = df["Precipitacao(mm)_epagri"] #.resample('D').sum()
    temp = df["TempArInst(C)_epagri"] #.resample('D').mean()
    df = pd.merge(prec,temp,left_index=True, right_index=True, how='outer')
    
    return(df)

def plot_com_datas_reais(df, municipio, nome_sistema):
    # Garantir que o índice é datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Ordenar índice
    df = df.sort_index()
    
    # Filtrar apenas Março 2026
    df = df[(df.index >= data_i) & (df.index <= data_f)]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    
    config_precip = {
        'Precipitação_ifsc': {
            'cor': '#e41a1c',
            'hatch': '',
            'hatch_color': 'white',
            'alpha': 0.7,
            'edgecolor': 'black',
            'linewidth': 0.5,
            'label': 'IFSC'
        },
        'precMERGE': {
            'cor': '#377eb8',
            'hatch': '',
            'hatch_color': 'white',
            'alpha': 0.7,
            'edgecolor': 'black',
            'linewidth': 0.5,
            'label': 'MERGE'
        },
        'Precipitacao(mm)_epagri': {
            'cor': '#4daf4a',
            'hatch': '',
            'hatch_color': 'white',
            'alpha': 0.7,
            'edgecolor': 'black',
            'linewidth': 0.5,
            'label': 'Epagri'
        },
        'precGFS_07d': {
            'cor': '#984ea3',
            'hatch': 'ooo',
            'hatch_color': 'white',
            'alpha': 0.7,
            'edgecolor': 'black',
            'linewidth': 0.5,
            'label': f'GFS {fct1}H'
        },
        'precGFS_15d': {
            'cor': '#ff7f00',
            'hatch': 'xxx',
            'hatch_color': 'white',
            'alpha': 0.7,
            'edgecolor': 'black',
            'linewidth': 0.5,
            'label': f'GFS {fct2}H'
        }
    }
    
    # ============================================
    # GRÁFICO 1: Precipitação (VERSÃO OTIMIZADA)
    # ============================================
    cols_precip_exist = [col for col in config_precip.keys() if col in df.columns]
    
    if cols_precip_exist:
        df_precip = df[cols_precip_exist].copy()
        df_precip = df_precip.apply(pd.to_numeric, errors='coerce')
        
        # Garantir que é diário (resample se necessário)
        #for col in cols_precip_exist:
        #    if col in ['Precipitacao(mm)_epagri', 'precMERGE', 'Precipitação_ifsc']:
        #        df_precip[col] = df_precip[col].resample('D').sum()
        #    else:  # GFS etc
        #        df_precip[col] = df_precip[col].resample('D').mean()
        
        n_barras = len(cols_precip_exist)
        largura_barra = 0.8 / n_barras  # 0.8 de largura total, dividida entre as barras
        labels_adicionadas = set()
        
        for j, col in enumerate(cols_precip_exist):
            # Filtra valores válidos e positivos
            serie = df_precip[col]
            mascara = (serie > 0) & pd.notna(serie)
            valores_positivos = serie[mascara]
            
            if len(valores_positivos) > 0:
                cfg = config_precip[col]
                offset = (j - (n_barras-1)/2) * largura_barra  # Centraliza as barras
                
                # Define label apenas na primeira ocorrência da coluna
                label = cfg['label'] if col not in labels_adicionadas else None
                
                # Plota TODAS as barras da coluna de uma vez
                ax1.bar(valores_positivos.index + pd.Timedelta(days=offset), 
                       valores_positivos.values,
                       width=largura_barra,
                       #alpha=cfg['alpha'],
                       color=cfg['cor'],
                       edgecolor=cfg['edgecolor'],
                       linewidth=cfg['linewidth'],
                       hatch=cfg['hatch'],
                       label=label,
                       zorder=3)
                
                labels_adicionadas.add(col)
        
        ax1.set_title(f"{municipio} - {calendar.month_name[mes]} {data_i.strftime('%Y')}", fontsize=12)
        ax1.set_ylabel('Precipitação (mm/dia)', fontsize=12)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3, axis='y')
    
    # ============================================
    # GRÁFICO 2: Temperatura
    # ============================================
    cols_temp = ['Temperatura_ifsc', 'tempSAMET', 'TempArInst(C)_epagri',
                 'tempGFS_07d', 'tempGFS_15d', 'tempGFS_geral']
    cols_temp_exist = [col for col in cols_temp if col in df.columns]
    
    estilo_completo_temp = {
        'Temperatura_ifsc': {
            'cor': '#e41a1c', 
            'marcador': 'o', 
            'linha': '-',
            'espessura': 2,
            'tamanho_marcador': 5,
            'label': 'IFSC'
        },
        'tempSAMET': {
            'cor': '#377eb8', 
            'marcador': 'o', 
            'linha': '-', 
            'espessura': 1.5,
            'tamanho_marcador': 4,
            'label': 'SAMeT'
        },
        'TempArInst(C)_epagri': {
            'cor': '#4daf4a',
            'marcador': 'o',
            'linha': '-',
            'espessura': 1.5,
            'tamanho_marcador': 5,
            'label': 'Epagri'
        },
        'tempGFS_07d': {
            'cor': '#984ea3',
            'marcador': 'D',
            'linha': ':',
            'espessura': 1.5,
            'tamanho_marcador': 4,
            'label': f'GFS {fct1}H'
        },
        'tempGFS_15d': {
            'cor': '#ff7f00',
            'marcador': 'v',
            'linha': ':',
            'espessura': 1.5,
            'tamanho_marcador': 4,
            'label': f'GFS {fct2}H'
        }
    }
    
    if cols_temp_exist:
        df_temp = df[cols_temp_exist].copy()
        df_temp = df_temp.apply(pd.to_numeric, errors='coerce')
        df_temp_daily = df_temp.resample('D').mean()
        
        for col in cols_temp_exist:
            if col in df_temp_daily.columns and df_temp_daily[col].notna().any():
                estilo = estilo_completo_temp.get(col, {
                    'cor': '#333333', 
                    'marcador': 'o', 
                    'linha': '-', 
                    'espessura': 1.5,
                    'tamanho_marcador': 4,
                    'label': col
                })
                ax2.plot(df_temp_daily.index, df_temp_daily[col], 
                        marker=estilo['marcador'],
                        linestyle=estilo['linha'],
                        linewidth=estilo['espessura'],
                        markersize=estilo['tamanho_marcador'],
                        label=estilo['label'],
                        color=estilo['cor'],
                        alpha=0.8)
    
    ax2.set_ylabel('Temperatura Média Diária (°C)', fontsize=10)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='both')
    
    # ============================================
    # Ajustes comuns
    # ============================================
    from matplotlib.dates import DateFormatter
    
    for ax in [ax1, ax2]:
        ax.set_xlim(data_i, data_f)
        ax.xaxis.set_major_locator(DayLocator())
        ax.xaxis.set_major_formatter(DateFormatter('%d'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax.grid(True, alpha=0, axis='x', linestyle=':')
    
    plt.subplots_adjust(hspace=4)
    plt.tight_layout(h_pad=2)
    plt.savefig(f"{path_save}/boletim_{nome_sistema}_{data_i.strftime('%Y%m%d')}.png")
    plt.show()


# Carregar dados

for i,j in municipios:
	
	municipio_ifsc = estacao(f"{path_dados}/{i}_ifsc.csv")
	municipio_samet = samet(f"{i}")
	#municipio_epagri = epagri(f"{path_dados}/{i}_epagri.csv")
	municipio_merge = merge(f"{i}") 
	municipio_gfs = gfs(f'{i}')
	
	municipio = municipio_ifsc #.join(municipio_epagri, how='outer' )
	municipio = municipio.join(municipio_samet, how='outer')
	municipio = municipio.join(municipio_merge, how='outer')
	municipio = municipio.join(municipio_gfs, how='outer')
	
	municipio.index = pd.to_datetime(municipio.index)
	municipio = municipio.sort_index()
	
	plot_com_datas_reais(municipio, f"{j}",f'{i}')
	
	print(f"{j} OK ","\n"*2)
