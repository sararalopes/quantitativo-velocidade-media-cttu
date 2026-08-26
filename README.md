# 🚦 Análise de Velocidade das Vias — CTTU Recife

Projeto de exploração, preparação, indexação e consulta de dados de tráfego da cidade do Recife, utilizando **Python, Pandas, Elasticsearch, Kibana, Docker e Flask**.

O projeto foi desenvolvido como um exercício prático de **engenharia e análise de dados**, partindo dos arquivos CSV disponibilizados no Portal de Dados Abertos do Recife e chegando a uma aplicação com API REST e interface web para consulta dos dados.

---

## 📌 Objetivo

Analisar o quantitativo de veículos por faixa de velocidade em intervalos de 15 minutos, utilizando dados de janeiro a junho de 2026, com foco na comparação entre dois períodos definidos para este estudo:

- **Férias:** janeiro, fevereiro e junho;
- **Não férias:** março, abril e maio.

O objetivo da comparação é observar se a **distribuição das velocidades dos veículos** apresenta mudanças entre os dois períodos.

> **Importante:** a classificação `ferias` / `nao_ferias` é uma regra metodológica adotada neste projeto para fins de análise. Ela não representa uma classificação oficial fornecida pelo dataset.

---

## 🧰 Tecnologias utilizadas

- **Python 3**
- **Pandas** — exploração, consolidação e preparação dos dados
- **Matplotlib** — exploração visual inicial
- **Elasticsearch 9.4.4** — armazenamento, consultas e agregações
- **Kibana 9.4.4** — visualizações e dashboard
- **Docker / Docker Compose** — ambiente do Elastic Stack
- **Flask** — API REST
- **HTML, CSS e JavaScript** — interface web para consumo da API

---

## 🗂️ Estrutura do projeto

```text
quantitativo_velocidade_media_cttu/
│
├── data/
│   ├── CSVs originais
│   ├── dados_consolidados.csv
│   ├── dados_preparados.csv
│   ├── dados_longos.csv
│   └── dados_final.csv
│
├── src/
│   ├── api.py
│   ├── analise_consolidada.py
│   ├── carga_teste.py
│   ├── conexao_elastic.py
│   ├── consultas.py
│   ├── criar_indice.py
│   ├── exploracao.py
│   ├── ingestao.py
│   ├── inserir_teste.py
│   ├── preparacao.py
│   ├── preparacao_final.py
│   ├── teste_formato_longo.py
│   ├── transformacao.py
│   └── visualizacao.py
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

> Os arquivos de dados intermediários foram mantidos para tornar explícito o fluxo de transformação durante o desenvolvimento. Para um repositório público, arquivos CSV muito grandes não devem ser versionados diretamente.

---

# 1. 📥 Origem e entendimento dos dados

O dataset escolhido apresenta o **quantitativo de veículos por equipamento, faixa da via e intervalo de 15 minutos**, distribuído em diferentes faixas de velocidade.

O dicionário de dados descreve as seguintes faixas:

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

Inicialmente foi planejada uma ingestão via API do Portal de Dados Abertos do Recife. Como o acesso à base via API não estava disponível para o desenvolvimento do projeto, foram utilizados os arquivos CSV disponibilizados.

### Período analisado

Foram utilizados os meses:

```text
Janeiro/2026
Fevereiro/2026
Março/2026
Abril/2026
Maio/2026
Junho/2026
```

---

# 2. 🔎 Exploração inicial

Cada arquivo foi explorado individualmente antes de qualquer transformação.

Foram verificadas:

- quantidade de linhas e colunas;
- nomes das colunas;
- tipos de dados;
- estatísticas descritivas;
- valores nulos;
- registros duplicados;
- quantidade de equipamentos;
- faixas da via;
- horários disponíveis;
- intervalos de 15 minutos;
- comportamento das colunas de velocidade.

### Estrutura encontrada

Cada CSV possui **18 colunas** e as análises iniciais mostraram:

- 46 equipamentos;
- 4 faixas da via: `A`, `B`, `C` e `D`;
- horários de `0` a `23`;
- 96 intervalos de 15 minutos por dia;
- nenhum valor nulo identificado;
- nenhuma linha duplicada identificada.

Alguns campos chegaram inicialmente como texto, mesmo quando representavam datas ou categorias que posteriormente foram mapeadas para tipos mais adequados.

---

# 3. 🧩 Consolidação dos seis meses

Os seis CSVs foram lidos com Pandas e concatenados em um único DataFrame.

Fluxo:

```text
Janeiro ─┐
Fevereiro ┤
Março ────┤
Abril ────┼──> dados_consolidados.csv
Maio ─────┤
Junho ────┘
```

### Resultado

```text
Linhas: 2.157.698
Colunas: 18
```

A distribuição de registros por mês foi:

| Mês | Registros |
|---|---:|
| Janeiro | 360.691 |
| Fevereiro | 341.796 |
| Março | 376.055 |
| Abril | 351.579 |
| Maio | 366.464 |
| Junho | 361.113 |
| **Total** | **2.157.698** |

Durante a consolidação, a quantidade de linhas foi novamente validada e não foram encontrados nulos ou duplicados.

---

# 4. 📊 Exploração do conjunto consolidado

Com o DataFrame completo, foram feitas análises de:

- registros por mês;
- registros por equipamento;
- registros por faixa da via;
- registros por hora;
- total de veículos por faixa de velocidade;
- total de veículos por mês;
- total de veículos por hora.

## Volume por faixa da via

A quantidade de registros por faixa foi:

| Faixa | Registros |
|---|---:|
| A | 758.202 |
| B | 757.906 |
| C | 475.950 |
| D | 165.640 |

Isso mostrou que as faixas A e B possuem significativamente mais registros que C e D, algo que deve ser considerado ao comparar equipamentos apenas por volume bruto de registros.

## Total contabilizado de veículos

Somando as 11 colunas originais de velocidade, foi obtido o total de:

**201.201.485 veículos contabilizados.**

Esse número é diferente do número de registros, pois cada registro representa um intervalo/equipamento/faixa e contém contagens de veículos distribuídas entre as velocidades.

### Distribuição geral por velocidade

| Faixa de velocidade | Veículos |
|---|---:|
| 0–10 km/h | 2.284.854 |
| 11–20 km/h | 9.251.795 |
| 21–30 km/h | 25.599.118 |
| 31–40 km/h | 65.826.186 |
| 41–50 km/h | 74.520.710 |
| 51–60 km/h | 22.826.716 |
| 61–70 km/h | 727.879 |
| 71–80 km/h | 122.102 |
| 81–90 km/h | 31.563 |
| 91–100 km/h | 8.023 |
| Acima de 100 km/h | 2.539 |

### Principal observação exploratória

As faixas **31–60 km/h** concentram a maior parte dos veículos contabilizados, com destaque para a faixa **41–50 km/h**, que possui o maior volume.

As velocidades acima de 80 km/h representam uma parcela muito pequena do total observado.

---

# 5. 📈 Visualização exploratória

Foram criados gráficos em Matplotlib para entender o comportamento antes da indexação.

### Gráficos produzidos

- Total de veículos por mês;
- Total de veículos por hora;
- Total de veículos por faixa de velocidade;
- Distribuição das faixas de velocidade por mês.

## Comportamento por hora

A análise temporal mostrou um padrão claro:

- volumes menores durante a madrugada;
- forte crescimento a partir das primeiras horas da manhã;
- volume elevado durante o dia;
- novo pico no fim da tarde;
- redução progressiva à noite.

A análise horária foi posteriormente reproduzida no Elasticsearch/Kibana.

---

# 6. 🧹 Preparação dos dados

Depois da exploração, iniciou-se a etapa de preparação.

## Conversão da data

A coluna `data`, inicialmente interpretada como texto, foi convertida para um tipo temporal com Pandas.

Também foram verificadas datas inválidas:

```text
Datas inválidas: 0
```

## Criação do período analítico

Foi criada a coluna `periodo` utilizando a regra definida para o estudo:

```python
if mes in [1, 2, 6]:
    return "ferias"

if mes in [3, 4, 5]:
    return "nao_ferias"
```

Resultado:

| Mês | Período |
|---|---|
| Janeiro | Férias |
| Fevereiro | Férias |
| Março | Não férias |
| Abril | Não férias |
| Maio | Não férias |
| Junho | Férias |

---

# 7. 🔄 Transformação para formato longo

O dataset original possuía 11 colunas diferentes para as faixas de velocidade:

```text
qtd_0a10km
qtd_11a20km
qtd_21a30km
...
qtd_acimade100km
```

Para facilitar consultas e agregações no Elasticsearch, essas colunas foram transformadas com `pandas.melt()`.

### Antes

```text
1 linha
├── qtd_0a10km
├── qtd_11a20km
├── qtd_21a30km
├── ...
└── qtd_acimade100km
```

### Depois

```text
1 linha
├── faixa_velocidade
└── quantidade
```

### Resultado

```text
2.157.698 linhas
        ×
11 faixas
        =
23.734.678 linhas
```

O dataset transformado passou a possuir 10 campos principais, antes da criação do campo temporal consolidado.

### Zeros mantidos

Foi tomada a decisão de **manter os registros com `quantidade = 0`**, preservando a informação de que determinada combinação de intervalo/equipamento/faixa de velocidade foi observada com contagem zero.

Resultado:

```text
Registros com quantidade = 0: 15.135.283
Percentual: 63,77%
```

Esse comportamento foi tratado como uma característica do modelo escolhido, e não como erro de dados.

---

# 8. 🕐 Criação do campo temporal consolidado

Foi criado o campo:

```text
data_hora_inicio
```

A partir da combinação entre:

```text
data
+
minutos_intervalo
```

Exemplo:

```text
2026-01-01 + 00:15-00:30
→
2026-01-01T00:15:00
```

Esse campo foi criado para facilitar consultas temporais no Elasticsearch.

O campo foi validado sem valores inválidos:

```text
Datas inválidas: 0
```

A coluna `quantidade` permaneceu numérica (`int64`) e apresentou:

```text
Mínimo: 0
Máximo: 378
```

---

# 9. 🐳 Docker + Elasticsearch + Kibana

Foi criado um ambiente local utilizando Docker Compose com dois serviços:

```text
Docker
├── Elasticsearch 9.4.4 → localhost:9200
└── Kibana 9.4.4        → localhost:5601
```

O ambiente foi configurado como um cluster local de um único nó.

Para simplificar o desenvolvimento local, a segurança do Elasticsearch foi desabilitada no ambiente de estudo. Essa configuração não deve ser utilizada como padrão para produção.

### Validação

O Elasticsearch foi acessado com sucesso em:

```text
http://localhost:9200
```

E o Kibana em:

```text
http://localhost:5601
```

---

# 10. 🔌 Integração Python → Elasticsearch

Foi instalada a biblioteca oficial do cliente Python:

```bash
pip install elasticsearch
```

A conexão foi validada com:

```python
es = Elasticsearch("http://localhost:9200")
es.ping()
```

Resultado:

```text
Conectado: True
```

---

# 11. 🗃️ Índice e Mapping

Foi criado o índice:

```text
trafego_recife
```

### Mapping definido

| Campo | Tipo Elasticsearch |
|---|---|
| `ano` | integer |
| `mes` | integer |
| `equipamento` | keyword |
| `faixa` | keyword |
| `data` | date |
| `hora` | integer |
| `minutos_intervalo` | keyword |
| `periodo` | keyword |
| `faixa_velocidade` | keyword |
| `quantidade` | integer |
| `data_hora_inicio` | date |

A modelagem foi escolhida de forma a diferenciar campos numéricos, temporais e categóricos.

---

# 12. 🚀 Ingestão dos dados

A ingestão foi feita utilizando a API Bulk do Elasticsearch, com leitura do CSV em blocos pelo Pandas.

Foi evitado o envio documento a documento com chamadas individuais, devido ao volume do dataset.

### Resultado final

```text
Documentos esperados: 23.734.678
Documentos inseridos: 23.734.678
Erros: 0
```

Validação posterior pelo `_count`:

```text
23.734.678 documentos
```

O índice foi configurado com `number_of_replicas = 0`, coerente com o ambiente local de um único nó.

O estado do cluster permaneceu `yellow` por causa da ausência de um segundo nó para alocação de réplica, enquanto os shards primários permaneceram ativos.

---

# 13. 🔍 Consultas e agregações no Elasticsearch

Foram desenvolvidas consultas para demonstrar diferentes recursos do Elasticsearch.

### Consultas simples

- `term` para valores exatos (`keyword`);
- `bool + filter` para combinação de condições;
- `range` para intervalos temporais;
- `count` para quantidade de documentos.

### Agregações

- `sum` para somar o campo `quantidade`;
- `terms` para agrupar por categoria;
- agregações aninhadas por `periodo` e `faixa_velocidade`.

### Validação dos resultados

Os valores calculados pelo Pandas foram comparados com agregações no Elasticsearch.

Resultado:

```text
Pandas total de veículos:          201.201.485
Elasticsearch total de veículos:   201.201.485
```

A distribuição por faixa de velocidade também apresentou os mesmos valores nos dois ambientes.

---

# 14. 🏖️ Férias × Não férias

Essa foi a principal análise do projeto.

### Volume total

| Período | Veículos |
|---|---:|
| Férias | 98.280.376 |
| Não férias | 102.921.109 |
| **Total** | **201.201.485** |

Como os volumes totais são diferentes, a comparação foi normalizada em percentual para avaliar a **composição das velocidades**.

### Distribuição percentual

| Faixa | Não férias | Férias | Diferença (p.p.) |
|---|---:|---:|---:|
| 0–10 | 1,23% | 1,04% | -0,19 |
| 11–20 | 4,88% | 4,31% | -0,57 |
| 21–30 | 13,19% | 12,23% | -0,96 |
| 31–40 | 32,76% | 32,67% | -0,09 |
| 41–50 | 36,47% | 37,63% | +1,16 |
| 51–60 | 11,05% | 11,65% | +0,60 |
| 61–70 | 0,34% | 0,38% | +0,04 |
| 71–80 | 0,06% | 0,06% | ~0 |
| 81–90 | 0,01% | 0,02% | +0,01 |
| 91–100 | 0,00% | 0,00% | ~0 |
| Acima de 100 | 0,00% | 0,00% | ~0 |

### Principal observação

No período classificado como férias, houve **maior participação relativa** nas faixas de 41–50 km/h e 51–60 km/h, enquanto as faixas de 11–30 km/h apresentaram menor participação.

A maior diferença observada foi na faixa de **41–50 km/h**, com:

```text
Não férias → 36,47%
Férias     → 37,63%
Diferença  → +1,16 p.p.
```

> Esta é uma análise descritiva dos dados. O projeto não busca estabelecer causalidade nem afirmar que o período de férias, por si só, causou mudanças de comportamento.

---

# 15. 📊 Dashboard no Kibana

Foi criado um dashboard com indicadores e visualizações para apresentação dos resultados.

### KPIs

- **Total de veículos:** 201.201.485
- **Veículos — Férias:** 98.280.376
- **Veículos — Não férias:** 102.921.109
- **Equipamentos monitorados:** 46

### Visualizações produzidas

- Total de veículos por faixa de velocidade;
- Distribuição das faixas de velocidade por período;
- Participação dos períodos por faixa de velocidade (%);
- Distribuição percentual das faixas de velocidade por período;
- Quantidade de veículos por hora e período;
- Top 10 equipamentos por quantidade de veículos.

O intervalo temporal do dashboard foi configurado para abranger todo o período estudado:

```text
31/12/2025 00:00:00
até
01/07/2026 00:00:00
```

O uso do início do dia seguinte como limite superior evita perda de registros do último dia do período.

---

# 16. 🌐 API Flask

A aplicação Flask foi criada para oferecer uma camada de acesso ao Elasticsearch.

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

## CRUD implementado

### Read

```http
GET /dados
GET /dados/<documento_id>
```

### Create

```http
POST /dados
```

### Update

```http
PUT /dados/<documento_id>
```

### Delete

```http
DELETE /dados/<documento_id>
```

## Consultas específicas

```http
GET /dados/periodo/<periodo>
GET /dados/velocidade/<faixa>
GET /dados/equipamento/<equipamento>
GET /dados/data?inicio=...&fim=...
GET /dados/filtrar?...filtros
```

A última rota permite combinar múltiplos filtros, por exemplo:

```text
periodo + velocidade + equipamento + intervalo de datas
```

O Flask monta uma consulta `bool/filter` para o Elasticsearch.

---

# 17. 🖥️ Front-end

Foi criada uma interface web simples utilizando:

- HTML;
- CSS;
- JavaScript;
- Flask/Jinja para servir a página.

A interface permite:

- consultar por período;
- consultar por velocidade;
- consultar por equipamento;
- consultar por data;
- combinar filtros;
- listar dados;
- buscar documento por ID;
- criar documento;
- atualizar documento;
- excluir documento.

O objetivo do front-end é facilitar a demonstração do projeto sem depender exclusivamente do terminal e do `curl` durante a apresentação.

---

# 18. ▶️ Como executar o projeto

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd quantitativo_velocidade_media_cttu
```

## 2. Criar o ambiente virtual

```bash
python3 -m venv .venv
```

Ativar:

```bash
source .venv/bin/activate
```

## 3. Instalar as dependências

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

## 5. Iniciar a API

```bash
python src/api.py
```

A aplicação ficará disponível em:

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

> Para reproduzir a ingestão completa em uma instalação nova, é necessário primeiro preparar os CSVs e criar o índice/mapping. A carga completa foi realizada durante o desenvolvimento e resultou em 23.734.678 documentos.

---

# 19. 🧪 Exemplos de uso da API

## Listar dados

```bash
curl http://localhost:5000/dados
```

## Buscar por ID

```bash
curl http://localhost:5000/dados/SEU_ID
```

## Consultar férias

```bash
curl http://localhost:5000/dados/periodo/ferias
```

## Consultar faixa de velocidade

```bash
curl http://localhost:5000/dados/velocidade/41-50
```

## Consultar equipamento

```bash
curl http://localhost:5000/dados/equipamento/CTTU-9466
```

## Consultar intervalo de data

```bash
curl "http://localhost:5000/dados/data?inicio=2026-04-10T22:00:00&fim=2026-04-10T23:00:00"
```

## Consulta combinada

```bash
curl "http://localhost:5000/dados/filtrar?periodo=ferias&velocidade=41-50&equipamento=CTTU-9466"
```

---

# 20. 🧠 Principais aprendizados

Durante o desenvolvimento foram trabalhados, de forma prática:

- exploração de dados com Pandas;
- validação de qualidade dos dados;
- consolidação de múltiplos arquivos;
- transformação wide → long;
- criação de variáveis derivadas;
- modelagem de dados para Elasticsearch;
- uso de `keyword`, `integer` e `date`;
- ingestão em massa com Bulk API;
- consultas `term`, `range` e `bool/filter`;
- agregações `terms` e `sum`;
- visualização e exploração no Kibana;
- construção de API REST com Flask;
- implementação de CRUD;
- integração entre front-end, Flask e Elasticsearch;
- uso de Docker para infraestrutura local.

---

# 21. 🚧 Próximos passos

O projeto foi mantido propositalmente simples e com foco didático. Algumas melhorias possíveis para uma evolução futura são:

- refatorar a API Flask em módulos separados;
- criar funções auxiliares para reduzir repetição no código;
- adicionar validação mais robusta dos documentos recebidos;
- implementar paginação nos endpoints de consulta;
- criar testes automatizados;
- adicionar tratamento de erros mais específico;
- melhorar a segurança e autenticação da API;
- usar uma estratégia de ingestão mais otimizada para ambientes de produção;
- transformar o dashboard em uma aplicação mais completa;
- separar configurações de desenvolvimento e produção.

---

# 📎 Resumo dos números do projeto

```text
Arquivos analisados:            6 meses
Período:                         Jan/2026 – Jun/2026
Registros originais:            2.157.698
Faixas de velocidade:            11
Equipamentos:                    46
Faixas da via:                   4 (A–D)
Intervalos por dia:             96
Documentos no Elasticsearch:    23.734.678
Veículos contabilizados:        201.201.485
Erros na ingestão:               0
```

---

## 👩‍💻 Projeto desenvolvido para fins acadêmicos

Projeto desenvolvido como exercício prático de integração entre **análise de dados, Elasticsearch, Kibana, Docker e desenvolvimento de APIs com Flask**.
