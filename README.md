# Eng07-04 — Aplicativo de Estacionamento no Campus

**Engenharia de Software 2026/1 — AV1: Dos Requisitos ao Prototipo Inicial**

Sistema para visualizacao de vagas de estacionamento no campus universitario em tempo real.

## Alunos e Divisao de Funcionalidades

| Aluno | Requisitos | Arquivos Principais |
|---|---|---|
| **Ruan Trizotti** | RF01 (Mapa de Vagas em Tempo Real) + RF03 (Vagas Reservadas) | `routes/mapa.py`, `routes/reservadas.py`, `models/vagas.py`, `templates/mapa.html`, `static/js/mapa.js` |
| **Adolfo Mendonca** | RF02 (Reporte Manual de Vagas) | `routes/reservadas.py`, `models/vagas.py`, `static/js/mapa.js`, `templates/mapa.html`, `static/css/style.css`, `database.py` |
| **Arthur Palma**  | RF04 (Acesso Rapido) + RF05 (Multiplataforma) | `routes/auth.py` , `models/usuarios.py` , `templates/login.html` , `database.py` , `app.py` |

## Requisitos Implementados

### RF01 — Mapa de Vagas em Tempo Real
- Mapa visual com vagas coloridas (verde = livre, vermelho = ocupada)
- Atualizacao automatica via polling AJAX a cada 60 segundos
- Resumo por setor com contadores e barra de progresso
- Cache offline no localStorage para funcionamento com Wi-Fi instavel
- Indicador de status online/offline

### RF02 — Reporte Manual de Vagas
- Atualizacao manual de status para vagas de alunos (livre/ocupada)
- Reserva e desreserva manual de vagas de alunos
- Regras de validacao para impedir reserva de vaga ocupada
- Regras para impedir alteracao de status em vaga reservada por aluno
- Endpoints dedicados para reservar e desreservar via API

### RF03 — Identificacao de Vagas Reservadas
- Vagas de funcionarios exibidas em roxo com icone de cadeado
- Modal com alerta de restricao ao clicar em vaga reservada
- Setor da Biblioteca destacado com borda especial
- Bloqueio que impede alunos de alterar status de vagas reservadas
- Legenda visivel com todos os tipos de vaga

## Stack Tecnologica

| Camada | Tecnologia |
|---|---|
| Backend | Python + Flask |
| Frontend | HTML/CSS/JavaScript (Jinja2 templates) |
| Banco de Dados | SQLite (local) |
| Tempo Real | Polling AJAX (60s) |

## Estrutura do Projeto

```
estacionamento-campus/
├── app.py                  # Ponto de entrada do Flask
├── config.py               # Configuracoes
├── database.py             # Inicializacao SQLite + seed de dados
├── requirements.txt        # Dependencias (Flask)
├── models/
│   └── vagas.py            # CRUD de vagas e setores
├── routes/
│   ├── mapa.py             # RF01: rotas do mapa
│   └── reservadas.py       # RF02/RF03: status, reserva e restricoes
├── static/
│   ├── css/style.css       # Estilos visuais
│   └── js/mapa.js          # Polling AJAX, cache, modal e acoes de reserva
└── templates/
    ├── base.html            # Layout base
    └── mapa.html            # Pagina principal do mapa
```

## Como Executar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Executar o servidor
python3 app.py

# 3. Acessar no navegador
# http://localhost:5050
```

O banco de dados SQLite e criado automaticamente na primeira execucao com dados de exemplo (4 setores, 80 vagas).

## API Endpoints

| Metodo | Rota | Descricao |
|---|---|---|
| GET | `/` | Pagina principal do mapa |
| GET | `/api/vagas` | Todas as vagas (JSON) |
| GET | `/api/setores` | Resumo por setor |
| GET | `/api/vagas/setor/<id>` | Vagas de um setor |
| GET | `/api/vagas/reservadas` | Vagas de funcionarios |
| GET | `/api/vagas/<id>/info` | Detalhes de uma vaga |
| POST | `/api/vagas/<id>/status` | Atualizar status (bloqueado para reservadas) |
| POST | `/api/vagas/<id>/reservar` | Reservar vaga de aluno livre |
| POST | `/api/vagas/<id>/desreservar` | Remover reserva de vaga de aluno |
