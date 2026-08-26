from flask import Flask, jsonify, request, render_template
from elasticsearch import Elasticsearch


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

ES_URL = "http://localhost:9200"

INDICE = "trafego_recife"

es = Elasticsearch(ES_URL)

# Rota padrão que abre o front-end da aplicação

@app.route("/", methods=["GET"])
def home():

    return render_template("index.html")


# Aqui eu inicio minhas operações de CRUD. Primero o READ com GET

@app.route("/dados", methods=["GET"])
def listar_dados():

    resposta = es.search(

        index=INDICE,

        size=10

    )

    documentos = []

    for hit in resposta["hits"]["hits"]:

        documentos.append({

            "id": hit["_id"],

            **hit["_source"]

        })

    return jsonify({

        "total": resposta["hits"]["total"]["value"],

        "dados": documentos

    })


@app.route("/dados/<documento_id>", methods=["GET"])
def buscar_dado(documento_id):

    try:

        resposta = es.get(

            index=INDICE,

            id=documento_id

        )

        return jsonify({

            "id": resposta["_id"],

            **resposta["_source"]

        })

    except Exception as erro:

        print("ERRO AO BUSCAR DOCUMENTO:")

        print(erro)

        return jsonify({

            "erro": str(erro)

        }), 500


# Aqui eu faço minha segunda operação de CRUD, o CREATE

@app.route("/dados", methods=["POST"])
def criar_dado():

    documento = request.get_json()

    if not documento:

        return jsonify({

            "erro": "Nenhum dado foi enviado"

        }), 400

    resposta = es.index(

        index=INDICE,

        document=documento

    )

    return jsonify({

        "mensagem": "Documento criado com sucesso",

        "id": resposta["_id"]

    }), 201


# Aqui vou iniciar minha operação de UPDATE, com PUT

@app.route("/dados/<documento_id>", methods=["PUT"])
def atualizar_dado(documento_id):

    documento = request.get_json()

    if not documento:

        return jsonify({

            "erro": "Nenhum dado foi enviado"

        }), 400

    try:

        resposta = es.update(

            index=INDICE,

            id=documento_id,

            doc=documento

        )

        return jsonify({

            "mensagem": "Documento atualizado com sucesso",

            "id": resposta["_id"]

        })

    except Exception as erro:

        print("ERRO AO ATUALIZAR DOCUMENTO:")

        print(erro)

        return jsonify({

            "erro": str(erro)

        }), 404

# Aqui vou iniciar minha operação de DELETE, com DELETE

@app.route("/dados/<documento_id>", methods=["DELETE"])
def deletar_dado(documento_id):

    try:

        resposta = es.delete(

            index=INDICE,

            id=documento_id

        )

        return jsonify({

            "mensagem": "Documento removido com sucesso",

            "id": resposta["_id"]

        })

    except Exception as erro:

        print("ERRO AO REMOVER DOCUMENTO:")

        print(erro)

        return jsonify({

            "erro": str(erro)

        }), 404

# Aqui faço uma consulta específica por período

@app.route("/dados/periodo/<periodo>", methods=["GET"])
def consultar_por_periodo(periodo):

    periodos_validos = ["ferias", "nao_ferias"]

    if periodo not in periodos_validos:

        return jsonify({
            "erro": "Periodo invalido",
            "valores_permitidos": periodos_validos
        }), 400

    consulta = {
        "query": {
            "term": {
                "periodo": periodo
            }
        }
    }

    try:

        resposta = es.search(
            index=INDICE,
            query=consulta["query"],
            size=10
        )

        documentos = []

        for hit in resposta["hits"]["hits"]:

            documentos.append({
                "id": hit["_id"],
                **hit["_source"]
            })

        return jsonify({
            "periodo": periodo,
            "total_documentos": resposta["hits"]["total"]["value"],
            "dados": documentos
        })

    except Exception as erro:

        print("ERRO AO CONSULTAR PERÍODO:")

        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500

# Aqui faço uma consulta específica por faixa de velocidade

@app.route("/dados/velocidade/<faixa>", methods=["GET"])
def consultar_por_velocidade(faixa):

    faixas_validas = [
        "0-10",
        "11-20",
        "21-30",
        "31-40",
        "41-50",
        "51-60",
        "61-70",
        "71-80",
        "81-90",
        "91-100",
        "acima_100"
    ]

    if faixa not in faixas_validas:
        return jsonify({
            "erro": "Faixa de velocidade inválida",
            "valores_permitidos": faixas_validas
        }), 400

    consulta = {
        "query": {
            "term": {
                "faixa_velocidade": faixa
            }
        }
    }

    try:

        resposta = es.search(
            index=INDICE,
            query=consulta["query"],
            size=10
        )

        documentos = []

        for hit in resposta["hits"]["hits"]:

            documentos.append({
                "id": hit["_id"],
                **hit["_source"]
            })

        return jsonify({
            "faixa_velocidade": faixa,
            "total_documentos": resposta["hits"]["total"]["value"],
            "dados": documentos
        })

    except Exception as erro:

        print("ERRO AO CONSULTAR VELOCIDADE:")

        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500

# Aqui faço uma consulta específica por equipamento

@app.route("/dados/equipamento/<equipamento>", methods=["GET"])
def consultar_por_equipamento(equipamento):

    consulta = {
        "query": {
            "term": {
                "equipamento": equipamento
            }
        }
    }

    try:

        resposta = es.search(
            index=INDICE,
            query=consulta["query"],
            size=10
        )

        documentos = []

        for hit in resposta["hits"]["hits"]:

            documentos.append({
                "id": hit["_id"],
                **hit["_source"]
            })

        return jsonify({
            "equipamento": equipamento,
            "total_documentos": resposta["hits"]["total"]["value"],
            "dados": documentos
        })

    except Exception as erro:

        print("ERRO AO CONSULTAR EQUIPAMENTO:")

        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500

# Aqui faço uma consulta por intervalo de datas

@app.route("/dados/data", methods=["GET"])
def consultar_por_data():

    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    if not inicio or not fim:

        return jsonify({
            "erro": "Informe os parâmetros 'inicio' e 'fim'"
        }), 400

    consulta = {
        "query": {
            "range": {
                "data_hora_inicio": {
                    "gte": inicio,
                    "lt": fim
                }
            }
        }
    }

    try:

        resposta = es.search(
            index=INDICE,
            query=consulta["query"],
            size=10
        )

        documentos = []

        for hit in resposta["hits"]["hits"]:

            documentos.append({
                "id": hit["_id"],
                **hit["_source"]
            })

        return jsonify({
            "inicio": inicio,
            "fim": fim,
            "total_documentos": resposta["hits"]["total"]["value"],
            "dados": documentos
        })

    except Exception as erro:

        print("ERRO AO CONSULTAR DATA:")

        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500

# Consulta combinada usando os filtros informados pelo usuário

@app.route("/dados/filtrar", methods=["GET"])
def filtrar_dados():

    filtros = []

    periodo = request.args.get("periodo")
    velocidade = request.args.get("velocidade")
    equipamento = request.args.get("equipamento")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    # Filtro por período
    if periodo:

        if periodo not in ["ferias", "nao_ferias"]:

            return jsonify({
                "erro": "Período inválido"
            }), 400

        filtros.append({
            "term": {
                "periodo": periodo
            }
        })

    # Filtro por velocidade
    if velocidade:

        filtros.append({
            "term": {
                "faixa_velocidade": velocidade
            }
        })

    # Filtro por equipamento
    if equipamento:

        filtros.append({
            "term": {
                "equipamento": equipamento
            }
        })

    # Filtro por data inicial e final
    if inicio or fim:

        intervalo = {}

        if inicio:
            intervalo["gte"] = inicio

        if fim:
            intervalo["lt"] = fim

        filtros.append({
            "range": {
                "data_hora_inicio": intervalo
            }
        })

    # Se nenhum filtro foi informado
    if not filtros:

        return jsonify({
            "erro": "Informe pelo menos um filtro"
        }), 400

    consulta = {
        "query": {
            "bool": {
                "filter": filtros
            }
        }
    }

    try:

        resposta = es.search(
            index=INDICE,
            query=consulta["query"],
            size=10
        )

        documentos = []

        for hit in resposta["hits"]["hits"]:

            documentos.append({
                "id": hit["_id"],
                **hit["_source"]
            })

        return jsonify({
            "total_documentos": resposta["hits"]["total"]["value"],
            "filtros_aplicados": filtros,
            "dados": documentos
        })

    except Exception as erro:

        print("ERRO AO REALIZAR FILTRO COMBINADO:")

        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500

print("\n===== ROTAS REGISTRADAS =====")

for regra in app.url_map.iter_rules():

    print(

        regra,

        regra.methods

    )


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )