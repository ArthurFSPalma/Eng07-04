"""
database.py - Inicializacao do banco SQLite e seed de dados.

Cria as tabelas 'setores', 'vagas' e 'usuarios' e popula com dados realistas
simulando o estacionamento de um campus universitario.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from config import DATABASE


def get_db():
    """Retorna uma conexao com o banco SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas se nao existirem."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS setores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            descricao   TEXT,
            total_vagas INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS vagas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            setor_id    INTEGER NOT NULL,
            numero      TEXT    NOT NULL,
            tipo        TEXT    NOT NULL CHECK(tipo IN ('aluno', 'funcionario')),
            status      TEXT    NOT NULL DEFAULT 'livre' CHECK(status IN ('livre', 'ocupada')),
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (setor_id) REFERENCES setores(id)
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            senha_hash  TEXT    NOT NULL,
            tipo        TEXT    NOT NULL DEFAULT 'aluno'
                                CHECK(tipo IN ('aluno', 'funcionario')),
            criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    conn.close()
    print("[DB] Tabelas criadas com sucesso.")


def seed_db():
    """
    Popula o banco com dados realistas do campus.
    4 setores com total de ~80 vagas, incluindo vagas de funcionarios
    proximas a biblioteca (conforme documento do cliente).
    Tambem cria 2 usuarios de exemplo para testes.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Verifica se ja tem dados
    count = cursor.execute("SELECT COUNT(*) FROM setores").fetchone()[0]
    if count > 0:
        print("[DB] Banco ja possui dados. Seed ignorado.")
        conn.close()
        return

    # =====================================================
    # SETORES DO CAMPUS
    # =====================================================
    setores = [
        ("Setor A - Biblioteca",    "Proximo a biblioteca central",      20),
        ("Setor B - Engenharia",    "Proximo ao bloco de engenharia",     25),
        ("Setor C - Administrativo","Proximo ao predio administrativo",   20),
        ("Setor D - Esportes",      "Proximo ao ginasio e quadras",       15),
    ]

    cursor.executemany(
        "INSERT INTO setores (nome, descricao, total_vagas) VALUES (?, ?, ?)",
        setores
    )

    # =====================================================
    # VAGAS POR SETOR
    # =====================================================
    setor_configs = [
        {"setor_id": 1, "total": 20, "funcionario_inicio": 1, "funcionario_fim": 8,  "prefixo": "A"},
        {"setor_id": 2, "total": 25, "funcionario_inicio": 1, "funcionario_fim": 3,  "prefixo": "B"},
        {"setor_id": 3, "total": 20, "funcionario_inicio": 1, "funcionario_fim": 6,  "prefixo": "C"},
        {"setor_id": 4, "total": 15, "funcionario_inicio": 0, "funcionario_fim": 0,  "prefixo": "D"},
    ]

    vagas = []
    random.seed(42)
    agora = datetime.now()

    for config in setor_configs:
        for i in range(1, config["total"] + 1):
            numero = f"{config['prefixo']}-{i:02d}"
            tipo   = "funcionario" if config["funcionario_inicio"] <= i <= config["funcionario_fim"] else "aluno"
            status = "ocupada" if random.random() < 0.6 else "livre"
            minutos_atras = random.randint(0, 30)
            timestamp = (agora - timedelta(minutes=minutos_atras)).strftime("%Y-%m-%d %H:%M:%S")
            vagas.append((config["setor_id"], numero, tipo, status, timestamp))

    cursor.executemany(
        "INSERT INTO vagas (setor_id, numero, tipo, status, atualizado_em) VALUES (?, ?, ?, ?, ?)",
        vagas
    )

    # =====================================================
    # USUARIOS DE EXEMPLO (RF04)
    # =====================================================
    import hashlib

    def _hash(senha):
        salt = "estacionamento_campus_salt"
        return hashlib.sha256(f"{salt}{senha}".encode()).hexdigest()

    usuarios_seed = [
        ("Aluno Teste",        "aluno@campus.edu",       _hash("123456"), "aluno"),
        ("Prof. Funcionario",  "funcionario@campus.edu", _hash("123456"), "funcionario"),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        usuarios_seed
    )

    conn.commit()
    conn.close()

    total = sum(c["total"] for c in setor_configs)
    func  = sum(c["funcionario_fim"] - max(c["funcionario_inicio"] - 1, 0) for c in setor_configs)
    print(f"[DB] Seed concluido: {len(setores)} setores, {total} vagas ({func} de funcionarios), {len(usuarios_seed)} usuarios.")


if __name__ == "__main__":
    init_db()
    seed_db()
    print("[DB] Banco inicializado com sucesso!")
