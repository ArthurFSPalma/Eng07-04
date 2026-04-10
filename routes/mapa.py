"""
routes/mapa.py - Rotas do RF01: Mapa de Vagas em Tempo Real

Todas as rotas exigem autenticacao.
"""

from flask import Blueprint, render_template, jsonify
from routes.auth import login_requerido, usuario_logado
from models.vagas import (
    get_all_vagas,
    get_vagas_por_setor,
    get_all_setores,
    get_resumo_setores
)

mapa_bp = Blueprint('mapa', __name__)


@mapa_bp.route('/')
@login_requerido
def index():
    """Renderiza a pagina principal do mapa de estacionamento."""
    setores = get_all_setores()
    user = usuario_logado()
    return render_template('mapa.html', setores=setores, usuario=user)


@mapa_bp.route('/api/vagas')
@login_requerido
def api_vagas():
    vagas = get_all_vagas()
    return jsonify({
        "sucesso": True,
        "total": len(vagas),
        "vagas": vagas,
        "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@mapa_bp.route('/api/setores')
@login_requerido
def api_setores():
    resumo = get_resumo_setores()
    return jsonify({
        "sucesso": True,
        "setores": resumo
    })


@mapa_bp.route('/api/vagas/setor/<int:setor_id>')
@login_requerido
def api_vagas_setor(setor_id):
    vagas = get_vagas_por_setor(setor_id)
    if not vagas:
        return jsonify({"sucesso": False, "erro": "Setor nao encontrado ou sem vagas."}), 404
    return jsonify({
        "sucesso": True,
        "setor_id": setor_id,
        "total": len(vagas),
        "vagas": vagas
    })
