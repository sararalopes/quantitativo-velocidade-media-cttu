import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor

arquivo = "data/dados_consolidados.csv"

df = pd.read_csv(arquivo)

print("Dados carregados!")
print(f"Linhas: {len(df):,}")
print(f"Colunas: {len(df.columns)}")

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

df["volume"] = df[colunas_velocidade].sum(axis=1)

# Criando data e hora
df["data_hora"] = pd.to_datetime(
    df["data"].astype(str)
    + " "
    + df["minutos_intervalo"].str[:5]
)

# Agregando por equipamento + intervalo
df_reg = (
    df.groupby(
        ["equipamento", "data_hora"],
        as_index=False
    )["volume"]
    .sum()
)

# Ordenando os dados
df_reg = df_reg.sort_values(
    ["equipamento", "data_hora"]
).reset_index(drop=True)

# Criando variáveis de tempo
df_reg["hora"] = df_reg["data_hora"].dt.hour

df_reg["minuto"] = df_reg["data_hora"].dt.minute

df_reg["dia_da_semana"] = (
    df_reg["data_hora"].dt.dayofweek
)

df_reg["mes"] = (
    df_reg["data_hora"].dt.month
)

# Fazer um histórico para os meus dados
grupo = df_reg.groupby("equipamento")["volume"]

df_reg["lag_1"] = grupo.shift(1)

df_reg["lag_4"] = grupo.shift(4)

df_reg["lag_96"] = grupo.shift(96)

# Criação de novas médias 

df_reg["rolling_4"] = (
    df_reg
    .groupby("equipamento")["volume"]
    .transform(
        lambda x: x.shift(1).rolling(4).mean()
    )
)

df_reg["rolling_96"] = (
    df_reg
    .groupby("equipamento")["volume"]
    .transform(
        lambda x: x.shift(1).rolling(96).mean()
    )
)

# Criando alvo de +15 minutos
df_reg["data_hora_futuro"] = (
    df_reg["data_hora"]
    + pd.Timedelta(minutes=15)
)

df_alvo = df_reg[
    ["equipamento", "data_hora", "volume"]
].copy()

df_alvo = df_alvo.rename(
    columns={
        "data_hora": "data_hora_futuro",
        "volume": "volume_futuro_15min"
    }
)

df_reg = df_reg.merge(
    df_alvo,
    on=["equipamento", "data_hora_futuro"],
    how="left"
)

print("\nValores ausentes após criação do alvo correto:")

print(
    df_reg[
        [
            "lag_1",
            "lag_4",
            "lag_96",
            "volume_futuro_15min"
        ]
    ].isnull().sum()
)

total_linhas = len(df_reg)

targets_validos = (
    df_reg["volume_futuro_15min"]
    .notna()
    .sum()
)

print("\nTargets válidos:")
print(targets_validos)

print("\nPercentual de targets válidos:")
print(
    targets_validos / total_linhas * 100
)

# Alvo de +1 hora

df_15 = df_reg[
    [
        "equipamento",
        "data_hora",
        "volume"
    ]
].copy()

for minutos in [15, 30, 45, 60]:

    df_15[f"data_hora_{minutos}"] = (
        df_15["data_hora"]
        + pd.Timedelta(minutes=minutos)
    )

    df_futuro = df_reg[
        [
            "equipamento",
            "data_hora",
            "volume"
        ]
    ].copy()

    df_futuro = df_futuro.rename(
        columns={
            "data_hora": f"data_hora_{minutos}",
            "volume": f"volume_{minutos}"
        }
    )

    df_15 = df_15.merge(
        df_futuro,
        on=[
            "equipamento",
            f"data_hora_{minutos}"
        ],
        how="left"
    )

df_15["volume_futuro_1h"] = (
    df_15["volume_15"]
    + df_15["volume_30"]
    + df_15["volume_45"]
    + df_15["volume_60"]
)

print("\nEstatísticas do target de 1 hora:")
print(
    df_15["volume_futuro_1h"].describe()
)

print("\nTargets válidos de 1 hora:")
print(
    df_15["volume_futuro_1h"].notna().sum()
)

# =========================
# Modelo - 1 dia
# =========================

# Criar data sem horário
df_diario = df_reg.copy()

df_diario["data"] = (
    df_diario["data_hora"].dt.normalize()
)


# =========================
# Agregar volume por dia
# =========================

df_diario = (
    df_diario
    .groupby(
        ["equipamento", "data"],
        as_index=False
    )["volume"]
    .sum()
)

df_diario = df_diario.sort_values(
    ["equipamento", "data"]
).reset_index(drop=True)


# =========================
# Variáveis temporais
# =========================

df_diario["dia_da_semana"] = (
    df_diario["data"].dt.dayofweek
)

df_diario["mes"] = (
    df_diario["data"].dt.month
)


# =========================
# Histórico diário
# =========================

grupo_diario = (
    df_diario
    .groupby("equipamento")["volume"]
)

df_diario["lag_1_dia"] = (
    grupo_diario.shift(1)
)

df_diario["lag_7_dias"] = (
    grupo_diario.shift(7)
)

df_diario["media_7_dias"] = (
    df_diario
    .groupby("equipamento")["volume"]
    .transform(
        lambda x: x.shift(1)
        .rolling(7)
        .mean()
    )
)

# Dar um bizoo nos meus resultados
print("\nPrimeiras linhas:")
print(df_reg.head(10))

print("\nQuantidade de linhas:")
print(len(df_reg))

print("\nValores ausentes:")
print(df_reg.isnull().sum())

# VErificar se o intervalo entre os meus registros está sendo respeitado
df_reg["proximo_intervalo"] = (
    df_reg.groupby("equipamento")["data_hora"]
    .shift(-1)
)

df_reg["diferenca_minutos"] = (
    (
        df_reg["proximo_intervalo"]
        - df_reg["data_hora"]
    )
    .dt.total_seconds()
    / 60
)

print("\nDistribuição dos intervalos até o próximo registro:")
print(
    df_reg["diferenca_minutos"]
    .value_counts()
    .sort_index()
    .head(20)
)

# Estatísticas até agora

df_modelo = df_reg.dropna(
    subset=[
        "lag_1",
        "lag_4",
        "lag_96",
        "volume_futuro_15min"
    ]
).copy()

print("\nEstatísticas do target:")
print(
    df_modelo["volume_futuro_15min"].describe()
)

print("\nValores mínimos e máximos do target:")
print(
    "Mínimo:",
    df_modelo["volume_futuro_15min"].min()
)
print(
    "Máximo:",
    df_modelo["volume_futuro_15min"].max()
)
print("\nQuantidade de linhas disponíveis para modelagem:")
print(len(df_modelo))

# Definir meus alvos X e Y
features = [
    "hora",
    "minuto",
    "dia_da_semana",
    "mes",
    "lag_1",
    "lag_4",
    "lag_96"
]

X = df_modelo[features]

y = df_modelo["volume_futuro_15min"]


# Vou separar meu modelo de jan - abril para treino e mai e jun para teste
data_corte = pd.Timestamp("2026-05-01")

treino = df_modelo["data_hora"] < data_corte
teste = df_modelo["data_hora"] >= data_corte

X_train = X[treino]
X_test = X[teste]

y_train = y[treino]
y_test = y[teste]

# Ver se dividiu tudo certinho 
print("\nFeatures utilizadas:")
print(features)

print("\nFormato do treino:")
print(X_train.shape)

print("\nFormato do teste:")
print(X_test.shape)

print("\nPeríodo do treino:")
print(
    df_modelo.loc[treino, "data_hora"].min(),
    "até",
    df_modelo.loc[treino, "data_hora"].max()
)

print("\nPeríodo do teste:")
print(
    df_modelo.loc[teste, "data_hora"].min(),
    "até",
    df_modelo.loc[teste, "data_hora"].max()
)

print('\n',df_modelo.head(10)) # Quero ver como está ficando

# Vou começar a treinar meu modelo com o clássico Linear Regression, depois eu posso evoluir
modelo_baseline = LinearRegression()

modelo_baseline.fit(
    X_train,
    y_train
)

# Iniciando as minhas previsões
y_pred = modelo_baseline.predict(
    X_test
)

print("\nModelo treinado com sucesso!")

print("\nPrimeiras previsões:")
print(y_pred[:10])

print("\nPrimeiros valores reais:")
print(y_test.iloc[:10].values)

# Avaliando as paradas 
mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)

print("\nMétricas do modelo baseline:")
print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²:   {r2:.4f}")

"""
MAE:  46.60 -> em média, o modelo erra 46.60 veículos por previsão
RMSE: 74.87 -> também está em número de veículos, mas penaliza mais os erros grandes. Então tem uns erro parrudo puxando essa métrica para cima
R²:   0.8691 -> essa taxa de 0.8 não é muito boa mas, também não é ruim. Quanto mais perto de 1(100%), melhor.

A baseline apresentou bom poder preditivo mesmo utilizando apenas características temporais e valores históricos do volume. Tipo assim, ele nem sabe ainda para qual equipamento está prevendo, então nem está considerando equiapmentos que puxam a velocidade mais para baixo ou p cima.

Serassse adicionar meu equipamento na previsão do modelo fará uma diferencça positiva nos meus resultados?
"""

# Vou iniciar uma análise de modelo agora incluindo a informação de equipamento
features_numericas = [
    "hora",
    "minuto",
    "dia_da_semana",
    "mes",
    "lag_1",
    "lag_4",
    "lag_96"
]

features_categoricas = [
    "equipamento"
]

X = df_modelo[
    features_numericas + features_categoricas
]

y = df_modelo["volume_futuro_15min"]

data_corte = pd.Timestamp("2026-05-01")

treino = df_modelo["data_hora"] < data_corte
teste = df_modelo["data_hora"] >= data_corte

X_train = X[treino]
X_test = X[teste]

y_train = y[treino]
y_test = y[teste]

preprocessamento = ColumnTransformer(
    transformers=[
        (
            "numericas",
            "passthrough",
            features_numericas
        ),
        (
            "categoricas",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            features_categoricas
        )
    ]
)

modelo_2 = Pipeline(
    steps=[
        (
            "preprocessamento",
            preprocessamento
        ),
        (
            "regressao",
            LinearRegression()
        )
    ]
)

modelo_2.fit(
    X_train,
    y_train
)

y_pred_2 = modelo_2.predict(
    X_test
)

mae_2 = mean_absolute_error(
    y_test,
    y_pred_2
)

rmse_2 = mean_squared_error(
    y_test,
    y_pred_2
) ** 0.5

r2_2 = r2_score(
    y_test,
    y_pred_2
)

print("\nMétricas do Modelo 2:")
print(f"MAE:  {mae_2:.2f}")
print(f"RMSE: {rmse_2:.2f}")
print(f"R²:   {r2_2:.4f}")

"""
Métricas do Modelo 2:
MAE:  46.80
RMSE: 74.82
R²:   0.8693

Mairromeno os mesmos valores do teste de baseline. O RMSE diminiu um tiquin, o que é um bom sinal.
"""

# Criar clusterização usando apenas o período de treino

# Garantir que a coluna data_hora exista no dataframe original
if "data_hora" not in df.columns:
    df["data_hora"] = pd.to_datetime(
        df["data"].astype(str)
        + " "
        + df["minutos_intervalo"].str[:5]
    )

# Filtrar os dados de treino
df_cluster_treino = df[
    df["data_hora"] < data_corte
].copy()

print("\nPeríodo utilizado para criar os clusters:")
print(
    df_cluster_treino["data_hora"].min(),
    "até",
    df_cluster_treino["data_hora"].max()
)

# Eu vou precisar particionar meu cluster novamente pq na parte de cllusterização usei jan - jun. Agora meu modelo de regressão está trabalhando com dos dados de mai e jun para o perfil de teste. Oq significa que não posso usar esses dados para previsão

# Criando perfil de velocidade por equipamento
perfil_treino = (
    df_cluster_treino
    .groupby("equipamento")[colunas_velocidade]
    .sum()
    .reset_index()
)

# Volume total de cada equipamento no período de treino
perfil_treino["total_veiculos"] = (
    perfil_treino[colunas_velocidade]
    .sum(axis=1)
)

# Calculando percentual de cada faixa
colunas_percentuais = []

for coluna in colunas_velocidade:

    nova_coluna = coluna.replace(
        "qtd_",
        "perc_"
    )

    perfil_treino[nova_coluna] = (
        perfil_treino[coluna]
        / perfil_treino["total_veiculos"]
        * 100
    )

    colunas_percentuais.append(nova_coluna)

# Criando matriz de features do K-Means
X_cluster_treino = perfil_treino[
    colunas_percentuais
]


# Pradonizando minhas features
scaler_cluster_treino = StandardScaler()

X_cluster_treino_scaled = (
    scaler_cluster_treino.fit_transform(
        X_cluster_treino
    )
)

# Treinar dnv meu KMeans com k4
kmeans_treino = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

perfil_treino["cluster"] = (
    kmeans_treino.fit_predict(
        X_cluster_treino_scaled
    )
)


# Checar se as minhas informaçõe estão consistentes com oq eu conclui anteriormente
print("\nQuantidade de equipamentos por cluster:")

print(
    perfil_treino["cluster"]
    .value_counts()
    .sort_index()
)

print("\nEquipamentos e seus clusters:")

print(
    perfil_treino[
        ["equipamento", "cluster"]
    ]
    .sort_values(
        ["cluster", "equipamento"]
    )
    .to_string(index=False)
)

mapa_clusters = perfil_treino[
    ["equipamento", "cluster"]
].copy()

# Adicionando os clusters à base de modelagem
df_modelo = df_modelo.merge(
    mapa_clusters,
    on="equipamento",
    how="left"
)

# Verificar aqui se existem clusters ausentes
print("\nClusters ausentes:")

print(
    df_modelo["cluster"].isnull().sum()
)

# Quantidade de observações por cluster
print("\nQuantidade de observações por cluster:")

print(
    df_modelo["cluster"]
    .value_counts()
    .sort_index()
)

# Adicionar o perfil comportamental do equipamento, identificado pelo K-Means, melhora a previsão do volume de veículos?

# Modelo 3 - com cluster
features_numericas = [
    "hora",
    "minuto",
    "dia_da_semana",
    "mes",
    "lag_1",
    "lag_4",
    "lag_96"
]

features_categoricas = [
    "cluster"
]

X = df_modelo[
    features_numericas + features_categoricas
]

y = df_modelo["volume_futuro_15min"]


# Divisão temporal
data_corte = pd.Timestamp("2026-05-01")

treino = df_modelo["data_hora"] < data_corte
teste = df_modelo["data_hora"] >= data_corte

X_train = X[treino]
X_test = X[teste]

y_train = y[treino]
y_test = y[teste]


# Pré processamento
preprocessamento_cluster = ColumnTransformer(
    transformers=[
        (
            "numericas",
            "passthrough",
            features_numericas
        ),
        (
            "cluster",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            features_categoricas
        )
    ]
)


# Meu pipeline
modelo_3 = Pipeline(
    steps=[
        (
            "preprocessamento",
            preprocessamento_cluster
        ),
        (
            "regressao",
            LinearRegression()
        )
    ]
)


# Treino do modelo
modelo_3.fit(
    X_train,
    y_train
)


# PRevisões
y_pred_3 = modelo_3.predict(
    X_test
)


# Métricas
mae_3 = mean_absolute_error(
    y_test,
    y_pred_3
)

rmse_3 = mean_squared_error(
    y_test,
    y_pred_3
) ** 0.5

r2_3 = r2_score(
    y_test,
    y_pred_3
)


print("\nMétricas do Modelo 3:")
print(f"MAE:  {mae_3:.2f}")
print(f"RMSE: {rmse_3:.2f}")
print(f"R²:   {r2_3:.4f}")

"""
Métricas do Modelo 3:
MAE:  46.66
RMSE: 74.85
R²:   0.8691

Aqui eu estou com resultados beem parecidos com os meus anteriores também. Ele está ainda mais próximo da minha análise do baseline dq do modelo com informações de equipamento

A inclusão do cluster comportamental não apresentou ganho significativo em relação à baseline, indicando que, para a previsão de 15 minutos utilizando regressão linear, as variáveis temporais e os históricos recentes já capturam grande parte da informação disponível.
"""


# Modelo 4 - histórico enriquecido
df_modelo_4 = df_reg.dropna(
    subset=[
        "lag_1",
        "lag_4",
        "lag_96",
        "rolling_4",
        "rolling_96",
        "volume_futuro_15min"
    ]
).copy()


features_modelo_4 = [
    "hora",
    "minuto",
    "dia_da_semana",
    "mes",
    "lag_1",
    "lag_4",
    "lag_96",
    "rolling_4",
    "rolling_96"
]

X = df_modelo_4[features_modelo_4]

y = df_modelo_4["volume_futuro_15min"]


# Divisão temporal
treino_4 = df_modelo_4["data_hora"] < data_corte
teste_4 = df_modelo_4["data_hora"] >= data_corte

X_train_4 = X[treino_4]
X_test_4 = X[teste_4]

y_train_4 = y[treino_4]
y_test_4 = y[teste_4]


# Treinar modelo 4
modelo_4 = LinearRegression()

modelo_4.fit(
    X_train_4,
    y_train_4
)

# Previsões do modelo 4
y_pred_4 = modelo_4.predict(
    X_test_4
)

# Métricas do modelo 4
mae_4 = mean_absolute_error(
    y_test_4,
    y_pred_4
)

rmse_4 = mean_squared_error(
    y_test_4,
    y_pred_4
) ** 0.5

r2_4 = r2_score(
    y_test_4,
    y_pred_4
)

print("\nFeatures utilizadas no Modelo 4:")
print(features_modelo_4)

print("\nQuantidade de linhas disponíveis para o Modelo 4:")
print(len(df_modelo_4))

print("\nMétricas do Modelo 4:")
print(f"MAE:  {mae_4:.2f}")
print(f"RMSE: {rmse_4:.2f}")
print(f"R²:   {r2_4:.4f}")

# Modelo 5 - Random Forest
features_rf = [
    "hora",
    "minuto",
    "dia_da_semana",
    "mes",
    "lag_1",
    "lag_4",
    "lag_96",
    "rolling_4",
    "rolling_96"
]

X_rf = df_modelo_4[features_rf]

y_rf = df_modelo_4["volume_futuro_15min"]

treino_rf = (
    df_modelo_4["data_hora"] < data_corte
)

teste_rf = (
    df_modelo_4["data_hora"] >= data_corte
)

X_train_rf = X_rf[treino_rf]
X_test_rf = X_rf[teste_rf]

y_train_rf = y_rf[treino_rf]
y_test_rf = y_rf[teste_rf]


modelo_5 = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

modelo_5.fit(
    X_train_rf,
    y_train_rf
)

y_pred_5 = modelo_5.predict(
    X_test_rf
)

# Métricas
mae_5 = mean_absolute_error(
    y_test_rf,
    y_pred_5
)

rmse_5 = mean_squared_error(
    y_test_rf,
    y_pred_5
) ** 0.5

r2_5 = r2_score(
    y_test_rf,
    y_pred_5
)

print("\nMétricas do Modelo 5 - Random Forest:")
print(f"MAE:  {mae_5:.2f}")
print(f"RMSE: {rmse_5:.2f}")
print(f"R²:   {r2_5:.4f}")

"""
O comportamento temporal recente é muito mais relevante para a previsão de curto prazo do que simplesmente identificar o equipamento ou seu cluster. E, uma vez enriquecidas essas informações temporais, um modelo não linear consegue capturar relações que a Regressão Linear não capturou.

"""

# Checar a importância das features
importancias = pd.DataFrame({
    "feature": features_rf,
    "importancia": modelo_5.feature_importances_
})

importancias = (
    importancias
    .sort_values(
        "importancia",
        ascending=False
    )
    .reset_index(drop=True)
)

print("\nImportância das features - Random Forest:")
print(importancias)

# Bora ver se essa bomba não está em overfitting

y_pred_5_train = modelo_5.predict(
    X_train_rf
)

mae_5_train = mean_absolute_error(
    y_train_rf,
    y_pred_5_train
)

rmse_5_train = mean_squared_error(
    y_train_rf,
    y_pred_5_train
) ** 0.5

r2_5_train = r2_score(
    y_train_rf,
    y_pred_5_train
)


print("\nDesempenho do Modelo 5 - Treino:")
print(f"MAE:  {mae_5_train:.2f}")
print(f"RMSE: {rmse_5_train:.2f}")
print(f"R²:   {r2_5_train:.4f}")


print("\nDesempenho do Modelo 5 - Teste:")
print(f"MAE:  {mae_5:.2f}")
print(f"RMSE: {rmse_5:.2f}")
print(f"R²:   {r2_5:.4f}")

"""
Estou decidida a continuar minhas avalições com o modelo random forest regression. Porém, a partir daqui irei treinar alguns modelos a mais que são, tecnicamente mais modernos apenas para fins de estudo. 
"""

# =========================
# Modelo 6 - HistGradientBoosting
# =========================

from sklearn.ensemble import HistGradientBoostingRegressor

modelo_6 = HistGradientBoostingRegressor(
    max_iter=300,
    learning_rate=0.08,
    max_leaf_nodes=31,
    random_state=42
)

modelo_6.fit(
    X_train_rf,
    y_train_rf
)

# =========================
# Previsões
# =========================

y_pred_6 = modelo_6.predict(
    X_test_rf
)

# =========================
# Métricas
# =========================

mae_6 = mean_absolute_error(
    y_test_rf,
    y_pred_6
)

rmse_6 = mean_squared_error(
    y_test_rf,
    y_pred_6
) ** 0.5

r2_6 = r2_score(
    y_test_rf,
    y_pred_6
)

print("\nMétricas do Modelo 6 - HistGradientBoosting:")
print(f"MAE:  {mae_6:.2f}")
print(f"RMSE: {rmse_6:.2f}")
print(f"R²:   {r2_6:.4f}")

# =========================
# Modelo 7 - XGBoost
# =========================

from xgboost import XGBRegressor

modelo_7 = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

modelo_7.fit(
    X_train_rf,
    y_train_rf
)


# =========================
# Previsões
# =========================

y_pred_7 = modelo_7.predict(
    X_test_rf
)


# =========================
# Métricas
# =========================

mae_7 = mean_absolute_error(
    y_test_rf,
    y_pred_7
)

rmse_7 = mean_squared_error(
    y_test_rf,
    y_pred_7
) ** 0.5

r2_7 = r2_score(
    y_test_rf,
    y_pred_7
)

print("\nMétricas do Modelo 7 - XGBoost:")
print(f"MAE:  {mae_7:.2f}")
print(f"RMSE: {rmse_7:.2f}")
print(f"R²:   {r2_7:.4f}")

# =========================
# Comparação dos modelos
# =========================

comparacao_modelos = pd.DataFrame({
    "modelo": [
        "Linear Regression",
        "Random Forest",
        "HistGradientBoosting",
        "XGBoost"
    ],
    "MAE": [
        mae,
        mae_5,
        mae_6,
        mae_7
    ],
    "RMSE": [
        rmse,
        rmse_5,
        rmse_6,
        rmse_7
    ],
    "R2": [
        r2,
        r2_5,
        r2_6,
        r2_7
    ]
})

print("\nComparação dos modelos:")
print(
    comparacao_modelos
    .sort_values("R2", ascending=False)
    .to_string(index=False)
)

"""
| Modelo               |       MAE |      RMSE |         R² |
| -------------------- | --------: | --------: | ---------: |
| Regressão Linear     |     46,60 |     74,87 |     0,8691 |
| Random Forest        | **32,80** |     58,09 |     0,9212 |
| HistGradientBoosting |     32,92 | **57,83** | **0,9219** |
| XGBoost              |     32,91 | **57,83** | **0,9219** |

A comparação entre os modelos mostrou uma diferença expressiva entre a Regressão Linear e os modelos baseados em árvores. Enquanto a Regressão Linear apresentou R² de 0,8691, Random Forest, HistGradientBoosting e XGBoost alcançaram aproximadamente 0,92. Isso sugere que relações não lineares entre o histórico temporal do tráfego e o volume futuro são relevantes para a previsão de 15 minutos. Entre os modelos de árvores, os resultados foram bastante próximos, sem uma diferença expressiva que justificasse, nesta etapa exploratória, a escolha de um modelo em detrimento dos demais.

"""

# Treinando modelos das próximas métricas, 1h, 1 dia, 1 semana

# Base do modelo de 1 hora
df_modelo_1h = df_reg.copy()

df_modelo_1h["volume_futuro_1h"] = (
    df_15["volume_futuro_1h"].values
)

df_modelo_1h = df_modelo_1h.dropna(
    subset=[
        "lag_1",
        "lag_4",
        "lag_96",
        "rolling_4",
        "rolling_96",
        "volume_futuro_1h"
    ]
).copy()

features_1h = [
    "hora",
    "minuto",
    "dia_da_semana",
    "mes",
    "lag_1",
    "lag_4",
    "lag_96",
    "rolling_4",
    "rolling_96"
]

X_1h = df_modelo_1h[features_1h]

y_1h = df_modelo_1h["volume_futuro_1h"]

# Divisão temporal
treino_1h = (
    df_modelo_1h["data_hora"] < data_corte
)

teste_1h = (
    df_modelo_1h["data_hora"] >= data_corte
)

X_train_1h = X_1h[treino_1h]
X_test_1h = X_1h[teste_1h]

y_train_1h = y_1h[treino_1h]
y_test_1h = y_1h[teste_1h]

print("\nFormato do treino - 1 hora:")
print(X_train_1h.shape)

print("\nFormato do teste - 1 hora:")
print(X_test_1h.shape)

# Random Forest - 1 hora
modelo_1h = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

modelo_1h.fit(
    X_train_1h,
    y_train_1h
)

y_pred_1h = modelo_1h.predict(
    X_test_1h
)

# Métricas - 1 hora
mae_1h = mean_absolute_error(
    y_test_1h,
    y_pred_1h
)

rmse_1h = mean_squared_error(
    y_test_1h,
    y_pred_1h
) ** 0.5

r2_1h = r2_score(
    y_test_1h,
    y_pred_1h
)

print("\nMétricas do Random Forest - 1 hora:")
print(f"MAE:  {mae_1h:.2f}")
print(f"RMSE: {rmse_1h:.2f}")
print(f"R²:   {r2_1h:.4f}")

erro_mae_relativo = (
    mae_1h
    / y_test_1h.mean()
    * 100
)

print(
    f"MAE relativo à média: "
    f"{erro_mae_relativo:.2f}%"
)

print("\nEstatísticas do target de 1 hora:")
print(
    y_1h.describe()
)

y_pred_1h_train = modelo_1h.predict(
    X_train_1h
)

mae_1h_train = mean_absolute_error(
    y_train_1h,
    y_pred_1h_train
)

rmse_1h_train = mean_squared_error(
    y_train_1h,
    y_pred_1h_train
) ** 0.5

r2_1h_train = r2_score(
    y_train_1h,
    y_pred_1h_train
)


print("\nDesempenho do Random Forest - 1 hora - Treino:")
print(f"MAE:  {mae_1h_train:.2f}")
print(f"RMSE: {rmse_1h_train:.2f}")
print(f"R²:   {r2_1h_train:.4f}")

print("\nDesempenho do Random Forest - 1 hora - Teste:")
print(f"MAE:  {mae_1h:.2f}")
print(f"RMSE: {rmse_1h:.2f}")
print(f"R²:   {r2_1h:.4f}")


# Criar target do dia seguinte

df_alvo_dia = df_diario[
    ["equipamento", "data", "volume"]
].copy()

df_alvo_dia["data"] = (
    df_alvo_dia["data"]
    - pd.Timedelta(days=1)
)

df_alvo_dia = df_alvo_dia.rename(
    columns={
        "data": "data_previsao",
        "volume": "volume_futuro_1d"
    }
)

df_diario = df_diario.rename(
    columns={
        "data": "data_previsao"
    }
)

df_diario = df_diario.merge(
    df_alvo_dia,
    on=["equipamento", "data_previsao"],
    how="left"
)


# Remover linhas sem histórico/target

df_modelo_1d = df_diario.dropna(
    subset=[
        "lag_1_dia",
        "lag_7_dias",
        "media_7_dias",
        "volume_futuro_1d"
    ]
).copy()


# Estatísticas do target

print("\nEstatísticas do target - 1 dia:")

print(
    df_modelo_1d[
        "volume_futuro_1d"
    ].describe()
)

# Features

features_1d = [
    "dia_da_semana",
    "mes",
    "lag_1_dia",
    "lag_7_dias",
    "media_7_dias"
]

X_1d = df_modelo_1d[
    features_1d
]

y_1d = df_modelo_1d[
    "volume_futuro_1d"
]


# Divisão temporal

data_corte_1d = pd.Timestamp(
    "2026-05-01"
)

treino_1d = (
    df_modelo_1d["data_previsao"]
    < data_corte_1d
)

teste_1d = (
    df_modelo_1d["data_previsao"]
    >= data_corte_1d
)

X_train_1d = X_1d[treino_1d]
X_test_1d = X_1d[teste_1d]

y_train_1d = y_1d[treino_1d]
y_test_1d = y_1d[teste_1d]


print("\nFormato do treino - 1 dia:")
print(X_train_1d.shape)

print("\nFormato do teste - 1 dia:")
print(X_test_1d.shape)


# Random Forest - 1 dia

modelo_1d = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

modelo_1d.fit(
    X_train_1d,
    y_train_1d
)

# Previsões

y_pred_1d = modelo_1d.predict(
    X_test_1d
)

# Métricas - teste

mae_1d = mean_absolute_error(
    y_test_1d,
    y_pred_1d
)

rmse_1d = mean_squared_error(
    y_test_1d,
    y_pred_1d
) ** 0.5

r2_1d = r2_score(
    y_test_1d,
    y_pred_1d
)

mae_relativo_1d = (
    mae_1d
    / y_test_1d.mean()
    * 100
)


print("\nMétricas do Random Forest - 1 dia:")
print(f"MAE:  {mae_1d:.2f}")
print(f"RMSE: {rmse_1d:.2f}")
print(f"R²:   {r2_1d:.4f}")
print(
    f"MAE relativo à média: "
    f"{mae_relativo_1d:.2f}%"
)

# Diagnóstico de overfitting

y_pred_1d_train = modelo_1d.predict(
    X_train_1d
)

mae_1d_train = mean_absolute_error(
    y_train_1d,
    y_pred_1d_train
)

rmse_1d_train = mean_squared_error(
    y_train_1d,
    y_pred_1d_train
) ** 0.5

r2_1d_train = r2_score(
    y_train_1d,
    y_pred_1d_train
)


print("\nDesempenho do Random Forest - 1 dia - Treino:")
print(f"MAE:  {mae_1d_train:.2f}")
print(f"RMSE: {rmse_1d_train:.2f}")
print(f"R²:   {r2_1d_train:.4f}")

print("\nDesempenho do Random Forest - 1 dia - Teste:")
print(f"MAE:  {mae_1d:.2f}")
print(f"RMSE: {rmse_1d:.2f}")
print(f"R²:   {r2_1d:.4f}")

modelo_1d_ajustado = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    random_state=42,
    n_jobs=-1
)

modelo_1d_ajustado.fit(
    X_train_1d,
    y_train_1d
)

y_pred_1d_ajustado = (
    modelo_1d_ajustado.predict(X_test_1d)
)

mae_1d_ajustado = mean_absolute_error(
    y_test_1d,
    y_pred_1d_ajustado
)

rmse_1d_ajustado = mean_squared_error(
    y_test_1d,
    y_pred_1d_ajustado
) ** 0.5

r2_1d_ajustado = r2_score(
    y_test_1d,
    y_pred_1d_ajustado
)

print("\nRandom Forest 1 dia - max_depth=8:")
print(f"MAE:  {mae_1d_ajustado:.2f}")
print(f"RMSE: {rmse_1d_ajustado:.2f}")
print(f"R²:   {r2_1d_ajustado:.4f}")

y_pred_1d_ajustado_train = (
    modelo_1d_ajustado.predict(X_train_1d)
)

r2_1d_ajustado_train = r2_score(
    y_train_1d,
    y_pred_1d_ajustado_train
)

print(
    f"R² treino: {r2_1d_ajustado_train:.4f}"
)

# =========================
# Modelo - 1 semana
# =========================

# Criar base semanal a partir do volume diário
df_semanal = df_diario.copy()

# Definir semana de segunda a domingo
df_semanal["semana"] = (
    df_semanal["data_previsao"]
    .dt.to_period("W-SUN")
    .apply(lambda x: x.start_time)
)

# Agregar volume por equipamento + semana
df_semanal = (
    df_semanal
    .groupby(
        ["equipamento", "semana"],
        as_index=False
    )["volume"]
    .sum()
)

df_semanal = df_semanal.sort_values(
    ["equipamento", "semana"]
).reset_index(drop=True)


# =========================
# Variáveis temporais
# =========================

df_semanal["semana_do_ano"] = (
    df_semanal["semana"].dt.isocalendar().week.astype(int)
)

df_semanal["mes"] = (
    df_semanal["semana"].dt.month
)


# =========================
# Histórico semanal
# =========================

grupo_semanal = (
    df_semanal
    .groupby("equipamento")["volume"]
)

df_semanal["lag_1_semana"] = (
    grupo_semanal.shift(1)
)

df_semanal["lag_4_semanas"] = (
    grupo_semanal.shift(4)
)

df_semanal["media_4_semanas"] = (
    df_semanal
    .groupby("equipamento")["volume"]
    .transform(
        lambda x: x.shift(1)
        .rolling(4)
        .mean()
    )
)


# =========================
# Criar target da próxima semana
# =========================

df_alvo_semana = df_semanal[
    ["equipamento", "semana", "volume"]
].copy()

df_alvo_semana["semana"] = (
    df_alvo_semana["semana"]
    - pd.Timedelta(days=7)
)

df_alvo_semana = df_alvo_semana.rename(
    columns={
        "semana": "semana_previsao",
        "volume": "volume_futuro_1semana"
    }
)

df_semanal = df_semanal.rename(
    columns={
        "semana": "semana_previsao"
    }
)

df_semanal = df_semanal.merge(
    df_alvo_semana,
    on=[
        "equipamento",
        "semana_previsao"
    ],
    how="left"
)


# =========================
# Manter apenas semanas completas
# =========================

df_modelo_1semana = df_semanal.dropna(
    subset=[
        "lag_1_semana",
        "lag_4_semanas",
        "media_4_semanas",
        "volume_futuro_1semana"
    ]
).copy()


# =========================
# Estatísticas do target
# =========================

print("\nEstatísticas do target - 1 semana:")

print(
    df_modelo_1semana[
        "volume_futuro_1semana"
    ].describe()
)


# =========================
# Features
# =========================

features_1semana = [
    "semana_do_ano",
    "mes",
    "lag_1_semana",
    "lag_4_semanas",
    "media_4_semanas"
]

X_1semana = df_modelo_1semana[
    features_1semana
]

y_1semana = df_modelo_1semana[
    "volume_futuro_1semana"
]


# =========================
# Divisão temporal
# =========================

data_corte_1semana = pd.Timestamp(
    "2026-05-04"
)

treino_1semana = (
    df_modelo_1semana["semana_previsao"]
    < data_corte_1semana
)

teste_1semana = (
    df_modelo_1semana["semana_previsao"]
    >= data_corte_1semana
)

X_train_1semana = X_1semana[
    treino_1semana
]

X_test_1semana = X_1semana[
    teste_1semana
]

y_train_1semana = y_1semana[
    treino_1semana
]

y_test_1semana = y_1semana[
    teste_1semana
]


print("\nFormato do treino - 1 semana:")
print(X_train_1semana.shape)

print("\nFormato do teste - 1 semana:")
print(X_test_1semana.shape)


# =========================
# Random Forest - 1 semana
# =========================

modelo_1semana = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    random_state=42,
    n_jobs=-1
)

modelo_1semana.fit(
    X_train_1semana,
    y_train_1semana
)


# =========================
# Previsões
# =========================

y_pred_1semana = modelo_1semana.predict(
    X_test_1semana
)


# =========================
# Métricas - teste
# =========================

mae_1semana = mean_absolute_error(
    y_test_1semana,
    y_pred_1semana
)

rmse_1semana = mean_squared_error(
    y_test_1semana,
    y_pred_1semana
) ** 0.5

r2_1semana = r2_score(
    y_test_1semana,
    y_pred_1semana
)

mae_relativo_1semana = (
    mae_1semana
    / y_test_1semana.mean()
    * 100
)


print("\nMétricas do Random Forest - 1 semana:")
print(f"MAE:  {mae_1semana:.2f}")
print(f"RMSE: {rmse_1semana:.2f}")
print(f"R²:   {r2_1semana:.4f}")
print(
    f"MAE relativo à média: "
    f"{mae_relativo_1semana:.2f}%"
)


# =========================
# Diagnóstico de overfitting
# =========================

y_pred_1semana_train = (
    modelo_1semana.predict(
        X_train_1semana
    )
)

mae_1semana_train = mean_absolute_error(
    y_train_1semana,
    y_pred_1semana_train
)

rmse_1semana_train = mean_squared_error(
    y_train_1semana,
    y_pred_1semana_train
) ** 0.5

r2_1semana_train = r2_score(
    y_train_1semana,
    y_pred_1semana_train
)


print("\nDesempenho do Random Forest - 1 semana - Treino:")
print(f"MAE:  {mae_1semana_train:.2f}")
print(f"RMSE: {rmse_1semana_train:.2f}")
print(f"R²:   {r2_1semana_train:.4f}")

print("\nDesempenho do Random Forest - 1 semana - Teste:")
print(f"MAE:  {mae_1semana:.2f}")
print(f"RMSE: {rmse_1semana:.2f}")
print(f"R²:   {r2_1semana:.4f}")

"""
E o treino semanal tem somente:
641 observações

O horizonte semanal apresentou a menor capacidade de generalização entre os quatro horizontes avaliados, com R² de 0,5488 e MAE relativo de 18,70%. A forte diferença entre treino (R² = 0,9668) e teste (R² = 0,5488) indica overfitting significativo, associado principalmente à redução da quantidade de observações disponíveis para treinamento.

"""