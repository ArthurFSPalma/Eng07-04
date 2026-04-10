"""
app.py - Ponto de entrada do Aplicativo de Estacionamento no Campus.

Inicializa o Flask, registra os blueprints e cria o banco de dados.

Para executar: python app.py
Acesse: http://localhost:5050
"""

from datetime import timedelta
from flask import Flask
from config import DEBUG, SECRET_KEY
from database import init_db, seed_db
from routes.mapa import mapa_bp
from routes.reservadas import reservadas_bp
from routes.auth import auth_bp          # RF04: autenticacao opcional


def create_app():
    """Factory function do Flask."""
    app = Flask(__name__)
    app.config['DEBUG']      = DEBUG
    app.config['SECRET_KEY'] = SECRET_KEY

    # RF04: sessao permanente de 30 dias
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

    # Registra os Blueprints (rotas)
    app.register_blueprint(mapa_bp)        # RF01: Mapa de vagas
    app.register_blueprint(reservadas_bp)  # RF03: Vagas reservadas
    app.register_blueprint(auth_bp)        # RF04: Login opcional

    # Inicializa o banco de dados
    with app.app_context():
        init_db()
        seed_db()

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print(" ESTACIONAMENTO DO CAMPUS")
    print(" Acesse: http://localhost:5050")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5050, debug=DEBUG)
