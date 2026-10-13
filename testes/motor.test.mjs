// Testes do motor de busca (site/motor.js) contra o site gerado.
// Uso: python scripts/gerar_site.py _site && node --test testes/motor.test.mjs
// SITE_DIR aponta outra pasta gerada, se preciso.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = resolve(RAIZ, process.env.SITE_DIR || '_site');
const ler = f => readFileSync(join(SITE, f));
const json = f => JSON.parse(ler(f).toString('utf8'));
const motor = await import(pathToFileURL(join(SITE, 'motor.js')));
const M = motor.criarMotor({indice: json('index.json'), cnae: json('cnae.json'), sinonimos: json('sinonimos.json'), ambitos: json('ambitos.json')});

test('manifesto descreve a publicação', () => {
  const man = json('manifesto.json');
  assert.equal(man.motor, motor.MOTOR_VERSAO);
  assert.equal(man.formato_indice, motor.FORMATO_INDICE);
  assert.equal(man.commit, M.info().commit);
  for (const [f, sha] of Object.entries(man.arquivos))
    assert.equal(createHash('sha256').update(ler(f)).digest('hex'), sha, f);
});

test('site usa o motor publicado, sem cópia da regra de busca', () => {
  const html = ler('index.html').toString('utf8');
  assert.match(html, /from '\.\/motor\.js'/);
  assert.doesNotMatch(html, /function (buscar|pontuar|triagem|conceitos)\(/);
});

test('índice em formato desconhecido é recusado', () => {
  assert.throws(() => motor.criarMotor({indice: {formato: 99, docs: {}, blocos: []}}), /formato/);
});

test('CNAE informado por código é sugerido sem ambiguidade', () => {
  const cs = M.triagemCnae('3101-2/00');
  assert.equal(cs.length, 1);
  assert.equal(cs[0].codigo, '3101200');
  assert.equal(cs[0].rotulo, '3101-2/00');
  assert.equal(cs[0].sugerido, true);
});

test('busca livre com CNAE admite a lista de enquadramento pelo código', () => {
  const r = M.buscaLivre({q: 'usina de argamassa', cnaes: ['2330-3/05']});
  assert.equal(r.modo, 'livre');
  assert.deepEqual(r.consulta.cnae.codigos, ['2330305']);
  const n = r.normas.find(n => n.motivo.includes('CNAE 2330-3/05'));
  assert.ok(n, 'nenhuma norma admitida pelo CNAE');
  assert.equal(r.total.normas, r.normas.length);
  for (const t of n.trechos) {
    assert.match(t.url, /^https:\/\/github\.com\/leoparreira21\/base-legislacao-ambiental\/blob\/[0-9a-f]{40}\//);
    let fim = 0;
    for (const [a, b] of t.destaques) { assert.ok(a >= fim && b > a && b <= t.texto.length); fim = b; }
  }
});

test('códigos CNAE fora da tabela do IBGE são ignorados', () => {
  assert.equal(M.buscaLivre({q: 'argamassa', cnaes: ['0000000']}).consulta.cnae, null);
});

test('paginação de normas', () => {
  const todas = M.buscaLivre({q: 'resíduos de serviços de saúde'});
  const pag = M.buscaLivre({q: 'resíduos de serviços de saúde', limiteNormas: 2, offset: 1});
  assert.equal(pag.total.normas, todas.total.normas);
  assert.deepEqual(pag.normas.map(n => n.arquivo), todas.normas.slice(1, 3).map(n => n.arquivo));
});

test('análise de caso: eixos na ordem do site e nota da rede pública', () => {
  const r = M.analiseCaso({campos: {atividade: 'clínica odontológica', agua: 'rede', localizacao: '-', residuos: 'resíduos de serviços de saúde'}});
  assert.deepEqual(r.eixos.map(e => e.id), ['atividade', 'modalidade', 'agua', 'efluentes', 'residuos']);
  const agua = r.eixos.find(e => e.id === 'agua');
  assert.ok(agua.nota && agua.normas.length === 0);
  assert.ok(r.eixos.find(e => e.id === 'residuos').normas.length > 0);
});

test('opções do caso: valores únicos e eixos que o site conhece', () => {
  for (const [k, ops] of Object.entries(motor.OPCOES_CASO)) {
    const vals = ops.map(o => o.valor);
    assert.equal(new Set(vals).size, vals.length, k);
  }
  assert.equal(motor.OPCOES_CASO.localizacao[0].valor, 'manancial area protegida');
});

test('tags da base viram blocos de busca e absorvem as palavras que cobrem', () => {
  const termos = q => M.buscaLivre({q}).consulta.termos;
  assert.deepEqual(termos('pátio de caminhões').map(t => t.termo), ['#patio-caminhao']);
  const agua = termos('outorga poço água subterrânea');
  assert.deepEqual(agua.map(t => t.termo).sort(), ['#agua-subterranea', '#outorga', '#poco']);
  // tag contida em outra maior fica de fora
  const rss = termos('resíduos de serviços de saúde');
  assert.equal(rss.length, 1);
  assert.ok(rss[0].tags.includes('residuo-servico-saude'));
  // sem tag correspondente: só palavras
  assert.deepEqual(termos('clínica odontológica').map(t => [t.termo, t.tags.length]), [['clinic', 0], ['odontologic', 0]]);
  // bloco de tag mais palavra solta
  assert.deepEqual(termos('efluente sanitário').map(t => t.termo), ['#efluente', 'sanitari']);
});

test('recurso e recursos não são blocos de busca nem admitem normas pela ementa', () => {
  const r = M.buscaLivre({q: 'recursos minerais'});
  assert.ok(!r.consulta.termos.some(t => t.termo === 'recurs'));
  const h = M.buscaLivre({q: 'recursos hídricos'});
  assert.ok(!h.normas.some(n => /^instrucao-normativa-ibama-(13-2021|23-2025)$/.test(n.arquivo)), 'norma admitida só por «recursos» na ementa');
});
