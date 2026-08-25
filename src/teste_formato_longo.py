import pandas as pd

df = pd.read_csv("data/dados_preparados.csv")


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

amostra = df.head(5).copy()

df_longo = amostra.melt(
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

print(df_longo)













