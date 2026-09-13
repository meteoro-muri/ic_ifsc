import pandas as pd
import numpy as np
import xarray as xr
import sys
import matplotlib.pyplot as plt
import subprocess
import geopandas as gpd
import seaborn as sns
from datetime import datetime, timedelta, date


ano = sys.argv[1]
mes = sys.argv[2]
dia = sys.argv[3]

data_inicial = date(int(ano), int(mes), int(dia))
data_final = data_inicial + timedelta(days=14)


#subprocess.run(f"scp  meteoro@172.16.0.110:/home/meteoro/DADOS/dados/operacao/gfs/0p25/{ano}{mes}/{ano}{mes}{dia}/gfs.t00z.pgrb2.0p25.{ano}{mes}{dia}00.f001_f120.nc . \n scp meteoro@172.16.0.110:/home/meteoro/DADOS/dados/operacao/gfs/0p25/{ano}{mes}/{ano}{mes}{dia}/gfs.t00z.pgrb2.0p25.{ano}{mes}{dia}00.f123_f384.nc .", shell=True)
#subprocess.run(f"scp  meteoro@172.16.0.110:/home/meteoro/DADOS/dados/operacao/gfs/0p25/{ano}{mes}/{ano}{mes}{dia}/gfs.t00z.pgrb2.0p25.{ano}{mes}{dia}00.f123_f384.nc .", shell=True)

gfs1 = xr.open_dataset(f'gfs.t00z.pgrb2.0p25.{ano}{mes}{dia}00.f001_f120.nc')
gfs2 = xr.open_dataset(f'gfs.t00z.pgrb2.0p25.{ano}{mes}{dia}00.f123_f384.nc')

gfs = xr.merge([gfs1, gfs2])
gfs['prate'] = gfs['prate'] * 3600
gfs['tmp2m'] = gfs['tmp2m'] - 273

gfs = gfs.sel(latitude=-27.06, longitude=-52.5, method='nearest')
df_gfs = gfs.to_dataframe()
df_gfs = df_gfs.loc[:, ['prate', 'tmp2m']]

print("###################DADOS GFS################### \n", df_gfs,"\n######################################\n")

#sys.exit()

print("\n\n\n\n###################################\n\n\n")

df_climenv = pd.read_csv("/home/sifapsc/scripts/meteoromuri/climenv/dados_multilab.csv",
                   encoding='utf-8',
                   sep=",",
                   header = 0,
                   index_col= False)
df_climenv['Data'] = pd.to_datetime(df_climenv['Data'])
df_climenv['Data'] = df_climenv['Data'].dt.tz_localize(None)
df_climenv = df_climenv.set_index('Data')
df_climenv.index.name = 'time'
print("###################DADOS CLIMENV################### \n", df_climenv,"\n######################################\n")

df_epagri = pd.read_csv("/home/sifapsc/scripts/meteoromuri/climenv/dados_epagri_chapeco.csv",
                   encoding='iso-8859-1',
                   sep=",",
                   header = 1,
                   index_col= False,
                   on_bad_lines='skip')

df_epagri['Data'] = pd.to_datetime(df_epagri['Data Horario'], dayfirst = True)
df_epagri['Data'] = df_epagri['Data'].dt.tz_localize(None)
df_epagri['Data'] = df_epagri['Data'].dt.strftime('%Y-%m-%d %H:%M:%S')
df_epagri = df_epagri.set_index('Data')
df_epagri.index.name = 'time'
print(f"{ano}-{mes}-{dia} 00:00:00")
print(df_epagri)
df_epagri.loc[df_epagri["Data Horario"] >= f"{dia}/{mes}/{ano} 00:00:00"]
print(df_epagri)
sys.exit()


print("###################DADOS epagri################### \n", df_epagri,"\n######################################\n")




print("\n\n\n\n###################################\n\n\n")

'''
df_inmet = pd.read_csv("/home/sifapsc/scripts/meteoromuri/climenv/dados_inmet.csv",
                   encoding='utf-8',
                   sep=",",
                   header = 0,
                   index_col= False)
df_inmet['Data'] = pd.to_datetime(df_inmet['Data'])
df_inmet['Data'] = df_inmet['Data'].dt.tz_localize(None)
df_inmet = df_inmet.set_index('Data')
df_inmet.index.name = 'time'
print("###################DADOS INMET################### \n", df_inmet,"\n######################################\n")
'''

print("\n\n\n\n###################################\n\n\n")


merge = xr.open_dataset('/home/sifapsc/scripts/meteoromuri/climenv/climenv_merge.nc')
merge = merge['prec'].sel(time=slice(f'{data_inicial} 03:00:00', f'{data_final} 12:00:00')).sel(lat=-27.06, lon=-52.5, method='nearest')
df_merge = merge.to_dataframe()
df_merge.drop(columns=['lat','lon'], inplace=True)
df_merge.columns = ['prec']
df_merge['prec'] = df_merge['prec'] * 100
pd.to_datetime(df_merge.index, utc=True)
print("###################DADOS MERGE################### \n", df_merge,"\n######################################\n")

print("\n\n\n\n###################################\n\n\n")

samet = xr.open_dataset('/home/sifapsc/scripts/meteoromuri/climenv/climenv_samet.nc')
samet = samet.sel(lat=-27.06, lon=-52.5, method='nearest').sel(time=slice(f'{data_inicial} 03:00:00', f'{data_final} 12:00:00'))
df_samet = samet.to_dataframe()
df_samet.drop(columns=['lat','lon','nobs'], inplace=True)
print(df_samet)
print("###################DADOS SAMET################### \n", df_samet,"\n######################################\n")

print("\n\n\n\n###################################\n\n\n")

df_climenv = df_climenv.add_suffix('_climenv')
df_merge = df_merge.add_suffix('_merge')
#df_inmet = df_inmet.add_suffix('_inmet')
df_gfs = df_gfs.add_suffix('_gfs')
df_samet = df_samet.add_suffix('_samet')
df_epagri = df_epagri.add_suffix('_epagri')

print("\n\n\n\n###################################\n\n\n")



chapeco = df_gfs
chapeco = chapeco.join(df_merge)
#chapeco = chapeco.join(df_inmet)
chapeco = chapeco.join(df_climenv)
chapeco = chapeco.join(df_samet)
chapeco = chapeco.join(df_epagri)

print(chapeco.columns)
chapeco.to_csv("chapeco.csv")
#sys.exit()
#sys.exit()
#floripa = gfs.sel(latitude=-23.3, longitude=-48.5, method='nearest')
#floripa = floripa.to_dataframe()


#print(chapeco['prate'])
#print(chapeco['tmp2m'])
#print(floripa['prate'])
#print(floripa['prate'])

'''
f, axs = plt.subplots(4, 2, sharey=True)
axs[0, 0].bar(chapeco.index, chapeco["Precipitação_climenv"])
axs[0, 0].set_title("Precipitação_climenv")
axs[1, 0].bar(chapeco.index, chapeco["prec_merge"])
axs[1, 0].set_title("Precipitação_merge")
#axs[2, 0].bar(chapeco.index, chapeco["Precipitação_inmet"])
#axs[2, 0].set_title("Precipitação_inmet")
axs[3, 0].bar(chapeco.index, chapeco["prate_gfs"])
axs[3, 0].set_title("Precipitação_gfs")

axs[0, 1].plot(chapeco.index, chapeco['Temperatura_climenv'], color = 'orange')
axs[0, 1].set_title("Temperatura_climenv")
axs[1, 1].plot(chapeco.index, chapeco['tt2m_samet'], color = 'orange')
axs[1, 1].set_title("Temperatura_samet")
axs[2, 1].plot(chapeco.index, chapeco['tmp2m_gfs'], color = 'orange')
axs[2, 1].set_title("Temperatura_gfs")
#axs[3, 1].plot(chapeco.index, chapeco['Temperatura_inmet'], color = 'orange')
#axs[3, 1].set_title("Temperatura_inmet")

plt.subplots_adjust(
    hspace=0.5)

plt.show()
'''
# Resetar o índice para ter uma coluna numérica
chapeco_plot = chapeco.reset_index().copy()
chapeco_plot['indice_numerico'] = range(len(chapeco_plot))

# Criar figura com 2 subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# Colunas
colunas_precip = ['Precipitação_climenv', 'prec_merge', 'prate_gfs', 'Precipitacao(mm)_epagri']
colunas_temp = ['Temperatura_climenv', 'tt2m_samet', 'tmp2m_gfs', 'TempArInst(C)_epagri']

# GRÁFICO 1: Precipitações
for col in colunas_precip:
    if col in chapeco_plot.columns:
        sns.barplot(data=chapeco_plot, 
                   x='indice_numerico', 
                   y=col, 
                   ax=ax1,
                   label=col,
                   alpha=0.7)

ax1.set_title('Comparação de Precipitações', fontsize=14, fontweight='bold')
ax1.set_ylabel('Precipitação (mm)', fontsize=12)
ax1.set_xlabel('')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# GRÁFICO 2: Temperaturas
for col in colunas_temp:
    if col in chapeco_plot.columns:
        sns.lineplot(data=chapeco_plot, 
                    x='indice_numerico', 
                    y=col, 
                    ax=ax2,
                    marker='o',
                    markersize=4,
                    linewidth=2,
                    label=col)

ax2.set_title('Comparação de Temperaturas', fontsize=14, fontweight='bold')
ax2.set_ylabel('Temperatura (°C)', fontsize=12)
ax2.set_xlabel('Índice (dias/período)', fontsize=12)
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
