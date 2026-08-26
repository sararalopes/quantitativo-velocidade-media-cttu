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