import pandas as pd

arquivo = "data/dados_consolidados.csv"

df = pd.read_csv(arquivo)

print("Dados carregados!")
print(f"Linhas: {len(df):,}")
print(f"Colunas: {len(df.columns)}")

# Definir faixas de velocidade
colunas_velocidade = [
    "qtd_0a10km",
    "qtd_11a20km",
    "qtd_21a30km",
    "qtd_31a40km",
    "qtd_41a50km",
    "qtd_51a60km",
    "qtd_61a70km",
    "qtd_71a80km",
    "qtd_81a90km",
    "qtd_91a100km",
    "qtd_acimade100km"
]

# Somar o volume por equipamento
df_equipamentos = (
    df.groupby("equipamento")[colunas_velocidade]
    .sum()
    .reset_index()
)

# Calcular o total de veículos
df_equipamentos["total_veiculos"] = (
    df_equipamentos[colunas_velocidade]
    .sum(axis=1)
)

# Calcular percentual
for coluna in colunas_velocidade:

    nova_coluna = coluna.replace("qtd_", "perc_")

    df_equipamentos[nova_coluna] = (
        df_equipamentos[coluna]
        / df_equipamentos["total_veiculos"]
        * 100
    )

# Selecionar colunas finais
colunas_percentuais = [
    coluna.replace("qtd_", "perc_")
    for coluna in colunas_velocidade
]

df_clusterizacao = df_equipamentos[
    ["equipamento"] + colunas_percentuais + ["total_veiculos"]
]


# Salvar a bomba do dataset

saida = "data/dados_clusterizacao.csv"

df_clusterizacao.to_csv(
    saida,
    index=False
)

# Ver se está tudo certinho
print("\nDataset de clusterização criado!")
print(f"Linhas: {len(df_clusterizacao):,}")
print(f"Colunas: {len(df_clusterizacao.columns)}")

print("\nPrimeiras linhas:")
print(df_clusterizacao.head())

print("\nSoma dos percentuais:")
print(
    df_clusterizacao[colunas_percentuais]
    .sum(axis=1)
    .head()
)