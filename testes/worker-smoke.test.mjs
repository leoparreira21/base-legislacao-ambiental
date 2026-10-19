import {test} from "node:test";
import assert from "node:assert/strict";

const URL = "https://legislacao-ambiental-api.leoparreira1007.workers.dev";
const requisitar=async (rota,init={})=>{
  const res=await fetch(URL+rota,{signal:AbortSignal.timeout(90000),...init});
  const corpo=await res.text();
  let json;try{json=JSON.parse(corpo)}catch{throw Error("Resposta não JSON "+res.status+" "+corpo.slice(0,300))}
  return {res,json};
};
test("Metadados do Worker estão disponíveis", async ()=>{
  const {res,json}=await requisitar("/");
  assert.equal(res.status,200);
  assert.equal(json.servico,"legislacao-ambiental-api");
});
test("Saúde dos índices publicados", async ()=>{
  const {res,json}=await requisitar("/health");
  assert.equal(res.status,200,JSON.stringify(json));
  assert.equal(json.status,"ok");
  assert.equal(json.indices.dispositivos,true);
  assert.equal(json.indices.grafo,true);
  assert.equal(json.ai ?? json.ia,true);
});
test("Rota de IA rejeita chamadas sem autorização", async ()=>{
  const {res}=await requisitar("/api/legislacao/analisar",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});
  assert.equal(res.status,401);
});
test("Consulta de candidatos não faz inferência e retorna eixos", async ()=>{
  const {res,json}=await requisitar("/api/legislacao/candidatos",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
    campos:{atividade:"Atividade médica ambulatorial com exames complementares",modalidade:"renovacao licenca operacao",agua:"rede",efluentes:"lancamento rede coletora esgoto"},
    cnaes:["8630-5/02"]
  })});
  assert.equal(res.status,200,JSON.stringify(json).slice(0,900));
  assert.match(json.commit,/^[a-f0-9]{40}$/);
  assert.ok(Array.isArray(json.eixos)&&json.eixos.length>=3);
});
