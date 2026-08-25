import pandas as pd

df_consolidado = "../data/dados_consolidados.csv"
df = pd.read_csv(df_consolidado, sep=",", encoding="utf-8")

# Estou sempre colocando UTF-8 pq as vzes, as bases do dados recife tem caracteres especiais 

print("="*30, "Total de Registros", "="*30)
print(df.shape)

print("="*30, "Total por Mês", "="*30)
print(df["mes"].value_counts().sort_index())

print("="*30, "Total por Equipamento", "="*30)
print(df["equipamento"].value_counts())

print("="*30, "Total por Faixa", "="*30)
print(df["faixa"].value_counts().sort_index())

print("="*30, "Total por Hora", "="*30)
print(df["hora"].value_counts().sort_index())

print("="*30, "Total de veículos por velocidade", "="*30)

# Eu quero ver quantos veículos eu tenho na minha base. Mas, as quantidades são dividida por faixas de veolocidade, por isso eu vou juntar tudo para saber quantos veículos eu tenho nessa base. 
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

total_velocidade = df[colunas_velocidade].sum()

print(total_velocidade)

print("="*30, "Total de veículos", "="*30)
total_veiculos = df[colunas_velocidade].sum().sum()
print(total_veiculos)

print("="*30, "Total de veículos por mês", "="*30)
total_por_mes = (
    df.groupby("mes")[colunas_velocidade].sum()
)
print(total_por_mes)

# Agora eu quero aproveitar que tenho meu total de veiculos e observar os periodos de maior fluxo

print("="*30, "Total de veículos por hora", "="*30)
total_por_hora = (
    df.groupby("hora")[colunas_velocidade].sum()
)
print(total_por_hora)













