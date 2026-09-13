import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Carregar dados
df = pd.read_csv('chapeco.csv')

# Converter time para datetime
df['time'] = pd.to_datetime(df['time'])

# 1. VERIFICAR INFORMAÇÕES BÁSICAS DO DATAFRAME
print("="*50)
print("INFORMAÇÕES DO DATAFRAME")
print("="*50)
print(df.info())
print("\n")

# 2. VERIFICAR VALORES AUSENTES POR COLUNA
print("="*50)
print("VALORES AUSENTES POR COLUNA")
print("="*50)
print(df.isnull().sum())
print("\n")

# 3. VERIFICAR ESTATÍSTICAS BÁSICAS
print("="*50)
print("ESTATÍSTICAS BÁSICAS")
print("="*50)
print(df[['tmp2m_gfs', 'Temperatura_climenv', 'tt2m_samet']].describe())
print("\n")

# 4. VERIFICAR PERÍODO DE CADA COLUNA
print("="*50)
print("PERÍODO DE CADA COLUNA")
print("="*50)
for col in ['tmp2m_gfs', 'Temperatura_climenv', 'tt2m_samet']:
    if col in df.columns:
        non_null = df[col].notna()
        print(f"\n{col}:")
        print(f"  Início: {df.loc[non_null, 'time'].min()}")
        print(f"  Fim: {df.loc[non_null, 'time'].max()}")
        print(f"  Total registros: {non_null.sum()}")
        print(f"  Percentual preenchido: {(non_null.sum()/len(df))*100:.2f}%")

# 5. VERIFICAR SE HÁ PULOS OU FALHAS
print("\n" + "="*50)
print("VERIFICANDO PULOS TEMPORAIS")
print("="*50)

# Ordenar por time
df = df.sort_values('time')

# Calcular diferença entre timestamps consecutivos
df['time_diff'] = df['time'].diff()

print(f"Frequência esperada: Horária")
print(f"Diferença mínima: {df['time_diff'].min()}")
print(f"Diferença máxima: {df['time_diff'].max()}")
print(f"Diferença média: {df['time_diff'].mean()}")

# Verificar se há gaps > 1 hora
gaps = df[df['time_diff'] > pd.Timedelta(hours=1.5)]
if len(gaps) > 0:
    print(f"\nEncontrados {len(gaps)} gaps > 1.5 horas:")
    for idx, row in gaps.iterrows():
        print(f"  Gap em {row['time']} de {row['time_diff']}")

# 6. VISUALIZAR A DISPONIBILIDADE DOS DADOS
fig, axes = plt.subplots(3, 1, figsize=(15, 10))

for i, col in enumerate(['tmp2m_gfs', 'Temperatura_climenv', 'tt2m_samet']):
    if col in df.columns:
        # Criar máscara para dados não nulos
        mascara = df[col].notna()
        
        # Plotar pontos onde há dados
        axes[i].scatter(df.loc[mascara, 'time'], 
                       [i]*mascara.sum(), 
                       s=1, alpha=0.5, c='green')
        
        # Plotar pontos onde não há dados
        axes[i].scatter(df.loc[~mascara, 'time'], 
                       [i]*(~mascara).sum(), 
                       s=1, alpha=0.5, c='red')
        
        axes[i].set_title(f'Disponibilidade de dados: {col}')
        axes[i].set_yticks([])
        axes[i].set_xlabel('Tempo')

plt.tight_layout()
plt.show()

# 7. VERIFICAR VALORES EXTREMOS OU INVÁLIDOS
print("\n" + "="*50)
print("VERIFICANDO VALORES EXTREMOS")
print("="*50)

for col in ['tmp2m_gfs', 'Temperatura_climenv', 'tt2m_samet']:
    if col in df.columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - 3 * iqr
        limite_superior = q3 + 3 * iqr
        
        outliers = df[(df[col] < limite_inferior) | (df[col] > limite_superior)]
        
        print(f"\n{col}:")
        print(f"  Q1: {q1:.2f}")
        print(f"  Q3: {q3:.2f}")
        print(f"  IQR: {iqr:.2f}")
        print(f"  Limites: [{limite_inferior:.2f}, {limite_superior:.2f}]")
        print(f"  Outliers: {len(outliers)}")

# 8. SOLUÇÃO: TRATAR DADOS PROBLEMÁTICOS

# Opção A: Remover linhas com NaN apenas na coluna problemática
df_clean = df.dropna(subset=['tt2m_samet'], how='all')

# Opção B: Interpolar valores faltantes (se fizer sentido para seus dados)
df['tt2m_samet_interpolado'] = df['tt2m_samet'].interpolate(method='linear', limit_direction='both')

# Opção C: Preencher com valores vizinhos
df['tt2m_samet_ffill'] = df['tt2m_samet'].fillna(method='ffill').fillna(method='bfill')

# 9. PLOTAR NOVAMENTE COM OS DADOS TRATADOS
plt.figure(figsize=(14, 8))

# Plotar dados originais (com problemas)
sns.lineplot(data=df, x='time', y='tmp2m_gfs', label='tmp2m_gfs', linewidth=1.5)
sns.lineplot(data=df, x='time', y='Temperatura_climenv', label='Temperatura_climenv', linewidth=1.5)

# Plotar dados tratados da coluna problemática
if 'tt2m_samet_interpolado' in df.columns:
    sns.lineplot(data=df, x='time', y='tt2m_samet_interpolado', 
                 label='tt2m_samet (interpolado)', linewidth=1.5, linestyle='--')

# Configurar eixo x
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.xticks(rotation=45)

plt.title('Comparação de Temperaturas (com dados tratados)', fontsize=14, fontweight='bold')
plt.xlabel('Data')
plt.ylabel('Temperatura (°C)')
plt.legend(title='Variáveis', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 10. SOLUÇÃO RÁPIDA: Forçar plotagem ignorando NaN
plt.figure(figsize=(14, 8))

# Plotar ignorando NaN
plt.plot(df['time'], df['tmp2m_gfs'], linewidth=1.5, label='tmp2m_gfs')
plt.plot(df['time'], df['Temperatura_climenv'], linewidth=1.5, label='Temperatura_climenv')
plt.plot(df['time'], df['tt2m_samet'], linewidth=1.5, label='tt2m_samet', alpha=0.7)

# Configurar eixo x
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.xticks(rotation=45)

plt.title('Comparação de Temperaturas (plot direto com matplotlib)', fontsize=14, fontweight='bold')
plt.xlabel('Data')
plt.ylabel('Temperatura (°C)')
plt.legend(title='Variáveis', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
