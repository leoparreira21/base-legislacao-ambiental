import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {criarMotor,CATEGORIAS_FUNCAO} from '../_site/motor.js';
import {checkAI} from '../cloudflare/legislacao-ambiental-api/worker.mjs';
import {selecionarEvidencias} from '../cloudflare/legislacao-ambiental-api/recuperacao.mjs';
const ler=f=>JSON.parse(readFileSync(new URL('../_site/'+f,import.meta.url),'utf8'));
const M=criarMotor({indice:ler('index.json'),cnae:ler('cnae.json'),sinonimos:ler('sinonimos.json'),ambitos:ler('ambitos.json')});
test('Filtro funcional mantém somente trechos da função escolhida',()=>{
  const todos=M.buscaLivre({q:'renovação licença'});
  const r=M.buscaLivre({q:'renovação licença',filtros:{categoria:'licenciamento'}});
  assert.ok(r.normas.length);
  assert.ok(r.total.trechos<=todos.total.trechos);
  for(const n of r.normas)for(const t of n.trechos)assert.ok(t.funcao.categorias.includes('licenciamento'));
  assert.equal(M.buscaLivre({q:'licença',filtros:{categoria:'inventada'}}).total.trechos,0);
});
test('Relatório liga cada classificação a ID, texto e hash',()=>{
  const r=ler('classificacao.json');assert.equal(r.formato,'funcional/1');
  assert.ok(r.dispositivos.length>30000);
  assert.equal(new Set(r.dispositivos.map(d=>d.chave)).size,r.dispositivos.length);
  for(const d of r.dispositivos){assert.match(d.funcao.texto_sha256,/^[a-f0-9]{64}$/);assert.ok(d.funcao.categorias.every(c=>Object.hasOwn(CATEGORIAS_FUNCAO,c)));}
});
test('Função do chat vem da fonte, independentemente da saída da IA',()=>{
  const commit='a'.repeat(40), funcao={categorias:['licenciamento'],estado:'sugerida'};
  const source={chave:'norma#art1_cpt',id:'art1_cpt',texto:'O requerimento de licença deverá apresentar os documentos exigidos.',linhas:[1,2],url:'https://example.test',elegivel:true,funcao};
  const r=checkAI({response:{commit,itens:[{chave:source.chave,classificacao:'condicionada',funcao:{categorias:['inventada']},fundamentacao:'Conferir os documentos.',evidencias:[{chave:source.chave,trecho:source.texto}]}],lacunas:[]}},commit,[source]);
  assert.deepEqual(r.itens[0].funcao,funcao);
});
