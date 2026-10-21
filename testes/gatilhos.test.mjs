import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {OPCOES_CASO} from '../site/motor.js';
import {avaliarGatilhos} from '../cloudflare/legislacao-ambiental-api/recuperacao.mjs';
import {checkAI} from '../cloudflare/legislacao-ambiental-api/worker.mjs';

const curados=JSON.parse(fs.readFileSync(new URL('../consultas/gatilhos.json',import.meta.url),'utf8')).gatilhos;
const rede={campo:'efluentes',valores:['lancamento rede coletora esgoto'],trecho:'em rede coletora de esgotos',origem:'rdc-anvisa-222-2018#art81_cpt'};
const fato={fato:'A rede coletora está conectada à estação de tratamento de esgoto.',trecho:'conectada à estação de tratamento',origem:'rdc-anvisa-222-2018#art81_cpt'};

test('Valores curados existem no formulário e não são "Não informado"',()=>{
  for(const [chave,g] of Object.entries(curados)) for(const c of g.condicoes) if(c.campo) for(const v of c.valores) {
    const o=OPCOES_CASO[c.campo]?.find(x=>x.valor===v);
    assert.ok(o&&!/^Não informado/.test(o.rotulo),chave+': '+c.campo+'='+v);
  }
});

test('Avaliação: valor exato atende, outro valor contradiz, vazio e triagem ficam não informados, fato nunca é confirmado',()=>{
  const estado=campos=>avaliarGatilhos([rede],campos)[0];
  assert.equal(estado({efluentes:'lancamento rede coletora esgoto'}).estado,'atendida');
  const contra=estado({efluentes:'infiltracao solo sumidouro'});
  assert.equal(contra.estado,'nao_atendida');
  assert.equal(contra.informado,'Solo / fossa e sumidouro');
  assert.equal(estado({}).estado,'nao_informada');
  assert.equal(avaliarGatilhos([{...rede,campo:'localizacao',valores:['manancial abastecimento']}],{localizacao:'manancial area protegida'})[0].estado,'nao_informada');
  assert.equal(avaliarGatilhos([fato],{efluentes:'lancamento rede coletora esgoto'})[0].estado,'a_confirmar');
  assert.equal(estado({}).descricao,'Destino dos efluentes: Rede coletora de esgoto');
});

test('Servidor rebaixa "aplicavel" se uma condição curada não está atendida e publica as condições',()=>{
  const sha='7e5ef6bd0143b350d8ad111ee38937d0bf53edb5', key='rdc-anvisa-222-2018#art81_cpt';
  const texto='O lançamento de rejeitos líquidos em rede coletora de esgotos, conectada à estação de tratamento, deve atender às normas ambientais.';
  const resposta={itens:[{chave:key,classificacao:'aplicavel',fundamentacao:'Efluente vai à rede.',evidencias:[{chave:key,trecho:'em rede coletora de esgotos'}]}],lacunas:[]};
  const base=(gs,campos)=>[{chave:key,texto,elegivel:true,arquivo:'normas/rdc-anvisa-222-2018.md',linhas:[694,694],url:'https://github.com/x',gatilhos:avaliarGatilhos(gs,campos)}];
  const naRede={efluentes:'lancamento rede coletora esgoto'};
  const item=checkAI({response:resposta},sha,base([rede,fato],naRede)).itens[0];
  assert.equal(item.classificacao,'condicionada');
  assert.deepEqual(item.condicoes.map(c=>c.estado),['atendida','a_confirmar']);
  assert.equal(checkAI({response:resposta},sha,base([rede],naRede)).itens[0].classificacao,'aplicavel');
  const contra=checkAI({response:resposta},sha,base([rede],{efluentes:'infiltracao solo sumidouro'})).itens[0];
  assert.equal(contra.classificacao,'condicionada');
  assert.equal(contra.condicoes[0].estado,'nao_atendida');
});
