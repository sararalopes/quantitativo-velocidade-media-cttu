import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

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

df["volume"] = (
    df[colunas_velocidade]
    .sum(axis=1)
)

df["data_hora"] = pd.to_datetime(
    df["data"].astype(str)
    + " "
    + df["minutos_intervalo"].str[:5]
)

df_clf = (
    df.groupby(
        ["equipamento", "data_hora"],
        as_index=False
    )["volume"]
    .sum()
)

df_clf = df_clf.sort_values(
    ["equipamento", "data_hora"]
).reset_index(drop=True)

# Variáveis temporais
df_clf["hora"] = (
    df_clf["data_hora"].dt.hour
)

df_clf["minuto"] = (
    df_clf["data_hora"].dt.minute
)

df_clf["dia_da_semana"] = (
    df_clf["data_hora"].dt.dayofweek
)

df_clf["mes"] = (
    df_clf["data_hora"].dt.month
)

# Histórico
grupo = (
    df_clf
    .groupby("equipamento")["volume"]
)

df_clf["lag_1"] = (
    grupo.shift(1)
)

df_clf["lag_4"] = (
    grupo.shift(4)
)

df_clf["lag_96"] = (
    grupo.shift(96)
)

# Médias móveis
df_clf["rolling_4"] = (
    df_clf
    .groupby("equipamento")["volume"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(4)
        .mean()
    )
)

df_clf["rolling_96"] = (
    df_clf
    .groupby("equipamento")["volume"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(96)
        .mean()
    )
)

#  Alvo de +15 minutos
df_clf["data_hora_futuro"] = (
    df_clf["data_hora"]
    + pd.Timedelta(minutes=15)
)

df_alvo = df_clf[
    [
        "equipamento",
        "data_hora",
        "volume"
    ]
].copy()

df_alvo = df_alvo.rename(
    columns={
        "data_hora":
            "data_hora_futuro",
        "volume":
            "volume_futuro_15min"
    }
)

df_clf = df_clf.merge(
    df_alvo,
    on=[
        "equipamento",
        "data_hora_futuro"
    ],
    how="left"
)

# linhas sem histórico/target

df_clf = df_clf.dropna(
    subset=[
        "lag_1",
        "lag_4",
        "lag_96",
        "rolling_4",
        "rolling_96",
        "volume_futuro_15min"
    ]
).copy()

data_corte = pd.Timestamp(
    "2026-05-01"
)

treino = (
    df_clf["data_hora"] < data_corte
)

teste = (
    df_clf["data_hora"] >= data_corte
)

limite_baixo = (
    df_clf.loc[
        treino,
        "volume_futuro_15min"
    ]
    .quantile(1 / 3)
)

limite_alto = (
    df_clf.loc[
        treino,
        "volume_futuro_15min"
    ]
    .quantile(2 / 3)
)

print("\nLimites das classes:")
print(
    f"Baixo: até {limite_baixo:.2f}"
)

print(
    f"Médio: acima de {limite_baixo:.2f} "
    f"até {limite_alto:.2f}"
)

print(
    f"Alto: acima de {limite_alto:.2f}"
)

def classificar_fluxo(volume):

    if volume <= limite_baixo:
        return "baixo"

    elif volume <= limite_alto:
        return "medio"

    else:
        return "alto"


df_clf["classe_fluxo"] = (
    df_clf["volume_futuro_15min"]
    .apply(classificar_fluxo)
)

print("\nDistribuição das classes:")

print(
    df_clf[
        "classe_fluxo"
    ].value_counts(
        normalize=True
    )
)

# X e y
features = [
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

X = df_clf[features]

y = df_clf["classe_fluxo"]

X_train = X[treino]
X_test = X[teste]

y_train = y[treino]
y_test = y[teste]


print("\nFormato do treino:")
print(X_train.shape)

print("\nFormato do teste:")
print(X_test.shape)

# Random Forest 
modelo_clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

modelo_clf.fit(
    X_train,
    y_train
)

# predict 
y_pred = modelo_clf.predict(
    X_test
)

# Métricas
# =========================
# Métricas
# =========================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    average="macro"
)

recall = recall_score(
    y_test,
    y_pred,
    average="macro"
)

f1 = f1_score(
    y_test,
    y_pred,
    average="macro"
)

print("\nMétricas do Random Forest Classifier:")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nRelatório de classificação:")
print(
    classification_report(
        y_test,
        y_pred,
        digits=4
    )
)

# Matriz de confusao
# fig, ax = plt.subplots(figsize=(7, 6))

# ConfusionMatrixDisplay.from_predictions(
#     y_test,
#     y_pred,
#     labels=[
#         "baixo",
#         "medio",
#         "alto"
#     ],
#     display_labels=[
#         "Baixo",
#         "Médio",
#         "Alto"
#     ],
#     ax=ax
# )

# ax.set_title(
#     "Matriz de Confusão - Random Forest Classifier"
# )

# plt.tight_layout()
# plt.show()

# Avaliação do modelo
y_pred_train = modelo_clf.predict(
    X_train
)

accuracy_train = accuracy_score(
    y_train,
    y_pred_train
)

precision_train = precision_score(
    y_train,
    y_pred_train,
    average="macro"
)

recall_train = recall_score(
    y_train,
    y_pred_train,
    average="macro"
)

f1_train = f1_score(
    y_train,
    y_pred_train,
    average="macro"
)

print("\nMétricas no treino:")
print(f"Accuracy:  {accuracy_train:.4f}")
print(f"Precision: {precision_train:.4f}")
print(f"Recall:    {recall_train:.4f}")
print(f"F1-score:  {f1_train:.4f}")

# Clusterização usando apenas o período de treino

# perfil de velocidade usando janeiro a abril
df_cluster_treino = df[
    df["data_hora"] < data_corte
].copy()


perfil_treino = (
    df_cluster_treino
    .groupby("equipamento")[colunas_velocidade]
    .sum()
    .reset_index()
)


perfil_treino["total_veiculos"] = (
    perfil_treino[colunas_velocidade]
    .sum(axis=1)
)


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

    colunas_percentuais.append(
        nova_coluna
    )


X_cluster = perfil_treino[
    colunas_percentuais
]

scaler_cluster = StandardScaler()

X_cluster_scaled = (
    scaler_cluster.fit_transform(X_cluster)
)


kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

perfil_treino["cluster"] = (
    kmeans.fit_predict(
        X_cluster_scaled
    )
)

mapa_clusters = perfil_treino[
    ["equipamento", "cluster"]
].copy()

df_clf = df_clf.merge(
    mapa_clusters,
    on="equipamento",
    how="left"
)

treino_cluster = (
    df_clf["data_hora"] < data_corte
)

teste_cluster = (
    df_clf["data_hora"] >= data_corte
)

print("\nClusters ausentes:")
print(
    df_clf["cluster"].isnull().sum()
)

# Com cluster
features_numericas = [
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

features_categoricas = [
    "cluster"
]


X_cluster_clf = df_clf[
    features_numericas + features_categoricas
]

y_cluster_clf = df_clf[
    "classe_fluxo"
]

# Treino e teste
X_train_cluster = X_cluster_clf[treino_cluster]
X_test_cluster = X_cluster_clf[teste_cluster]

y_train_cluster = y_cluster_clf[treino_cluster]
y_test_cluster = y_cluster_clf[teste_cluster]

# Pré-processamento
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

# Random Forest
modelo_clf_cluster = Pipeline(
    steps=[
        (
            "preprocessamento",
            preprocessamento_cluster
        ),
        (
            "classificador",
            RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)


modelo_clf_cluster.fit(
    X_train_cluster,
    y_train_cluster
)

# Previsões
y_pred_cluster = (
    modelo_clf_cluster.predict(
        X_test_cluster
    )
)

# Métricas
accuracy_cluster = accuracy_score(
    y_test_cluster,
    y_pred_cluster
)

precision_cluster = precision_score(
    y_test_cluster,
    y_pred_cluster,
    average="macro"
)

recall_cluster = recall_score(
    y_test_cluster,
    y_pred_cluster,
    average="macro"
)

f1_cluster = f1_score(
    y_test_cluster,
    y_pred_cluster,
    average="macro"
)


print("\nMétricas do Random Forest Classifier + Cluster:")
print(
    f"Accuracy:  {accuracy_cluster:.4f}"
)

print(
    f"Precision: {precision_cluster:.4f}"
)

print(
    f"Recall:    {recall_cluster:.4f}"
)

print(
    f"F1-score:  {f1_cluster:.4f}"
)

# Matriz de confusão
# fig, ax = plt.subplots(
#     figsize=(7, 6)
# )

# ConfusionMatrixDisplay.from_predictions(
#     y_test_cluster,
#     y_pred_cluster,
#     labels=[
#         "baixo",
#         "medio",
#         "alto"
#     ],
#     display_labels=[
#         "Baixo",
#         "Médio",
#         "Alto"
#     ],
#     ax=ax
# )

# ax.set_title(
#     "Matriz de Confusão - Random Forest + Cluster"
# )

# plt.tight_layout()
# plt.show()

# A clusterização é útil para descobrir e interpretar perfis de equipamentos, mas o cluster não acrescentou informação relevante para os modelos supervisionados mais uma vez

# Avaliação no treino
y_pred_cluster_train = (
    modelo_clf_cluster.predict(
        X_train_cluster
    )
)

accuracy_cluster_train = (
    accuracy_score(
        y_train_cluster,
        y_pred_cluster_train
    )
)

precision_cluster_train = (
    precision_score(
        y_train_cluster,
        y_pred_cluster_train,
        average="macro"
    )
)

recall_cluster_train = (
    recall_score(
        y_train_cluster,
        y_pred_cluster_train,
        average="macro"
    )
)

f1_cluster_train = (
    f1_score(
        y_train_cluster,
        y_pred_cluster_train,
        average="macro"
    )
)


print("\nMétricas do Classificador + Cluster - Treino:")
print(f"Accuracy:  {accuracy_cluster_train:.4f}")
print(f"Precision: {precision_cluster_train:.4f}")
print(f"Recall:    {recall_cluster_train:.4f}")
print(f"F1-score:  {f1_cluster_train:.4f}")

# =========================
# Classificador 3 - Logistic Regression
# =========================

features_logistica = [
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

X_logistica = df_clf[
    features_logistica
]

y_logistica = df_clf[
    "classe_fluxo"
]


# =========================
# Divisão temporal
# =========================

treino_log = (
    df_clf["data_hora"] < data_corte
)

teste_log = (
    df_clf["data_hora"] >= data_corte
)

X_train_log = X_logistica[treino_log]
X_test_log = X_logistica[teste_log]

y_train_log = y_logistica[treino_log]
y_test_log = y_logistica[teste_log]


# =========================
# Padronização
# =========================

scaler_log = StandardScaler()

X_train_log_scaled = scaler_log.fit_transform(
    X_train_log
)

X_test_log_scaled = scaler_log.transform(
    X_test_log
)


# =========================
# Logistic Regression
# =========================

modelo_log = LogisticRegression(
    max_iter=1000,
    solver="lbfgs",
    random_state=42
)

modelo_log.fit(
    X_train_log_scaled,
    y_train_log
)


# =========================
# Previsões
# =========================

y_pred_log = modelo_log.predict(
    X_test_log_scaled
)


# =========================
# Métricas
# =========================

accuracy_log = accuracy_score(
    y_test_log,
    y_pred_log
)

precision_log = precision_score(
    y_test_log,
    y_pred_log,
    average="macro"
)

recall_log = recall_score(
    y_test_log,
    y_pred_log,
    average="macro"
)

f1_log = f1_score(
    y_test_log,
    y_pred_log,
    average="macro"
)


print("\nMétricas da Logistic Regression:")
print(f"Accuracy:  {accuracy_log:.4f}")
print(f"Precision: {precision_log:.4f}")
print(f"Recall:    {recall_log:.4f}")
print(f"F1-score:  {f1_log:.4f}")

# =========================
# Matriz de confusão
# =========================

# fig, ax = plt.subplots(
#     figsize=(7, 6)
# )

# ConfusionMatrixDisplay.from_predictions(
#     y_test_log,
#     y_pred_log,
#     labels=[
#         "baixo",
#         "medio",
#         "alto"
#     ],
#     display_labels=[
#         "Baixo",
#         "Médio",
#         "Alto"
#     ],
#     ax=ax
# )

# ax.set_title(
#     "Matriz de Confusão - Logistic Regression"
# )

# plt.tight_layout()
# plt.show()

# =========================
# Avaliação no treino
# =========================

y_pred_log_train = modelo_log.predict(
    X_train_log_scaled
)

accuracy_log_train = accuracy_score(
    y_train_log,
    y_pred_log_train
)

precision_log_train = precision_score(
    y_train_log,
    y_pred_log_train,
    average="macro"
)

recall_log_train = recall_score(
    y_train_log,
    y_pred_log_train,
    average="macro"
)

f1_log_train = f1_score(
    y_train_log,
    y_pred_log_train,
    average="macro"
)

print("\nMétricas da Logistic Regression - Treino:")
print(f"Accuracy:  {accuracy_log_train:.4f}")
print(f"Precision: {precision_log_train:.4f}")
print(f"Recall:    {recall_log_train:.4f}")
print(f"F1-score:  {f1_log_train:.4f}")

# =========================
# Classificador 4 - HistGradientBoosting
# =========================

features_hgb = [
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

X_hgb = df_clf[
    features_hgb
]

y_hgb = df_clf[
    "classe_fluxo"
]


# =========================
# Divisão temporal
# =========================

treino_hgb = (
    df_clf["data_hora"] < data_corte
)

teste_hgb = (
    df_clf["data_hora"] >= data_corte
)

X_train_hgb = X_hgb[treino_hgb]
X_test_hgb = X_hgb[teste_hgb]

y_train_hgb = y_hgb[treino_hgb]
y_test_hgb = y_hgb[teste_hgb]


# =========================
# HistGradientBoosting
# =========================

modelo_hgb = HistGradientBoostingClassifier(
    max_iter=300,
    learning_rate=0.08,
    max_leaf_nodes=31,
    random_state=42
)

modelo_hgb.fit(
    X_train_hgb,
    y_train_hgb
)


# =========================
# Previsões
# =========================

y_pred_hgb = modelo_hgb.predict(
    X_test_hgb
)


# =========================
# Métricas
# =========================

accuracy_hgb = accuracy_score(
    y_test_hgb,
    y_pred_hgb
)

precision_hgb = precision_score(
    y_test_hgb,
    y_pred_hgb,
    average="macro"
)

recall_hgb = recall_score(
    y_test_hgb,
    y_pred_hgb,
    average="macro"
)

f1_hgb = f1_score(
    y_test_hgb,
    y_pred_hgb,
    average="macro"
)

print("\nMétricas do HistGradientBoosting:")
print(f"Accuracy:  {accuracy_hgb:.4f}")
print(f"Precision: {precision_hgb:.4f}")
print(f"Recall:    {recall_hgb:.4f}")
print(f"F1-score:  {f1_hgb:.4f}")

# =========================
# Classificador 5 - XGBoost
# =========================

features_xgb = [
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

X_xgb = df_clf[
    features_xgb
]

y_xgb = df_clf[
    "classe_fluxo"
]


# =========================
# Codificar classes
# =========================

encoder_classes = LabelEncoder()

y_xgb_encoded = encoder_classes.fit_transform(
    y_xgb
)


# =========================
# Divisão temporal
# =========================

treino_xgb = (
    df_clf["data_hora"] < data_corte
)

teste_xgb = (
    df_clf["data_hora"] >= data_corte
)

X_train_xgb = X_xgb[treino_xgb]
X_test_xgb = X_xgb[teste_xgb]

y_train_xgb = y_xgb_encoded[treino_xgb]
y_test_xgb = y_xgb_encoded[teste_xgb]


# =========================
# XGBoost
# =========================

modelo_xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=3,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

modelo_xgb.fit(
    X_train_xgb,
    y_train_xgb
)


# =========================
# Previsões
# =========================

y_pred_xgb_encoded = modelo_xgb.predict(
    X_test_xgb
)

y_pred_xgb = encoder_classes.inverse_transform(
    y_pred_xgb_encoded
)

y_test_xgb_original = (
    encoder_classes.inverse_transform(
        y_test_xgb
    )
)


# =========================
# Métricas
# =========================

accuracy_xgb = accuracy_score(
    y_test_xgb_original,
    y_pred_xgb
)

precision_xgb = precision_score(
    y_test_xgb_original,
    y_pred_xgb,
    average="macro"
)

recall_xgb = recall_score(
    y_test_xgb_original,
    y_pred_xgb,
    average="macro"
)

f1_xgb = f1_score(
    y_test_xgb_original,
    y_pred_xgb,
    average="macro"
)

print("\nMétricas do XGBoost:")
print(f"Accuracy:  {accuracy_xgb:.4f}")
print(f"Precision: {precision_xgb:.4f}")
print(f"Recall:    {recall_xgb:.4f}")
print(f"F1-score:  {f1_xgb:.4f}")

# =========================
# Comparação dos classificadores
# =========================

comparacao_classificadores = pd.DataFrame({
    "modelo": [
        "Random Forest",
        "Random Forest + Cluster",
        "Logistic Regression",
        "HistGradientBoosting",
        "XGBoost"
    ],
    "accuracy": [
        accuracy,
        accuracy_cluster,
        accuracy_log,
        accuracy_hgb,
        accuracy_xgb
    ],
    "precision": [
        precision,
        precision_cluster,
        precision_log,
        precision_hgb,
        precision_xgb
    ],
    "recall": [
        recall,
        recall_cluster,
        recall_log,
        recall_hgb,
        recall_xgb
    ],
    "f1": [
        f1,
        f1_cluster,
        f1_log,
        f1_hgb,
        f1_xgb
    ]
})

print("\nComparação dos classificadores:")
print(
    comparacao_classificadores
    .sort_values(
        "f1",
        ascending=False
    )
    .to_string(index=False)
)

# HistGradientBoosting apresentou o melhor desempenho entre os modelos avaliados, porém com diferença mínima em relação ao Random Forest e ao XGBoost.

"""

Comparação dos classificadores:
                 modelo  accuracy  precision   recall       f1
   HistGradientBoosting  0.913876   0.912490 0.912921 0.912653
Random Forest + Cluster  0.913334   0.912099 0.912380 0.912209
                XGBoost  0.913326   0.912008 0.912325 0.912138
          Random Forest  0.912861   0.911552 0.911888 0.911685
    Logistic Regression  0.877085   0.876844 0.874715 0.875406

"""
