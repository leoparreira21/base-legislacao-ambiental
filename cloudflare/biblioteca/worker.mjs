// Worker da biblioteca: arquivos estáticos (a biblioteca e as páginas das normas, em ASSETS)
// e a API de consulta no texto dos dispositivos (D1 "legislacao-ambiental", em DB).
// A API é a que Leo publicou em 14/11/2026 pelo painel; aqui ela passou a ser versionada e
// a responder com JSON de erro (consulta FTS mal formada derrubava o Worker com erro 1101).

const CAMPOS_BUSCA = `
  l.nome        AS legislacao_nome,
  l.slug        AS legislacao_slug,
  l.ementa      AS legislacao_ementa,
  l.categoria   AS legislacao_categoria,
  d.rotulo      AS dispositivo_rotulo,
  d.tipo        AS dispositivo_tipo,
  d.texto       AS dispositivo_texto,
  d.estrutura   AS dispositivo_estrutura,
  d.id_html     AS dispositivo_id_html,
  d.revogado    AS dispositivo_revogado`;

const comLink = (r) => ({
  ...r,
  link: r.dispositivo_id_html ? `${r.legislacao_slug}.html#${r.dispositivo_id_html}` : `${r.legislacao_slug}.html`,
});

async function buscar(env, q, { limit = 20, soVigentes = true, categoria, tipo } = {}) {
  let sql = `SELECT ${CAMPOS_BUSCA}
    FROM dispositivos_fts
    JOIN dispositivos d ON d.id = dispositivos_fts.rowid
    JOIN legislacoes l ON l.id = d.legislacao_id
    WHERE dispositivos_fts MATCH ?`;
  const args = [q];
  if (categoria) { sql += ' AND l.categoria = ?'; args.push(categoria); }
  if (tipo) { sql += ' AND d.tipo = ?'; args.push(tipo); }
  if (soVigentes) sql += ' AND d.revogado = 0';
  sql += ' ORDER BY rank LIMIT ?';
  args.push(limit);
  const { results } = await env.DB.prepare(sql).bind(...args).all();
  const resultados = results.map(comLink);
  return { query: q, total: resultados.length, resultados };
}

async function api(request, env, url) {
  if (url.pathname === '/api/buscar' && request.method === 'GET') {
    const q = url.searchParams.get('q');
    const limit = Math.min(parseInt(url.searchParams.get('limit') || '20', 10) || 20, 100);
    const soVigentes = url.searchParams.get('so_vigentes') !== 'false';
    if (!q || q.trim().length < 3) {
      return Response.json({ erro: 'Parâmetro "q" deve ter no mínimo 3 caracteres' }, { status: 400 });
    }
    return Response.json(await buscar(env, q, { limit, soVigentes }));
  }

  if (url.pathname === '/api/buscar-avancado' && request.method === 'POST') {
    const { q, categoria, tipo, so_vigentes = true } = await request.json();
    if (!q) return Response.json({ erro: 'Campo "q" é obrigatório' }, { status: 400 });
    return Response.json(await buscar(env, q, { limit: 50, soVigentes: so_vigentes, categoria, tipo }));
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
        tipo: r.tipo, rotulo: r.rotulo, texto: r.texto, estrutura: r.estrutura,
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
      endpoints: {
        'GET /api/buscar?q=texto': 'Busca full-text',
        'GET /api/legislacao/:slug': 'Dispositivos de uma legislação',
        'GET /api/listar': 'Lista todas as legislações',
        'POST /api/buscar-avancado': 'Busca com filtros',
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
          { erro: fts ? 'Consulta inválida. Use palavras simples, AND, OR, NOT, aspas ou * no fim da palavra.' : 'Erro ao consultar a base.' },
          { status: fts ? 400 : 500 },
        );
      }
    }
    return env.ASSETS.fetch(request);
  },
};
