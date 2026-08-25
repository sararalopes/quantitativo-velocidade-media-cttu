import pandas as pd
from pathlib import Path

pasta_data = Path("data/")

arquivos = [
    "2026-janeiro-quantitativo-das-vias-por-velocidade-media.csv",
    "2026-fevereiro-quantitativo-das-vias-por-velocidade-media.csv",
    "2026-marco-quantitativo-das-vias-por-velocidade-media.csv",
    "2026-abril-quantitativo-das-vias-por-velocidade-media.csv",
    "2026-maio-quantitativo-das-vias-por-velocidade-media.csv",
    "2026-junho-quantitativo-das-vias-por-velocidade-media.csv",
]

dataframes = []

for arquivo in arquivos:
    caminho = pasta_data / arquivo 

    print(f"Lendo: {arquivo}")

    df = pd.read_csv(caminho, sep=";", encoding="utf-8")

    dataframes.append(df)

df = pd.concat(dataframes, ignore_index=True)

arquivo_saida = pasta_data / "dados_consolidados.csv"

df.to_csv(arquivo_saida, index=False)

print(f"\nDataset consolidado salvo em: {arquivo_saida}")

# Vou dar uma olhada nas mesmas coisas que olhei individualmente, só para ver se está tudo nos conformes

print("="*30, "Métricas de Tudo Junto", "="*30)
print(df.head(10))
print(df.shape)
print(df.columns)
print(df.info())
print(df.describe())

print("Quantidade de nulos:",df.isnull().sum())
print("Duplicados:", df.duplicated().sum())
print(df["equipamento"].nunique())
print(df["equipamento"].unique())
print(df["faixa"].unique())
print(df["hora"].unique())
print(df["minutos_intervalo"].unique())