"""
models/vagas.py - Camada de acesso a dados (Model) para vagas e setores.

Contem todas as funcoes CRUD para interagir com o banco SQLite.
Utilizado pelos endpoints da API (routes/).
"""

from database import get_db
from datetime import datetime


# =====================================================
# SETORES
# =====================================================

def get_all_setores():
    """Retorna todos os setores com contagem de vagas livres e ocupadas."""
    conn = get_db()
    setores = conn.execute('''
        SELECT
            s.id,
            s.nome,
            s.descricao,
            s.total_vagas,
            COALESCE(SUM(CASE WHEN v.status = 'livre' THEN 1 ELSE 0 END), 0) AS livres,
            COALESCE(SUM(CASE WHEN v.status = 'ocupada' THEN 1 ELSE 0 END), 0) AS ocupadas,
            COALESCE(SUM(CASE WHEN v.tipo = 'funcionario' THEN 1 ELSE 0 END), 0) AS reservadas_funcionario,
            COALESCE(SUM(CASE WHEN v.tipo = 'aluno' AND v.reservado = 1 THEN 1 ELSE 0 END), 0) AS reservadas_aluno
        FROM setores s
        LEFT JOIN vagas v ON v.setor_id = s.id
        GROUP BY s.id
        ORDER BY s.id
    ''').fetchall()
    conn.close()
    return [dict(s) for s in setores]


def get_setor_by_id(setor_id):
    """Retorna um setor especifico pelo ID."""
    conn = get_db()
    setor = conn.execute(
        "SELECT * FROM setores WHERE id = ?", (setor_id,)
    ).fetchone()
    conn.close()
    return dict(setor) if setor else None


# =====================================================
# VAGAS
# =====================================================

def get_all_vagas():
    """Retorna todas as vagas com informacao do setor."""
    conn = get_db()
    vagas = conn.execute('''
        SELECT
            v.id,
            v.setor_id,
            v.numero,
            v.tipo,
            v.status,
            v.reservado,
            v.atualizado_em,
            s.nome AS setor_nome
        FROM vagas v
        JOIN setores s ON s.id = v.setor_id
        ORDER BY v.setor_id, v.numero
    ''').fetchall()
    conn.close()
    return [dict(v) for v in vagas]


def get_vagas_por_setor(setor_id):
    """Retorna todas as vagas de um setor especifico."""
    conn = get_db()
    vagas = conn.execute('''
        SELECT
            v.id,
            v.setor_id,
            v.numero,
            v.tipo,
            v.status,
            v.reservado,
            v.atualizado_em
        FROM vagas v
        WHERE v.setor_id = ?
        ORDER BY v.numero
    ''', (setor_id,)).fetchall()
    conn.close()
    return [dict(v) for v in vagas]


def get_vaga_by_id(vaga_id):
    """Retorna detalhes de uma vaga especifica (usado no RF03 para popup)."""
    conn = get_db()
    vaga = conn.execute('''
        SELECT
            v.id,
            v.setor_id,
            v.numero,
            v.tipo,
            v.status,
            v.reservado,
            v.atualizado_em,
            s.nome AS setor_nome,
            s.descricao AS setor_descricao
        FROM vagas v
        JOIN setores s ON s.id = v.setor_id
        WHERE v.id = ?
    ''', (vaga_id,)).fetchone()
    conn.close()
    return dict(vaga) if vaga else None


def get_vagas_reservadas():
    """
    RF03: Retorna somente vagas do tipo 'funcionario' (reservadas).
    Usado para destacar no mapa e bloquear acoes de alunos.
    """
    conn = get_db()
    vagas = conn.execute('''
        SELECT
            v.id,
            v.setor_id,
            v.numero,
            v.tipo,
            v.status,
            v.reservado,
            v.atualizado_em,
            s.nome AS setor_nome
        FROM vagas v
        JOIN setores s ON s.id = v.setor_id
        WHERE v.tipo = 'funcionario'
        ORDER BY v.setor_id, v.numero
    ''').fetchall()
    conn.close()
    return [dict(v) for v in vagas]


def atualizar_status_vaga(vaga_id, novo_status, usuario_tipo="aluno"):
    """
    Atualiza o status de uma vaga (livre/ocupada).
    - Alunos so podem alterar vagas tipo 'aluno'
    - Funcionarios/admin podem alterar vagas tipo 'funcionario'
    """
    conn = get_db()

    vaga = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()
    if not vaga:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao encontrada."}

    # Aluno tentando alterar vaga de funcionario
    if vaga["tipo"] == "funcionario" and usuario_tipo == "aluno":
        conn.close()
        return {
            "sucesso": False,
            "erro": "Vaga reservada para funcionarios. Alunos nao podem alterar o status desta vaga."
        }

    # Funcionario tentando alterar vaga de aluno
    if vaga["tipo"] == "aluno" and usuario_tipo in ("funcionario",):
        conn.close()
        return {
            "sucesso": False,
            "erro": "Funcionarios nao podem alterar vagas de alunos."
        }

    # Vaga reservada deve ser desreservada antes
    if vaga["reservado"] == 1:
        conn.close()
        return {
            "sucesso": False,
            "erro": "Vaga reservada. Desreserve a vaga antes de alterar o status."
        }

    # Valida o status
    if novo_status not in ("livre", "ocupada"):
        conn.close()
        return {"sucesso": False, "erro": "Status invalido. Use 'livre' ou 'ocupada'."}

    # Atualiza
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE vagas SET status = ?, atualizado_em = ? WHERE id = ?",
        (novo_status, agora, vaga_id)
    )
    conn.commit()
    conn.close()

    return {
        "sucesso": True,
        "mensagem": f"Vaga {vaga['numero']} atualizada para '{novo_status}'."
    }


def get_resumo_setores():
    """
    RF01: Retorna resumo rapido para o mapa — contadores por setor.
    Dados leves para polling frequente.
    """
    conn = get_db()
    resumo = conn.execute('''
        SELECT
            s.id,
            s.nome,
            s.total_vagas,
            COALESCE(SUM(CASE WHEN v.status = 'livre' AND v.tipo = 'aluno' THEN 1 ELSE 0 END), 0) AS livres_aluno,
            COALESCE(SUM(CASE WHEN v.status = 'ocupada' AND v.tipo = 'aluno' THEN 1 ELSE 0 END), 0) AS ocupadas_aluno,
            COALESCE(SUM(CASE WHEN v.tipo = 'aluno' AND v.reservado = 1 THEN 1 ELSE 0 END), 0) AS reservadas_aluno,
            COALESCE(SUM(CASE WHEN v.tipo = 'funcionario' AND v.status = 'livre' THEN 1 ELSE 0 END), 0) AS livres_func,
            COALESCE(SUM(CASE WHEN v.tipo = 'funcionario' AND v.status = 'ocupada' THEN 1 ELSE 0 END), 0) AS ocupadas_func,
            COALESCE(SUM(CASE WHEN v.tipo = 'funcionario' AND v.reservado = 1 THEN 1 ELSE 0 END), 0) AS reservadas_func
        FROM setores s
        LEFT JOIN vagas v ON v.setor_id = s.id
        GROUP BY s.id
        ORDER BY s.id
    ''').fetchall()
    conn.close()
    return [dict(r) for r in resumo]


def reservar_vaga(vaga_id, usuario_tipo="aluno"):
    """
    Reserva uma vaga.
    - Aluno so pode reservar vaga tipo 'aluno'
    - Funcionario/admin pode reservar vaga tipo 'funcionario'
    """
    conn = get_db()
    vaga = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()

    if not vaga:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao encontrada."}

    # Aluno tentando reservar vaga de funcionario
    if vaga["tipo"] == "funcionario" and usuario_tipo == "aluno":
        conn.close()
        return {"sucesso": False, "erro": "Alunos nao podem reservar vagas de funcionarios."}

    # Funcionario/admin tentando reservar vaga de aluno
    if vaga["tipo"] == "aluno" and usuario_tipo in ("funcionario", "admin"):
        conn.close()
        return {"sucesso": False, "erro": "Funcionarios devem reservar vagas do tipo funcionario."}

    if vaga["reservado"] == 1:
        conn.close()
        return {"sucesso": False, "erro": "Vaga ja esta reservada."}

    if vaga["status"] != "livre":
        conn.close()
        return {"sucesso": False, "erro": "Apenas vagas livres podem ser reservadas."}

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE vagas SET reservado = 1, atualizado_em = ? WHERE id = ?",
        (agora, vaga_id)
    )
    conn.commit()
    conn.close()

    return {"sucesso": True, "mensagem": f"Vaga {vaga['numero']} reservada com sucesso."}


def desreservar_vaga(vaga_id, usuario_tipo="aluno"):
    """
    Remove a reserva de uma vaga.
    - Aluno so pode desreservar vaga tipo 'aluno'
    - Funcionario/admin pode desreservar vaga tipo 'funcionario'
    """
    conn = get_db()
    vaga = conn.execute("SELECT * FROM vagas WHERE id = ?", (vaga_id,)).fetchone()

    if not vaga:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao encontrada."}

    if vaga["tipo"] == "funcionario" and usuario_tipo == "aluno":
        conn.close()
        return {"sucesso": False, "erro": "Alunos nao podem desreservar vagas de funcionarios."}

    if vaga["tipo"] == "aluno" and usuario_tipo in ("funcionario", "admin"):
        conn.close()
        return {"sucesso": False, "erro": "Funcionarios nao podem desreservar vagas de alunos."}

    if vaga["reservado"] == 0:
        conn.close()
        return {"sucesso": False, "erro": "Vaga nao esta reservada."}

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE vagas SET reservado = 0, atualizado_em = ? WHERE id = ?",
        (agora, vaga_id)
    )
    conn.commit()
    conn.close()

    return {"sucesso": True, "mensagem": f"Reserva da vaga {vaga['numero']} removida."}
