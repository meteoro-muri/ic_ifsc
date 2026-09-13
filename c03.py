###################################################################################################
# Script que monitora a relação de PRECIPTAÇÃO nas Cidades de Joinville, Blumenau e Florianópolis #
# (Projeto Dengue)                                                                                #
#                                                                                                 #
# Autor: Júlia Barreto da Silva                                                                   #
#                                                                                                 #
# LaCAC/Multlab/IFSC - Florianópolis  --- Data: 3 de abril de 2025                                # #                                                                                                 #
###################################################################################################

## Importando Bibliotecas ##

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import matplotlib.dates as mdates
import xarray as xr
import matplotlib.pyplot as plt

## Abrindo Arquivos ##

import pandas as pd
import matplotlib.pyplot as plt

'''
# Carregar o arquivo
df = pd.read_csv('prec_obs_2.csv')

df.columns = df.columns.str.strip()  # Remove espaços extras
df['time'] = pd.to_datetime(df['time'])  # Agora deve funcionar

print(df.columns)

sys.exit()
'''

#lendo arquivo nc merge
#ds = xr.open_dataset('../../climatologias/dados_clim_prec/jul2025/MERGE_CPTEC_MONTHLY_ACUMULADO_SB_2025.nc')

ds = xr.open_dataset('~/DADOS/dados/operacao/merge/CDO.MERGE/MERGE_CPTEC_DAILY_SB_2025.nc')

# Coordenadas aproximadas de Fortaleza dos Valos
#lat_ponto = -28.79
#lon_ponto = -53.22

# Selecionar o ponto mais próximo
#prec_ponto = ds['prec'].sel(lat=lat_ponto, lon=lon_ponto, method='nearest')

lat_bounds = slice(-29, -28)  # Adjust according to the specific area
lon_bounds = slice(-53.75, -52.5) #região de fortaleza dos valos

# Seleciona todos os pontos dentro do retângulo em torno do ponto
mask = ds['time'].dt.month >= 5
recorte = ds['prec'].sel(lat = lat_bounds, lon = lon_bounds).sel(time=mask)

media_area = recorte.mean(dim=['lat', 'lon'])

serie_prec = media_area.to_series()


#serie_prec_mensal = serie_prec.resample('M').sum()
#serie_prec_mensal.index = serie_prec_mensal.index.to_period('M').to_timestamp()
serie_prec_diaria = serie_prec.resample('D').sum()
serie_prec_diaria.index = serie_prec.index.to_period('D').to_timestamp()

import matplotlib.dates as mdates

dates_num = mdates.date2num(serie_prec_diaria.index)

#print(serie_prec_mensal.max)
#sys.exit()
plt.figure(figsize=(15,6))
plt.bar(serie_prec.index, serie_prec.values, color='royalblue', alpha=1.0)#, #width=20)
plt.title('Precipitação diária acumulada - Fortaleza dos Valos (MERGE)')
plt.ylabel('Precipitação (mm)')
plt.xlabel('Data')
plt.grid(True, axis='y')  # Apenas grade horizontal, se quiser

# Alinhar os ticks exatamente nos meses
#ax = plt.gca()
#ax.xaxis.set_major_locator(mdates.MonthLocator())
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#================================================================================
#================================================================================

# Plot mensal

# Seleciona todos os pontos dentro do retângulo em torno do ponto
recorte = ds['prec'].sel(lat = lat_bounds, lon = lon_bounds)

media_area = recorte.mean(dim=['lat', 'lon'])

serie_prec = media_area.to_series()


serie_prec_mensal = serie_prec.resample('M').sum()
serie_prec_mensal.index = serie_prec_mensal.index.to_period('M').to_timestamp()
#serie_prec_diaria = serie_prec.resample('D').sum()
#serie_prec_diaria.index = serie_prec.index.to_period('D').to_timestamp()

import matplotlib.dates as mdates

dates_num = mdates.date2num(serie_prec_mensal.index)

#print(serie_prec_mensal.max)
#sys.exit()
plt.figure(figsize=(15,6))
plt.bar(serie_prec_mensal.index, serie_prec_mensal.values, color='royalblue', alpha=1.0, width=20)
plt.title('Precipitação mensal acumulada - Fortaleza dos Valos (MERGE)')
plt.ylabel('Precipitação (mm)')
plt.xlabel('Data')
plt.grid(True, axis='y')  # Apenas grade horizontal, se quiser

# Alinhar os ticks exatamente nos meses
#ax = plt.gca()
#ax.xaxis.set_major_locator(mdates.MonthLocator())
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print(serie_prec_mensal)
#================================================================================
#================================================================================


#Temperatura obs

# Ajuste o caminho conforme o seu arquivo
tmax = xr.open_dataset('~/DADOS/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_DAILY_SB_TMAX_2025.nc')
tmed = xr.open_dataset('~/DADOS/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_DAILY_SB_TMED_2025.nc')
tmin = xr.open_dataset('~/DADOS/dados/operacao/samet/CDO.SAMET/SAMeT_CPTEC_DAILY_SB_TMIN_2025.nc')

# Seleciona todos os pontos dentro do retângulo em torno do ponto
#mask_tmax = tmax['time'].dt.month >= 5
#mask_tmin = tmin['time'].dt.month >= 5
#mask_tmed = tmed['time'].dt.month >= 5
recorte_tmax = tmax['tmax'].sel(lat = lat_bounds, lon = lon_bounds)#.sel(time=mask_tmax)
recorte_tmed = tmed['tmed'].sel(lat = lat_bounds, lon = lon_bounds)#.sel(time=mask_tmed)
recorte_tmin = tmin['tmin'].sel(lat = lat_bounds, lon = lon_bounds)#.sel(time=mask_tmin)

media_area_tmax = recorte_tmax.mean(dim=['lat', 'lon'])
media_area_tmed = recorte_tmed.mean(dim=['lat', 'lon'])
media_area_tmin = recorte_tmin.mean(dim=['lat', 'lon'])

serie_temp_tmax = media_area_tmax.to_series()
serie_temp_tmed = media_area_tmed.to_series()
serie_temp_tmin = media_area_tmin.to_series()

serie_temp_tmax_mj = serie_temp_tmax[serie_temp_tmax.index.month.isin([5, 6, 7])]
serie_temp_tmed_mj = serie_temp_tmed[serie_temp_tmed.index.month.isin([5, 6, 7])]
serie_temp_tmin_mj = serie_temp_tmin[serie_temp_tmin.index.month.isin([5, 6, 7])]

plt.figure(figsize=(15,6))

plt.plot(serie_temp_tmed_mj.index, serie_temp_tmed_mj.values, label='Temperatura Média', color='orange')
plt.plot(serie_temp_tmax_mj.index, serie_temp_tmax_mj.rolling(1).max(), label='Temperatura Máxima', color='red', linestyle='--')
plt.plot(serie_temp_tmin_mj.index, serie_temp_tmin_mj.rolling(1).min(), label='Temperatura Mínima', color='blue', linestyle='--')

plt.title('Temperatura Máxima, Mínima e Média - Fortaleza dos Valos (SAMET)')
plt.ylabel('Temperatura (°C)')
plt.xlabel('Data')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

sys.exit()
#================================================================================
#================================================================================

# O SCRIPT VAI PARAR AQU, SÓ PRECISA ISSO

#================================================================================
#================================================================================

# Calcula a média entre as colunas de precipitação ignorando os NaNs
df['media_prec'] = df[['prec1', 'prec2', 'prec3', 'prec4']].mean(axis=1, skipna=True)



# Plot com barras separadas por série
plt.figure(figsize=(14, 6))
for i, col in enumerate(df.columns[1:]):
    plt.bar(df['time'] + pd.Timedelta(days=i), df[col], width=2, label=col)

plt.xlabel('Data')
plt.ylabel('Precipitação (mm)')
plt.title('Precipitação ao longo do tempo')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()


# Plot: precipitações individuais + média
plt.figure(figsize=(14, 6))

# Plot das barras individuais
for i, col in enumerate(['prec1', 'prec2', 'prec3', 'prec4']):
    plt.bar(df['time'] + pd.Timedelta(days=i), df[col], width=1.5, label=col, alpha=0.6)

# Linha com a média
plt.plot(df['time'], df['media_prec'], color='Blue', linewidth=2, label='Média', marker='o')

# Configurações
plt.xlabel('Data')
plt.ylabel('Precipitação (mm)')
plt.title('Precipitação diária e média entre estações')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()


sys.exit()

#url = "https://raw.githubusercontent.com/matheusf30/dados_dengue/refs/heads/main/prec_se.csv" #raw
url = "prec_obs_2.csv"

prec = pd.read_csv(url)

print(prec.head())
# Diferença na apresentação gráfica

###Analise das Variáveis###

print(prec.info())             #Exibe informações gerais sobre o DataFrame, como o número de entradas, colunas, e tipos de dados.
print("="*50)                   
print(prec.dtypes)             #Exibe os tipos de dados de cada coluna.
print("="*50)
print(prec.describe())         #Exibe estatísticas descritivas das colunas numéricas, como média, desvio padrão, valor mínimo e máximo, etc.


prec["time"] = pd.to_datetime(prec["time"])
print(prec.dtypes)

plt.figure(figsize=(10, 6))

# Usando as cores especificadas para cada cidade
time = np.arange(len(prec["time"]))
largura = 0.2

plt.bar(semanas - largura, prec["prec1"], label="Florianópolis", color="#1f77b4", width= 0.2, alpha = 0.8)  # Azul
plt.bar(semanas, prec["prec2"], label="Joinville", color="#ff7f0e", width= 0.2, alpha = 0.8)  # Laranja
plt.bar(semanas + largura, prec["prec3"], label="Blumenau", color="#2ca02c", width= 0.2, alpha = 0.8)  # Verde
plt.bar(semanas + largura, prec["prec4"], label="Blumenau", color="#2ca02c", width= 0.2, alpha = 0.8)  # Verde

# Título e rótulos
#plt.title(f"Análise de Precipitação em 2023")
plt.xlabel("Dias")
plt.ylabel("Precipitação acumulada (mm/dia)")

# Adicionando a legenda
plt.legend()

# Exibindo a grade
plt.grid(True)

# Altera o fundo do gráfico para a cor 'honeydew'
plt.gca().patch.set_facecolor("honeydew")  

# Exibe o gráfico
plt.show()









plt.figure(figsize=(10, 6))

# Usando as cores especificadas para cada cidade
semanas = np.arange(len(prec24["Semana"]))
largura = 0.2
plt.bar(semanas - largura, prec24["FLORIANÓPOLIS"], label="Florianópolis", color="#1f77b4", width= 0.2, alpha = 0.8)  # Azul
plt.bar(semanas, prec24["JOINVILLE"], label="Joinville", color="#ff7f0e", width= 0.2, alpha = 0.8)  # Laranja
plt.bar(semanas + largura, prec24["BLUMENAU"], label="Blumenau", color="#2ca02c", width= 0.2, alpha = 0.8)  # Verde

# Título e rótulos
#plt.title(f"Análise de Precipitação em 2024")
plt.xlabel("Semanas Epidemiológicas")
plt.ylabel("Precipitação acumulada (mm)")

# Adicionando a legenda
plt.legend()

# Exibindo a grade
plt.grid(True)

# Altera o fundo do gráfico para a cor 'honeydew'

plt.gca().patch.set_facecolor("honeydew")  

# Exibe o gráfico
plt.show()










