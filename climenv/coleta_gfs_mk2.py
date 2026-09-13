import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import matplotlib.dates as mdates

df = pd.read_csv('chapeco.csv')
print(df.columns)

df['time'] = pd.to_datetime(df['time'])

sns.set_style("darkgrid")
sns.set_palette("husl")

# Criar subplots - isso retorna ax como um array de 2 elementos (1D)
fig, ax = plt.subplots(2, 1, figsize=(10, 8))  # Adicionei figsize para melhor visualização

# Lista das colunas de temperatura que você quer plotar
colunas_temp = ['tmp2m_gfs', 'Temperatura_climenv', 'tt2m_samet']
colunas_prec = ['prate_gfs', 'prec_merge', 'Precipitação_climenv']

# Plotar temperaturas no primeiro subplot (ax[0])
for coluna in colunas_temp:
    if coluna in df.columns:
        sns.lineplot(data=df, x='time', y=coluna, label=coluna, linewidth=1.5, ax=ax[0])

# Plotar precipitação no segundo subplot (ax[1])
for coluna in colunas_prec:
    if coluna in df.columns:
        sns.lineplot(data=df, x='time', y=coluna, label=coluna, linewidth=1.5, ax=ax[1])

# Configurar eixo x para o primeiro subplot
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax[0].xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax[0].tick_params(axis='x', rotation=45)

# Configurar eixo x para o segundo subplot
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax[1].tick_params(axis='x', rotation=45)

# Títulos e labels
ax[0].set_title('Comparação de Temperaturas', fontsize=14, fontweight='bold')
ax[0].set_ylabel('Temperatura (°C)')
ax[0].legend(title='Variáveis', bbox_to_anchor=(1.05, 1), loc='upper left')
ax[0].grid(True, alpha=0.3)

ax[1].set_title('Comparação de Precipitação', fontsize=14, fontweight='bold')
ax[1].set_xlabel('Data')
ax[1].set_ylabel('Precipitação (mm)')
ax[1].legend(title='Variáveis', bbox_to_anchor=(1.05, 1), loc='upper left')
ax[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
