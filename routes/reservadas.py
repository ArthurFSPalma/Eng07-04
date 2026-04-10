"""
routes/reservadas.py - Rotas do RF03: Vagas Reservadas
Usa reservado_por (aluno/funcionario/null)
"""

from flask import Blueprint, jsonify, request, session
from routes.auth import login_requerido
from models.vagas import (
    get_vagas_reservadas, get_vaga_by_id,
    atualizar_status_vaga, reservar_vaga, desreservar_vaga
)

reservadas_bp = Blueprint('reservadas', __name__)


def _tipo_usuario():
    return session.get('usuario_tipo', 'aluno')


@reservadas_bp.route('/api/vagas/reservadas')
@login_requerido
def api_vagas_reservadas():
    vagas = get_vagas_reservadas()
    return jsonify({"sucesso": True, "total": len(vagas), "vagas": vagas})


@reservadas_bp.route('/api/vagas/<int:vaga_id>/info')
@login_requerido
def api_vaga_info(vaga_id):
    vaga = get_vaga_by_id(vaga_id)
    if not vaga:
        return jsonify({"sucesso": False, "erro": "Vaga nao encontrada."}), 404
    return jsonify({
        "sucesso": True,
        "vaga": vaga,
        "is_reservada": vaga["tipo"] == "funcionario",
        "usuario_tipo": _tipo_usuario()
    })


@reservadas_bp.route('/api/vagas/<int:vaga_id>/status', methods=['POST'])
@login_requerido
def api_atualizar_status(vaga_id):
    dados = request.get_json()
    if not dados or 'status' not in dados:
        return jsonify({"sucesso": False, "erro": "Envie JSON com campo 'status'."}), 400
    resultado = atualizar_status_vaga(vaga_id, dados['status'], _tipo_usuario())
    code = 200 if resultado["sucesso"] else (403 if "permissao" in resultado.get("erro","").lower() or "nao podem" in resultado.get("erro","").lower() else 400)
    return jsonify(resultado), code


@reservadas_bp.route('/api/vagas/<int:vaga_id>/reservar', methods=['POST'])
@login_requerido
def api_reservar_vaga(vaga_id):
    resultado = reservar_vaga(vaga_id, _tipo_usuario())
    return jsonify(resultado), 200 if resultado["sucesso"] else 400


@reservadas_bp.route('/api/vagas/<int:vaga_id>/desreservar', methods=['POST'])
@login_requerido
def api_desreservar_vaga(vaga_id):
    resultado = desreservar_vaga(vaga_id, _tipo_usuario())
    return jsonify(resultado), 200 if resultado["sucesso"] else 400
