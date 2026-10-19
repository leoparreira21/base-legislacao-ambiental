import test from "node:test";
import assert from "node:assert/strict";
import {performance} from "node:perf_hooks";
import {readFile} from "node:fs/promises";
import {join} from "node:path";
import worker from "../cloudflare/legislacao-ambiental-api/worker.mjs";

// Usa os arquivos publicados no GitHub Pages; com SITE_DIR, os de um _site local.
const BASE="https://leoparreira21.github.io/base-legislacao-ambiental/";
const SITE_DIR=process.env.SITE_DIR;
const CASE={
  campos:{
    atividade:"Atividade médica ambulatorial com recursos para realização de exames complementares",
    modalidade:"renovacao licenca operacao",
    agua:"rede",
    efluentes:"lancamento rede coletora esgoto",
    residuos:"gerenciamento residuos servico saude"
  },
  cnaes:["8630-5/02"]
};
const shorten=x=>String(x).slice(0,500);

test("Integração integral: índices publicados → motor → grafo → AI mock → contrato e fontes", {timeout:240000}, async()=>{
  const realFetch=globalThis.fetch;
  const cache=new Map();
  const times={};
  const started=performance.now();
  // Baixa sob demanda o que o Worker pedir (índices do motor e fatias por norma)
  const load=async name=>{
    if(cache.has(name))return cache.get(name);
    const began=performance.now();
    let bytes;
    if(SITE_DIR)bytes=new Uint8Array(await readFile(join(SITE_DIR,name)));
    else{
      const response=await realFetch(BASE+name,{signal:AbortSignal.timeout(90000)});
      assert.equal(response.status,200,name+" não publicado");
      bytes=new Uint8Array(await response.arrayBuffer());
    }
    cache.set(name,bytes);
    times[name]={bytes:bytes.byteLength,load_ms:Math.round(performance.now()-began)};
    return bytes;
  };
  const expected=JSON.parse(new TextDecoder().decode(await load("manifesto.json")));
  const version=expected.commit;
  assert.match(version,/^[0-9a-f]{40}$/);
  let inferencias=0, evidencias=[];
  const env={
    ANALYZE_TOKEN:"segredo-somente-teste-nao-real",
    AI:{run:async(model,params)=>{
      inferencias++;
      assert.match(model,/^@cf\//);
      const request=JSON.parse(params.messages.find(m=>m.role==="user").content);
      assert.equal(request.commit,version);
      assert.ok(Array.isArray(request.evidencias));
      assert.ok(request.evidencias.length>0,"Motor não selecionou dispositivos");
      evidencias=request.evidencias;
      const principal=evidencias.find(e=>e.papel==="principal")||evidencias[0];
      const quote=principal.texto.slice(0,110).replace(/\s+/g," ").trim();
      assert.ok(quote.length>=10);
      return {response:JSON.stringify({
        versao:"1.0",
        commit:request.commit,
        itens:[{
          chave:principal.chave,
          classificacao:"condicionada",
          fundamentacao:"Analisar a hipótese de incidência e confirmar as condições do empreendimento.",
          evidencias:[{chave:principal.chave,trecho:quote}]
        }],
        lacunas:["Verificar exigências específicas do licenciamento"]
      })};
    }}
  };
  try{
    globalThis.fetch=async(input,options)=>{
      const url=String(input);
      if(!url.startsWith(BASE))throw Error("Worker tentou consultar fonte externa: "+url);
      const filename=url.slice(BASE.length);
      if(!(filename in expected.arquivos)&&filename!=="manifesto.json")throw Error("Fonte fora do manifesto: "+filename);
      return new Response(await load(filename),{status:200,headers:{"content-type":"application/json"}});
    };
    const request=new Request("https://teste.local/api/legislacao/analisar",{
      method:"POST",
      headers:{"Content-Type":"application/json","Authorization":"Bearer segredo-somente-teste-nao-real"},
      body:JSON.stringify(CASE)
    });
    const response=await worker.fetch(request,env);
    const text=await response.text();
    let data;
    try{data=JSON.parse(text)}catch{throw Error("Resposta não JSON "+response.status+" "+shorten(text))}
    assert.equal(response.status,200,JSON.stringify(data).slice(0,850));
    assert.equal(inferencias,1);
    assert.equal(data.status,"analisado");
    assert.equal(data.versao,"consulta-hibrida/1");
    assert.equal(data.commit,version);
    assert.equal(data.itens.length,1);
    assert.ok(data.evidencias_selecionadas>0);
    assert.ok(data.itens[0].fonte.url.includes(version));
    // A rota com IA lê só as fatias das normas selecionadas, nunca os índices inteiros
    const baixados=Object.keys(times);
    assert.ok(baixados.some(n=>n.startsWith("fatias/")),"nenhuma fatia baixada: "+baixados.join(", "));
    assert.ok(!baixados.includes("dispositivos.json")&&!baixados.includes("grafo.json"),"baixou índice inteiro: "+baixados.join(", "));
    console.log("INTEGRACAO:",JSON.stringify({commit:version,numero_evidencias:evidencias.length,item:data.itens[0].chave,arquivos:times,elapsed_ms:Math.round(performance.now()-started)}));
  }finally{
    globalThis.fetch=realFetch;
  }
});
