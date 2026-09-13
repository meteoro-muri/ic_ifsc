import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas as pd
import sys
import geopandas as gpd

ds = xr.open_dataset(
        '/home/sifapsc/scripts/meteoromuri/TCC/gfas_hysplit.grib', 
        engine='cfgrib',
    )
    
print(ds)
