// Worker da biblioteca: arquivos estáticos (a biblioteca e as páginas das normas, em ASSETS)
// e a API de consulta no texto dos dispositivos (D1 "legislacao-ambiental", em DB).
// A API é a que Leo publicou em 14/11/2026 pelo painel; aqui ela passou a ser versionada e
// a responder com JSON de erro (consulta FTS mal formada derrubava o Worker com erro 1101).
// Em 27/11/2026 entraram as regras que Leo montou no chat do Cloudflare (publicadas por
// fora do repositório, o que apagou a biblioteca): consulta simples e avançada, filtros
// por tipo de norma, esfera, ano e revogados, /api/filtros e os termos para o destaque.

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
  if (f.ocultarRevogados) sql += ' AND COALESCE(l.revogado, 0) = 0 AND d.revogado = 0';
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

const ERRO_SIMPLES = 'Informe ao menos um termo com 2 caracteres ou mais.';
const DICA_AVANCADA = 'Na consulta avançada use AND, OR, NOT, NEAR(termo1 termo2, 10), "frase exata", prefixo* e parênteses. '
  + 'Os operadores devem estar em MAIÚSCULAS e NOT não pode iniciar a expressão.';

async function api(request, env, url) {
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
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api' || url.pathname.startsWith('/api/')) {
      try {
        return await api(request, env, url);
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
