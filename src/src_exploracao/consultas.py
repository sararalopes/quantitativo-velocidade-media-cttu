from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# Quantos documentos pertencem ao período ferias?

INDICE = "trafego_recife"

consulta = {
    "query": {
        "term": {
            "periodo": "ferias"
        }
    }
}


resposta = es.count(
    index=INDICE,
    query=consulta["query"]
)


print("Documentos no período de férias:")
print(resposta["count"])

consulta = {
    "query": {
        "term": {
            "faixa_velocidade": "41-50"
        }
    }
}

# Quantos documentos pertencem a faixa de 41-50 km/h?

resposta = es.count(
    index=INDICE,
    query=consulta["query"]
)


print("\nDocumentos na faixa 41-50 km/h:")
print(resposta["count"])

# Quantos documentos são de férias e estão na faixa 41–50 km/h?

consulta = {
    "query": {
        "bool": {
            "filter": [
                {
                    "term": {
                        "periodo": "ferias"
                    }
                },
                {
                    "term": {
                        "faixa_velocidade": "41-50"
                    }
                }
            ]
        }
    }
}


resposta = es.count(
    index=INDICE,
    query=consulta["query"]
)


print("\nFérias + faixa 41-50 km/h:")
print(resposta["count"])

# Quantos documentos estão no dia 1º de janeiro entre 00:00 e 01:00?

consulta = {
    "query": {
        "range": {
            "data_hora_inicio": {
                "gte": "2026-01-01T00:00:00",
                "lt": "2026-01-01T01:00:00"
            }
        }
    }
}


resposta = es.count(
    index=INDICE,
    query=consulta["query"]
)


print("\nDocumentos entre 00:00 e 01:00:")
print(resposta["count"])

# Farei minha primeira consulta de agregação. Estou usando a faixa de 0-10 pois é a que foi inserida nos 2k de doc
consulta = {
    "size": 0,
    "query": {
        "term": {
            "faixa_velocidade": "0-10"
        }
    },
    "aggs": {
        "total_veiculos": {
            "sum": {
                "field": "quantidade"
            }
        }
    }
}

resposta = es.search(
    index=INDICE,
    body=consulta
)

print(f"\nQual é a soma de veículos para essa faixa de velocidade?", resposta["aggregations"]["total_veiculos"]["value"], "\n")

# Total de veículos por faixa de velocidade

consulta = {
    "size": 0,
    "aggs": {
        "veiculos_por_velocidade": {
            "terms": {
                "field": "faixa_velocidade",
                "size": 20
            },
            "aggs": {
                "total_veiculos": {
                    "sum": {
                        "field": "quantidade"
                    }
                }
            }
        }
    }
}


resposta = es.search(
    index=INDICE,
    body=consulta
)


buckets = resposta["aggregations"]["veiculos_por_velocidade"]["buckets"]


for bucket in buckets:
    faixa = bucket["key"]
    total = bucket["total_veiculos"]["value"]

    print(f"{faixa:>10} km/h → {total:,.0f}")

# Total de veiculos

consulta = {
    "size": 0,
    "aggs": {
        "total_veiculos": {
            "sum": {
                "field": "quantidade"
            }
        }
    }
}

resposta = es.search(
    index=INDICE,
    body=consulta
)

total = resposta["aggregations"]["total_veiculos"]["value"]

print(f"\nTotal de veículos: {total:,.0f}")

# Como os veículos se distribuem entre as faixas de velocidade em cada período?

consulta = {
    "size": 0,
    "aggs": {
        "por_periodo": {
            "terms": {
                "field": "periodo",
                "size": 2
            },
            "aggs": {
                "por_velocidade": {
                    "terms": {
                        "field": "faixa_velocidade",
                        "size": 20
                    },
                    "aggs": {
                        "total_veiculos": {
                            "sum": {
                                "field": "quantidade"
                            }
                        }
                    }
                }
            }
        }
    }
}


resposta = es.search(
    index=INDICE,
    body=consulta
)


for periodo in resposta["aggregations"]["por_periodo"]["buckets"]:

    nome_periodo = periodo["key"]

    buckets = periodo["por_velocidade"]["buckets"]

    total_periodo = sum(
        bucket["total_veiculos"]["value"]
        for bucket in buckets
    )

    print(f"\n--- {nome_periodo.upper()} ---")

    print(f"Total de veículos: {total_periodo:,.0f}\n")

    for velocidade in buckets:

        faixa = velocidade["key"]

        total = velocidade["total_veiculos"]["value"]

        percentual = (
            total / total_periodo * 100
        )

        print(
            f"{faixa:>10} km/h → "
            f"{total:,.0f} veículos "
            f"({percentual:.2f}%)"
        )

"""

--- NAO_FERIAS ---
Total de veículos: 102,921,109

      0-10 km/h → 1,265,690 veículos (1.23%)
     11-20 km/h → 5,019,149 veículos (4.88%)
     21-30 km/h → 13,578,394 veículos (13.19%)
     31-40 km/h → 33,713,431 veículos (32.76%)
     41-50 km/h → 37,538,471 veículos (36.47%)
     51-60 km/h → 11,375,619 veículos (11.05%)
     61-70 km/h → 351,612 veículos (0.34%)
     71-80 km/h → 58,545 veículos (0.06%)
     81-90 km/h → 15,181 veículos (0.01%)
    91-100 km/h → 3,810 veículos (0.00%)
 acima_100 km/h → 1,207 veículos (0.00%)

--- FERIAS ---
Total de veículos: 98,280,376

      0-10 km/h → 1,019,164 veículos (1.04%)
     11-20 km/h → 4,232,646 veículos (4.31%)
     21-30 km/h → 12,020,724 veículos (12.23%)
     31-40 km/h → 32,112,755 veículos (32.67%)
     41-50 km/h → 36,982,239 veículos (37.63%)
     51-60 km/h → 11,451,097 veículos (11.65%)
     61-70 km/h → 376,267 veículos (0.38%)
     71-80 km/h → 63,557 veículos (0.06%)
     81-90 km/h → 16,382 veículos (0.02%)
    91-100 km/h → 4,213 veículos (0.00%)
 acima_100 km/h → 1,332 veículos (0.00%)

"""

# Na distribuição observada, o período classificado como férias apresentou maior participação relativa de veículos nas faixas de 41–50 km/h e 51–60 km/h, enquanto as faixas de 11–30 km/h apresentaram menor participação em comparação ao período não férias.