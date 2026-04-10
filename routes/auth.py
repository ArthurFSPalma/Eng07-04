"""
routes/auth.py - Blueprint de autenticacao.

Login OBRIGATORIO para acessar o sistema.
Sessao persistida por 30 dias via cookie permanente.
Conta admin para monitoramento de vagas de funcionarios.
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from functools import wraps
from datetime import timedelta
from models.usuarios import autenticar_usuario, criar_usuario, buscar_usuario_por_id

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

SESSION_DURATION = timedelta(days=30)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def usuario_logado():
    """Retorna dados do usuario logado ou None."""
    usuario_id = session.get('usuario_id')
    if usuario_id:
        return buscar_usuario_por_id(usuario_id)
    return None


def login_requerido(f):
    """Decorator — redireciona para /auth/login se nao autenticado."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not usuario_logado():
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"sucesso": False, "erro": "Login necessario."}), 401
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return wrapper


def admin_requerido(f):
    """Decorator — exige usuario do tipo 'admin'."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = usuario_logado()
        if not user:
            if request.is_json:
                return jsonify({"sucesso": False, "erro": "Login necessario."}), 401
            return redirect(url_for('auth.login', next=request.path))
        if user['tipo'] != 'admin':
            if request.is_json:
                return jsonify({"sucesso": False, "erro": "Acesso restrito a administradores."}), 403
            return redirect(url_for('mapa.index'))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if usuario_logado():
        return redirect(url_for('mapa.index'))

    if request.method == 'GET':
        next_url = request.args.get('next', '/')
        return render_template('login.html', next_url=next_url)

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
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if usuario_logado():
        return redirect(url_for('mapa.index'))

    if request.method == 'GET':
        return render_template('login.html', modo='registro')

    dados = request.get_json() if request.is_json else request.form

    nome  = (dados.get('nome') or '').strip()
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''
    tipo  = dados.get('tipo') or 'aluno'

    # Bloqueia criacao de admin pelo formulario publico
    if tipo == 'admin':
        tipo = 'aluno'

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

    session.permanent = True
    session['usuario_id'] = usuario['id']
    session['usuario_nome'] = usuario['nome']
    session['usuario_tipo'] = usuario['tipo']

    if request.is_json:
        return jsonify({"sucesso": True, "usuario": usuario}), 201

    return redirect(url_for('mapa.index'))


@auth_bp.route('/status')
def status():
    usuario = usuario_logado()
    if usuario:
        return jsonify({
            "logado": True,
            "nome": usuario['nome'],
            "tipo": usuario['tipo'],
            "email": usuario['email']
        })
    return jsonify({"logado": False})
