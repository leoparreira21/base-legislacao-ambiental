import test from 'node:test';
import assert from 'node:assert/strict';
import {buscarComplementar,evidenciasComplementares} from '../site/complementar.js';
import {checkAI} from '../cloudflare/legislacao-ambiental-api/worker.mjs';
const data={formato:'complementar/1',commit:'a'.repeat(40),documentos:[{id:'resolucao-conama-999-2025',titulo:'Resolução CONAMA 999',orgao:'conama',arquivo:'reguladores/teste.md',vigencia:'nao_verificada',url:'https://github.com/leoparreira21/ctresb-leis/blob/'+ 'a'.repeat(40)+'/reguladores/teste.md',artigos:[{id:'art1',texto:'Art. 1º A supressão de vegetação nativa depende das condições expressas neste artigo.',linhas:[10,12]}]}]};
test('recupera artigo específico e mantém origem; rejeita coincidência genérica e filtro incompatível',()=>{
  const hit=buscarComplementar(data,'supressão vegetação')[0];assert.ok(hit);assert.match(hit.url,/#L10-L12$/);
  assert.equal(buscarComplementar(data,'atividade médica resíduos hospitalares vegetação').length,0);
  assert.equal(buscarComplementar(data,'supressão vegetação',{esfera:'estadual'}).length,0);
  assert.equal(buscarComplementar(data,'supressão vegetação',{categoria:'licenciamento'}).length,0);
  assert.equal(buscarComplementar(data,'').length,0);
});
test('origem complementar nunca recebe conclusão definitiva de aplicável',()=>{
  const ev=evidenciasComplementares(data,{campos:{atividade:'supressão vegetação'}});assert.equal(ev.length,1);
  const r=checkAI({response:{itens:[{chave:ev[0].chave,classificacao:'aplicavel',fundamentacao:'Conferir as condições.',evidencias:[{chave:ev[0].chave,trecho:ev[0].texto}]}],lacunas:[]}},'b'.repeat(40),ev);
  assert.equal(r.itens[0].classificacao,'condicionada');assert.equal(r.itens[0].origem,'ctresb-leis');
  assert.equal(r.itens[0].fonte.url,ev[0].url);
});
test('citação inventada permanece rejeitada',()=>{
  const ev=evidenciasComplementares(data,{campos:{atividade:'supressão vegetação'}});
  assert.throws(()=>checkAI({response:{itens:[{chave:ev[0].chave,classificacao:'contextual',fundamentacao:'Conferir.',evidencias:[{chave:ev[0].chave,trecho:'Citação inventada de norma não recuperada.'}]}],lacunas:[]}},'b'.repeat(40),ev));
});
