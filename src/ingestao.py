import time

import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk


ARQUIVO = "data/dados_final.csv"
INDICE = "trafego_recife"

# Quantidade de linhas lidas pelo Pandas de cada vez
CHUNK_SIZE = 10_000

# Quantidade de documentos enviados por operação Bulk
BULK_CHUNK_SIZE = 1_000


es = Elasticsearch("http://localhost:9200", request_timeout=120)

print("Preparando índice para ingestão...")

es.indices.put_settings(
    index=INDICE,
    settings={
        "refresh_interval": "-1",
        "number_of_replicas": 0
    }
)

def gerar_documentos():

    for df in pd.read_csv(
        ARQUIVO,
        chunksize=CHUNK_SIZE
    ):

        for linha in df.itertuples(index=False):

            documento = {
                "ano": int(linha.ano),
                "mes": int(linha.mes),
                "equipamento": linha.equipamento,
                "faixa": linha.faixa,
                "data": linha.data,
                "hora": int(linha.hora),
                "minutos_intervalo": linha.minutos_intervalo,
                "periodo": linha.periodo,
                "faixa_velocidade": linha.faixa_velocidade,
                "quantidade": int(linha.quantidade),
                "data_hora_inicio": linha.data_hora_inicio,
            }

            yield {
                "_index": INDICE,
                "_source": documento
            }

print("Iniciando ingestão...")
print(f"Arquivo: {ARQUIVO}")
print(f"Chunk Pandas: {CHUNK_SIZE}")
print(f"Bulk chunk: {BULK_CHUNK_SIZE}")

inicio = time.time()

sucessos = 0
erros = 0


for sucesso, informacao in streaming_bulk(
    es,
    gerar_documentos(),
    chunk_size=BULK_CHUNK_SIZE,
    max_retries=3,
    raise_on_error=False
):

    if sucesso:
        sucessos += 1

    else:
        erros += 1

    total_processado = sucessos + erros

    if total_processado % 100_000 == 0:

        tempo = time.time() - inicio

        print(
            f"Processados: {total_processado:,} | "
            f"Sucesso: {sucessos:,} | "
            f"Erros: {erros:,} | "
            f"Tempo: {tempo / 60:.2f} min"
        )


tempo_total = time.time() - inicio

print(f"Sucessos: {sucessos:,}")
print(f"Erros: {erros:,}")
print(f"Tempo total: {tempo_total / 60:.2f} minutos")

print("\nRestaurando configurações do índice...")

es.indices.put_settings(
    index=INDICE,
    settings={
        "refresh_interval": "1s",
        "number_of_replicas": 0
    }
)

print("Configurações restauradas.")