import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import worker from '../cloudflare/legislacao-ambiental-api/worker.mjs';
const base='https://leoparreira21.github.io/base-legislacao-ambiental/';
const caso={campos:{atividade:'supressão vegetação nativa'}};
test('Worker integra snapshot real, confere citações e tolera falha isolada do complemento',async()=>{
  const real=globalThis.fetch;let fail=false,old=false,received=[];
  const env={ANALYZE_TOKEN:'teste',AI:{run:async(_model,params)=>{
    received=JSON.parse(params.input[1].content).evidencias;
    const e=received.find(e=>e.origem==='ctresb-leis'&&e.papel==='principal')||received[0];
    return {response:{itens:[{chave:e.chave,classificacao:'aplicavel',fundamentacao:'Confirmar âmbito e vigência.',evidencias:[{chave:e.chave,trecho:e.texto.slice(0,100)}]}],lacunas:[]}};
  }}};
  globalThis.fetch=async url=>{
    assert.ok(String(url).startsWith(base));
    const file=String(url).slice(base.length);
    if(fail&&file==='ctresb-index.json')return new Response('corrompido');
    let data=await readFile('_site/'+file);
    if(old&&file==='manifesto.json'){const m=JSON.parse(data);delete m.arquivos['ctresb-index.json'];data=JSON.stringify(m);}
    return new Response(data);
  };
  const call=()=>worker.fetch(new Request('https://teste/api/legislacao/analisar',{method:'POST',headers:{authorization:'Bearer teste','Content-Type':'application/json'},body:JSON.stringify(caso)}),env);
  try {
    let r=await call();assert.equal(r.status,200);let body=await r.json();
    assert.ok(received.some(e=>e.origem==='ctresb-leis'));
    assert.equal(body.itens[0].classificacao,'condicionada');
    assert.match(body.itens[0].fonte.url,/ctresb-leis\/blob\/[a-f0-9]{40}\//);
    assert.ok(body.lacunas.some(l=>l.includes('ctresb-leis')));
    fail=true;r=await call();assert.equal(r.status,200);body=await r.json();
    assert.ok(body.lacunas.some(l=>l.includes('complementar indisponível')));
    assert.ok(!received.some(e=>e.origem==='ctresb-leis'));
    fail=false;old=true;r=await call();assert.equal(r.status,200);
    assert.ok(!received.some(e=>e.origem==='ctresb-leis'));
  } finally {globalThis.fetch=real;}
});
