from elasticsearch import Elasticsearch


es = Elasticsearch("http://localhost:9200")


print("Conectado:", es.ping())

print("\nInformações do Elasticsearch:")
print(es.info())