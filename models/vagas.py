"""
models/vagas.py - Camada de acesso a dados para vagas e setores.

Logica de reserva:
  - Funcionario pode reservar QUALQUER vaga e sobrescrever reserva de aluno
  - Aluno so pode reservar vagas tipo 'aluno' que nao estejam reservadas por funcionario
  - Admin pode tudo
"""

from database import get_db
from datetime import datetime


# =====================================================
# SETORES
# =====================================================

def get_all_setores():
    conn = get_db()
    setores = conn.execute('''
        SELECT
            s.id,
            s.nome,
            s.descricao,
            s.total_vagas,
            COALESCE(SUM(CASE WHEN v.status = 'livre' AND v.reservado_por IS NULL THEN 1 ELSE 0 END), 0) AS livres,
            COALESCE(SUM(CASE WHEN v.status = 'ocupada' THEN 1 ELSE 0 END), 0) AS ocupadas,
            COALESCE(SUM(CASE WHEN v.reservado_por = 'aluno' THEN 1 ELSE 0 END), 0) AS reservadas_aluno,
            COALESCE(SUM(CASE WHEN v.reservado_por = 'funcionario' THEN 1 ELSE 0 END), 0) AS reservadas_func,
            COALESCE(SUM(CASE WHEN v.tipo = 'funcionario' THEN 1 ELSE 0 END), 0) AS vagas_funcionario
        FROM setores s
        LEFT JOIN vagas v ON v.setor_id = s.id
        GROUP BY s.id
        ORDER BY s.id
    ''').fetchall()
    conn.close()
    return [dict(s) for s in setores]


def get_setor_by_id(setor_id):
    conn = get_db()
    setor = conn.execute("SELECT * FROM setores WHERE id = ?", (setor_id,)).fetchone()
    conn.close()
    return dict(setor) if setor else None


# =====================================================
# VAGAS
# =====================================================

def get_all_vagas():
    conn = get_db()
    vagas = conn.execute('''
        SELECT v.id, v.setor_id, v.numero, v.tipo, v.status,
               v.reservado_por, v.atualizado_em, s.nome AS setor_nome
        FROM vagas v
        JOIN setores s ON s.id = v.setor_id
        ORDER BY v.setor_id, v.numero
    ''').fetchall()
    conn.close()
    return [dict(v) for v in vagas]


def get_vagas_por_setor(setor_id):
    conn = get_db()
    vagas = conn.execute('''
        SELECT v.id, v.setor_id, v.numero, v.tipo, v.status,
               v.reservado_por, v.atualizado_em
        FROM vagas v WHERE v.setor_id = ?
        ORDER BY v.numero
    ''', (setor_id,)).fetchall()
    conn.close()
    return [dict(v) for v in vagas]


def get_vaga_by_id(vaga_id):
    conn = get_db()
    vaga = conn.execute('''
        SELECT v.id, v.setor_id, v.numero, v.tipo, v.status,
               v.reservado_por, v.atualizado_em,
               s.nome AS setor_nome, s.descricao AS setor_descricao
        FROM vagas v
        JOIN setores s ON s.id = v.setor_id
        WHERE v.id = ?
    ''', (vaga_id,)).fetchone()
    conn.close()
    return dict(vaga) if vaga else None


def get_vagas_reservadas():
    conn = get_db()
    vagas = conn.execute('''
        SELECT v.id, v.setor_id, v.numero, v.tipo, v.status,
               v.reservado_por, v.atualizado_em, s.nome AS setor_nome
        FROM vagas v
        JOIN setores s ON s.id = v.setor_id
        WHERE v.reservado_por IS NOT NULL
        ORDER BY v.setor_id, v.numero
    ''').fetchall()
    conn.close()
    return [dict(v) for v in vagas]


def get_resumo_setores():
    conn = get_db()
    resumo = conn.execute('''
        SELECT
            s.id, s.nome, s.total_vagas,
            COALESCE(SUM(CASE WHEN v.status = 'livre' AND v.reservado_por IS NULL THEN 1 ELSE 0 END), 0) AS livres,
            COALESCE(SUM(CASE WHEN v.status = 'ocupada' THEN 1 ELSE 0 END), 0) AS ocupadas,
            COALESCE(SUM(CASE WHEN v.reservado_por = 'aluno' THEN 1 ELSE 0 END), 0) AS reservadas_aluno,
            COALESCE(SUM(CASE WHEN v.reservado_por = 'funcionario' THEN 1 ELSE 0 END), 0) AS reservadas_func
        FROM setores s
        LEFT JOIN vagas v ON v.setor_id = s.id
        GROUP BY s.id ORDER BY s.id
    ''').fetchall()
    conn.close()
    return [dict(r) for r in resumo]


# =====================================================
# ATUALIZAR STATUS
# =====================================================

def atualizar_status_vaga(vaga_id, novo_status, usuario_tipo="aluno"):
    conn = get_db()
    vaga = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()

    if not vaga:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao encontrada."}

    # Aluno nao pode alterar vaga de funcionario
    if vaga["tipo"] == "funcionario" and usuario_tipo == "aluno":
        conn.close()
        return {"sucesso": False, "erro": "Alunos nao podem alterar vagas de funcionarios."}

    # Vaga reservada por funcionario: so funcionario/admin pode alterar
    if vaga["reservado_por"] == "funcionario" and usuario_tipo == "aluno":
        conn.close()
        return {"sucesso": False, "erro": "Vaga reservada por funcionario. Sem permissao."}

    # Vaga reservada precisa ser desreservada primeiro
    if vaga["reservado_por"] is not None:
        conn.close()
        return {"sucesso": False, "erro": "Desreserve a vaga antes de alterar o status."}

    if novo_status not in ("livre", "ocupada"):
        conn.close()
        return {"sucesso": False, "erro": "Status invalido. Use 'livre' ou 'ocupada'."}

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE vagas SET status = ?, atualizado_em = ? WHERE id = ?",
                 (novo_status, agora, vaga_id))
    conn.commit()
    conn.close()
    return {"sucesso": True, "mensagem": f"Vaga {vaga['numero']} atualizada para '{novo_status}'."}


# =====================================================
# RESERVAR / DESRESERVAR
# =====================================================

def reservar_vaga(vaga_id, usuario_tipo="aluno"):
    """
    - Funcionario/admin: pode reservar QUALQUER vaga. Se ja reservada por aluno, sobrescreve.
    - Aluno: so pode reservar vaga tipo 'aluno', nao reservada por funcionario.
    """
    conn = get_db()
    vaga = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()

    if not vaga:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao encontrada."}

    if vaga["status"] != "livre":
        conn.close()
        return {"sucesso": False, "erro": "Apenas vagas livres podem ser reservadas."}

    is_func_or_admin = usuario_tipo in ("funcionario", "admin")

    if not is_func_or_admin:
        # ALUNO
        if vaga["tipo"] == "funcionario":
            conn.close()
            return {"sucesso": False, "erro": "Alunos nao podem reservar vagas de funcionarios."}

        if vaga["reservado_por"] == "funcionario":
            conn.close()
            return {"sucesso": False, "erro": "Vaga reservada por funcionario. Sem permissao."}

        if vaga["reservado_por"] == "aluno":
            conn.close()
            return {"sucesso": False, "erro": "Vaga ja esta reservada por outro aluno."}

    else:
        # FUNCIONARIO / ADMIN — pode sobrescrever reserva de aluno
        if vaga["reservado_por"] == "funcionario":
            conn.close()
            return {"sucesso": False, "erro": "Vaga ja esta reservada por outro funcionario."}
        # Se reservada por aluno, sobrescreve silenciosamente

    reservado_por = "funcionario" if is_func_or_admin else "aluno"
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE vagas SET reservado_por = ?, atualizado_em = ? WHERE id = ?",
                 (reservado_por, agora, vaga_id))
    conn.commit()
    conn.close()

    msg = f"Vaga {vaga['numero']} reservada com sucesso."
    if vaga["reservado_por"] == "aluno" and is_func_or_admin:
        msg = f"Vaga {vaga['numero']} reservada. Reserva anterior de aluno foi substituida."
    return {"sucesso": True, "mensagem": msg}


def desreservar_vaga(vaga_id, usuario_tipo="aluno"):
    """
    - Funcionario/admin: pode desreservar qualquer vaga.
    - Aluno: so pode desreservar vagas reservadas por aluno.
    """
    conn = get_db()
    vaga = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()

    if not vaga:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao encontrada."}

    if vaga["reservado_por"] is None:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao esta reservada."}

    is_func_or_admin = usuario_tipo in ("funcionario", "admin")

    if not is_func_or_admin:
        if vaga["reservado_por"] == "funcionario":
            conn.close()
            return {"sucesso": False, "erro": "Alunos nao podem remover reserva de funcionario."}

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE vagas SET reservado_por = NULL, atualizado_em = ? WHERE id = ?",
                 (agora, vaga_id))
    conn.commit()
    conn.close()
    return {"sucesso": True, "mensagem": f"Reserva da vaga {vaga['numero']} removida."}
