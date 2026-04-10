"""
routes/mapa.py - Rotas do RF01: Mapa de Vagas em Tempo Real

Endpoints:
    GET /              -> Pagina principal com mapa visual
    GET /api/vagas     -> JSON com todas as vagas (para polling AJAX)
    GET /api/setores   -> JSON com resumo dos setores
    GET /api/vagas/<setor_id> -> JSON com vagas de um setor
"""

from flask import Blueprint, render_template, jsonify
from models.vagas import (
    get_all_vagas,
    get_vagas_por_setor,
    get_all_setores,
    get_resumo_setores
)

mapa_bp = Blueprint('mapa', __name__)


@mapa_bp.route('/')
def index():
    """Renderiza a pagina principal do mapa de estacionamento."""
    setores = get_all_setores()
    return render_template('mapa.html', setores=setores)


@mapa_bp.route('/api/vagas')
def api_vagas():
    """
    RF01: Retorna todas as vagas em formato JSON.
    Chamado via AJAX a cada 60 segundos para atualizacao em tempo real.
    """
    vagas = get_all_vagas()
    return jsonify({
        "sucesso": True,
        "total": len(vagas),
        "vagas": vagas,
        "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@mapa_bp.route('/api/setores')
def api_setores():
    """RF01: Retorna resumo por setor (contadores de vagas)."""
    resumo = get_resumo_setores()
    return jsonify({
        "sucesso": True,
        "setores": resumo
    })


@mapa_bp.route('/api/vagas/setor/<int:setor_id>')
def api_vagas_setor(setor_id):
    """Retorna vagas de um setor especifico."""
    vagas = get_vagas_por_setor(setor_id)
    if not vagas:
        return jsonify({"sucesso": False, "erro": "Setor nao encontrado ou sem vagas."}), 404

    return jsonify({
        "sucesso": True,
        "setor_id": setor_id,
        "total": len(vagas),
        "vagas": vagas
    })
