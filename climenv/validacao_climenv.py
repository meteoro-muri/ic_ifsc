import pandas as pd
import numpy as np
import xarray as xr
import sys
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely import wkt

merge = xr.open_dataset('/home/meteoro/scripts/scripts_muri/climenv/dados_merge.nc')

gfs = xr.open_dataset('/home/meteoro/scripts/scripts_muri/climenv/gfs.nc')
print(gfs.head())

df_climenv = pd.read_csv("/home/meteoro/scripts/scripts_muri/climenv/dados.csv",
                   encoding='utf-8',
                   sep=",",
                   header = 0,
                   index_col= False)

df_inmet = pd.read_csv("/home/meteoro/scripts/scripts_muri/climenv/inmet.csv",
                   encoding='utf-8',
                   sep=",",
                   header = 0,
                   index_col= False)
		   


df_climenv['Data'] = pd.to_datetime(df_climenv['Data'])
df_climenv['Data'] = df_climenv['Data'].dt.tz_localize(None)
df_climenv = df_climenv.set_index('Data')
df_climenv.index.name = 'time'
print("###################DADOS CLIMENV################### \n", df_climenv,"\n######################################\n")


merge = merge['prec'].sel(lat=-27.06, lon=-52.5, method='nearest').sel(time=slice('2025-12-02 03:00:00', '2026-03-02 12:00:00'))
df_merge = merge.to_dataframe()
df_merge.drop(columns=['lat','lon'], inplace=True)
df_merge.columns = ['prec']
df_merge['prec'] = df_merge['prec'] * 100
pd.to_datetime(df_merge.index, utc=True)
print("###################DADOS MERGE################### \n", df_merge,"\n######################################\n")

gfs = gfs['prate'].sel(lat=-27.06, lon=-52.5, method='nearest').sel(time=slice('2025-12-02 03:00:00', '2026-03-02 12:00:00'))
df_gfs = gfs.to_dataframe()
df_gfs.drop(columns=['lat','lon'], inplace=True)
df_gfs.columns = ['prec']
df_gfs['prec'] = df_gfs['prec'] * 100
pd.to_datetime(df_gfs.index, utc=True)
print("###################DADOS GFS################### \n", df_merge,"\n######################################\n")

#sys.exit()

df_inmet['Data'] = pd.to_datetime(df_inmet['Data'])
df_inmet['Data'] = df_inmet['Data'].dt.tz_localize(None)
df_inmet = df_inmet.set_index('Data')
df_inmet.index.name = 'time'
print("###################DADOS INMET################### \n", df_inmet,"\n######################################\n")



df_climenv = df_climenv.add_suffix('_climenv')
df_merge = df_merge.add_suffix('_merge')
df_inmet = df_inmet.add_suffix('_inmet')
df_gfs = df_gfs.add_suffix('_gfs')

df_final = df_climenv.join(df_merge)
print("###################DF UNIFICADO################### \n", df_final,"\n######################################\n")
df_final = df_final.join(df_inmet)
print("###################DF UNIFICADO################### \n", df_final,"\n######################################\n")
df_final = df_final.join(df_gfs)
print("###################DF UNIFICADO################### \n", df_final,"\n######################################\n")



print(df_final['prec_merge'])
#sys.exit()

f, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
ax1.bar(df_final.index, df_final["Precipitação_climenv"])
ax1.set_title("Precipitação_climenv")
ax2.bar(df_final.index, df_final["prec_merge"])
ax2.set_title("Precipitação_merge")
ax3.bar(df_final.index, df_final["Precipitação_inmet"])
ax3.set_title("Precipitação_inmet")
ax4.bar(df_final.index, df_final["prec_gfs"])
ax4.set_title("Precipitação_gfs")
plt.ylabel("Precipitação (mm)")
plt.subplots_adjust(
    hspace=0.5)
#plt.title("Acumulado diário de Precipitação")
plt.show()





























