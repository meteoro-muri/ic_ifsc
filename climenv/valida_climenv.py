import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime, timedelta
import sys
import matplotlib.dates as mdates

merge = xr.open_dataset('/home/sifapsc/scripts/meteoromuri/climenv/mar/merge_mar2026.grib2')
print(merge)
