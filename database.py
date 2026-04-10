"""
database.py - Inicializacao do banco SQLite e seed de dados.

Cria as tabelas 'setores' e 'vagas' e popula com dados realistas
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            total_vagas INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setor_id INTEGER NOT NULL,
            numero TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('aluno', 'funcionario')),
            status TEXT NOT NULL DEFAULT 'livre' CHECK(status IN ('livre', 'ocupada')),
            reservado INTEGER NOT NULL DEFAULT 0 CHECK(reservado IN (0, 1)),
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (setor_id) REFERENCES setores(id)
        );
    ''')

    # Migracao simples para bancos antigos que ainda nao possuem a coluna.
    colunas_vagas = [c[1] for c in cursor.execute("PRAGMA table_info(vagas)").fetchall()]
    if "reservado" not in colunas_vagas:
        cursor.execute(
            "ALTER TABLE vagas ADD COLUMN reservado INTEGER NOT NULL DEFAULT 0 CHECK(reservado IN (0, 1))"
        )

    conn.commit()
    conn.close()
    print("[DB] Tabelas criadas com sucesso.")


def seed_db():
    """
    Popula o banco com dados realistas do campus.
    4 setores com total de ~80 vagas, incluindo vagas de funcionarios
    proximas a biblioteca (conforme documento do cliente).
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
        ("Setor A - Biblioteca", "Proximo a biblioteca central", 20),
        ("Setor B - Engenharia", "Proximo ao bloco de engenharia", 25),
        ("Setor C - Administrativo", "Proximo ao predio administrativo", 20),
        ("Setor D - Esportes", "Proximo ao ginasio e quadras", 15),
    ]

    cursor.executemany(
        "INSERT INTO setores (nome, descricao, total_vagas) VALUES (?, ?, ?)",
        setores
    )

    # =====================================================
    # VAGAS POR SETOR
    # =====================================================
    # Setor A (Biblioteca): 20 vagas — 8 de funcionario (RF03: area da biblioteca)
    vagas = []
    setor_configs = [
        {
            "setor_id": 1,
            "total": 20,
            "funcionario_inicio": 1,
            "funcionario_fim": 8,   # Vagas A-01 a A-08 sao de funcionarios
            "prefixo": "A"
        },
        {
            "setor_id": 2,
            "total": 25,
            "funcionario_inicio": 1,
            "funcionario_fim": 3,   # Vagas B-01 a B-03 sao de funcionarios
            "prefixo": "B"
        },
        {
            "setor_id": 3,
            "total": 20,
            "funcionario_inicio": 1,
            "funcionario_fim": 6,   # Vagas C-01 a C-06 sao de funcionarios
            "prefixo": "C"
        },
        {
            "setor_id": 4,
            "total": 15,
            "funcionario_inicio": 0,
            "funcionario_fim": 0,   # Nenhuma vaga de funcionario
            "prefixo": "D"
        },
    ]

    random.seed(42)  # Reproducibilidade
    agora = datetime.now()

    for config in setor_configs:
        for i in range(1, config["total"] + 1):
            numero = f"{config['prefixo']}-{i:02d}"
            tipo = "funcionario" if config["funcionario_inicio"] <= i <= config["funcionario_fim"] else "aluno"

            # Simula: ~60% das vagas ocupadas no horario de pico
            status = "ocupada" if random.random() < 0.6 else "livre"

            # Timestamp aleatorio nos ultimos 30 minutos
            minutos_atras = random.randint(0, 30)
            timestamp = (agora - timedelta(minutes=minutos_atras)).strftime("%Y-%m-%d %H:%M:%S")

            vagas.append((config["setor_id"], numero, tipo, status, timestamp))

    cursor.executemany(
        "INSERT INTO vagas (setor_id, numero, tipo, status, atualizado_em) VALUES (?, ?, ?, ?, ?)",
        vagas
    )

    conn.commit()
    conn.close()

    total = sum(c["total"] for c in setor_configs)
    func = sum(c["funcionario_fim"] - max(c["funcionario_inicio"] - 1, 0) for c in setor_configs)
    print(f"[DB] Seed concluido: {len(setores)} setores, {total} vagas ({func} de funcionarios).")


if __name__ == "__main__":
    init_db()
    seed_db()
    print("[DB] Banco inicializado com sucesso!")
