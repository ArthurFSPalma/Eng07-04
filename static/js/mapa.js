/**
 * mapa.js - Logica do frontend do Mapa de Estacionamento
 *
 * RF01: Polling AJAX a cada 60s, cache offline (localStorage)
 * RF03: Visual de vagas reservadas, modal com alerta, bloqueio de acao
 */

// === CONFIGURACAO ===
const INTERVALO_POLLING = 60; // segundos
let countdown = INTERVALO_POLLING;
let timerInterval = null;

// === INICIALIZACAO ===
document.addEventListener('DOMContentLoaded', () => {
    atualizarMapa();
    iniciarCountdown();
});

// =====================================================
// RF01: POLLING AJAX - Atualiza mapa a cada 60 segundos
// =====================================================

function iniciarCountdown() {
    countdown = INTERVALO_POLLING;
    atualizarCountdownDisplay();

    if (timerInterval) clearInterval(timerInterval);

    timerInterval = setInterval(() => {
        countdown--;
        atualizarCountdownDisplay();

        if (countdown <= 0) {
            atualizarMapa();
            countdown = INTERVALO_POLLING;
        }
    }, 1000);
}

function atualizarCountdownDisplay() {
    const el = document.getElementById('countdown');
    if (el) el.textContent = countdown;
}

async function atualizarMapa() {
    try {
        const response = await fetch('/api/vagas');

        if (!response.ok) throw new Error('Erro na requisicao');

        const dados = await response.json();

        if (dados.sucesso) {
            renderizarMapa(dados.vagas);
            atualizarResumo();
            salvarCache(dados);
            setOnline(true);
            atualizarTimestamp(dados.timestamp);
        }

        countdown = INTERVALO_POLLING;

    } catch (erro) {
        console.warn('[RF01] Falha no polling, usando cache:', erro.message);
        carregarCache();
        setOnline(false);
    }
}

// =====================================================
// RF01: RENDERIZACAO DO MAPA
// RF03: Vagas reservadas com cor roxa e cadeado
// =====================================================

function renderizarMapa(vagas) {
    const container = document.getElementById('mapa-vagas');

    // Agrupa vagas por setor
    const setores = {};
    vagas.forEach(vaga => {
        if (!setores[vaga.setor_id]) {
            setores[vaga.setor_id] = {
                nome: vaga.setor_nome,
                vagas: []
            };
        }
        setores[vaga.setor_id].vagas.push(vaga);
    });

    let html = '';

    // Banner offline (RF01: modo offline)
    html += '<div id="offline-banner" class="offline-banner">';
    html += '📡 Sem conexao. Exibindo dados do cache (ultima atualizacao disponivel).';
    html += '</div>';

    for (const [setorId, setor] of Object.entries(setores)) {
        // RF03: Classe especial para setor da Biblioteca (setor 1)
        const isBiblioteca = setorId === '1';
        const classeExtra = isBiblioteca ? 'biblioteca' : '';

        html += `<div class="setor-bloco ${classeExtra}">`;
        html += `<h3>${setor.nome}</h3>`;
        html += '<div class="vagas-grid">';

        setor.vagas.forEach(vaga => {
            // RF03: Determina classe CSS baseado no tipo e status
            let classeVaga = '';
            let icone = '';

            if (vaga.tipo === 'funcionario') {
                // RF03: Vaga reservada - sempre roxa independente do status
                classeVaga = 'reservada';
                icone = vaga.status === 'livre' ? '🔓' : '🔒';
            } else if (vaga.reservado === 1) {
                classeVaga = 'reserva-aluno';
                icone = '🟦';
            } else {
                classeVaga = vaga.status;
                icone = vaga.status === 'livre' ? '✅' : '🚗';
            }

            html += `
                <div class="vaga ${classeVaga}"
                     data-id="${vaga.id}"
                     data-tipo="${vaga.tipo}"
                     data-status="${vaga.status}"
                     data-reservado="${vaga.reservado}"
                     onclick="abrirModal(${vaga.id})"
                     title="Vaga ${vaga.numero} - ${vaga.tipo === 'funcionario' ? 'RESERVADA FUNCIONARIO' : (vaga.reservado === 1 ? 'RESERVADA ALUNO' : vaga.status)}">
                    <span class="vaga-status-icon">${icone}</span>
                    <span class="vaga-numero">${vaga.numero}</span>
                </div>
            `;
        });

        html += '</div></div>';
    }

    container.innerHTML = html;
}

// =====================================================
// RF01: ATUALIZACAO DO RESUMO DOS SETORES
// =====================================================

async function atualizarResumo() {
    try {
        const response = await fetch('/api/setores');
        const dados = await response.json();

        if (dados.sucesso) {
            dados.setores.forEach(setor => {
                const livresEl = document.getElementById(`livres-${setor.id}`);
                const ocupadasEl = document.getElementById(`ocupadas-${setor.id}`);
                const reservadasAlunoEl = document.getElementById(`reservadas-aluno-${setor.id}`);

                const totalLivres = setor.livres_aluno + setor.livres_func;
                const totalOcupadas = setor.ocupadas_aluno + setor.ocupadas_func;

                if (livresEl) livresEl.textContent = totalLivres;
                if (ocupadasEl) ocupadasEl.textContent = totalOcupadas;
                if (reservadasAlunoEl) reservadasAlunoEl.textContent = setor.reservadas_aluno;

                // Atualiza barra de progresso
                const card = document.querySelector(`.resumo-card[data-setor-id="${setor.id}"]`);
                if (card) {
                    const barra = card.querySelector('.barra-fill');
                    const percentual = setor.total_vagas > 0
                        ? Math.round((totalLivres / setor.total_vagas) * 100)
                        : 0;
                    if (barra) barra.style.width = `${percentual}%`;

                    const small = card.querySelector('small');
                    if (small) small.textContent = `${percentual}% disponivel`;
                }
            });
        }
    } catch (erro) {
        console.warn('[RF01] Erro ao atualizar resumo:', erro.message);
    }
}

// =====================================================
// RF03: MODAL DE DETALHES DA VAGA
// =====================================================

async function abrirModal(vagaId) {
    const modal = document.getElementById('modal-vaga');
    const body = document.getElementById('modal-body');

    try {
        const response = await fetch(`/api/vagas/${vagaId}/info`);
        const dados = await response.json();

        if (!dados.sucesso) {
            body.innerHTML = '<p>Erro ao carregar informacoes da vaga.</p>';
            modal.style.display = 'flex';
            return;
        }

        const vaga = dados.vaga;
        const isReservada = dados.is_reservada;
        const isReservadaAluno = vaga.tipo === 'aluno' && vaga.reservado === 1;
        const classeStatus = isReservada ? 'reservada' : (isReservadaAluno ? 'reserva-aluno' : vaga.status);

        let html = '';

        // Header do modal
        html += '<div class="modal-vaga-header">';
        html += `<div class="modal-vaga-badge ${classeStatus}">`;
        html += isReservada ? '🔒' : (vaga.status === 'livre' ? '✅' : '🚗');
        html += '</div>';
        html += '<div>';
        html += `<h2>Vaga ${vaga.numero}</h2>`;
        html += `<p style="color:#666; font-size:0.85rem">${vaga.setor_nome}</p>`;
        html += '</div></div>';

        // Informacoes
        html += '<div class="modal-info">';
        const statusTexto = isReservadaAluno
            ? '🔵 Reservada (Aluno)'
            : (vaga.status === 'livre' ? '🟢 Livre' : '🔴 Ocupada');
        html += `<p><strong>Status:</strong> ${statusTexto}</p>`;
        html += `<p><strong>Tipo:</strong> ${vaga.tipo === 'funcionario' ? '🔒 Funcionario' : '🎓 Aluno'}</p>`;
        html += `<p><strong>Ultima atualizacao:</strong> ${vaga.atualizado_em}</p>`;
        html += '</div>';

        // RF03: Alerta especial para vagas reservadas
        if (isReservada && dados.restricao) {
            html += '<div class="alerta-reservada">';
            html += `<div class="alerta-titulo">⚠️ VAGA RESERVADA</div>`;
            html += `<div class="alerta-texto">${dados.restricao.mensagem}</div>`;
            html += `<div class="alerta-texto" style="margin-top:4px"><strong>Tipo autorizado:</strong> ${dados.restricao.tipo_autorizado}</div>`;
            html += `<div class="alerta-texto" style="margin-top:4px">${dados.restricao.alerta}</div>`;
            html += '</div>';
        }

        // Botoes de acao
        html += '<div class="modal-actions">';

        if (isReservada) {
            // RF03: Botoes desabilitados para vagas reservadas
            html += '<button class="btn btn-livre" disabled title="Vagas reservadas nao podem ser alteradas">🔒 Marcar Livre</button>';
            html += '<button class="btn btn-ocupada" disabled title="Vagas reservadas nao podem ser alteradas">🔒 Marcar Ocupada</button>';
        } else {
            // Vagas de alunos podem ser alteradas
            html += `<button class="btn btn-livre" onclick="alterarStatus(${vaga.id}, 'livre')" ${(vaga.status === 'livre' || isReservadaAluno) ? 'disabled' : ''}>✅ Marcar Livre</button>`;
            html += `<button class="btn btn-ocupada" onclick="alterarStatus(${vaga.id}, 'ocupada')" ${(vaga.status === 'ocupada' || isReservadaAluno) ? 'disabled' : ''}>🚗 Marcar Ocupada</button>`;

            if (isReservadaAluno) {
                html += `<button class="btn btn-desreservar" onclick="desreservarVaga(${vaga.id})">❌ Desreservar</button>`;
            } else {
                html += `<button class="btn btn-reservar" onclick="reservarVaga(${vaga.id})" ${vaga.status !== 'livre' ? 'disabled' : ''}>🟦 Reservar</button>`;
            }
        }

        html += '<button class="btn btn-fechar" onclick="fecharModal()">Fechar</button>';
        html += '</div>';

        body.innerHTML = html;
        modal.style.display = 'flex';

    } catch (erro) {
        body.innerHTML = '<p>Erro de conexao. Tente novamente.</p>';
        modal.style.display = 'flex';
    }
}

function fecharModal() {
    document.getElementById('modal-vaga').style.display = 'none';
}

// Fecha modal clicando fora
document.addEventListener('click', (e) => {
    const modal = document.getElementById('modal-vaga');
    if (e.target === modal) {
        fecharModal();
    }
});

// =====================================================
// RF03: ALTERAR STATUS DA VAGA (com bloqueio de reservadas)
// =====================================================

async function alterarStatus(vagaId, novoStatus) {
    try {
        const response = await fetch(`/api/vagas/${vagaId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: novoStatus })
        });

        const dados = await response.json();

        if (dados.sucesso) {
            fecharModal();
            atualizarMapa(); // Recarrega o mapa imediatamente
        } else {
            // RF03: Mostra erro (ex: tentativa de alterar vaga reservada)
            alert(dados.erro || 'Erro ao atualizar vaga.');
        }

    } catch (erro) {
        alert('Erro de conexao. Tente novamente.');
    }
}

async function reservarVaga(vagaId) {
    try {
        const response = await fetch(`/api/vagas/${vagaId}/reservar`, { method: 'POST' });
        const dados = await response.json();

        if (dados.sucesso) {
            fecharModal();
            atualizarMapa();
        } else {
            alert(dados.erro || 'Erro ao reservar vaga.');
        }
    } catch (erro) {
        alert('Erro de conexao. Tente novamente.');
    }
}

async function desreservarVaga(vagaId) {
    try {
        const response = await fetch(`/api/vagas/${vagaId}/desreservar`, { method: 'POST' });
        const dados = await response.json();

        if (dados.sucesso) {
            fecharModal();
            atualizarMapa();
        } else {
            alert(dados.erro || 'Erro ao desreservar vaga.');
        }
    } catch (erro) {
        alert('Erro de conexao. Tente novamente.');
    }
}

// =====================================================
// RF01: CACHE OFFLINE (localStorage)
// =====================================================

function salvarCache(dados) {
    try {
        localStorage.setItem('estacionamento_cache', JSON.stringify({
            vagas: dados.vagas,
            timestamp: dados.timestamp,
            salvo_em: new Date().toISOString()
        }));
    } catch (e) {
        console.warn('[RF01] Erro ao salvar cache:', e.message);
    }
}

function carregarCache() {
    try {
        const cache = localStorage.getItem('estacionamento_cache');
        if (cache) {
            const dados = JSON.parse(cache);
            renderizarMapa(dados.vagas);
            atualizarTimestamp(`Cache: ${dados.timestamp}`);

            // Mostra banner offline
            const banner = document.getElementById('offline-banner');
            if (banner) banner.classList.add('visivel');
        } else {
            document.getElementById('mapa-vagas').innerHTML =
                '<div class="loading">Sem dados em cache. Conecte-se a internet.</div>';
        }
    } catch (e) {
        console.warn('[RF01] Erro ao carregar cache:', e.message);
    }
}

// =====================================================
// STATUS DE CONEXAO
// =====================================================

function setOnline(online) {
    const badge = document.getElementById('status-conexao');
    if (badge) {
        badge.textContent = online ? '🟢 Online' : '🔴 Offline';
        badge.className = `status-badge ${online ? 'online' : 'offline'}`;
    }

    const banner = document.getElementById('offline-banner');
    if (banner && online) {
        banner.classList.remove('visivel');
    }
}

function atualizarTimestamp(ts) {
    const el = document.getElementById('ultima-atualizacao');
    if (el) el.textContent = `Atualizado: ${ts}`;
}
