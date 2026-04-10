"""
routes/reservadas.py - Rotas do RF03: Identificacao de Vagas Reservadas

Endpoints:
    GET  /api/vagas/reservadas      -> JSON com todas as vagas de funcionarios
    GET  /api/vagas/<id>/info       -> JSON com detalhes de uma vaga (popup)
    POST /api/vagas/<id>/status     -> Atualiza status (bloqueia se reservada)
"""

from flask import Blueprint, jsonify, request
from models.vagas import (
    get_vagas_reservadas,
    get_vaga_by_id,
    atualizar_status_vaga,
    reservar_vaga,
    desreservar_vaga
)

reservadas_bp = Blueprint('reservadas', __name__)


@reservadas_bp.route('/api/vagas/reservadas')
def api_vagas_reservadas():
    """
    RF03: Retorna todas as vagas do tipo 'funcionario'.
    Usado para marcacao visual no mapa (cor roxa + icone cadeado).
    """
    vagas = get_vagas_reservadas()
    return jsonify({
        "sucesso": True,
        "total": len(vagas),
        "vagas": vagas
    })


@reservadas_bp.route('/api/vagas/<int:vaga_id>/info')
def api_vaga_info(vaga_id):
    """
    RF03: Retorna detalhes de uma vaga especifica.
    Usado quando o usuario clica em uma vaga no mapa.
    Se a vaga for reservada, inclui informacao de restricao.
    """
    vaga = get_vaga_by_id(vaga_id)

    if not vaga:
        return jsonify({"sucesso": False, "erro": "Vaga nao encontrada."}), 404

    resposta = {
        "sucesso": True,
        "vaga": vaga,
        "is_reservada": vaga["tipo"] == "funcionario"
    }

    # RF03: Adiciona mensagem de restricao para vagas reservadas
    if vaga["tipo"] == "funcionario":
        resposta["restricao"] = {
            "mensagem": f"Vaga {vaga['numero']} reservada para FUNCIONARIOS/DOCENTES.",
            "tipo_autorizado": "Funcionario / Docente",
            "setor": vaga["setor_nome"],
            "alerta": "Alunos NAO podem estacionar nesta vaga."
        }

    return jsonify(resposta)


@reservadas_bp.route('/api/vagas/<int:vaga_id>/status', methods=['POST'])
def api_atualizar_status(vaga_id):
    """
    Atualiza o status de uma vaga (livre/ocupada).
    RF03: Se a vaga for de funcionario, retorna erro 403.
    """
    dados = request.get_json()

    if not dados or 'status' not in dados:
        return jsonify({
            "sucesso": False,
            "erro": "Envie JSON com campo 'status' ('livre' ou 'ocupada')."
        }), 400

    resultado = atualizar_status_vaga(vaga_id, dados['status'])

    if resultado["sucesso"]:
        return jsonify(resultado)
    else:
        # RF03: Se for vaga reservada, retorna 403 Forbidden
        status_code = 403 if "reservada" in resultado.get("erro", "") else 400
        return jsonify(resultado), status_code


@reservadas_bp.route('/api/vagas/<int:vaga_id>/reservar', methods=['POST'])
def api_reservar_vaga(vaga_id):
    """Reserva uma vaga de aluno livre."""
    resultado = reservar_vaga(vaga_id)
    status_code = 200 if resultado["sucesso"] else 400
    return jsonify(resultado), status_code


@reservadas_bp.route('/api/vagas/<int:vaga_id>/desreservar', methods=['POST'])
def api_desreservar_vaga(vaga_id):
    """Remove a reserva de uma vaga de aluno."""
    resultado = desreservar_vaga(vaga_id)
    status_code = 200 if resultado["sucesso"] else 400
    return jsonify(resultado), status_code
