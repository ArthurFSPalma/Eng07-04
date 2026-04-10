"""
app.py - Ponto de entrada do Aplicativo de Estacionamento no Campus.

Inicializa o Flask, registra os blueprints e cria o banco de dados.
Para executar: python app.py
Acesse: http://localhost:5000
"""

from flask import Flask
from config import DEBUG, SECRET_KEY
from database import init_db, seed_db
from routes.mapa import mapa_bp
from routes.reservadas import reservadas_bp


def create_app():
    """Factory function do Flask."""
    app = Flask(__name__)
    app.config['DEBUG'] = DEBUG
    app.config['SECRET_KEY'] = SECRET_KEY

    # Registra os Blueprints (rotas)
    app.register_blueprint(mapa_bp)        # RF01: Mapa de vagas
    app.register_blueprint(reservadas_bp)  # RF03: Vagas reservadas

    # Inicializa o banco de dados
    with app.app_context():
        init_db()
        seed_db()

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("  ESTACIONAMENTO DO CAMPUS")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5050, debug=DEBUG)
