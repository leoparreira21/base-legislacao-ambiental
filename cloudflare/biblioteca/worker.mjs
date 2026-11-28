// Worker da biblioteca: arquivos estáticos (a biblioteca e as páginas das normas, em ASSETS)
// e a API de consulta no texto dos dispositivos (D1 "legislacao-ambiental", em DB).
// A API é a que Leo publicou em 14/11/2026 pelo painel; aqui ela passou a ser versionada e
// a responder com JSON de erro (consulta FTS mal formada derrubava o Worker com erro 1101).
// Em 27/11/2026 entraram as regras que Leo montou no chat do Cloudflare (publicadas por
// fora do repositório, o que apagou a biblioteca): consulta simples e avançada, filtros
// por tipo de norma, esfera, ano e revogados, /api/filtros e os termos para o destaque.
// Em 28/11/2026: registro das buscas sem resultado (tabela buscas_sem_resultado) e a
// página /api/lacunas, protegida pelo secret LACUNAS_TOKEN.


// ── Consulta simples: o Worker remove acentos e monta a expressão FTS5 ──────────────────
// "resíduos sólidos" → residuos OR residuo OR solidos OR solido OR "residuos solidos"
// ── Consulta avançada: a expressão vai ao FTS5 como foi escrita (AND, OR, NOT, NEAR,
// "frase", prefixo*, parênteses) ─────────────────────────────────────────────────────────
const MAPA_ACENTOS = { 'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'õ': 'o', 'ô': 'o', 'ú': 'u', 'ç': 'c' };
const OPERADORES_FTS = new Set(['and', 'or', 'not', 'near']);
const LIMITE_CLAUSULAS = 16; // teto de variações geradas na consulta simples

const normalizar = (texto) => String(texto).toLowerCase()
  .replace(/[áàãâéêíóõôúç]/g, (c) => MAPA_ACENTOS[c] || c)
  .replace(/[^a-z0-9]+/g, ' ').trim();

function extrairTermos(texto) {
  const termos = [];
  for (const t of normalizar(texto).split(' ')) {
    if (!t || t.length < 2 || OPERADORES_FTS.has(t) || termos.includes(t)) continue;
    termos.push(t);
  }
  return termos;
}

// Variações de plural (o FTS5 não faz stemming). Candidato errado não casa nada.
function variantesPlural(t) {
  const n = t.length;
  const v = [];
  const add = (x) => { if (x && x.length >= 3 && x !== t && !v.includes(x)) v.push(x); };
  if (t.endsWith('s')) {
    if (n >= 5 && /(oes|aes|aos)$/.test(t)) add(t.slice(0, -3) + 'ao'); // poluicoes, paes, orgaos
    else if (n >= 4 && t.endsWith('is')) { add(t.slice(0, -2) + 'l'); add(t.slice(0, -1)); } // animais, leis
    else if (n >= 5 && t.endsWith('es')) { add(t.slice(0, -2)); add(t.slice(0, -1)); } // autores, fases
    else if (n >= 4) add(t.slice(0, -1)); // residuos
  } else {
    const u = t[n - 1];
    if ('aeiou'.includes(u)) add(t + 's');
    else if (u === 'r' || u === 'z') add(t + 'es');
    else if (u === 'l') add(t.slice(0, -1) + 'is');
    else if (u === 'm') add(t.slice(0, -1) + 'ns');
    else if (n >= 5 && t.endsWith('ao')) { add(t.slice(0, -2) + 'oes'); add(t.slice(0, -2) + 'aos'); }
  }
  return v;
}

// combinações de tamanho k que preservam a ordem dos termos
function combinacoes(n, k) {
  const out = [];
  const idx = Array.from({ length: k }, (_, i) => i);
  for (;;) {
    out.push(idx.slice());
    let i = k - 1;
    while (i >= 0 && idx[i] === n - k + i) i--;
    if (i < 0) return out;
    idx[i]++;
    for (let j = i + 1; j < k; j++) idx[j] = idx[j - 1] + 1;
  }
}

export function construirConsultaSimples(texto) {
  const termos = extrairTermos(texto);
  if (!termos.length) return null;
  const clausulas = [];
  const push = (c) => { if (clausulas.length < LIMITE_CLAUSULAS && !clausulas.includes(c)) clausulas.push(c); };
  for (const t of termos) { push(t); variantesPlural(t).forEach(push); }
  for (let tam = 2; tam <= termos.length && clausulas.length < LIMITE_CLAUSULAS; tam++) {
    for (const combo of combinacoes(termos.length, tam)) push(`"${combo.map((i) => termos[i]).join(' ')}"`);
  }
  return clausulas.join(' OR ');
}

// Termos para o destaque no front-end
function termosSimples(texto) {
  const termos = [];
  for (const t of extrairTermos(texto)) termos.push(t, ...variantesPlural(t));
  return [...new Set(termos)];
}

function termosAvancados(expressao) {
  const termos = [];
  const semFrases = String(expressao).replace(/"([^"]+)"/g, (_, frase) => { termos.push(frase.trim()); return ' '; });
  for (const bruto of semFrases.split(/[^\p{L}\p{N}]+/u)) {
    const t = bruto.trim();
    if (!t || t.length < 2 || OPERADORES_FTS.has(t.toLowerCase()) || /^\d+$/.test(t)) continue; // número: distância do NEAR
    termos.push(t);
  }
  return [...new Set(termos)];
}

// modo "simples" (padrão) ou "avancado"; null quando não há o que buscar
function montarConsulta(q, modo) {
  const texto = String(q ?? '').trim();
  if (modo === 'avancado') return texto ? { modo, expressao: texto, termos: termosAvancados(texto) } : null;
  const expressao = construirConsultaSimples(texto);
  return expressao ? { modo: 'simples', expressao, termos: termosSimples(texto) } : null;
}

// ── Filtros laterais (colunas preenchidas a partir do frontmatter) ──────────────────────
const marcadores = (arr) => arr.map(() => '?').join(',');

export function lerFiltros(src) {
  const lista = (v) => String(v ?? '').split(',').map((s) => s.trim()).filter(Boolean);
  const booleano = (v, padrao) => (v === undefined || v === null || v === '' ? padrao : !(v === false || v === 'false' || v === '0'));
  return {
    tipos: lista(src.tipo_norma),
    esferas: lista(src.esfera),
    anos: lista(src.ano).map((a) => parseInt(a, 10)).filter((n) => !Number.isNaN(n)),
    tipoDispositivo: String(src.tipo || '').trim(),
    // so_vigentes é o nome antigo do mesmo filtro
    ocultarRevogados: booleano(src.ocultar_revogados ?? src.so_vigentes, true),
  };
}

// trecho do WHERE (com d = dispositivos e l = legislacoes já no FROM)
function whereFiltros(f) {
  let sql = '';
  const args = [];
  if (f.tipos.length) { sql += ` AND l.tipo_norma IN (${marcadores(f.tipos)})`; args.push(...f.tipos); }
  if (f.esferas.length) { sql += ` AND l.esfera IN (${marcadores(f.esferas)})`; args.push(...f.esferas); }
  if (f.anos.length) { sql += ` AND l.ano IN (${marcadores(f.anos)})`; args.push(...f.anos); }
  if (f.tipoDispositivo) { sql += ' AND d.tipo = ?'; args.push(f.tipoDispositivo); }
  // Norma revogada é a de situacao = 'revogada' (README); a coluna l.revogado foi preenchida
  // pela carga a partir da tag de controle #revogado, que marca dispositivos, e não serve aqui.
  if (f.ocultarRevogados) sql += " AND COALESCE(l.situacao, 'vigente') <> 'revogada' AND d.revogado = 0";
  return { sql, args };
}

const CAMPOS_BUSCA = `
  l.nome        AS legislacao_nome,
  l.slug        AS legislacao_slug,
  l.ementa      AS legislacao_ementa,
  l.categoria   AS legislacao_categoria,
  l.tipo_norma  AS legislacao_tipo_norma,
  l.esfera      AS legislacao_esfera,
  l.ano         AS legislacao_ano,
  l.revogado    AS legislacao_revogado,
  d.rotulo      AS dispositivo_rotulo,
  d.tipo        AS dispositivo_tipo,
  d.texto       AS dispositivo_texto,
  d.estrutura   AS dispositivo_estrutura,
  d.id_html     AS dispositivo_id_html,
  d.revogado    AS dispositivo_revogado`;

// Rótulo completo do dispositivo. No D1, alíneas e itens de artigo vêm só com o próprio
// nome ("alínea \"j\"", "item 2"), sem o artigo e o inciso; dispositivos diferentes com o
// mesmo texto ficavam indistinguíveis na consulta. O caminho é refeito pelo id LexML
// (art19_cpt_inc6_alij → Art. 19, caput, inciso VI, alínea "j").
const ROMANOS = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'], [100, 'C'], [90, 'XC'], [50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']];
const romano = (n) => ROMANOS.reduce((s, [v, r]) => { while (n >= v) { s += r; n -= v; } return s; }, '');
const ordinal = (n) => (Number(n) < 10 ? `${n}º` : String(n));

function caminhoDoId(id) {
  const partes = id.split('_');
  partes.pop(); // o último é o próprio dispositivo, já nomeado no rótulo
  const nomes = [];
  for (let i = 0; i < partes.length; i++) {
    const p = partes[i];
    let m;
    if (p === 'adct') nomes.push('ADCT');
    else if ((m = p.match(/^art(\d+)(?:-([a-z]+))?$/))) nomes.push(`Art. ${ordinal(m[1])}${m[2] ? '-' + m[2].toUpperCase() : ''}`);
    else if (p === 'cpt') nomes.push('caput');
    else if (p === 'par' && partes[i + 1] === 'unico') { nomes.push('parágrafo único'); i++; }
    else if (p === 'par1u') nomes.push('parágrafo único');
    else if ((m = p.match(/^par(\d+)$/))) nomes.push(`§ ${ordinal(m[1])}`);
    else if ((m = p.match(/^inc(\d+)(?:-[a-z]+)?$/))) nomes.push(`inciso ${romano(Number(m[1]))}`);
    else if ((m = p.match(/^ali([a-z])(?:-[a-z]+)?$/))) nomes.push(`alínea "${m[1]}"`);
    else if ((m = p.match(/^item(\d+)(?:-[a-z]+)?$/))) nomes.push(`item ${m[1]}`);
    else if ((m = p.match(/^ite([\d-]+)$/))) nomes.push(`item ${m[1].replace(/-/g, '.')}`);
    else return null; // forma desconhecida: fica o rótulo original
  }
  return nomes.join(', ');
}

export function rotuloCompleto(rotulo, id) {
  if (!rotulo || !id || !/^(alínea|item )/.test(rotulo)) return rotulo;
  const caminho = caminhoDoId(id);
  return caminho ? `${caminho}, ${rotulo}` : rotulo;
}

const comLink = (r) => ({
  ...r,
  dispositivo_rotulo: rotuloCompleto(r.dispositivo_rotulo, r.dispositivo_id_html),
  link: r.dispositivo_id_html ? `${r.legislacao_slug}.html#${r.dispositivo_id_html}` : `${r.legislacao_slug}.html`,
});

async function buscar(env, expressao, filtros, limit = 20) {
  const f = whereFiltros(filtros);
  const { results } = await env.DB.prepare(`SELECT ${CAMPOS_BUSCA}
    FROM dispositivos_fts
    JOIN dispositivos d ON d.id = dispositivos_fts.rowid
    JOIN legislacoes l ON l.id = d.legislacao_id
    WHERE dispositivos_fts MATCH ?${f.sql}
    ORDER BY rank LIMIT ?`).bind(expressao, ...f.args, limit).all();
  const resultados = results.map(comLink);
  return { total: resultados.length, resultados };
}

// Busca agrupada por norma: cada norma aparece uma vez, com o número de dispositivos em
// que a busca aparece e o dispositivo mais relevante (menor rank do FTS5) para abrir.
async function buscarPorNorma(env, expressao, filtros, limit = 100) {
  const f = whereFiltros(filtros);
  const { results } = await env.DB.prepare(`
    WITH hits AS (
      SELECT d.legislacao_id, d.rotulo, d.tipo, d.texto, d.estrutura, d.id_html, d.revogado,
             dispositivos_fts.rank AS r
      FROM dispositivos_fts
      JOIN dispositivos d ON d.id = dispositivos_fts.rowid
      JOIN legislacoes l ON l.id = d.legislacao_id
      WHERE dispositivos_fts MATCH ?${f.sql}
    ), ord AS (
      SELECT *, ROW_NUMBER() OVER (PARTITION BY legislacao_id ORDER BY r) AS pos,
             COUNT(*) OVER (PARTITION BY legislacao_id) AS ocorrencias
      FROM hits
    )
    SELECT l.nome AS legislacao_nome, l.slug AS legislacao_slug, l.ementa AS legislacao_ementa,
           l.categoria AS legislacao_categoria, l.tipo_norma AS legislacao_tipo_norma,
           l.esfera AS legislacao_esfera, l.ano AS legislacao_ano, l.revogado AS legislacao_revogado,
           o.rotulo AS dispositivo_rotulo, o.tipo AS dispositivo_tipo,
           o.texto AS dispositivo_texto, o.estrutura AS dispositivo_estrutura,
           o.id_html AS dispositivo_id_html, o.revogado AS dispositivo_revogado, o.ocorrencias
    FROM ord o
    JOIN legislacoes l ON l.id = o.legislacao_id
    WHERE o.pos = 1
    ORDER BY o.r
    LIMIT ?`).bind(expressao, ...f.args, limit).all();
  const normas = results.map(comLink);
  return {
    total_normas: normas.length,
    total_dispositivos: normas.reduce((s, n) => s + n.ocorrencias, 0),
    normas,
  };
}

// Todos os dispositivos de uma norma que casam com a busca (lista do cartão da norma).
async function buscarNaNorma(env, expressao, filtros, slug, offset = 0) {
  const f = whereFiltros(filtros);
  const { results } = await env.DB.prepare(`SELECT ${CAMPOS_BUSCA}
    FROM dispositivos_fts
    JOIN dispositivos d ON d.id = dispositivos_fts.rowid
    JOIN legislacoes l ON l.id = d.legislacao_id
    WHERE dispositivos_fts MATCH ? AND l.slug = ?${f.sql}
    ORDER BY d.ordem, d.id LIMIT 1000 OFFSET ?`).bind(expressao, slug, ...f.args, offset).all();
  return { slug, total: results.length, proximo_offset: results.length === 1000 ? offset + results.length : null, resultados: results.map(comLink) };
}

const ERRO_SIMPLES = 'Informe ao menos um termo com 2 caracteres ou mais.';const DICA_AVANCADA = 'Na consulta avançada use AND, OR, NOT, NEAR(termo1 termo2, 10), "frase exata", prefixo* e parênteses. '
  + 'Os operadores devem estar em MAIÚSCULAS e NOT não pode iniciar a expressão.';

// ── Lacunas: buscas da faixa principal que não retornaram nenhuma norma ────────────────
// Só a busca agrupada sem slug grava (as chamadas com slug são a lista da norma e o
// localizador). A gravação roda em ctx.waitUntil e nunca atrasa nem derruba a busca.
// Não se guarda IP, user-agent nem qualquer dado pessoal: só o termo e os filtros.
const MIN_CARACTERES_LACUNA = 3;
const STATUS_LACUNA = new Set(['pendente', 'resolvido', 'ignorar']);
const ORDENS_LACUNAS = {
  ocorrencias: 'ocorrencias DESC, ultima_vez DESC',
  recente: 'ultima_vez DESC, ocorrencias DESC',
};

function filtrosParaRegistro(f) {
  const ativos = {};
  if (f.tipos.length) ativos.tipo_norma = f.tipos;
  if (f.esferas.length) ativos.esfera = f.esferas;
  if (f.anos.length) ativos.ano = f.anos;
  if (f.tipoDispositivo) ativos.tipo = f.tipoDispositivo;
  ativos.ocultar_revogados = f.ocultarRevogados;
  return JSON.stringify(ativos);
}

function registrarLacuna(env, ctx, termo, modo, filtros) {
  if (!ctx || typeof ctx.waitUntil !== 'function') return;
  const termoNormalizado = normalizar(termo); // minúsculas, sem acentos, espaços simples
  if (termoNormalizado.length < MIN_CARACTERES_LACUNA) return;
  const termoOriginal = String(termo ?? '').trim().slice(0, 300);
  const filtrosJson = filtrosParaRegistro(filtros);
  ctx.waitUntil((async () => {
    try {
      await env.DB.prepare(`INSERT INTO buscas_sem_resultado
        (termo_normalizado, termo_original, modo, filtros, ocorrencias, primeira_vez, ultima_vez, status)
        VALUES (?, ?, ?, ?, 1, datetime('now'), datetime('now'), 'pendente')
        ON CONFLICT (termo_normalizado, modo) DO UPDATE SET
          ocorrencias    = ocorrencias + 1,
          termo_original = excluded.termo_original,
          filtros        = excluded.filtros,
          ultima_vez     = datetime('now'),
          status         = CASE WHEN status = 'resolvido' THEN 'pendente' ELSE status END`)
        .bind(termoNormalizado, termoOriginal, modo, filtrosJson).run();
    } catch {
      // registrar a lacuna é acessório: falha aqui não pode afetar a resposta da busca
    }
  })());
}

// Comparação do token sem vazar o valor (nem em mensagem de erro)
function tokenValido(informado, esperado) {
  if (typeof esperado !== 'string' || esperado === '') return false;
  if (typeof informado !== 'string' || informado === '') return false;
  const a = new TextEncoder().encode(informado);
  const b = new TextEncoder().encode(esperado);
  let diferenca = a.length ^ b.length;
  const n = Math.max(a.length, b.length);
  for (let i = 0; i < n; i++) diferenca |= (a[i] ?? 0) ^ (b[i] ?? 0);
  return diferenca === 0;
}

const escaparHtml = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

async function listarLacunas(env, status, ordem) {
  const filtroStatus = status === 'todos' ? 'todos' : (STATUS_LACUNA.has(status) ? status : 'pendente');
  const nomeOrdem = ORDENS_LACUNAS[ordem] ? ordem : 'ocorrencias';
  const campos = 'id, termo_original, termo_normalizado, modo, filtros, ocorrencias, primeira_vez, ultima_vez, status, observacao';
  const sql = filtroStatus === 'todos'
    ? `SELECT ${campos} FROM buscas_sem_resultado ORDER BY ${ORDENS_LACUNAS[nomeOrdem]}`
    : `SELECT ${campos} FROM buscas_sem_resultado WHERE status = ? ORDER BY ${ORDENS_LACUNAS[nomeOrdem]}`;
  const stmt = env.DB.prepare(sql);
  const { results } = filtroStatus === 'todos' ? await stmt.all() : await stmt.bind(filtroStatus).all();
  return { filtroStatus, ordem: nomeOrdem, resultados: results };
}

function csvLacunas(resultados) {
  const celula = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const linhas = [['termo', 'modo', 'filtros', 'ocorrencias', 'primeira_vez', 'ultima_vez', 'status', 'observacao'].map(celula).join(',')];
  for (const r of resultados) {
    linhas.push([r.termo_original, r.modo, r.filtros, r.ocorrencias, r.primeira_vez, r.ultima_vez, r.status, r.observacao].map(celula).join(','));
  }
  return linhas.join('\r\n') + '\r\n';
}

function paginaLacunas(resultados, { filtroStatus, ordem, token }) {
  const t = encodeURIComponent(token);
  const link = (status, ord) => `/api/lacunas?token=${t}&status=${encodeURIComponent(status)}&ordem=${encodeURIComponent(ord)}`;
  const aba = (valor, rotulo) => `<a class="aba${filtroStatus === valor ? ' ativa' : ''}" href="${link(valor, ordem)}">${rotulo}</a>`;
  const ordenacao = (valor, rotulo) => `<a class="aba${ordem === valor ? ' ativa' : ''}" href="${link(filtroStatus, valor)}">${rotulo}</a>`;
  const acao = `/api/lacunas?token=${t}&status=${encodeURIComponent(filtroStatus)}&ordem=${encodeURIComponent(ordem)}`;

  const linhas = resultados.map((r) => {
    const botoes = ['resolvido', 'ignorar', 'pendente'].map((s) =>
      `<button type="submit" name="status" value="${s}"${r.status === s ? ' disabled' : ''}>${s}</button>`).join('');
    return `<tr>
      <td><strong>${escaparHtml(r.termo_original)}</strong><div class="sub">${escaparHtml(r.termo_normalizado)}</div></td>
      <td>${escaparHtml(r.modo)}</td>
      <td class="sub">${escaparHtml(r.filtros)}</td>
      <td class="num">${escaparHtml(r.ocorrencias)}</td>
      <td class="sub">${escaparHtml(r.primeira_vez)}<br>${escaparHtml(r.ultima_vez)}</td>
      <td>${escaparHtml(r.status)}</td>
      <td>
        <form method="post" action="${acao}">
          <input type="hidden" name="id" value="${escaparHtml(r.id)}">
          <input type="hidden" name="voltar_status" value="${escaparHtml(filtroStatus)}">
          <input type="hidden" name="voltar_ordem" value="${escaparHtml(ordem)}">
          <input class="obs" name="observacao" value="${escaparHtml(r.observacao)}" placeholder="observação">
          <div class="botoes">${botoes}</div>
        </form>
      </td>
    </tr>`;
  }).join('\n');

  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Lacunas da biblioteca</title>
<style>
  body { font: 14px/1.45 system-ui, sans-serif; margin: 24px; color: #1f2933; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  p.intro { margin: 0 0 16px; color: #52606d; }
  .abas { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }
  .aba { padding: 4px 10px; border: 1px solid #cbd2d9; border-radius: 999px; text-decoration: none; color: #1f2933; }
  .aba.ativa { background: #1f2933; color: #fff; border-color: #1f2933; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border-bottom: 1px solid #e4e7eb; padding: 8px; text-align: left; vertical-align: top; }
  th { background: #f5f7fa; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
  .sub { color: #7b8794; font-size: 12px; }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  .obs { width: 100%; box-sizing: border-box; margin-bottom: 4px; }
  .botoes { display: flex; gap: 4px; }
  button { font: inherit; padding: 2px 8px; cursor: pointer; }
  button[disabled] { opacity: .45; cursor: default; }
  .vazio { padding: 24px; text-align: center; color: #7b8794; }
</style>
</head>
<body>
<h1>Lacunas da biblioteca</h1>
<p class="intro">Buscas da faixa principal que não retornaram nenhuma norma. Datas em UTC.</p>
<div class="abas">
  ${aba('pendente', 'Pendentes')}${aba('resolvido', 'Resolvidas')}${aba('ignorar', 'Ignoradas')}${aba('todos', 'Todas')}
  <span style="width:12px"></span>
  ${ordenacao('ocorrencias', 'Mais buscadas')}${ordenacao('recente', 'Mais recentes')}
  <span style="width:12px"></span>
  <a class="aba" href="/api/lacunas.csv?token=${t}&status=${encodeURIComponent(filtroStatus)}&ordem=${encodeURIComponent(ordem)}">Baixar CSV</a>
</div>
<table>
<thead><tr><th>Termo</th><th>Modo</th><th>Filtros</th><th>Ocorr.</th><th>Primeira / última</th><th>Status</th><th>Ação</th></tr></thead>
<tbody>
${linhas || '<tr><td colspan="7" class="vazio">Nenhuma busca sem resultado neste filtro.</td></tr>'}
</tbody>
</table>
</body>
</html>`;
}

async function api(request, env, url, ctx) {
  // GET /api/buscar?q=&modo=simples|avancado + filtros
  //   &agrupar=norma → uma linha por norma; &slug= → dispositivos de uma norma (com &offset=)
  if (url.pathname === '/api/buscar' && request.method === 'GET') {
    const sp = url.searchParams;
    const consulta = montarConsulta(sp.get('q'), sp.get('modo'));
    if (!consulta) return Response.json({ erro: sp.get('modo') === 'avancado' ? 'Escreva a expressão da consulta avançada.' : ERRO_SIMPLES }, { status: 400 });
    const filtros = lerFiltros(Object.fromEntries(sp));
    const slug = sp.get('slug');
    const inteiro = (nome, padrao, teto) => Math.min(parseInt(sp.get(nome) || String(padrao), 10) || padrao, teto);
    const cabecalho = { modo: consulta.modo, query: sp.get('q'), consulta_executada: consulta.expressao, termos: consulta.termos };
    let corpo;
    if (slug) {
      const offset = Number(sp.get('offset') || '0');
      if (!Number.isSafeInteger(offset) || offset < 0) return Response.json({ erro: 'Deslocamento inválido.' }, { status: 400 });
      corpo = await buscarNaNorma(env, consulta.expressao, filtros, slug, offset);
    } else if (sp.get('agrupar') === 'norma') {
      corpo = await buscarPorNorma(env, consulta.expressao, filtros, inteiro('limit', 100, 300));
      // faixa principal da biblioteca: só aqui a busca sem resultado vira lacuna
      if (corpo.total_normas === 0) registrarLacuna(env, ctx, sp.get('q'), consulta.modo, filtros);
    } else {
      corpo = await buscar(env, consulta.expressao, filtros, inteiro('limit', 20, 100));
    }
    return Response.json({ ...cabecalho, ...corpo });
  }

  // POST /api/buscar-avancado (body: q + filtros + limit): mantido para quem já usa
  if (url.pathname === '/api/buscar-avancado' && request.method === 'POST') {
    let body;
    try { body = await request.json(); } catch { return Response.json({ erro: 'Corpo JSON inválido.' }, { status: 400 }); }
    const consulta = montarConsulta(body?.q, 'avancado');
    if (!consulta) return Response.json({ erro: 'Campo "q" é obrigatório.', dica: DICA_AVANCADA }, { status: 400 });
    const corpo = await buscar(env, consulta.expressao, lerFiltros(body), Math.min(parseInt(body.limit, 10) || 50, 100));
    return Response.json({ modo: 'avancado', query: body.q, consulta_executada: consulta.expressao, termos: consulta.termos, ...corpo });
  }

  // GET /api/filtros: valores disponíveis para os filtros, com o número de normas
  if (url.pathname === '/api/filtros' && request.method === 'GET') {
    const contar = (col, ordem) => env.DB.prepare(`SELECT ${col} AS valor, COUNT(*) AS total FROM legislacoes
      WHERE ${col} IS NOT NULL AND ${col} <> '' GROUP BY ${col} ORDER BY ${col} ${ordem}`).all();
    const [tipos, esferas, anos] = await Promise.all([contar('tipo_norma', 'ASC'), contar('esfera', 'ASC'), contar('ano', 'DESC')]);
    return Response.json({ tipos: tipos.results, esferas: esferas.results, anos: anos.results });
  }

  if (url.pathname.startsWith('/api/legislacao/') && request.method === 'GET') {
    const slug = decodeURIComponent(url.pathname.split('/api/legislacao/')[1]);
    const { results } = await env.DB.prepare(`
      SELECT l.nome, l.ementa, l.slug, l.categoria, l.data_publicacao, l.situacao,
             d.tipo, d.rotulo, d.texto, d.estrutura, d.id_html, d.revogado, d.ordem
      FROM legislacoes l
      LEFT JOIN dispositivos d ON d.legislacao_id = l.id
      WHERE l.slug = ?
      ORDER BY d.ordem ASC`).bind(slug).all();
    if (results.length === 0) return Response.json({ erro: 'Legislação não encontrada' }, { status: 404 });
    const [p] = results;
    return Response.json({
      nome: p.nome, ementa: p.ementa, slug: p.slug, categoria: p.categoria,
      data_publicacao: p.data_publicacao, situacao: p.situacao,
      dispositivos: results.filter((r) => r.rotulo !== null).map((r) => ({
        tipo: r.tipo, rotulo: rotuloCompleto(r.rotulo, r.id_html), texto: r.texto, estrutura: r.estrutura,
        id_html: r.id_html, revogado: r.revogado, ordem: r.ordem,
        link: r.id_html ? `${r.slug}.html#${r.id_html}` : `${r.slug}.html`,
      })),
    });
  }

  if (url.pathname === '/api/listar' && request.method === 'GET') {
    const { results } = await env.DB.prepare(`
      SELECT l.id, l.nome, l.ementa, l.slug, l.categoria, l.data_publicacao, l.situacao,
             COUNT(d.id) AS total_dispositivos
      FROM legislacoes l
      LEFT JOIN dispositivos d ON d.legislacao_id = l.id
      GROUP BY l.id
      ORDER BY l.nome ASC`).all();
    return Response.json({ total: results.length, legislacoes: results });
  }

  if (url.pathname.startsWith('/api/estrutura/') && request.method === 'GET') {
    const slug = decodeURIComponent(url.pathname.split('/api/estrutura/')[1]);
    const { results } = await env.DB.prepare(`
      SELECT DISTINCT d.estrutura
      FROM dispositivos d
      JOIN legislacoes l ON l.id = d.legislacao_id
      WHERE l.slug = ? AND d.estrutura IS NOT NULL
      ORDER BY d.ordem ASC`).bind(slug).all();
    return Response.json({ slug, estrutura: results.map((r) => r.estrutura) });
  }

  // GET /api/lacunas?token=...&status=pendente|resolvido|ignorar|todos&ordem=ocorrencias|recente
  if (url.pathname === '/api/lacunas' && request.method === 'GET') {
    const token = url.searchParams.get('token');
    if (!tokenValido(token, env.LACUNAS_TOKEN)) return new Response('Não encontrado', { status: 404 });
    const { filtroStatus, ordem, resultados } = await listarLacunas(env, url.searchParams.get('status') || 'pendente', url.searchParams.get('ordem') || 'ocorrencias');
    return new Response(paginaLacunas(resultados, { filtroStatus, ordem, token }), {
      headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' },
    });
  }

  // GET /api/lacunas.csv?token=... (mesmos filtros da tela)
  if (url.pathname === '/api/lacunas.csv' && request.method === 'GET') {
    const token = url.searchParams.get('token');
    if (!tokenValido(token, env.LACUNAS_TOKEN)) return new Response('Não encontrado', { status: 404 });
    const { resultados } = await listarLacunas(env, url.searchParams.get('status') || 'pendente', url.searchParams.get('ordem') || 'ocorrencias');
    return new Response(csvLacunas(resultados), {
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename="lacunas-biblioteca.csv"',
        'Cache-Control': 'no-store',
      },
    });
  }

  // POST /api/lacunas?token=... (form: id, status, observacao) → volta para a tela
  if (url.pathname === '/api/lacunas' && request.method === 'POST') {
    const token = url.searchParams.get('token');
    if (!tokenValido(token, env.LACUNAS_TOKEN)) return new Response('Não encontrado', { status: 404 });
    let form;
    try { form = await request.formData(); } catch { return Response.json({ erro: 'Corpo inválido.' }, { status: 400 }); }
    const id = parseInt(form.get('id'), 10);
    const status = String(form.get('status') ?? '');
    if (!Number.isSafeInteger(id) || !STATUS_LACUNA.has(status)) return Response.json({ erro: 'Status inválido.' }, { status: 400 });
    const observacao = String(form.get('observacao') ?? '').slice(0, 2000);
    await env.DB.prepare('UPDATE buscas_sem_resultado SET status = ?, observacao = ? WHERE id = ?')
      .bind(status, observacao || null, id).run();
    const voltarStatus = String(form.get('voltar_status') ?? 'pendente');
    const voltarOrdem = String(form.get('voltar_ordem') ?? 'ocorrencias');
    return Response.redirect(`${url.origin}/api/lacunas?token=${encodeURIComponent(token)}&status=${encodeURIComponent(voltarStatus)}&ordem=${encodeURIComponent(voltarOrdem)}`, 303);
  }

  if (url.pathname === '/api' || url.pathname === '/api/') {
    return Response.json({
      servico: 'Biblioteca de Legislação Ambiental',

      consulta: {
        simples: 'Termos separados por espaço. Acentos são removidos e o Worker monta a expressão com OR, incluindo as frases em que os termos aparecem juntos e na mesma ordem.',
        avancado: 'Expressão FTS5 livre: AND, OR, NOT, NEAR(a b, N), "frase", prefixo*, parênteses.',
      },
      endpoints: {
        'GET /api/buscar?q=termos': 'Consulta (params: modo=simples|avancado, tipo_norma, esfera, ano, tipo, ocultar_revogados, limit, agrupar=norma, slug, offset)',
        'POST /api/buscar-avancado': 'Consulta avançada (body: q, tipo_norma, esfera, ano, tipo, ocultar_revogados, limit)',
        'GET /api/filtros': 'Valores disponíveis para os filtros (tipo de norma, esfera, ano)',
        'GET /api/legislacao/:slug': 'Dispositivos de uma legislação',
        'GET /api/listar': 'Lista todas as legislações',
        'GET /api/estrutura/:slug': 'Estrutura hierárquica',
      },
    });
  }

  return Response.json({ erro: 'Rota não encontrada' }, { status: 404 });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api' || url.pathname.startsWith('/api/')) {
      try {
        return await api(request, env, url, ctx);
      } catch (err) {
        const fts = /fts5|syntax|MATCH|no such column/i.test(String(err?.message));
        return Response.json(
          fts ? { erro: 'Expressão de busca inválida.', dica: DICA_AVANCADA } : { erro: 'Erro ao consultar a base.' },
          { status: fts ? 400 : 500 },
        );
      }
    }
    return env.ASSETS.fetch(request);
  },
};
