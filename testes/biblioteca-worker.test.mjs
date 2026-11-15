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
  assert.deepEqual(chamadas[1].args, ['efluentes', 'norma-teste', 'inciso', 1000]);
  assert.match(chamadas[1].sql, /d\.revogado = 0/);
  assert.match(chamadas[1].sql, /ORDER BY d\.ordem, d\.id LIMIT 1000 OFFSET \?/);
});

test('deslocamento inválido não chega ao D1', async () => {
  for (const offset of ['-1', '1.5', 'NaN']) {
    const r = await worker.fetch(new Request(`https://biblioteca.test/api/buscar?q=efluentes&slug=norma&offset=${offset}`), {});
    assert.equal(r.status, 400);
  }
});
