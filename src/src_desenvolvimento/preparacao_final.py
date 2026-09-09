import pandas as pd

df = pd.read_csv("data/dados_longos.csv")

# Vou criar uma coluna que reuna meus dados referentes ao horário. Com isso, vou conseguir fazer consultas por faixa de horário no elastic

df["data_hora_inicio"] = pd.to_datetime(
    df["data"].astype(str)
    + " "
    + df["minutos_intervalo"].str[:5]
)


# Formato ISO compatível com Elasticsearch
df["data_hora_inicio"] = df["data_hora_inicio"].dt.strftime(
    "%Y-%m-%dT%H:%M:%S"
)

# Para ver como ficou 
print(
    df[
        [
            "data",
            "hora",
            "minutos_intervalo",
            "data_hora_inicio",
        ]
    ].head(10)
)

print(f"Tipo do dado:", df["data_hora_inicio"].dtype)
print(f"Ver sem tem nulos:", df["data_hora_inicio"].isna().sum())

print(f"Tipo do dado:", df["quantidade"].dtype)
print(f"Mínimo:", df["quantidade"].min())
print(f"Máximo:", df["quantidade"].max())

print(f"Faixas de velocidade\n:", df["faixa_velocidade"].unique())

# Salvar o dataset final

arquivo_saida = "data/dados_final.csv"

df.to_csv(
    arquivo_saida,
    index=False
)

print(arquivo_saida)



















