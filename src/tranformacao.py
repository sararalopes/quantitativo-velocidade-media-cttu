import pandas as pd

df = pd.read_csv("data/dados_preparados.csv")


print("="*30, "Dataset pré transformação", "="*30)
print(f"Linhas: {df.shape[0]}")
print(f"Colunas: {df.shape[1]}")

# Colocando o teste para jogo 

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
    "qtd_acimade100km",
]

df_longo = df.melt(
    id_vars=[
        "ano",
        "mes",
        "equipamento",
        "faixa",
        "data",
        "hora",
        "minutos_intervalo",
        "periodo",
    ],
    value_vars=colunas_velocidade,
    var_name="faixa_velocidade",
    value_name="quantidade",
)


print("="*30, "Dataset pós transformação", "="*30)
print(f"Linhas: {df_longo.shape[0]}")
print(f"Colunas: {df_longo.shape[1]}")

# Deixar os nomes das faixas mais bonitos agora

mapa_velocidade = {
    "qtd_0a10km": "0-10",
    "qtd_11a20km": "11-20",
    "qtd_21a30km": "21-30",
    "qtd_31a40km": "31-40",
    "qtd_41a50km": "41-50",
    "qtd_51a60km": "51-60",
    "qtd_61a70km": "61-70",
    "qtd_71a80km": "71-80",
    "qtd_81a90km": "81-90",
    "qtd_91a100km": "91-100",
    "qtd_acimade100km": "acima_100",
}


df_longo["faixa_velocidade"] = (
    df_longo["faixa_velocidade"]
    .map(mapa_velocidade)
)

# Papo de olhar se está tudo certinho agora

print(
    df_longo["faixa_velocidade"]
    .value_counts()
)

quantidade_zeros = (
    (df_longo["quantidade"] == 0)
    .sum()
)

print(f"Registros com quantidade = 0: {quantidade_zeros}")

print(
    f"Percentual de zeros: "
    f"{quantidade_zeros / len(df_longo) * 100:.2f}%"
)


print(f"Verificação de nulos:", df_longo.isnull().sum())

print("Duplicados:", df_longo.duplicated().sum())

# Uma amostra

print(
    df_longo[
        [
            "equipamento",
            "data",
            "hora",
            "minutos_intervalo",
            "periodo",
            "faixa_velocidade",
            "quantidade",
        ]
    ].head(20)
)


arquivo_saida = "data/dados_longos.csv"

df_longo.to_csv(
    arquivo_saida,
    index=False
)

print(arquivo_saida)