import xarray as xr

# Carrega o arquivo problemático (o xarray gerencia melhor os conflitos de atributos do CMIP6)
path_original = "/dados4/pesquisa/meteoromuri/earthsym/dados_extraidos/ts_Amon_GFDL-ESM4_ssp126_r1i1p1f1_gr1_20150116-21001216.nc"
path_novo = "/dados4/pesquisa/meteoromuri/earthsym/dados_extraidos/ts_pronto_para_cdo.nc"

# Abre o dataset dropando atributos globais problemáticos se necessário, ou apenas re-salvando
ds = xr.open_dataset(path_original, decode_times=True)

# Remove o atributo 'history' que foi explicitamente apontado no seu erro do CDO
if 'history' in ds.attrs:
    del ds.attrs['history']

# Salva em formato NetCDF clássico de 64-bit (NETCDF1_64BIT) que o CDO adora
ds.to_netcdf(path_novo, format="NETCDF4")
print("Arquivo re-gravado com sucesso!")
