/**
 * mapa.js - Frontend do Mapa de Estacionamento
 * 6 estados visuais, reservado_por (aluno/funcionario/null)
 * Funcionario pode reservar qualquer vaga e sobrescrever aluno
 */

const INTERVALO_POLLING = 60;
let countdown = INTERVALO_POLLING;
let timerInterval = null;

const SVG = {
    check: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>',
    car: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>',
    lock: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    bookmark: '<svg class="vaga-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
    user: '<svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>',
    shield: '<svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
    alertTri: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    wifi: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/></svg>',
    wifiOff: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/><path d="M10.71 5.05A16 16 0 0 1 22.56 9"/><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/></svg>',
    checkW: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>',
    carW: '<svg width="22" height="22" viewBox="0 0 24 24" fill="white"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>',
    lockW: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    bookmarkW: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>'
};

// === Determinar estado visual da vaga ===
function getEstadoVaga(vaga) {
    const isFunc = vaga.tipo === 'funcionario';

    if (vaga.reservado_por === 'funcionario') {
        return { classe: 'reserva-func', icone: SVG.lock, badge: SVG.shield, title: 'Reservada por Funcionario', badgeClass: 'reserva-func' };
    }
    if (vaga.reservado_por === 'aluno') {
        return { classe: 'reserva-aluno', icone: SVG.bookmark, badge: SVG.user, title: 'Reservada por Aluno', badgeClass: 'reserva-aluno' };
    }
    if (isFunc && vaga.status === 'livre') {
        return { classe: 'livre-func', icone: SVG.check, badge: SVG.shield, title: 'Livre (Funcionario)', badgeClass: 'livre-func' };
    }
    if (isFunc && vaga.status === 'ocupada') {
        return { classe: 'ocupada-func', icone: SVG.car, badge: SVG.shield, title: 'Ocupada (Funcionario)', badgeClass: 'ocupada-func' };
    }
    if (vaga.status === 'ocupada') {
        return { classe: 'ocupada-aluno', icone: SVG.car, badge: null, title: 'Ocupada', badgeClass: '' };
    }
    return { classe: 'livre-aluno', icone: SVG.check, badge: null, title: 'Livre', badgeClass: '' };
}

document.addEventListener('DOMContentLoaded', () => {
    atualizarMapa();
    iniciarCountdown();
});

function iniciarCountdown() {
    countdown = INTERVALO_POLLING;
    atualizarCountdownDisplay();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        countdown--;
        atualizarCountdownDisplay();
        if (countdown <= 0) { atualizarMapa(); countdown = INTERVALO_POLLING; }
    }, 1000);
}

function atualizarCountdownDisplay() {
    const el = document.getElementById('countdown');
    if (el) el.textContent = countdown;
}

async function atualizarMapa() {
    try {
        const response = await fetch('/api/vagas');
        if (response.status === 401) { window.location.href = '/auth/login'; return; }
        if (!response.ok) throw new Error('Erro');
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
        carregarCache();
        setOnline(false);
    }
}

// === MAPA ===

function renderizarMapa(vagas) {
    const container = document.getElementById('mapa-vagas');
    const setores = {};
    vagas.forEach(v => {
        if (!setores[v.setor_id]) setores[v.setor_id] = { nome: v.setor_nome, vagas: [] };
        setores[v.setor_id].vagas.push(v);
    });

    let html = '<div id="offline-banner" class="offline-banner">Sem conexao. Exibindo dados em cache.</div>';

    for (const [setorId, setor] of Object.entries(setores)) {
        const cls = setorId === '1' ? 'biblioteca' : '';
        html += `<div class="setor-bloco ${cls}"><h3>${setor.nome}</h3><div class="vagas-grid">`;

        setor.vagas.forEach(vaga => {
            const est = getEstadoVaga(vaga);
            const badgeHtml = est.badge ? `<span class="vaga-badge">${est.badge}</span>` : '';

            html += `<div class="vaga ${est.classe}" onclick="abrirModal(${vaga.id})" title="Vaga ${vaga.numero} - ${est.title}">
                ${badgeHtml}${est.icone}<span class="vaga-numero">${vaga.numero}</span>
            </div>`;
        });

        html += '</div></div>';
    }
    container.innerHTML = html;
}

// === RESUMO ===

async function atualizarResumo() {
    try {
        const response = await fetch('/api/setores');
        const dados = await response.json();
        if (!dados.sucesso) return;
        dados.setores.forEach(s => {
            const el = (id) => document.getElementById(id);
            if (el(`livres-${s.id}`)) el(`livres-${s.id}`).textContent = s.livres;
            if (el(`ocupadas-${s.id}`)) el(`ocupadas-${s.id}`).textContent = s.ocupadas;
            if (el(`res-func-${s.id}`)) el(`res-func-${s.id}`).textContent = s.reservadas_func;
            if (el(`res-aluno-${s.id}`)) el(`res-aluno-${s.id}`).textContent = s.reservadas_aluno;

            const card = document.querySelector(`.resumo-card[data-setor-id="${s.id}"]`);
            if (card) {
                const pct = s.total_vagas > 0 ? Math.round((s.livres / s.total_vagas) * 100) : 0;
                const barra = card.querySelector('.barra-fill');
                if (barra) barra.style.width = `${pct}%`;
                const sm = card.querySelector('small');
                if (sm) sm.textContent = `${pct}% disponivel`;
            }
        });
    } catch (e) {}
}

// === MODAL ===

async function abrirModal(vagaId) {
    const modal = document.getElementById('modal-vaga');
    const body = document.getElementById('modal-body');

    try {
        const response = await fetch(`/api/vagas/${vagaId}/info`);
        const dados = await response.json();
        if (!dados.sucesso) { body.innerHTML = '<p>Erro ao carregar.</p>'; modal.style.display = 'flex'; return; }

        const vaga = dados.vaga;
        const userTipo = dados.usuario_tipo || 'aluno';
        const est = getEstadoVaga(vaga);

        let html = '';

        // Header
        const badgeIcon = vaga.reservado_por ? SVG.lockW : (vaga.status === 'livre' ? SVG.checkW : SVG.carW);
        html += `<div class="modal-vaga-header">
            <div class="modal-vaga-badge ${est.classe}">${badgeIcon}</div>
            <div><h2 style="font-size:1.2rem;color:#1f2937">Vaga ${vaga.numero}</h2>
            <p style="color:#9ca3af;font-size:0.82rem">${vaga.setor_nome}</p></div></div>`;

        // Info
        html += `<div class="modal-info">
            <p><strong>Status:</strong> ${est.title}</p>
            <p><strong>Tipo de vaga:</strong> ${vaga.tipo === 'funcionario' ? 'Funcionario' : 'Aluno'}</p>
            <p><strong>Reservado por:</strong> ${vaga.reservado_por || 'Ninguem'}</p>
            <p><strong>Atualizado:</strong> ${vaga.atualizado_em}</p>
        </div>`;

        // Alerta para alunos em vaga de funcionario
        if (vaga.tipo === 'funcionario' && userTipo === 'aluno') {
            html += `<div class="alerta-reservada">
                <div class="alerta-titulo">${SVG.alertTri} VAGA DE FUNCIONARIO</div>
                <div class="alerta-texto">Esta vaga e exclusiva para funcionarios e docentes.</div>
                <div class="alerta-texto" style="margin-top:3px">Alunos nao podem reservar ou alterar esta vaga.</div>
            </div>`;
        }

        // Alerta para aluno quando reservada por funcionario
        if (vaga.reservado_por === 'funcionario' && userTipo === 'aluno') {
            html += `<div class="alerta-reservada">
                <div class="alerta-titulo">${SVG.alertTri} RESERVADA POR FUNCIONARIO</div>
                <div class="alerta-texto">Um funcionario reservou esta vaga. Alunos nao podem alterar.</div>
            </div>`;
        }

        // Botoes
        html += '<div class="modal-actions">';

        const isFuncAdmin = userTipo === 'funcionario' || userTipo === 'admin';
        const isAluno = userTipo === 'aluno';
        const isVagaFunc = vaga.tipo === 'funcionario';
        const isReservado = vaga.reservado_por !== null;
        const reservadoPorFunc = vaga.reservado_por === 'funcionario';
        const reservadoPorAluno = vaga.reservado_por === 'aluno';

        // Aluno em vaga de funcionario -> sem permissao
        if (isAluno && isVagaFunc) {
            html += '<button class="btn btn-fechar" style="flex:1" disabled>Sem permissao</button>';
        }
        // Aluno em vaga reservada por funcionario -> sem permissao
        else if (isAluno && reservadoPorFunc) {
            html += '<button class="btn btn-fechar" style="flex:1" disabled>Sem permissao</button>';
        }
        // Aluno com permissao (vaga de aluno)
        else if (isAluno) {
            html += `<button class="btn btn-livre" onclick="alterarStatus(${vaga.id},'livre')" ${(vaga.status==='livre'||isReservado)?'disabled':''}>Livre</button>`;
            html += `<button class="btn btn-ocupada" onclick="alterarStatus(${vaga.id},'ocupada')" ${(vaga.status==='ocupada'||isReservado)?'disabled':''}>Ocupada</button>`;
            if (reservadoPorAluno) {
                html += `<button class="btn btn-desreservar" onclick="desreservarVaga(${vaga.id})">Desreservar</button>`;
            } else if (!isReservado) {
                html += `<button class="btn btn-reservar" onclick="reservarVaga(${vaga.id})" ${vaga.status!=='livre'?'disabled':''}>Reservar</button>`;
            }
        }
        // Funcionario / Admin
        else if (isFuncAdmin) {
            html += `<button class="btn btn-livre" onclick="alterarStatus(${vaga.id},'livre')" ${(vaga.status==='livre'||isReservado)?'disabled':''}>Livre</button>`;
            html += `<button class="btn btn-ocupada" onclick="alterarStatus(${vaga.id},'ocupada')" ${(vaga.status==='ocupada'||isReservado)?'disabled':''}>Ocupada</button>`;
            if (isReservado) {
                html += `<button class="btn btn-desreservar" onclick="desreservarVaga(${vaga.id})">Desreservar</button>`;
            } else {
                html += `<button class="btn btn-reservar" onclick="reservarVaga(${vaga.id})" ${vaga.status!=='livre'?'disabled':''}>Reservar</button>`;
            }
        }

        html += '<button class="btn btn-fechar" onclick="fecharModal()">Fechar</button></div>';

        body.innerHTML = html;
        modal.style.display = 'flex';
    } catch (e) {
        body.innerHTML = '<p>Erro de conexao.</p>';
        modal.style.display = 'flex';
    }
}

function fecharModal() { document.getElementById('modal-vaga').style.display = 'none'; }
document.addEventListener('click', e => { if (e.target === document.getElementById('modal-vaga')) fecharModal(); });

// === ACOES ===

async function alterarStatus(vagaId, novoStatus) {
    try {
        const r = await fetch(`/api/vagas/${vagaId}/status`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({status:novoStatus}) });
        const d = await r.json();
        if (d.sucesso) { fecharModal(); atualizarMapa(); } else { alert(d.erro); }
    } catch(e) { alert('Erro de conexao.'); }
}

async function reservarVaga(vagaId) {
    try {
        const r = await fetch(`/api/vagas/${vagaId}/reservar`, { method:'POST' });
        const d = await r.json();
        if (d.sucesso) { fecharModal(); atualizarMapa(); } else { alert(d.erro); }
    } catch(e) { alert('Erro de conexao.'); }
}

async function desreservarVaga(vagaId) {
    try {
        const r = await fetch(`/api/vagas/${vagaId}/desreservar`, { method:'POST' });
        const d = await r.json();
        if (d.sucesso) { fecharModal(); atualizarMapa(); } else { alert(d.erro); }
    } catch(e) { alert('Erro de conexao.'); }
}

// === CACHE ===

function salvarCache(dados) {
    try { localStorage.setItem('est_cache', JSON.stringify({ vagas:dados.vagas, timestamp:dados.timestamp })); } catch(e) {}
}

function carregarCache() {
    try {
        const c = localStorage.getItem('est_cache');
        if (c) { const d=JSON.parse(c); renderizarMapa(d.vagas); atualizarTimestamp('Cache: '+d.timestamp); const b=document.getElementById('offline-banner'); if(b)b.classList.add('visivel'); }
        else { document.getElementById('mapa-vagas').innerHTML='<div class="loading">Sem dados em cache.</div>'; }
    } catch(e) {}
}

function setOnline(online) {
    const badge = document.getElementById('status-conexao');
    if (badge) { badge.innerHTML = online ? `${SVG.wifi} <span>Online</span>` : `${SVG.wifiOff} <span>Offline</span>`; badge.className = `status-badge ${online?'online':'offline'}`; }
    const b = document.getElementById('offline-banner'); if(b&&online) b.classList.remove('visivel');
}

function atualizarTimestamp(ts) { const el=document.getElementById('ultima-atualizacao'); if(el) el.textContent='Atualizado: '+ts; }
