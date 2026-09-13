import cdsapi
import zipfile
import os
import xarray as xr


dataset = "projections-cmip6"
request = {
    "temporal_resolution": "monthly",
    "experiment": "ssp2_4_5",
    "variable": "precipitation",
    "model": "cesm2",
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
    "year": [
        "2015", "2016", "2017",
        "2018", "2019", "2020",
        "2021", "2022", "2023",
        "2024", "2025", "2026",
        "2027", "2028", "2029",
        "2030", "2031", "2032",
        "2033", "2034", "2035",
        "2036", "2037", "2038",
        "2039", "2040", "2041",
        "2042", "2043", "2044",
        "2045", "2046", "2047",
        "2048", "2049", "2050",
        "2051", "2052", "2053",
        "2054", "2055", "2056",
        "2057", "2058", "2059",
        "2060", "2061", "2062",
        "2063", "2064", "2065",
        "2066", "2067", "2068",
        "2069", "2070", "2071",
        "2072", "2073", "2074",
        "2075", "2076", "2077",
        "2078", "2079", "2080",
        "2081", "2082", "2083",
        "2084", "2085", "2086",
        "2087", "2088", "2089",
        "2090", "2091", "2092",
        "2093", "2094", "2095",
        "2096", "2097", "2098",
        "2099", "2100"
    ]
}



# Define caminhos
output_dir = "/dados4/pesquisa/meteoromuri/earthsym/"
zip_path = os.path.join(output_dir, "prec_cesm2_ssp5_8_5.zip")

client = cdsapi.Client()

# Baixa salvando como .zip
print("Baixando arquivo...")
client.retrieve(dataset, request).download(zip_path)

# Extrai os NetCDFs internos
print("Extraindo arquivos NetCDF...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(output_dir)

# Opcional: deleta o arquivo .zip para não ocupar espaço duplicado
os.remove(zip_path)
print("Concluído!")
'''
# Carrega o arquivo problemático (o xarray gerencia melhor os conflitos de atributos do CMIP6)
path_original = "/dados4/pesquisa/meteoromuri/earthsym/pr_Amon_EC-Earth3-Veg-LR_ssp585_r1i1p1f1_gr_20150116-21001216.nc"
path_novo = "/dados4/pesquisa/meteoromuri/earthsym/prec_ec_earth3_veg_lr_ssp5_8_5.nc"

# Abre o dataset dropando atributos globais problemáticos se necessário, ou apenas re-salvando
ds = xr.open_dataset(path_original, decode_times=True)

# Remove o atributo 'history' que foi explicitamente apontado no seu erro do CDO
if 'history' in ds.attrs:
    del ds.attrs['history']

# Salva em formato NetCDF clássico de 64-bit (NETCDF1_64BIT) que o CDO adora
ds.to_netcdf(path_novo, format="NETCDF4")
print("Arquivo re-gravado com sucesso!")
'''

