import pandas as pd

arquivo_janeiro = "../data/2026-janeiro-quantitativo-das-vias-por-velocidade-media.csv"
arquivo_fevereiro = "../data/2026-fevereiro-quantitativo-das-vias-por-velocidade-media.csv"
arquivo_marco = "../data/2026-marco-quantitativo-das-vias-por-velocidade-media.csv"
arquivo_abril = "../data/2026-abril-quantitativo-das-vias-por-velocidade-media.csv"
arquivo_maio = "../data/2026-maio-quantitativo-das-vias-por-velocidade-media.csv"
arquivo_junho = "../data/2026-junho-quantitativo-das-vias-por-velocidade-media.csv"

df_janeiro = pd.read_csv(arquivo_janeiro, sep=";", encoding="utf-8")
df_fevereiro = pd.read_csv(arquivo_fevereiro, sep=";", encoding="utf-8")
df_marco = pd.read_csv(arquivo_marco, sep=";", encoding="utf-8")
df_abril = pd.read_csv(arquivo_abril, sep=";", encoding="utf-8")
df_maio = pd.read_csv(arquivo_maio, sep=";", encoding="utf-8")
df_junho = pd.read_csv(arquivo_junho, sep=";", encoding="utf-8")

# Aqui eu vou fazer uma breve exploração de cada arquivo de dados só para conferir se está de acordo com o que o dicionário de dados me disse. 
# Depois dessa verificação inicial de cada mês, farei uma breve análise dos meus dados.

print("="*30, "Métricas de Janeiro", "="*30)
print(df_janeiro.head(30))
print(df_janeiro.shape)
print(df_janeiro.columns)
print(df_janeiro.info())
print(df_janeiro.describe())

print("Quantidade de nulos:",df_janeiro.isnull().sum())
print("Duplicados:", df_janeiro.duplicated().sum())
print(df_janeiro["equipamento"].nunique())
print(df_janeiro["equipamento"].unique())
print(df_janeiro["faixa"].unique())
print(df_janeiro["hora"].unique())
print(df_janeiro["minutos_intervalo"].unique())

print("="*30, "Métricas de Fevereiro", "="*30)
print(df_fevereiro.head(30))
print(df_fevereiro.shape)
print(df_fevereiro.columns)
print(df_fevereiro.info())
print(df_fevereiro.describe())

print("Quantidade de nulos:",df_fevereiro.isnull().sum())
print("Duplicados:", df_fevereiro.duplicated().sum())
print(df_fevereiro["equipamento"].nunique())
print(df_fevereiro["equipamento"].unique())
print(df_fevereiro["faixa"].unique())
print(df_fevereiro["hora"].unique())
print(df_fevereiro["minutos_intervalo"].unique())

print("="*30, "Métricas de Março", "="*30)
print(df_marco.head(30))
print(df_marco.shape)
print(df_marco.columns)
print(df_marco.info())
print(df_marco.describe())

print("Quantidade de nulos:",df_marco.isnull().sum())
print("Duplicados:", df_marco.duplicated().sum())
print(df_marco["equipamento"].nunique())
print(df_marco["equipamento"].unique())
print(df_marco["faixa"].unique())
print(df_marco["hora"].unique())
print(df_marco["minutos_intervalo"].unique()) 

print("="*30, "Métricas de Abril", "="*30)
print(df_abril.head(30))
print(df_abril.shape)
print(df_abril.columns)
print(df_abril.info())
print(df_abril.describe())

print("Quantidade de nulos:",df_abril.isnull().sum())
print("Duplicados:", df_abril.duplicated().sum())
print(df_abril["equipamento"].nunique())
print(df_abril["equipamento"].unique())
print(df_abril["faixa"].unique())
print(df_abril["hora"].unique())
print(df_abril["minutos_intervalo"].unique())

print("="*30, "Métricas de Maio", "="*30)
print(df_maio.head(30))
print(df_maio.shape)
print(df_maio.columns)
print(df_maio.info())
print(df_maio.describe())

print("Quantidade de nulos:",df_maio.isnull().sum())
print("Duplicados:", df_maio.duplicated().sum())
print(df_maio["equipamento"].nunique())
print(df_maio["equipamento"].unique())
print(df_maio["faixa"].unique())
print(df_maio["hora"].unique())
print(df_maio["minutos_intervalo"].unique())

print("="*30, "Métricas de Junho", "="*30)
print(df_junho.head(30))
print(df_junho.shape)
print(df_junho.columns)
print(df_junho.info())
print(df_junho.describe())

print("Quantidade de nulos:",df_junho.isnull().sum())
print("Duplicados:", df_junho.duplicated().sum())
print(df_junho["equipamento"].nunique())
print(df_junho["equipamento"].unique())
print(df_junho["faixa"].unique())
print(df_junho["hora"].unique())
print(df_junho["minutos_intervalo"].unique())