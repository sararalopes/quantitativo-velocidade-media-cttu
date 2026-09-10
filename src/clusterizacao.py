import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

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

# Iniciando checagem da saúde do meu dataset

# Estatística das features
print("\nEstatísticas das features:")

print(
    df_clusterizacao[colunas_percentuais].describe().T
)

# Valores ausentes 
print("\nValores ausentes:")

print(
    df_clusterizacao[colunas_percentuais]
    .isnull()
    .sum()
)

# Iniciando normalização dos meus dados
scaler = StandardScaler()
X = df_clusterizacao[colunas_percentuais]
X_scaled = scaler.fit_transform(X)

print("\nFormato de X_scaled:")
print(X_scaled.shape)

print("\nMédia das features após padronização:")
print(X_scaled.mean(axis=0))

print("\nDesvio padrão das features após padronização:")
print(X_scaled.std(axis=0))

# Testando diferentes valores de K -> Escolhi trablhar com a visualização de ambas as principais validações: Silhouette Score e Elbow Method
resultados = []

for k in range(2, 9):

    modelo = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = modelo.fit_predict(X_scaled)

    inertia = modelo.inertia_

    silhouette = silhouette_score(
        X_scaled,
        labels
    )

    resultados.append({
        "k": k,
        "inertia": inertia,
        "silhouette": silhouette
    })


df_resultados = pd.DataFrame(resultados)

print("\nResultados dos testes de K:")
print(df_resultados)

# Plotando os gráficos para visualizar os dados dispostos em números anteriormente

# Elbow
# plt.figure(figsize=(8, 5))

# plt.plot(
#     df_resultados["k"],
#     df_resultados["inertia"],
#     marker="o"
# )

# plt.xlabel("Número de clusters (K)")
# plt.ylabel("Inertia")
# plt.title("Elbow Method")

# plt.xticks(df_resultados["k"])

# plt.show()

# Silhouette
# plt.figure(figsize=(8, 5))

# plt.plot(
#     df_resultados["k"],
#     df_resultados["silhouette"],
#     marker="o"
# )

# plt.xlabel("Número de clusters (K)")
# plt.ylabel("Silhouette Score")
# plt.title("Silhouette Score")

# plt.xticks(df_resultados["k"])

# plt.show()

# Vou iniciar minha avaliação na divisão de cluster. Inicialmente, meus dados retornado nos dois métodos apontam para um uso de 2 - 4 cluster. 
# Vou plotar minhas inforamções promovendo uma comparação de perfis com 2 e 4 clusters.

# Comparar K=2 e K=4
modelos = {}

for k in [2, 4]:

    modelo = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = modelo.fit_predict(X_scaled)

    modelos[k] = modelo

    df_clusterizacao[f"cluster_k{k}"] = labels

# Quantidade de equipamentos por cluster
for k in [2, 4]:

    print(f"\nQuantidade de equipamentos - K={k}:")

    print(
        df_clusterizacao[f"cluster_k{k}"]
        .value_counts()
        .sort_index()
    )

# Perfil médio dos clusters
for k in [2, 4]:

    coluna_cluster = f"cluster_k{k}"

    perfil = (
        df_clusterizacao
        .groupby(coluna_cluster)[colunas_percentuais]
        .mean()
    )

    print(f"\nPerfil médio dos clusters - K={k}:")
    print(perfil)

# Os testes iniciais indicaram K=2 como a solução mais promissora. O modelo apresentou o maior Silhouette Score entre os valores avaliados (0,386), além de produzir dois grupos com perfis de velocidade claramente distintos. O K=4 permitiu uma segmentação mais detalhada, porém gerou um cluster com apenas dois equipamentos e apresentou Silhouette inferior (0,358).
for k in [2, 4]:

    coluna_cluster = f"cluster_k{k}"

    print(f"\nEquipamentos por cluster - K={k}:")

    for cluster in sorted(df_clusterizacao[coluna_cluster].unique()):

        equipamentos = (
            df_clusterizacao[
                df_clusterizacao[coluna_cluster] == cluster
            ]["equipamento"]
            .tolist()
        )

        print(f"\nCluster {cluster}:")
        print(equipamentos)

# Analisar cluster pequeno
equipamentos_cluster_pequeno = ["CTTU-9471", "CTTU-9483"]

print("\nPerfil dos equipamentos do cluster 1 - K=4:")

perfil_pequeno = df_clusterizacao[
    df_clusterizacao["equipamento"].isin(equipamentos_cluster_pequeno)
][
    ["equipamento"] + colunas_percentuais + ["total_veiculos"]
]

print(perfil_pequeno.to_string(index=False))

# Centros dos clusters
modelo_k4 = modelos[4]

centroides_k4 = scaler.inverse_transform(
    modelo_k4.cluster_centers_
)

df_centroides = pd.DataFrame(
    centroides_k4,
    columns=colunas_percentuais
)

df_centroides.index.name = "cluster"

print("\nCentróides do K=4:")
print(df_centroides)

# Diferenças para o centro
for equipamento in equipamentos_cluster_pequeno:

    linha = df_clusterizacao[
        df_clusterizacao["equipamento"] == equipamento
    ]

    cluster = int(linha["cluster_k4"].iloc[0])

    valores = linha[colunas_percentuais].iloc[0].values

    centroide = centroides_k4[cluster]

    diferencas = abs(valores - centroide)

    df_diferencas = pd.DataFrame({
        "faixa": colunas_percentuais,
        "equipamento": valores,
        "centroide": centroide,
        "diferenca": diferencas
    })

    df_diferencas = df_diferencas.sort_values(
        "diferenca",
        ascending=False
    )

    print(f"\n{equipamento} - Cluster {cluster}")
    print(df_diferencas.to_string(index=False))

print(
    df_clusterizacao[
        df_clusterizacao["equipamento"].isin(equipamentos_cluster_pequeno)
    ][["equipamento"] + colunas_percentuais]
    .T
)

# Comparar volume dos equipamentos
print("\nVolume total por equipamento:")

print(
    df_clusterizacao[
        df_clusterizacao["equipamento"].isin(equipamentos_cluster_pequeno)
    ][["equipamento", "total_veiculos"]]
)

volume_clusters = (
    df_clusterizacao
    .groupby("cluster_k4")["total_veiculos"]
    .agg(["count", "mean", "median", "min", "max"])
)

print("\nVolume por cluster:")
print(volume_clusters)

# Quantidade de registros por equipamento
registros_equipamentos = (
    df.groupby("equipamento")
    .size()
    .reset_index(name="quantidade_registros")
)

print("\nQuantidade de registros dos equipamentos do cluster 1:")

print(
    registros_equipamentos[
        registros_equipamentos["equipamento"]
        .isin(equipamentos_cluster_pequeno)
    ]
)

# Distância dos equipamentos aos centros
from scipy.spatial.distance import cdist

X_dois = (
    df_clusterizacao[
        df_clusterizacao["equipamento"].isin(
            equipamentos_cluster_pequeno
        )
    ][colunas_percentuais]
)

X_dois_scaled = scaler.transform(X_dois)

distancias = cdist(
    X_dois_scaled,
    modelos[4].cluster_centers_,
    metric="euclidean"
)

df_distancias = pd.DataFrame(
    distancias,
    index=equipamentos_cluster_pequeno,
    columns=[
        "Cluster 0",
        "Cluster 1",
        "Cluster 2",
        "Cluster 3"
    ]
)

print("\nDistância aos centróides - K=4:")
print(df_distancias)

"""

Divisão com K=2:
Cluster 0 - 33 equipamentos -> tráfego mais concentrado em velocidades intermediárias
Cluster 1 - 13 equipamentos -> tráfego mais concentrado em velocidades elevadas

Divisão com K=4
Cluster 3 - 25 equiapamentos -> perfil mais lento
Cluster 0 - 02 equiapmentos -> 31–40 km/h predominante
Cluster 2 - 13 equipamentos -> 41–50 km/h predominante
Cluster 1 - 06 equipamentos -> perfil mais rápido, com maior participação em 51–60 km/h

Embora o Cluster 0 tenha apenas dois equipamentos, eles apresentam um perfil de velocidade consistente entre si e significativamente mais próximo do centróide desse cluster do que dos demais.

Distância aos centróides - K=4:
           Cluster 0  Cluster 1  Cluster 2  Cluster 3
CTTU-9471   8.161592   2.007073   5.971038   9.384931
CTTU-9483  11.771151   2.007073   9.551289  12.751485

"""

# PCA
pca = PCA(
    n_components=2
)

X_pca = pca.fit_transform(X_scaled)

print("\nFormato do PCA:")
print(X_pca.shape)

print("\nVariância explicada:")
print(pca.explained_variance_ratio_)

print(
    "\nVariância explicada acumulada:"
)
print(
    pca.explained_variance_ratio_.sum()
)

# Gráfico PCA - K=2
# plt.figure(figsize=(9, 6))

# for cluster in sorted(
#     df_clusterizacao["cluster_k2"].unique()
# ):

#     pontos = X_pca[
#         df_clusterizacao["cluster_k2"].values == cluster
#     ]

#     plt.scatter(
#         pontos[:, 0],
#         pontos[:, 1],
#         label=f"Cluster {cluster}"
#     )

# plt.xlabel("PC1")
# plt.ylabel("PC2")
# plt.title("PCA dos equipamentos - K=2")
# plt.legend()
# plt.grid(alpha=0.3)

# for i, equipamento in enumerate(
#     df_clusterizacao["equipamento"]
# ):

#     plt.annotate(
#         equipamento,
#         (X_pca[i, 0], X_pca[i, 1]),
#         fontsize=7,
#         xytext=(4, 4),
#         textcoords="offset points"
#     )

# plt.show()

# Gráfico PCA - K=4
# plt.figure(figsize=(9, 6))

# for cluster in sorted(
#     df_clusterizacao["cluster_k4"].unique()
# ):

#     pontos = X_pca[
#         df_clusterizacao["cluster_k4"].values == cluster
#     ]

#     plt.scatter(
#         pontos[:, 0],
#         pontos[:, 1],
#         label=f"Cluster {cluster}"
#     )

# plt.xlabel("PC1")
# plt.ylabel("PC2")
# plt.title("PCA dos equipamentos - K=4")
# plt.legend()
# plt.grid(alpha=0.3)

# for i, equipamento in enumerate(
#     df_clusterizacao["equipamento"]
# ):

#     plt.annotate(
#         equipamento,
#         (X_pca[i, 0], X_pca[i, 1]),
#         fontsize=7,
#         xytext=(4, 4),
#         textcoords="offset points"
#     )

# plt.show()

# K=2 apresentou o melhor Silhouette Score, mas K=4 foi escolhido como solução analítica por oferecer maior granularidade e produzir mais perfis de tráfego para interpretação.

# Resumo final dos clusters - K=4
cluster_final = "cluster_k4"

resumo_clusters = []

for cluster in sorted(df_clusterizacao[cluster_final].unique()):

    dados = df_clusterizacao[
        df_clusterizacao[cluster_final] == cluster
    ]

    perfil = dados[colunas_percentuais].mean()

    faixa_predominante = perfil.idxmax()

    percentual_predominante = perfil.max()

    resumo_clusters.append({
        "cluster": cluster,
        "quantidade_equipamentos": len(dados),
        "volume_medio": dados["total_veiculos"].mean(),
        "faixa_predominante": faixa_predominante,
        "percentual_predominante": percentual_predominante
    })


df_resumo_clusters = pd.DataFrame(resumo_clusters)

print("\nResumo dos clusters - K=4:")
print(
    df_resumo_clusters.to_string(index=False)
)

# Salvar resultado da clusterização para usar depois nas etapas de regressão e classificação
saida_clusterizacao = "data/dados_clusterizacao_final.csv"

df_clusterizacao.to_csv(
    saida_clusterizacao,
    index=False
)

print(
    f"\nResultado da clusterização salvo em: "
    f"{saida_clusterizacao}"
)