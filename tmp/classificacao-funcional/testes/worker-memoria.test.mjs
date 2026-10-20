// Memória da rota /analisar do Worker, com fetch e env.AI simulados (sem rede e sem IA).
// Uso: python scripts/gerar_site.py _site && node --test testes/worker-memoria.test.mjs
// SITE_DIR aponta outra pasta gerada; MEMORIA_MAX_MB muda o teto (padrão 110).
//
// Mede a memória viva (heapUsed + arrayBuffers, depois de um gc) a cada subrequisição,
// JSON.parse e chamada à IA. O motor de busca montado ocupa sozinho ~95 MB, igual em
// /candidatos; antes das fatias, /analisar passava de 300 MB por baixar dispositivos.json
// e grafo.json inteiros. O limite do Workers é 128 MB por isolate.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import v8 from 'node:v8';
import vm from 'node:vm';

v8.setFlagsFromString('--expose-gc');
const gc = vm.runInNewContext('gc');
const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = resolve(RAIZ, process.env.SITE_DIR || '_site');
const BASE = 'https://leoparreira21.github.io/base-legislacao-ambiental/';
const TETO = Number(process.env.MEMORIA_MAX_MB || 110) * 2 ** 20;
const FOLGA = 15 * 2 ** 20;  // o que /analisar pode somar ao motor
const MAX_SUBREQUISICOES = 50;  // plano Free do Workers
const TOKEN = 't'.repeat(32);

const worker = (await import(pathToFileURL(join(RAIZ, 'cloudflare/legislacao-ambiental-api/worker.mjs')))).default;
const {criarMotor} = await import(pathToFileURL(join(SITE, 'motor.js')));

const viva = () => { gc(); const m = process.memoryUsage(); return m.heapUsed + m.arrayBuffers; };
const mb = x => (x / 2 ** 20).toFixed(1) + ' MB';

const motor = (() => {
  const base = viva();
  const ler = f => JSON.parse(readFileSync(join(SITE, f), 'utf8'));
  let m = criarMotor({indice: ler('index.json'), cnae: ler('cnae.json'), sinonimos: ler('sinonimos.json'), ambitos: ler('ambitos.json')});
  const total = viva();
  m = null;
  return {base, total};
})();

let pico = 0, subrequisicoes = 0;
const amostra = () => { pico = Math.max(pico, viva()); };
const parse = JSON.parse;
globalThis.fetch = async url => {
  subrequisicoes++;
  amostra();
  const nome = String(url).slice(BASE.length);
  try { return new Response(readFileSync(join(SITE, nome))); } catch { return new Response('', {status: 404}); }
};
const env = {ANALYZE_TOKEN: TOKEN, AI: {run: async (modelo, {input:messages}) => {
  amostra();
  // IA falsa: devolve um item válido citando o primeiro dispositivo recebido
  const e = parse(messages[1].content).evidencias[0];
  const trecho = e.texto.replace(/\s+/g, ' ').trim().slice(0, 60);
  return {response: JSON.stringify({itens: [{chave: e.chave, classificacao: 'contextual', fundamentacao: 'teste',
    evidencias: [{chave: e.chave, trecho}]}], lacunas: []})};
}}};

const casos = parse(readFileSync(join(RAIZ, 'consultas/casos-auditoria.json'), 'utf8'))
  .map(c => ({id: c.id, campos: {atividade: c.consulta_inicial, outras: c.consultas.join(' ')}}));
casos.push(
  {id: 'ambulatorio-completo', cnaes: ['8630-5/02'], campos: {atividade: 'Atividade médica ambulatorial com exames complementares',
    modalidade: 'renovacao licenca operacao', agua: 'rede', efluentes: 'lancamento rede coletora esgoto', residuos: 'residuos servico saude'}},
  {id: 'argamassa-manancial', cnaes: ['2330-3/05'], campos: {atividade: 'usina de argamassa', agua: 'outorga poco agua subterranea',
    efluentes: 'infiltracao solo sumidouro', localizacao: 'manancial abastecimento'}},
);

test('motor montado cabe no teto', t => {
  t.diagnostic(`motor montado: ${mb(motor.total)} (antes dele: ${mb(motor.base)})`);
  assert.ok(motor.total <= TETO, `motor ${mb(motor.total)}`);
});

for (const caso of casos) {
  test(`/analisar ${caso.id}: memória e subrequisições`, async t => {
    pico = viva(); subrequisicoes = 0;
    JSON.parse = (...a) => { const r = parse(...a); amostra(); return r; };
    let res, corpo;
    try {
      res = await worker.fetch(new Request('https://teste/api/legislacao/analisar', {method: 'POST',
        headers: {authorization: 'Bearer ' + TOKEN, 'content-type': 'application/json'},
        body: JSON.stringify({campos: caso.campos, cnaes: caso.cnaes || []})}), env);
      corpo = await res.json();
    } finally { JSON.parse = parse; }
    t.diagnostic(`pico ${mb(pico)}, ${subrequisicoes} subrequisições`);
    assert.equal(res.status, 200, JSON.stringify(corpo));
    assert.equal(corpo.status, 'analisado');
    assert.ok(pico <= TETO, `pico ${mb(pico)} acima de ${mb(TETO)}`);
    assert.ok(pico <= motor.total + FOLGA, `pico ${mb(pico)}; motor montado ${mb(motor.total)}`);
    assert.ok(subrequisicoes <= MAX_SUBREQUISICOES, `${subrequisicoes} subrequisições`);
  });
}
