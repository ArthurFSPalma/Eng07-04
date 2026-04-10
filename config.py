import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Caminho do banco SQLite local
DATABASE = os.path.join(BASE_DIR, 'estacionamento.db')

# Configuracoes do Flask
DEBUG = True
SECRET_KEY = 'chave-secreta-dev-estacionamento-campus'
