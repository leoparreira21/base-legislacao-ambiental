import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../cloudflare/biblioteca/worker.mjs';

test('lista de dispositivos oferece continuação sem truncar o localizador', async () => {
  const chamadas = [];
  const env = { DB: { prepare(sql) {
    return { bind(...args) {
      chamadas.push({ sql, args });
      const offset = args.at(-1);
      return { async all() {
        return { results: Array.from({ length: offset === 0 ? 1000 : 1 }, (_, i) => ({
          legislacao_slug: 'norma-teste', dispositivo_id_html: `art${offset + i + 1}`,
        })) };
      } };
    } };
  } } };
  const url = 'https://biblioteca.test/api/buscar?q=efluentes&slug=norma-teste&tipo=inciso';
  const primeira = await (await worker.fetch(new Request(url), env)).json();
  assert.equal(primeira.total, 1000);
  assert.equal(primeira.proximo_offset, 1000);
  const segunda = await (await worker.fetch(new Request(`${url}&offset=${primeira.proximo_offset}`), env)).json();
  assert.equal(segunda.total, 1);
  assert.equal(segunda.proximo_offset, null);
  assert.equal(segunda.resultados[0].dispositivo_id_html, 'art1001');
  assert.deepEqual(chamadas[1].args, ['efluentes OR efluent OR efluente', 'norma-teste', 'inciso', 1000]);
  assert.match(chamadas[1].sql, /d\.revogado = 0/);
  assert.match(chamadas[1].sql, /ORDER BY d\.ordem, d\.id LIMIT 1000 OFFSET \?/);
});

test('deslocamento inválido não chega ao D1', async () => {
  for (const offset of ['-1', '1.5', 'NaN']) {
    const r = await worker.fetch(new Request(`https://biblioteca.test/api/buscar?q=efluentes&slug=norma&offset=${offset}`), {});
    assert.equal(r.status, 400);
  }
});

function bancoFalso(chamadas, results = []) {
  return { DB: { prepare(sql) {
    const exec = (args) => ({ async all() { chamadas.push({ sql, args }); return { results }; } });
    return { bind: (...args) => exec(args), all: () => exec([]).all() };
  } } };
}

test('consulta simples monta OR com plural e frase, e devolve os termos do destaque', async () => {
  const chamadas = [];
  const r = await (await worker.fetch(new Request('https://biblioteca.test/api/buscar?q=Resíduos%20sólidos&agrupar=norma'), bancoFalso(chamadas))).json();
  assert.equal(r.modo, 'simples');
  assert.equal(r.consulta_executada, 'residuos OR residuo OR solidos OR solido OR "residuos solidos"');
  assert.deepEqual(r.termos, ['residuos', 'residuo', 'solidos', 'solido']);
  assert.equal(chamadas[0].args[0], r.consulta_executada);
  assert.match(chamadas[0].sql, /PARTITION BY legislacao_id/);
});

test('consulta avançada vai ao FTS5 como foi escrita, com os filtros de norma', async () => {
  const chamadas = [];
  const q = 'NEAR(lançamento efluente, 10) AND "corpo receptor"';
  const url = `https://biblioteca.test/api/buscar?modo=avancado&agrupar=norma&q=${encodeURIComponent(q)}&tipo_norma=resolucao,portaria&esfera=estadual&ano=2020&ocultar_revogados=false`;
  const r = await (await worker.fetch(new Request(url), bancoFalso(chamadas))).json();
  assert.equal(r.modo, 'avancado');
  assert.deepEqual(r.termos, ['corpo receptor', 'lançamento', 'efluente']);
  assert.deepEqual(chamadas[0].args, [q, 'resolucao', 'portaria', 'estadual', 2020, 100]);
  assert.match(chamadas[0].sql, /l\.tipo_norma IN \(\?,\?\)/);
  assert.doesNotMatch(chamadas[0].sql, /revogado = 0/);
});

test('revogados ficam de fora por padrão (norma e dispositivo)', async () => {
  const chamadas = [];
  await worker.fetch(new Request('https://biblioteca.test/api/buscar?q=outorga'), bancoFalso(chamadas));
  assert.match(chamadas[0].sql, /COALESCE\(l\.situacao, 'vigente'\) <> 'revogada' AND d\.revogado = 0/);
  // a coluna l.revogado veio da tag de controle #revogado (dispositivos), não da situação da norma
  assert.doesNotMatch(chamadas[0].sql, /l\.revogado, 0\) = 0/);
});

test('consulta vazia não chega ao D1', async () => {
  for (const q of ['', 'a', 'and or']) {
    const r = await worker.fetch(new Request(`https://biblioteca.test/api/buscar?q=${encodeURIComponent(q)}`), {});
    assert.equal(r.status, 400);
  }
});

test('expressão FTS5 inválida responde 400 com a dica', async () => {
  const env = { DB: { prepare() { return { bind() { return { async all() { throw new Error('fts5: syntax error near "NOT"'); } }; } }; } } };
  const r = await worker.fetch(new Request('https://biblioteca.test/api/buscar?modo=avancado&q=NOT%20x'), env);
  assert.equal(r.status, 400);
  assert.match((await r.json()).dica, /MAIÚSCULAS/);
});

test('/api/filtros lista tipos, esferas e anos', async () => {
  const chamadas = [];
  const r = await (await worker.fetch(new Request('https://biblioteca.test/api/filtros'), bancoFalso(chamadas, [{ valor: 'lei', total: 3 }]))).json();
  assert.deepEqual(Object.keys(r), ['tipos', 'esferas', 'anos']);
  assert.equal(chamadas.length, 3);
});
