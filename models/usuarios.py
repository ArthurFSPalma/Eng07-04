"""
models/usuarios.py - CRUD de usuarios para RF04 (Acesso Rapido sem Login Obrigatorio).

Gerencia autenticacao opcional: qualquer usuario pode ver o mapa sem login.
Login e necessario apenas para funcionalidades avancadas (ex: reporte de vagas).
Sessao persistida por 30 dias apos login voluntario.
"""

import hashlib
import os
from database import get_db


def _hash_senha(senha: str) -> str:
    """Gera hash SHA-256 com salt fixo de ambiente (simples para prototipo)."""
    salt = "estacionamento_campus_salt"
    return hashlib.sha256(f"{salt}{senha}".encode()).hexdigest()


def criar_usuario(nome: str, email: str, senha: str, tipo: str = "aluno") -> dict | None:
    """
    Cria um novo usuario no banco.
    Retorna o usuario criado ou None se o email ja existir.
    tipo: 'aluno' ou 'funcionario'
    """
    conn = get_db()
    cursor = conn.cursor()

    # Verifica se email ja esta cadastrado
    existente = cursor.execute(
        "SELECT id FROM usuarios WHERE email = ?", (email,)
    ).fetchone()

    if existente:
        conn.close()
        return None

    senha_hash = _hash_senha(senha)
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo)
    )
    conn.commit()
    usuario_id = cursor.lastrowid
    conn.close()

    return {"id": usuario_id, "nome": nome, "email": email, "tipo": tipo}


def autenticar_usuario(email: str, senha: str) -> dict | None:
    """
    Verifica credenciais. Retorna dados do usuario ou None se invalido.
    """
    conn = get_db()
    cursor = conn.cursor()

    senha_hash = _hash_senha(senha)
    usuario = cursor.execute(
        "SELECT id, nome, email, tipo FROM usuarios WHERE email = ? AND senha_hash = ?",
        (email, senha_hash)
    ).fetchone()

    conn.close()

    if usuario:
        return dict(usuario)
    return None


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    """Busca usuario pelo ID (usado para recarregar sessao)."""
    conn = get_db()
    usuario = conn.execute(
        "SELECT id, nome, email, tipo FROM usuarios WHERE id = ?",
        (usuario_id,)
    ).fetchone()
    conn.close()
    return dict(usuario) if usuario else None
