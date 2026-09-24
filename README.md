# 🚦 Análise de Velocidade das Vias — CTTU Recife

Projeto de **engenharia, análise e modelagem de dados de tráfego** da cidade do Recife, utilizando dados abertos da CTTU e tecnologias como **Python, Pandas, Elasticsearch, Kibana, Docker, Flask e Machine Learning**.

O projeto começou com a construção de um pipeline para exploração, preparação, indexação e consulta dos dados e evoluiu para uma segunda etapa de **aprendizado de máquina**, com:

- **K-Means** para identificar perfis de comportamento entre equipamentos;
- **Random Forest Regressor** para prever volume de veículos;
- **Random Forest Classifier** para classificar o nível do fluxo.

---

## 📌 Pergunta orientadora

> **É possível identificar padrões de comportamento do tráfego e utilizar esses padrões para prever o volume de veículos e classificar o nível do fluxo?**

### Fase 1 — Engenharia e análise de dados

```text
CSV → Pandas/ETL → Elasticsearch → Kibana → Flask → Front-end
```

### Fase 2 — Machine Learning

```text
Dados históricos → Clusterização → Regressão → Classificação
```

As etapas de Machine Learning são analiticamente relacionadas, mas não dependem umas das outras para funcionar.

---

# 1. 📥 Fonte e dados utilizados

O dataset utilizado é o **Velocidade das Vias - Quantitativo por Velocidade Média**, disponibilizado pelo Portal de Dados Abertos do Recife.

Fonte:

http://dados.recife.pe.gov.br/

O conjunto apresenta o quantitativo de veículos por **equipamento, faixa da via e intervalo de 15 minutos**, distribuído em 11 faixas de velocidade média.

### Período analisado

```text
Janeiro/2026 → Junho/2026
```

### Dimensões principais

```text
6 meses
46 equipamentos
4 faixas da via (A, B, C e D)
11 faixas de velocidade
96 intervalos de 15 minutos por dia
2.157.698 registros originais
```

### Faixas de velocidade

```text
0–10 km/h
11–20 km/h
21–30 km/h
31–40 km/h
41–50 km/h
51–60 km/h
61–70 km/h
71–80 km/h
81–90 km/h
91–100 km/h
Acima de 100 km/h
```

> O acesso à base via API não estava disponível durante o desenvolvimento. Por isso, foram utilizados os arquivos CSV disponibilizados pelo portal.

---

# 2. 🗂️ Estrutura atual do projeto

```text
quantitativo_velocidade_media_cttu/
│
├── data/
│   ├── 2026-janeiro-quantitativo-das-vias-por-velocidade-media.csv
│   ├── 2026-fevereiro-quantitativo-das-vias-por-velocidade-media.csv
│   ├── 2026-marco-quantitativo-das-vias-por-velocidade-media.csv
│   ├── 2026-abril-quantitativo-das-vias-por-velocidade-media.csv
│   ├── 2026-maio-quantitativo-das-vias-por-velocidade-media.csv
│   ├── 2026-junho-quantitativo-das-vias-por-velocidade-media.csv
│   ├── dados_clusterizacao_final.csv
│   ├── dados_clusterizacao.csv
│   ├── dados_consolidados.csv
│   ├── dados_final.csv
│   ├── dados_longos.csv
│   └── dados_preparados.csv
│
├── src/
│   ├── src_desenvolvimento/
│   │   ├── carga_teste.py
│   │   ├── conexao_elastic.py
│   │   ├── criar_indice.py
│   │   ├── ingestao.py
│   │   ├── preparacao_final.py
│   │   ├── preparacao.py
│   │   ├── transformacao.py
│   │   └── visualizacao.py
│   │
│   ├── src_exploracao/
│   │   ├── analise_dados.py
│   │   ├── consultas.py
│   │   ├── exploracao.py
│   │   ├── inserir_teste.py
│   │   ├── juntar_datas.py
│   │   └── teste_formato_longo.py
│   │
│   ├── api.py
│   ├── classificacao.py
│   ├── clusterizacao.py
│   └── regressao.py
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

### Organização das pastas

- `src_desenvolvimento/`: scripts de preparação, transformação, indexação e infraestrutura.
- `src_exploracao/`: scripts auxiliares de exploração, consultas e testes.
- `clusterizacao.py`: aprendizado não supervisionado.
- `regressao.py`: previsão do volume.
- `classificacao.py`: classificação do fluxo.
- `api.py`: API Flask.
- `data/`: arquivos originais e datasets derivados.

---

# 3. 🔎 Exploração e preparação dos dados

Os arquivos foram analisados individualmente e depois consolidados com Pandas.

Foram verificados:

- estrutura das colunas;
- tipos de dados;
- valores nulos;
- registros duplicados;
- equipamentos;
- faixas da via;
- horários;
- intervalos de 15 minutos;
- distribuição das velocidades.

### Consolidação

Os seis arquivos foram concatenados em:

```text
data/dados_consolidados.csv
```

Resultado:

```text
2.157.698 registros
18 colunas
```

### Transformação

Foram realizadas, entre outras:

- conversão de datas;
- criação de campo temporal consolidado;
- criação do período analítico;
- agregações;
- transformação `wide → long`;
- criação de `faixa_velocidade` e `quantidade`.

As 11 colunas de velocidade foram transformadas em registros:

```text
2.157.698 × 11
=
23.734.678 registros
```

Os registros com `quantidade = 0` foram mantidos.

---

# 4. 🏖️ Análise descritiva — Férias × Não férias

Foi criada a seguinte regra metodológica:

```text
Férias:
Janeiro, Fevereiro e Junho

Não férias:
Março, Abril e Maio
```

> Essa classificação é uma regra adotada para este estudo e não representa uma classificação oficial fornecida pelo dataset.

O total contabilizado no período foi:

```text
201.201.485 veículos
```

A comparação foi feita principalmente pela **participação relativa das faixas de velocidade**, pois os volumes absolutos dos períodos são diferentes.

A maior diferença observada foi em **41–50 km/h**:

```text
Não férias → 36,47%
Férias     → 37,63%
Diferença  → +1,16 p.p.
```

Essa análise é **descritiva** e não estabelece causalidade.

---

# 5. 🐳 Docker + Elasticsearch + Kibana

A primeira fase construiu a infraestrutura para armazenar e explorar os dados.

### Serviços

```text
Docker Compose
├── Elasticsearch 9.4.4 → localhost:9200
└── Kibana 9.4.4        → localhost:5601
```

Índice criado:

```text
trafego_recife
```

O mapping diferencia campos `keyword`, `integer` e `date`.

### Ingestão

A carga foi realizada via **Bulk API**:

```text
Documentos inseridos: 23.734.678
Erros: 0
```

Validação do total de veículos:

```text
Pandas:          201.201.485
Elasticsearch:   201.201.485
```

---

# 6. 📊 Kibana

O Kibana foi utilizado para exploração visual e construção do dashboard.

Foram analisados, entre outros:

- volume por faixa de velocidade;
- distribuição percentual por período;
- volume por hora;
- comparação entre férias e não férias;
- equipamentos com maior volume.

A maior concentração de veículos ocorreu principalmente nas faixas entre **31 e 50 km/h**.

---

# 7. 🌐 Flask + Front-end

Foi criada uma aplicação web simples para consultar o Elasticsearch.

Arquitetura:

```text
Front-end
   ↓
Flask API
   ↓
Elasticsearch
   ↓
trafego_recife
```

### CRUD

```text
GET     /dados
POST    /dados
PUT     /dados/<id>
DELETE  /dados/<id>
```

Também foram criadas consultas por:

- período;
- velocidade;
- equipamento;
- intervalo de datas;
- filtros combinados.

---

# 8. 🤖 Fase 2 — Machine Learning

Com a base estruturada, o projeto avançou para aprendizado de máquina.

### 01 — Identificar padrões

**Os equipamentos possuem perfis de comportamento semelhantes?**

→ **K-Means**

### 02 — Prever volume

**É possível estimar o número de veículos futuros?**

→ **Random Forest Regressor**

### 03 — Classificar fluxo

**É possível transformar o volume em níveis de fluxo?**

→ **Random Forest Classifier**

---

# 9. 🧩 Clusterização — K-Means

A unidade de análise foi o **equipamento**.

Foram utilizadas as proporções das 11 faixas de velocidade para representar o perfil de cada equipamento.

O volume total foi mantido para interpretação, mas **não foi utilizado como entrada do K-Means**.

### Seleção de K

Foram avaliados diferentes valores utilizando:

- Elbow;
- Silhouette Score;
- interpretação dos perfis.

Resultados principais:

```text
K = 2 → Silhouette = 0,386
K = 4 → Silhouette = 0,358
```

K=2 apresentou o maior Silhouette, mas K=4 foi escolhido como solução analítica por oferecer maior granularidade e produzir perfis interpretáveis.

### Perfis encontrados com K=4

| Cluster | Equipamentos | Perfil predominante |
|---|---:|---|
| C0 | 25 | 31–40 km/h |
| C1 | 2 | 41–50 e 51–60 km/h |
| C2 | 13 | 41–50 km/h |
| C3 | 6 | 21–30 km/h |

O PCA com duas componentes explicou aproximadamente **76,47% da variância acumulada**.

### Observação

A clusterização foi útil para **segmentação e interpretação**, mas apresentou ganho pequeno quando utilizada como variável preditiva.

---

# 10. 📈 Regressão — previsão do volume

A regressão foi estruturada como uma previsão temporal.

### Divisão temporal

```text
Treino → Janeiro a Abril
Teste  → Maio e Junho
```

A divisão não foi aleatória para evitar que informações do futuro influenciassem o treinamento.

### Variáveis

```text
hora
minuto
dia_da_semana
mes
lag_1
lag_4
lag_96
rolling_4
rolling_96
```

### Histórico

```text
lag_1  → 15 minutos antes
lag_4  → aproximadamente 1 hora antes
lag_96 → aproximadamente 24 horas antes
```

As variáveis `rolling` foram calculadas com `shift(1)` para evitar utilização indevida do valor atual.

---

# 11. 📊 Resultados da regressão

### Modelo de referência

```text
Random Forest Regressor
```

### Teste

| Horizonte | MAE | RMSE | R² |
|---|---:|---:|---:|
| 15 minutos | 32,80 | 58,09 | 0,9212 |
| 1 hora | 110,30 | 181,77 | 0,9492 |
| 1 dia | 3.153,06 | 4.598,10 | 0,8286 |
| 1 semana | 28.964,06 | 52.115,25 | 0,5488 |

> O MAE não deve ser comparado isoladamente entre horizontes, porque os alvos estão em escalas diferentes.

### Principal observação

No modelo de 15 minutos, `lag_1` foi a variável mais importante, com importância aproximada de **0,864**.

O histórico imediatamente anterior foi o principal sinal para a previsão do próximo intervalo.

### Generalização

Os horizontes de curto prazo apresentaram melhor desempenho no teste. A previsão semanal apresentou maior dificuldade de generalização.

---

# 12. 🏷️ Classificação do nível de fluxo

A classificação foi realizada diretamente como um problema de três classes.

### Pontos de corte

Os limites foram calculados a partir dos **tercis do target no conjunto de treinamento**:

```text
Baixo  → até 133 veículos
Médio  → acima de 133 até 330 veículos
Alto   → acima de 330 veículos
```

Esses valores:

- não são limites oficiais de trânsito;
- são pontos de corte definidos estatisticamente para este experimento;
- foram calculados somente com os dados de treinamento.

### Distribuição das classes

```text
Baixo   → 34,25%
Médio   → 32,98%
Alto    → 32,77%
```

---

# 13. 🎯 Resultados da classificação

### Modelo principal

```text
Random Forest Classifier
```

### Teste

```text
Accuracy  → 0,9129
Precision → 0,9116
Recall    → 0,9119
F1 macro  → 0,9117
```

A maior parte dos erros ocorreu entre **classes adjacentes**, principalmente entre médio e baixo ou médio e alto.

Os erros entre baixo e alto foram pouco frequentes.

### Teste adicional com cluster

```text
F1 macro sem cluster → 0,9117
F1 macro com cluster → 0,9122
```

O ganho foi pequeno, indicando que o histórico recente do tráfego já concentra grande parte da informação relevante para a classificação de curto prazo.

---

# 14. 🧪 Comparação de modelos

Também foram realizados experimentos adicionais.

### Regressão — 15 minutos

Comparados:

- Linear Regression;
- Random Forest;
- HistGradientBoosting;
- XGBoost.

Os modelos baseados em árvores apresentaram desempenho superior à regressão linear.

### Classificação

Comparados:

- Random Forest;
- Logistic Regression;
- HistGradientBoosting;
- XGBoost.

A regressão logística apresentou desempenho inferior aos modelos baseados em árvores, enquanto os modelos de árvores apresentaram resultados próximos entre si.

Esses testes serviram como **comparação metodológica**, sem ampliar indefinidamente a busca por modelos.

---

# 15. 🔐 Data leakage e cuidados metodológicos

Durante a evolução dos modelos, foi identificado um ponto importante relacionado a **data leakage**.

A primeira clusterização havia sido calculada utilizando janeiro a junho.

Ao usar esse cluster como variável dos modelos supervisionados, informações do período de teste poderiam influenciar a construção do cluster.

### Correção

O K-Means utilizado nos modelos supervisionados foi reconstruído utilizando **somente janeiro a abril**, período de treinamento.

O mesmo cuidado foi aplicado aos pontos de corte da classificação.

### Regra geral

```text
Passado → treinamento
Futuro  → teste
```

---

# 16. 🧠 Principais aprendizados

## Engenharia e análise

- exploração e validação de dados;
- consolidação de múltiplos CSVs;
- transformação `wide → long`;
- criação de variáveis derivadas;
- agregações com Pandas.

## Elasticsearch e aplicação

- definição de mappings;
- tipos `keyword`, `integer` e `date`;
- Bulk API;
- consultas e agregações;
- Kibana;
- API REST com Flask;
- CRUD;
- integração com front-end;
- Docker Compose.

## Machine Learning

- K-Means;
- Elbow e Silhouette;
- StandardScaler;
- PCA;
- feature engineering temporal;
- lags;
- rolling features;
- divisão temporal treino/teste;
- Random Forest Regressor;
- Random Forest Classifier;
- métricas de regressão;
- matriz de confusão;
- Accuracy, Precision, Recall e F1-score;
- identificação e correção de data leakage.

### Principal aprendizado metodológico

> **Construir um modelo não é apenas escolher um algoritmo e observar uma métrica. É necessário estruturar corretamente os dados, respeitar a ordem temporal, evitar vazamento de informação e interpretar o resultado de acordo com o problema.**

---

# 17. ✅ Conclusão

A evolução do projeto transformou uma aplicação inicialmente voltada para **engenharia e análise de dados** em uma solução experimental com **modelagem preditiva**.

### Clusterização

Identificou quatro perfis de comportamento entre os equipamentos.

### Regressão

Permitiu prever o volume de veículos em horizontes de 15 minutos, 1 hora, 1 dia e 1 semana, com melhor desempenho nos horizontes mais curtos.

### Classificação

Permitiu categorizar o fluxo em baixo, médio e alto, com F1 macro próximo de 0,91.

### Síntese

Os experimentos indicaram que o **histórico recente do volume de veículos** é uma fonte importante de informação para previsões de curto prazo, enquanto a clusterização é mais útil para segmentação e interpretação do comportamento dos equipamentos.

---

# 18. ▶️ Como executar

## 1. Clonar o projeto

```bash
git clone https://github.com/sararalopes/quantitativo-velocidade-media-cttu.git
cd quantitativo_velocidade_media_cttu
```

## 2. Criar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## 4. Subir Elasticsearch e Kibana

```bash
docker compose up -d
```

Verificar:

```bash
docker compose ps
```

## 5. Executar a API

```bash
python src/api.py
```

Aplicação:

```text
http://localhost:5000
```

Elasticsearch:

```text
http://localhost:9200
```

Kibana:

```text
http://localhost:5601
```

## 6. Executar os modelos

Clusterização:

```bash
python src/clusterizacao.py
```

Regressão:

```bash
python src/regressao.py
```

Classificação:

```bash
python src/classificacao.py
```

> A execução da modelagem pressupõe que os CSVs necessários estejam disponíveis em `data/` e que o ambiente virtual tenha as dependências instaladas.

---

# 19. 🧪 Exemplos de uso da API

### Listar dados

```bash
curl http://localhost:5000/dados
```

### Buscar por ID

```bash
curl http://localhost:5000/dados/SEU_ID
```

### Consultar período

```bash
curl http://localhost:5000/dados/periodo/ferias
```

### Consultar velocidade

```bash
curl http://localhost:5000/dados/velocidade/41-50
```

### Consultar equipamento

```bash
curl http://localhost:5000/dados/equipamento/CTTU-9466
```

### Consultar intervalo de data

```bash
curl "http://localhost:5000/dados/data?inicio=2026-04-10T22:00:00&fim=2026-04-10T23:00:00"
```

### Consulta combinada

```bash
curl "http://localhost:5000/dados/filtrar?periodo=ferias&velocidade=41-50&equipamento=CTTU-9466"
```

---

# 20. 📎 Resumo dos principais números

```text
Período analisado:              Jan/2026 – Jun/2026
Registros originais:            2.157.698
Equipamentos:                    46
Faixas de velocidade:            11
Faixas da via:                    4
Documentos Elasticsearch:       23.734.678
Veículos contabilizados:       201.201.485

Clusters analisados:              4
R² — 15 min:                  0,9212
R² — 1 hora:                  0,9492
R² — 1 dia:                   0,8286
R² — 1 semana:                0,5488

F1 macro — classificação:       0,9117
```

---

## 👩‍💻 Projeto acadêmico

Projeto desenvolvido como exercício prático de integração entre:

**Engenharia de Dados + Análise de Dados + Elasticsearch + Kibana + APIs + Machine Learning**

Repositório:

https://github.com/sararalopes/quantitativo-velocidade-media-cttu