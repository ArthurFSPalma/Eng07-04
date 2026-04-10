/**
 * mapa.js - Frontend do Mapa de Estacionamento
 * RF01: Polling AJAX 60s, cache offline
 * RF03: Visual de vagas reservadas, modal com alerta, bloqueio
 * Icones SVG (sem emojis)
 */

const INTERVALO_POLLING = 60;
let countdown = INTERVALO_POLLING;
let timerInterval = null;

// SVG icons
const SVG = {
    check: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    car: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>',
    lock: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    lockOpen: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>',
    bookmark: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
    lockSmall: '<svg class="vaga-icon-lock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    alertTri: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    wifi: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/></svg>',
    wifiOff: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/><path d="M10.71 5.05A16 16 0 0 1 22.56 9"/><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/></svg>',
    checkBadge: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    carBadge: '<svg width="22" height="22" viewBox="0 0 24 24" fill="white"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>',
    lockBadge: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
};

document.addEventListener('DOMContentLoaded', () => {
    atualizarMapa();
    iniciarCountdown();
});

// === COUNTDOWN / POLLING ===

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
        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
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

// === RENDERIZACAO DO MAPA ===

function renderizarMapa(vagas) {
    const container = document.getElementById('mapa-vagas');
    const setores = {};
    vagas.forEach(vaga => {
        if (!setores[vaga.setor_id]) {
            setores[vaga.setor_id] = { nome: vaga.setor_nome, vagas: [] };
        }
        setores[vaga.setor_id].vagas.push(vaga);
    });

    let html = '';
    html += '<div id="offline-banner" class="offline-banner">';
    html += `${SVG.wifiOff} Sem conexao. Exibindo dados em cache.`;
    html += '</div>';

    for (const [setorId, setor] of Object.entries(setores)) {
        const isBiblioteca = setorId === '1';
        const classeExtra = isBiblioteca ? 'biblioteca' : '';

        html += `<div class="setor-bloco ${classeExtra}">`;
        html += `<h3>${setor.nome}</h3>`;
        html += '<div class="vagas-grid">';

        setor.vagas.forEach(vaga => {
            let classeVaga = '';
            let icone = '';
            let lockIcon = '';

            if (vaga.tipo === 'funcionario' && vaga.reservado === 1) {
                // Vaga de funcionario RESERVADA -> roxo com cadeado
                classeVaga = 'reservada';
                icone = SVG.lock;
                lockIcon = SVG.lockSmall;
            } else if (vaga.tipo === 'funcionario' && vaga.reservado === 0) {
                // Vaga de funcionario NAO reservada -> livre/ocupada normal mas com marcador
                classeVaga = vaga.status + ' func-vaga';
                icone = vaga.status === 'livre' ? SVG.check : SVG.car;
                lockIcon = SVG.lockSmall;
            } else if (vaga.tipo === 'aluno' && vaga.reservado === 1) {
                // Vaga de aluno RESERVADA -> azul
                classeVaga = 'reserva-aluno';
                icone = SVG.bookmark;
            } else {
                // Vaga de aluno normal
                classeVaga = vaga.status;
                icone = vaga.status === 'livre' ? SVG.check : SVG.car;
            }

            const titleText = (vaga.reservado === 1)
                ? (vaga.tipo === 'funcionario' ? 'RESERVADA FUNCIONARIO' : 'RESERVADA ALUNO')
                : vaga.status;

            html += `
                <div class="vaga ${classeVaga}"
                     data-id="${vaga.id}"
                     onclick="abrirModal(${vaga.id})"
                     title="Vaga ${vaga.numero} - ${titleText}">
                    ${lockIcon}
                    ${icone}
                    <span class="vaga-numero">${vaga.numero}</span>
                </div>
            `;
        });

        html += '</div></div>';
    }

    container.innerHTML = html;
}

// === ATUALIZACAO DO RESUMO ===

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

                const card = document.querySelector(`.resumo-card[data-setor-id="${setor.id}"]`);
                if (card) {
                    const barra = card.querySelector('.barra-fill');
                    const percentual = setor.total_vagas > 0 ? Math.round((totalLivres / setor.total_vagas) * 100) : 0;
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

// === MODAL ===

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
        const userTipo = dados.usuario_tipo || 'aluno';
        const isVagaFunc = vaga.tipo === 'funcionario';
        const isReservado = vaga.reservado === 1;
        const isReservadaFunc = isVagaFunc && isReservado;
        const isReservadaAluno = !isVagaFunc && isReservado;

        // Classe visual do badge
        let classeStatus = vaga.status;
        if (isReservadaFunc) classeStatus = 'reservada';
        else if (isReservadaAluno) classeStatus = 'reserva-aluno';

        let html = '';

        // Header
        html += '<div class="modal-vaga-header">';
        html += `<div class="modal-vaga-badge ${classeStatus}">`;
        html += isReservado ? SVG.lockBadge : (vaga.status === 'livre' ? SVG.checkBadge : SVG.carBadge);
        html += '</div>';
        html += '<div>';
        html += `<h2 style="font-size:1.2rem;color:#1f2937">Vaga ${vaga.numero}</h2>`;
        html += `<p style="color:#9ca3af;font-size:0.82rem">${vaga.setor_nome}</p>`;
        html += '</div></div>';

        // Info
        html += '<div class="modal-info">';
        let statusTexto = vaga.status === 'livre' ? 'Livre' : 'Ocupada';
        if (isReservadaFunc) statusTexto = 'Reservada (Funcionario)';
        else if (isReservadaAluno) statusTexto = 'Reservada (Aluno)';
        html += `<p><strong>Status:</strong> ${statusTexto}</p>`;
        html += `<p><strong>Tipo de vaga:</strong> ${isVagaFunc ? 'Funcionario' : 'Aluno'}</p>`;
        html += `<p><strong>Atualizado:</strong> ${vaga.atualizado_em}</p>`;
        html += '</div>';

        // Alerta para alunos em vagas de funcionario
        if (isVagaFunc && userTipo === 'aluno' && dados.restricao) {
            html += '<div class="alerta-reservada">';
            html += `<div class="alerta-titulo">${SVG.alertTri} VAGA DE FUNCIONARIO</div>`;
            html += `<div class="alerta-texto">${dados.restricao.mensagem}</div>`;
            html += `<div class="alerta-texto" style="margin-top:3px">${dados.restricao.alerta}</div>`;
            html += '</div>';
        }

        // Botoes
        html += '<div class="modal-actions">';

        const podeAlterar = (isVagaFunc && (userTipo === 'funcionario' || userTipo === 'admin'))
                         || (!isVagaFunc && (userTipo === 'aluno' || userTipo === 'admin'));

        if (podeAlterar) {
            // Botoes de status (desabilitados se reservado)
            html += `<button class="btn btn-livre" onclick="alterarStatus(${vaga.id}, 'livre')" ${(vaga.status === 'livre' || isReservado) ? 'disabled' : ''}>Livre</button>`;
            html += `<button class="btn btn-ocupada" onclick="alterarStatus(${vaga.id}, 'ocupada')" ${(vaga.status === 'ocupada' || isReservado) ? 'disabled' : ''}>Ocupada</button>`;

            // Reservar / Desreservar
            if (isReservado) {
                html += `<button class="btn btn-desreservar" onclick="desreservarVaga(${vaga.id})">Desreservar</button>`;
            } else {
                html += `<button class="btn btn-reservar" onclick="reservarVaga(${vaga.id})" ${vaga.status !== 'livre' ? 'disabled' : ''}>Reservar</button>`;
            }
        } else {
            // Usuario sem permissao nesta vaga
            html += '<button class="btn btn-livre" disabled>Sem permissao</button>';
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

document.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal-vaga')) fecharModal();
});

// === ACOES ===

async function alterarStatus(vagaId, novoStatus) {
    try {
        const response = await fetch(`/api/vagas/${vagaId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: novoStatus })
        });
        const dados = await response.json();
        if (dados.sucesso) { fecharModal(); atualizarMapa(); }
        else { alert(dados.erro || 'Erro ao atualizar vaga.'); }
    } catch (erro) { alert('Erro de conexao.'); }
}

async function reservarVaga(vagaId) {
    try {
        const response = await fetch(`/api/vagas/${vagaId}/reservar`, { method: 'POST' });
        const dados = await response.json();
        if (dados.sucesso) { fecharModal(); atualizarMapa(); }
        else { alert(dados.erro || 'Erro ao reservar vaga.'); }
    } catch (erro) { alert('Erro de conexao.'); }
}

async function desreservarVaga(vagaId) {
    try {
        const response = await fetch(`/api/vagas/${vagaId}/desreservar`, { method: 'POST' });
        const dados = await response.json();
        if (dados.sucesso) { fecharModal(); atualizarMapa(); }
        else { alert(dados.erro || 'Erro ao desreservar.'); }
    } catch (erro) { alert('Erro de conexao.'); }
}

// === CACHE OFFLINE ===

function salvarCache(dados) {
    try {
        localStorage.setItem('estacionamento_cache', JSON.stringify({
            vagas: dados.vagas, timestamp: dados.timestamp, salvo_em: new Date().toISOString()
        }));
    } catch (e) { console.warn('[RF01] Erro ao salvar cache:', e.message); }
}

function carregarCache() {
    try {
        const cache = localStorage.getItem('estacionamento_cache');
        if (cache) {
            const dados = JSON.parse(cache);
            renderizarMapa(dados.vagas);
            atualizarTimestamp(`Cache: ${dados.timestamp}`);
            const banner = document.getElementById('offline-banner');
            if (banner) banner.classList.add('visivel');
        } else {
            document.getElementById('mapa-vagas').innerHTML = '<div class="loading">Sem dados em cache.</div>';
        }
    } catch (e) { console.warn('[RF01] Erro ao carregar cache:', e.message); }
}

// === STATUS ===

function setOnline(online) {
    const badge = document.getElementById('status-conexao');
    if (badge) {
        badge.innerHTML = online
            ? `${SVG.wifi} <span>Online</span>`
            : `${SVG.wifiOff} <span>Offline</span>`;
        badge.className = `status-badge ${online ? 'online' : 'offline'}`;
    }
    const banner = document.getElementById('offline-banner');
    if (banner && online) banner.classList.remove('visivel');
}

function atualizarTimestamp(ts) {
    const el = document.getElementById('ultima-atualizacao');
    if (el) el.textContent = `Atualizado: ${ts}`;
}
