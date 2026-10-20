// Auditoria reproduzível, sem rede nem inferência paga.
// node scripts/auditar_assistente.mjs [caminho-para-payload-IA.json]
import fs from 'node:fs';
import worker from '../cloudflare/legislacao-ambiental-api/worker.mjs';
const BASE='https://leoparreira21.github.io/base-legislacao-ambiental/';
const caso={campos:{atividade:'Atividade médica ambulatorial com exames complementares',modalidade:'renovacao licenca operacao',agua:'rede',efluentes:'lancamento rede coletora esgoto',residuos:'residuos servico saude'},cnaes:['8630-5/02']};
const original=globalThis.fetch;
try {
  globalThis.fetch=async url=>{if(!String(url).startsWith(BASE))throw Error('Fonte externa');return new Response(fs.readFileSync('_site/'+String(url).slice(BASE.length)));};
  const response=await worker.fetch(new Request('https://test/api/legislacao/analisar',{method:'POST',headers:{authorization:'Bearer teste-local'},body:JSON.stringify(caso)}),{
    ANALYZE_TOKEN:'teste-local',AI:{run:async(model,params)=>{
      const data=JSON.parse(params.input[1].content);
      console.log(JSON.stringify({modelo:model,commit:data.commit,caracteres:params.input[1].content.length,evidencias:data.evidencias.length,principais:data.evidencias.filter(e=>e.papel==='principal').map(e=>({eixo:e.eixo,chave:e.chave})),ressalvaIndireta:data.evidencias.some(e=>e.chave==='resolucao-conama-430-2011#art1_par1u')},null,2));
      if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(params));
      return {response:{itens:[],lacunas:[]}};
    }}
  });
  if(response.status!==200)throw Error(await response.text());
}finally{globalThis.fetch=original;}
