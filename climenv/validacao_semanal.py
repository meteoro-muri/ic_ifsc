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
import metpy.calc as mpcalc
from metpy.units import units
from matplotlib.dates import DateFormatter, DayLocator

data_i = datetime(2026,7,15,00,00,00) ##Alterar a data de interesse aqui apenas##

data_a = data_i - timedelta(days=7)
data_f = data_i + timedelta(days=7)

#print(data_a)

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
path_save = Path('/home/sifapsc/scripts/climenv/img/')



def gfs(municipio):
    linhas_temp15 = []
    for arquivo in path_gfs.rglob(f'tmp2m_gfs_hor_{municipio}_f24_*.txt'):
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
    df3['timestamp'] = pd.to_datetime(df3['data'] + ' ' + df3['hora'])
    df3.set_index('timestamp', inplace = True)
    df3.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df3.rename(columns = {'valor' : 'tempGFS_07d'}, inplace = True)
    #print(f"tmp2m_hor_{municipio}_{data_a.strftime('%Y%m%d%H')}_15d.txt")
    #sys.exit()
    
    
    linhas_prec15 = []
    for arquivo in path_dados.rglob(f'prec_gfs_hor_{municipio}_f24_*.txt'):
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
    df4['timestamp'] = pd.to_datetime(df4['data'] + ' ' + df4['hora'])
    df4.set_index('timestamp', inplace = True)
    df4.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df4.rename(columns = {'valor' : 'precGFS_07d'}, inplace = True)
    #print(df4)
    
    linhas_temp7 = []
    for arquivo in path_dados.rglob(f'tmp2m_gfs_hor_{municipio}_f120_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    linhas_temp7.append(linha)
    # Lê os dados
    df5 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_temp7)),
    sep=r'\s+',  # separador é espaços em branco
    names=colunas,
    header=None)
    
    # Converte data para datetime
    df5['timestamp'] = pd.to_datetime(df5['data'] + ' ' + df5['hora'])
    df5.set_index('timestamp', inplace = True)
    df5.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df5.rename(columns = {'valor' : 'tempGFS_15d'}, inplace = True)
    df5.sort_index(inplace = True)
    #print(df5)
    
    linhas_prec7 = []
    for arquivo in path_dados.rglob(f'prec_gfs_hor_{municipio}_f120_*.txt'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                # Pula linhas que começam com cdo, # ou estão vazias
                if not (linha.startswith('cdo') or 
                       linha.startswith('#') or 
                       linha.strip() == ''):
                    linhas_prec7.append(linha)
    # Lê os dados
    df6 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_prec7)),
    sep=r'\s+',  # separador é espaços em branco
    names=colunas,
    header=None)
    
    # Converte data para datetime
    df6['timestamp'] = pd.to_datetime(df6['data'] + ' ' + df6['hora'])
    df6.set_index('timestamp', inplace = True)
    df6.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df6.rename(columns = {'valor' : 'precGFS_15d'}, inplace = True)
    df6.sort_index(inplace = True)
    #print(df6)
    
    
    df3 = pd.merge(df3, df4, left_index=True, right_index=True, how='outer')
    
    df5 = pd.merge(df5, df6, left_index=True, right_index=True, how='outer')
    
    df = df3.join(df5, how = 'outer')
    #print(df)
    return df
 

def merge(merge):
    linhas_prec = []
    with open(merge, 'r', encoding='utf-8') as f:
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
    df2['timestamp'] = pd.to_datetime(df2['data'] + ' ' + df2['hora'])
    df2.set_index('timestamp', inplace = True)
    df2.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df2.rename(columns = {'valor' : 'precMERGE'}, inplace = True)
    #print(df2)
    return(df2)

    
def samet(samet):
    linhas_temp = []
    with open(samet, 'r', encoding='utf-8') as f:
        for linha in f:
            # Pula linhas que começam com cdo, # ou estão vazias
            if not (linha.startswith('cdo') or 
                   linha.startswith('#') or 
                   linha.strip() == ''):
                linhas_temp.append(linha)
    
    # Lê os dados
    df2 = pd.read_csv(pd.io.common.StringIO(''.join(linhas_temp)), 
                     sep=r'\s+',  # separador é espaços em branco
                     names=colunas,
                     header=None)

    # Converte data para datetime
    df2['timestamp'] = pd.to_datetime(df2['data'] + ' ' + df2['hora'])
    df2.set_index('timestamp', inplace = True)
    df2.drop(columns = ['data', 'hora', 'latitude', 'longitude'], inplace = True)
    df2.rename(columns = {'valor' : 'tempSAMET'}, inplace = True)
    return(df2)
    
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
    return(df)

def plot_com_datas_reais(df, municipio, nome_sistema):
    # Garantir que o índice é datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Ordenar índice
    df = df.sort_index()
    
    # Filtrar apenas o período definido
    df = df[(df.index >= data_i) & (df.index <= data_f)]
    
        # Filtrar apenas o período definido
    df = df[(df.index >= data_i) & (df.index <= data_f)]
    
    # Pegar timestamps únicos
    timestamps_unicos = df.index.unique()
    
    
    
    #print(df2.index)
    #sys.exit()
    # ============================================
    # CONFIGURAÇÃO DOS SUBPLOTS (3 gráficos no total)
    # ============================================
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Configuração das colunas de precipitação
    config_precip = {
        'Precipitação_ifsc': {
            'cor': '#e41a1c', 
            'marcador': 'o', 
            'tamanho_marcador': 5,
            'label' : 'IFSC'
        },
        'precMERGE': {
            'cor': '#377eb8', 
            'marcador': '*',
            'tamanho_marcador': 4,
            'label' : 'MERGE'
        },
        'Precipitacao(mm)_epagri': {
            'cor': '#4daf4a',
            'marcador': '+',
            'tamanho_marcador': 5,
            'label': 'Epagri'
        },
        'precGFS_07d': {
            'cor': '#984ea3',
            'marcador': 'D',
            'tamanho_marcador': 4,
            'label': 'GFS f24'
        },
        'precGFS_15d': {
            'cor': '#ff7f00',
            'marcador': 'v',
            'tamanho_marcador': 4,
            'label' : 'GFS f120'
        }
    }
    
    # Colunas que existem no dataframe
    cols_precip_exist = [col for col in config_precip.keys() if col in df.columns]
    
    # Conjunto para controlar labels já adicionadas
    labels_adicionadas = set()
    
    # ============================================
    # GRÁFICO 1: Precipitação
    # ============================================
    if cols_precip_exist:
     df_precip = df[cols_precip_exist].copy()
     df_precip = df_precip.apply(pd.to_numeric, errors='coerce')
     df_precip = df[df>0]
     #max_val = df_precip.max().max()
    
     for col in cols_precip_exist:
         serie = df_precip[col]
         
         estilo = config_precip.get(col, {
             'cor': '#333333', 
             'marcador': 'o', 
             'tamanho_marcador': 4,
             'label': 'IFSC'  # usa o nome da coluna como label padrão
         })
        
         ax1.plot(serie.index, serie.values,
                 marker=estilo['marcador'],
                 markersize=estilo['tamanho_marcador'],
                 label=estilo['label'],
                 color=estilo['cor'],
                 linestyle='',  # sem linha, só marcadores
                 alpha=0.7)
								
					
    # Configurar eixo x para primeira metade
    x_posicoes = range(len(df.index))
    

    ax1.xaxis.set_major_locator(DayLocator())
    ax1.xaxis.set_major_formatter(DateFormatter('%d'))
    ax1.set_ylabel('Precipitação (mm/hora)', fontsize=12)
    ax1.legend(loc='best', fontsize=10, ncol=2)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Calcular ylim baseado nos dados
    
    #ax1.set_ylim(top=max_val + 1)
        
        
    
    # ============================================
    # GRÁFICO 2: Temperatura (dados completos)
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
            'label': 'GFS f24'
        },
        'tempGFS_15d': {
            'cor': '#ff7f00',
            'marcador': 'v',
            'linha': ':',
            'espessura': 1.5,
            'tamanho_marcador': 4,
            'label': 'GFS f120'
        }
    }
    
    if cols_temp_exist:
        for col in cols_temp_exist:
            if col in df.columns:
                temp_series = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(temp_series) > 0:
                    estilo = estilo_completo_temp.get(col, {
                        'cor': '#333333', 'marcador': 'o', 'linha': '-', 
                        'espessura': 1.5, 'tamanho_marcador': 4
                    })
                    ax2.plot(temp_series.index, temp_series.values,
                            marker=estilo['marcador'],
                            linestyle=estilo['linha'],
                            linewidth=estilo['espessura'],
                            markersize=estilo['tamanho_marcador'],
                            label=estilo['label'],
                            color=estilo['cor'],
                            alpha=0.7)
    
    #ax3.set_title(f'Temperatura Horária (Dados Completos) - {municipio}', fontsize=8)
    ax2.set_ylabel('Temperatura (°C)', fontsize=12)
    ax2.legend(loc='best', fontsize=10, ncol=2)
    ax2.grid(True, alpha=0.3, axis='both')
    
    # ============================================
    # Ajustes comuns
    # ============================================
    
    ax1.xaxis.set_major_formatter(DateFormatter('%d/%m'))
    ax2.xaxis.set_major_formatter(DateFormatter('%d/%m'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0, ha='right')
    ax1.grid(True, alpha=0.6, axis='x', linestyle=':')
    ax2.grid(True, alpha=0.6, axis='x', linestyle=':')
    
    ax1.set_title(f"{municipio} - Semana {data_i.strftime('%Y-%m-%d')}")
    plt.tight_layout()
    plt.savefig(f"{path_save}/semanal_{nome_sistema}_{data_i.strftime('%Y%m%d')}.png")
    plt.show()
    
def estatisticas(df,j):
	semana = df.loc[data_i : data_f]
	i = data_i
	k = 0
	while i != data_f:
		try:
			if i == semana.index[k]:
				print("DIA ANALISADO: ", i, "\n")
				print("DATA ANALISADA NA SERIE TEMPORAL:", semana.index[k], "\n")
				dia = semana.loc[i : i + timedelta(hours=23)]
				print(f"VALORES MÁXIMOS PARA {j} no dia {i.strftime('%Y-%m-%d')}\n",dia.max(), "\n\n")
				print(f"VALORES MÍNIMOS PARA {j} no dia {i.strftime('%Y-%m-%d')}\n",dia.min(), "\n\n")
				dir_vento = dia["Vento - Direção_ifsc"].mode()[0]
				print(f"DIREÇÃO PREDOMINANTE DO VENTO NO DIA {i.strftime('%Y-%m-%d')}", dir_vento, "°")
				dir_vento = mpcalc.angle_to_direction(dir_vento)
				print(f"DIREÇÃO PREDOMINANTE DO VENTO NO DIA {i.strftime('%Y-%m-%d')}", dir_vento)
				print("*"*80)
		except IndexError:
			print(f"DADOS AUSENTE PARA {j} NO DIA {i.strftime('%Y-%m-%d')} \n","*"*80, "\n")
			pass
		i += timedelta(days=1)
		k += 24
	#sys.exit()

# Carregar dados

for i,j in municipios:
	print(f"EXECUTANDO PARA {j}")
	municipio_ifsc = estacao(f"{path_dados}/{i}_ifsc.csv")
	###
	estatisticas(municipio_ifsc,j)
	
	###
	municipio_samet = samet(f"{path_dados}/samet_merge/samet_tmp2m_hor_{i}_{data_i.strftime('%Y%m%d%H')}_7.txt")
	municipio_merge = merge(f"{path_dados}/samet_merge/merge_prec_hor_{i}_{data_i.strftime('%Y%m%d%H')}_7.txt") 
	municipio_gfs = gfs(f'{i}')
	
	municipio = municipio_ifsc.join(municipio_samet, how='outer')
	municipio = municipio.join(municipio_merge, how='outer')
	municipio = municipio.join(municipio_gfs, how='outer')
	
	
	municipio.index = pd.to_datetime(municipio.index)
	municipio = municipio.sort_index()
	
	#print(municipio)
	#sys.exit()
	
	plot_com_datas_reais(municipio, f"{j}",f'{i}')
	
	print("="*100)
	
