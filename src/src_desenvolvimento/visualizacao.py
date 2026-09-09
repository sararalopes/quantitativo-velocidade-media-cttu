import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

df_consolidado = "data/dados_consolidados.csv"
df = pd.read_csv(df_consolidado, sep=",", encoding="utf-8")

# Só puxando novamente minhas colunas de velocidade
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

# Estava tendo um problema das imagens gerarem os gráficos com números em notação cientifica. Então, pedi ajuda ao chat e ele me deu essa função de formatação em milhões.
def formatar_milhoes(valor, pos):
    return f"{valor / 1_000_000:.0f}M"


formatador_milhoes = FuncFormatter(formatar_milhoes)

# Aqui vou começar a plotar meus gráficos. estou fazendo gráficos pq me ajuda muito na visualização dos meus resultados.

# Total de Veículos por mês

total_por_mes = (
    df.groupby("mes")[colunas_velocidade].sum()
)

total_por_mes["total_veiculos"] = total_por_mes.sum(axis=1)

plt.figure(figsize=(10, 5))

plt.bar(
    total_por_mes.index,
    total_por_mes["total_veiculos"]
)

plt.title("Total de veículos por mês")
plt.xlabel("Mês")
plt.ylabel("Quantidade de Veículos")
plt.xticks(range(1, 7))

plt.gca().yaxis.set_major_formatter(formatador_milhoes)
plt.tight_layout()
plt.show()

# Total de Veículos por hora

total_por_hora = (
    df.groupby("hora")[colunas_velocidade].sum()
)

total_por_hora["total_veiculos"] = total_por_hora.sum(axis=1)

plt.figure(figsize=(10, 5))

plt.plot (
    total_por_hora.index,
    total_por_hora["total_veiculos"],
    marker = "o"
)

plt.title("Total de Veículos por hora")
plt.xlabel("Hora")
plt.ylabel("Quantidade de veículos")
plt.xticks(range(0, 24))

plt.gca().yaxis.set_major_formatter(formatador_milhoes)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# Total por faixa de velocidade 

total_velocidade = df[colunas_velocidade].sum()

nomes_velocidade = [
    "0–10 km/h",
    "11–20 km/h",
    "21–30 km/h",
    "31–40 km/h",
    "41–50 km/h",
    "51–60 km/h",
    "61–70 km/h",
    "71–80 km/h",
    "81–90 km/h",
    "91–100 km/h",
    "Acima de 100 km/h",
]

plt.figure(figsize=(12, 6))

plt.bar (
    nomes_velocidade,
    total_velocidade.values
)

plt.title("Total de veículos por faixa de velocidade")
plt.xlabel("Faixa de velocidade")
plt.ylabel("Quantidade de veículos")

plt.xticks(rotation=45, ha="right")

plt.gca().yaxis.set_major_formatter(formatador_milhoes)
plt.tight_layout()
plt.show()

# Velocidade por mês

velocidade_por_mes = (
    df.groupby("mes")[colunas_velocidade]
    .sum()
)

# Transformamos cada mês em percentual
percentual_por_mes = (
    velocidade_por_mes
    .div(velocidade_por_mes.sum(axis=1), axis=0)
    * 100
)


plt.figure(figsize=(12, 6))

percentual_por_mes.columns = nomes_velocidade

percentual_por_mes.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.title("Distribuição das faixas de velocidade por mês")
plt.xlabel("Mês")
plt.ylabel("Participação (%)")

plt.xticks(rotation=0)

plt.legend(
    title="Velocidade (km/h)",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.tight_layout()
plt.show()

