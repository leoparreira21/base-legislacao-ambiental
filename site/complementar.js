// Mesma recuperação determinística no navegador e no Worker. Não certifica incidência.
import {tokens} from './motor.js';
export const AVISO_COMPLEMENTAR='Acervo complementar ctresb-leis: vigência e conversão não revisadas. Confira a publicação oficial, alterações e ressalvas antes de aplicar.';
export function buscarComplementar(indice, consulta, {limite=6, esfera='', categoria=''}={}) {
  if(!indice || indice.formato!=='complementar/1' || esfera==='estadual' || categoria) return [];
  const q=[...new Set(tokens(consulta))];
  if(!q.length) return [];
  const reference=consulta.toLowerCase().match(/\b(conama|ibama)\s*(?:n[ºo.]?\s*)?(\d+)(?:\/(\d{4}))?/);
  const article=consulta.match(/\bart(?:igo|\.)?\s*(\d+(?:-[a-z])?)/i);
  const result=[];
  for(const doc of indice.documentos) {
    const exact=!!reference && doc.orgao===reference[1] && doc.id.endsWith('-'+Number(reference[2])+'-'+doc.id.split('-').at(-1)) && (!reference[3]||doc.id.endsWith('-'+reference[3]));
    if(reference&&!exact)continue;
    const scope=new Set(tokens(doc.ementa||''));
    const scopeScore=q.filter(t=>scope.has(t)).length/q.length;
    for(const art of doc.artigos) {
      if(exact&&article&&art.id!=='art'+article[1].toLowerCase())continue;
      const words=new Set(tokens(art.texto));
      const matches=q.filter(t=>words.has(t));
      // Termos cumulativos: uma palavra genérica em uma pergunta longa não basta.
      if(!exact && (matches.length<Math.min(2,q.length) || matches.length/q.length<0.65)) continue;
      result.push({chave:'ctresb:'+doc.id+'#'+art.id,titulo:doc.titulo,rotulo:art.id.replace('art','Art. '),
        texto:art.texto,arquivo:doc.arquivo,linhas:art.linhas,
        url:doc.url+'#L'+art.linhas[0]+'-L'+art.linhas[1],fonte_oficial:doc.fonte_oficial,
        origem:'ctresb-leis',commit:indice.commit,vigencia:doc.vigencia,
        score:matches.length/q.length+0.5*scopeScore+(exact?2:0),norma:doc.id});
    }
  }
  result.sort((a,b)=>b.score-a.score||a.chave.localeCompare(b.chave));
  const counts=new Map();
  return result.filter(x=>{const n=counts.get(x.norma)||0;counts.set(x.norma,n+1);return n<2;}).slice(0,limite);
}
export function evidenciasComplementares(indice, caso) {
  const queries=[['pergunta',caso.pergunta],['atividade',caso.campos?.atividade],
    ...['residuos','outras','localizacao'].map(k=>[k,caso.campos?.[k]])].filter(([,q])=>q);
  const found=new Map();
  for(const [eixo,q] of queries) for(const hit of buscarComplementar(indice,q,{limite:4})) {
    if(found.has(hit.chave)||found.size>=4)continue;
    found.set(hit.chave,{...hit,eixo,papel:'principal',elegivel:true,funcao:null,tags:[],
      texto:hit.texto.slice(0,1800),truncado:hit.texto.length>1800,verificacao_pendente:true});
  }
  // Âmbito inicial acompanha os artigos recuperados; nunca presume aplicabilidade.
  for(const primary of [...found.values()]) {
    const doc=indice.documentos.find(d=>d.id===primary.norma);
    for(const art of doc.artigos.filter(a=>['art1','art2'].includes(a.id))) {
      const chave='ctresb:'+doc.id+'#'+art.id;
      if(found.has(chave))continue;
      found.set(chave,{...primary,chave,papel:'ambito',texto:art.texto.slice(0,1200),
        truncado:art.texto.length>1200,linhas:art.linhas,
        url:doc.url+'#L'+art.linhas[0]+'-L'+art.linhas[1]});
    }
  }
  return [...found.values()];
}
