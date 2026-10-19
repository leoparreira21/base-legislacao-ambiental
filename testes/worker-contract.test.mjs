import test from "node:test";
import assert from "node:assert/strict";
import { checkAI } from "../cloudflare/legislacao-ambiental-api/worker.mjs";

const sha="7e5ef6bd0143b350d8ad111ee38937d0bf53edb5";
const key="resolucao-conama-430-2011#art1_par1u";
const text="O lançamento indireto de efluentes no corpo receptor deverá observar o disposto nesta Resolução quando verificada a inexistência de legislação ou normas específicas.";
const evidence=[{chave:key,texto:text,elegivel:true,arquivo:"normas/resolucao-conama-430-2011.md",linhas:[42,42],url:"https://github.com/example"}];
const valid=()=>({versao:"1.0",commit:sha,itens:[{chave:key,classificacao:"condicionada",fundamentacao:"A incidência depende das regras locais aplicáveis.",evidencias:[{chave:key,trecho:"O lançamento indireto de efluentes no corpo receptor"}]}],lacunas:["Verificar regras da operadora"]});
test("A versão 1.0 emitida pelo modelo é substituída pela versão canônica",()=>{
 const r=checkAI({response:JSON.stringify(valid())},sha,evidence);
 assert.equal(r.versao,"consulta-hibrida/1");
 assert.equal(r.commit,sha);
 assert.equal(r.itens[0].fonte.arquivo,evidence[0].arquivo);
});
test("O servidor define versão e commit mesmo se a IA omitir ambos",()=>{
 const x=valid();delete x.versao;delete x.commit;
 const r=checkAI({response:JSON.stringify(x)},sha,evidence);
 assert.equal(r.versao,"consulta-hibrida/1");assert.equal(r.commit,sha);
});
test("Não aceita commit divergente gerado pelo modelo",()=>{
 const x=valid();x.commit="0000000000000000000000000000000000000000";
 assert.throws(()=>checkAI({response:JSON.stringify(x)},sha,evidence),/Contrato de IA inválido/);
});
test("Não aceita ID inventado ou não recuperado no pacote",()=>{
 const x=valid();x.itens[0].chave="lei-federal-ficticia#art1";
 assert.throws(()=>checkAI({response:JSON.stringify(x)},sha,evidence),/Item inválido/);
});
test("Não aceita citação literal inventada",()=>{
 const x=valid();x.itens[0].evidencias[0].trecho="Trecho inventado pelo modelo, sem relação com a norma.";
 assert.throws(()=>checkAI({response:JSON.stringify(x)},sha,evidence),/Trecho não encontrado/);
});
test("Não aceita resposta que não é JSON válido",()=>{
 assert.throws(()=>checkAI({response:"Sem normas a citar"},sha,evidence),/Objeto JSON não localizado/);
});
