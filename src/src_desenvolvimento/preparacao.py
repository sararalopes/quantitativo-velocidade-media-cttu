import pandas as pd

df_consolidado = "data/dados_consolidados.csv"
df = pd.read_csv(df_consolidado, sep=",", encoding="utf-8")

print("Dataset carregou dboa.")

# Vou converter minha coluna d data para datetime, hoje ela é tida como int
df["data"] = pd.to_datetime(
    df["data"],
    errors = "coerce"
)

print(f"Tipo do campo data:", df["data"].dtype) # Checar se foi direitin

print(f"Datas inválidas:", df["data"].isna().sum()) # Conferir se alguma data ficou inválida

# Aqui eu vou fazer uma função que vai separar meus meses em 2 períodos, de férias e fora dela. Minha hipótese inicial é analisar se existe variação significativa de velocidade entre esses dois periodos

def definir_periodo(mes):
    if mes in [1, 2, 6]:
        return "ferias"
    if mes in [3, 4, 5]:
        return "nao_ferias"

    return "outro"

df["periodo"] = df["mes"].apply(definir_periodo)

print(f"Distribuição do período: ", df["periodo"].value_counts())

print(f"Uma breve amostra:\n",
    df[ [
            "data",
            "mes",
            "periodo"
        ]
    ].head(10)
)

arquivo_saida = "data/dados_preparados.csv"

df.to_csv (
    arquivo_saida,
    index=False
)

print(arquivo_saida)