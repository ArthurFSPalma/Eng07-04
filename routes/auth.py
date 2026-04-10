"""
routes/auth.py - Blueprint de autenticacao para RF04.

RF04 - Acesso Rapido sem Login Obrigatorio:
  - Mapa de vagas acessivel sem autenticacao
  - Login voluntario para funcionalidades avancadas (reporte de vagas)
  - Sessao persistida por 30 dias via cookie permanente
  - Carregamento inicial sem splash screen de login
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from datetime import timedelta
from models.usuarios import autenticar_usuario, criar_usuario, buscar_usuario_por_id

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Sessao dura 30 dias (RF04: "lembrar sessao por pelo menos 30 dias")
SESSION_DURATION = timedelta(days=30)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def usuario_logado():
    """Retorna dados do usuario logado ou None (sessao anonima)."""
    usuario_id = session.get('usuario_id')
    if usuario_id:
        return buscar_usuario_por_id(usuario_id)
    return None


def login_requerido(f):
    """
    Decorator para rotas que exigem login (funcionalidades avancadas).
    Redireciona para /auth/login se nao autenticado.
    """
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not usuario_logado():
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  - Exibe pagina de login (opcional, usuario pode fechar e voltar ao mapa).
    POST - Processa credenciais; persiste sessao por 30 dias se valido.
    """
    # Se ja esta logado, volta ao mapa direto
    if usuario_logado():
        return redirect(url_for('mapa.index'))

    if request.method == 'GET':
        next_url = request.args.get('next', '/')
        return render_template('login.html', next_url=next_url)

    # POST: autenticacao
    dados = request.get_json() if request.is_json else request.form

    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''

    if not email or not senha:
        erro = "Preencha email e senha."
        if request.is_json:
            return jsonify({"sucesso": False, "erro": erro}), 400
        return render_template('login.html', erro=erro)

    usuario = autenticar_usuario(email, senha)

    if not usuario:
        erro = "Email ou senha incorretos."
        if request.is_json:
            return jsonify({"sucesso": False, "erro": erro}), 401
        return render_template('login.html', erro=erro, email=email)

    # Sessao permanente (30 dias)
    session.permanent = True
    session['usuario_id'] = usuario['id']
    session['usuario_nome'] = usuario['nome']
    session['usuario_tipo'] = usuario['tipo']

    if request.is_json:
        return jsonify({"sucesso": True, "usuario": usuario})

    next_url = dados.get('next_url') or '/'
    return redirect(next_url)


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """Encerra sessao e volta ao mapa (sem forcar re-login)."""
    session.clear()
    return redirect(url_for('mapa.index'))


@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    """Registro voluntario de novo usuario."""
    if usuario_logado():
        return redirect(url_for('mapa.index'))

    if request.method == 'GET':
        return render_template('login.html', modo='registro')

    dados = request.get_json() if request.is_json else request.form

    nome  = (dados.get('nome') or '').strip()
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''
    tipo  = dados.get('tipo') or 'aluno'

    if not nome or not email or not senha:
        erro = "Preencha todos os campos."
        if request.is_json:
            return jsonify({"sucesso": False, "erro": erro}), 400
        return render_template('login.html', modo='registro', erro=erro)

    usuario = criar_usuario(nome, email, senha, tipo)

    if not usuario:
        erro = "Este email ja esta cadastrado."
        if request.is_json:
            return jsonify({"sucesso": False, "erro": erro}), 409
        return render_template('login.html', modo='registro', erro=erro)

    # Faz login automatico apos registro
    session.permanent = True
    session['usuario_id'] = usuario['id']
    session['usuario_nome'] = usuario['nome']
    session['usuario_tipo'] = usuario['tipo']

    if request.is_json:
        return jsonify({"sucesso": True, "usuario": usuario}), 201

    return redirect(url_for('mapa.index'))


@auth_bp.route('/status')
def status():
    """
    API: retorna status da sessao atual.
    Usado pelo frontend para exibir nome do usuario ou botao de login.
    """
    usuario = usuario_logado()
    if usuario:
        return jsonify({
            "logado": True,
            "nome": usuario['nome'],
            "tipo": usuario['tipo']
        })
    return jsonify({"logado": False})
