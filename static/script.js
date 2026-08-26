const API = "";


// ==========================================
// VERIFICAR API
// ==========================================

async function verificarAPI() {

    try {

        const resposta = await fetch("/");

        if (resposta.ok) {

            document.getElementById("status").textContent =
                "API online";

        } else {

            document.getElementById("status").textContent =
                "API com erro";
        }

    } catch (erro) {

        document.getElementById("status").textContent =
            "API offline";
    }
}


// ==========================================
// MOSTRAR RESULTADOS
// ==========================================

function mostrarResultados(dados) {

    const container =
        document.getElementById("resultados");

    const contador =
        document.getElementById("resultado-contador");


    if (!dados || dados.length === 0) {

        container.innerHTML =
            `<p class="empty">
                Nenhum documento encontrado.
            </p>`;

        contador.textContent = "0 resultados";

        return;
    }


    contador.textContent =
        `${dados.length} resultados exibidos`;


    const colunas = Object.keys(dados[0]);


    let html = "<table><thead><tr>";


    for (const coluna of colunas) {

        html += `<th>${coluna}</th>`;
    }


    html += "</tr></thead><tbody>";


    for (const documento of dados) {

        html += "<tr>";


        for (const coluna of colunas) {

            html += `<td>${documento[coluna] ?? ""}</td>`;
        }


        html += "</tr>";
    }


    html += "</tbody></table>";


    container.innerHTML = html;
}


// ==========================================
// LISTAR DADOS
// ==========================================

async function listarDados() {

    const resposta =
        await fetch("/dados");

    const resultado =
        await resposta.json();


    mostrarResultados(resultado.dados);
}


// ==========================================
// BUSCAR POR ID
// ==========================================

async function buscarPorId() {

    const id =
        document.getElementById("documento-id").value.trim();


    if (!id) {

        alert("Informe um ID.");

        return;
    }


    const resposta =
        await fetch(`/dados/${id}`);


    const resultado =
        await resposta.json();


    if (!resposta.ok) {

        alert(resultado.erro || "Documento não encontrado.");

        return;
    }


    mostrarResultados([resultado]);
}


// ==========================================
// CONSULTAR PERÍODO
// ==========================================

async function consultarPeriodo() {

    const periodo =
        document.getElementById("periodo").value;


    if (!periodo) {

        alert("Selecione um período.");

        return;
    }


    const resposta =
        await fetch(`/dados/periodo/${periodo}`);


    const resultado =
        await resposta.json();


    mostrarResultados(resultado.dados);
}


// ==========================================
// CONSULTAR VELOCIDADE
// ==========================================

async function consultarVelocidade() {

    const velocidade =
        document.getElementById("velocidade").value;


    if (!velocidade) {

        alert("Selecione uma faixa de velocidade.");

        return;
    }


    const resposta =
        await fetch(`/dados/velocidade/${velocidade}`);


    const resultado =
        await resposta.json();


    mostrarResultados(resultado.dados);
}


// ==========================================
// CONSULTAR EQUIPAMENTO
// ==========================================

async function consultarEquipamento() {

    const equipamento =
        document.getElementById("equipamento").value.trim();


    if (!equipamento) {

        alert("Informe um equipamento.");

        return;
    }


    const resposta =
        await fetch(`/dados/equipamento/${equipamento}`);


    const resultado =
        await resposta.json();


    mostrarResultados(resultado.dados);
}


// ==========================================
// CONSULTAR DATA
// ==========================================

async function consultarData() {

    const inicio =
        document.getElementById("data-inicio").value;

    const fim =
        document.getElementById("data-fim").value;


    if (!inicio || !fim) {

        alert("Informe as duas datas.");

        return;
    }


    const inicioFormatado =
        inicio + ":00";


    const fimFormatado =
        fim + ":00";


    const url =
        `/dados/data?inicio=${encodeURIComponent(inicioFormatado)}&fim=${encodeURIComponent(fimFormatado)}`;


    const resposta =
        await fetch(url);


    const resultado =
        await resposta.json();


    mostrarResultados(resultado.dados);
}

// ==========================================
// FILTRO COMBINADO
// ==========================================

async function filtrarDados() {

    const periodo =
        document.getElementById("periodo").value;

    const velocidade =
        document.getElementById("velocidade").value;

    const equipamento =
        document.getElementById("equipamento").value.trim();

    const inicio =
        document.getElementById("data-inicio").value;

    const fim =
        document.getElementById("data-fim").value;


    const parametros = new URLSearchParams();


    // Período

    if (periodo) {

        parametros.append(
            "periodo",
            periodo
        );

    }


    // Velocidade

    if (velocidade) {

        parametros.append(
            "velocidade",
            velocidade
        );

    }


    // Equipamento

    if (equipamento) {

        parametros.append(
            "equipamento",
            equipamento
        );

    }


    // Data inicial

    if (inicio) {

        parametros.append(
            "inicio",
            inicio + ":00"
        );

    }


    // Data final

    if (fim) {

        parametros.append(
            "fim",
            fim + ":00"
        );

    }


    // Não deixa pesquisar sem nenhum filtro

    if (parametros.toString() === "") {

        alert(
            "Informe pelo menos um filtro."
        );

        return;
    }


    try {

        const resposta =
            await fetch(
                `/dados/filtrar?${parametros.toString()}`
            );


        const resultado =
            await resposta.json();


        if (!resposta.ok) {

            alert(
                resultado.erro ||
                "Erro ao realizar consulta."
            );

            return;
        }


        mostrarResultados(
            resultado.dados
        );


        document.getElementById(
            "resultado-contador"
        ).textContent =
            `${resultado.total_documentos} documentos encontrados`;


    } catch (erro) {

        alert(
            "Não foi possível realizar a consulta."
        );

        console.error(erro);
    }
}

// ==========================================
// CRIAR DOCUMENTO
// ==========================================

async function criarDocumento() {

    const texto =
        document.getElementById("criar-json").value;


    try {

        const documento =
            JSON.parse(texto);


        const resposta =
            await fetch("/dados", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(documento)

            });


        const resultado =
            await resposta.json();


        if (!resposta.ok) {

            alert(resultado.erro || "Erro ao criar documento.");

            return;
        }


        alert(
            `Documento criado!\nID: ${resultado.id}`
        );


        document.getElementById("documento-id").value =
            resultado.id;


    } catch (erro) {

        alert("JSON inválido.");
    }
}


// ==========================================
// ATUALIZAR DOCUMENTO
// ==========================================

async function atualizarDocumento() {

    const id =
        document.getElementById("atualizar-id").value.trim();


    const texto =
        document.getElementById("atualizar-json").value;


    if (!id) {

        alert("Informe o ID.");

        return;
    }


    try {

        const documento =
            JSON.parse(texto);


        const resposta =
            await fetch(`/dados/${id}`, {

                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(documento)

            });


        const resultado =
            await resposta.json();


        if (!resposta.ok) {

            alert(resultado.erro || "Erro ao atualizar documento.");

            return;
        }


        alert("Documento atualizado com sucesso.");

    } catch (erro) {

        alert("JSON inválido.");
    }
}


// ==========================================
// DELETAR DOCUMENTO
// ==========================================

async function deletarDocumento() {

    const id =
        document.getElementById("deletar-id").value.trim();


    if (!id) {

        alert("Informe o ID.");

        return;
    }


    const confirmar =
        confirm(
            "Tem certeza que deseja excluir este documento?"
        );


    if (!confirmar) {
        return;
    }


    const resposta =
        await fetch(`/dados/${id}`, {

            method: "DELETE"

        });


    const resultado =
        await resposta.json();


    if (!resposta.ok) {

        alert(resultado.erro || "Erro ao excluir documento.");

        return;
    }


    alert("Documento removido com sucesso.");
}


// ==========================================
// INICIAR
// ==========================================

verificarAPI();