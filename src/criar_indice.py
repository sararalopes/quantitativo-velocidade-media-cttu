from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

nome_indice = "trafego_recife"

# Apesar do treinamento não chegar a ensinar mapping, com a ajuda do chat estou fazendo o mapping dos meus dados
mapping = {
    "mappings": {
        "properties": {
            "ano": {
                "type": "integer"
            },
            "mes": {
                "type": "integer"
            },
            "equipamento": {
                "type": "keyword"
            },
            "faixa": {
                "type": "keyword"
            },
            "data": {
                "type": "date"
            },
            "hora": {
                "type": "integer"
            },
            "minutos_intervalo": {
                "type": "keyword"
            },
            "periodo": {
                "type": "keyword"
            },
            "faixa_velocidade": {
                "type": "keyword"
            },
            "quantidade": {
                "type": "integer"
            },
            "data_hora_inicio": {
                "type": "date"
            }
        }
    }
}

if es.indices.exists(index=nome_indice):
    print(f"O indíce '{nome_indice} já existe'")
else:
    resposta = es.indices.create(
        index=nome_indice,
        body=mapping
    )

print("Indice criado:")
print(resposta)
















