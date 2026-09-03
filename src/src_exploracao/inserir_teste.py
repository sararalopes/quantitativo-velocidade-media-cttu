from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# Seguindo os padrões do meu dataset, estou criando um doc novo só para testar se ta dando bom antes de subir minha base
documento = {
    "ano": 2026,
    "mes": 1,
    "equipamento": "CTTU-9111",
    "faixa": "A",
    "data": "2026-01-01",
    "hora": 0,
    "minutos_intervalo": "00:00-00:15",
    "periodo": "ferias",
    "faixa_velocidade": "31-40",
    "quantidade": 16,
    "data_hora_inicio": "2026-01-01T00:00:00"
}

resposta = es.index(
    index="trafego_recife",
    document=documento
)


print("Documento inserido:")
print(resposta)