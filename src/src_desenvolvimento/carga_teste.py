# Como eu tenho uma base muito grande, quero checar se está dando certinho mandando uma pequena ingestão antes

import pandas as pd

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

ARQUIVO = "data/dados_final.csv"
INDICE = "trafego_recife"
LIMITE = 2000

es = Elasticsearch("http://localhost:9200")

df = pd.read_csv(
    ARQUIVO,
    nrows=LIMITE
)


print(f"Registros carregados: {len(df)}")

# ISso aqui é a criação de um bulk. Um jeito de mandar grandes quantidades de dados para o elastic
def gerar_documentos(dataframe):

    for _, linha in dataframe.iterrows():

        documento = {
            "ano": int(linha["ano"]),
            "mes": int(linha["mes"]),
            "equipamento": linha["equipamento"],
            "faixa": linha["faixa"],
            "data": linha["data"],
            "hora": int(linha["hora"]),
            "minutos_intervalo": linha["minutos_intervalo"],
            "periodo": linha["periodo"],
            "faixa_velocidade": linha["faixa_velocidade"],
            "quantidade": int(linha["quantidade"]),
            "data_hora_inicio": linha["data_hora_inicio"],
        }

        yield {
            "_index": INDICE,
            "_source": documento
        }


sucessos, erros = bulk(
    es,
    gerar_documentos(df),
    chunk_size=500,
    raise_on_error=False
)

print(f"Documentos enviados com sucesso: {sucessos}")
print(f"Erros: {len(erros)}")


if erros:
    print("="* 10)
    print("PRIMEIRO ERRO")

    print(erros[0])