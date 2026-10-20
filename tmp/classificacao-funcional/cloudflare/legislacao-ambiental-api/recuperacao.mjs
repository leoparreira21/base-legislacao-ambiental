import {tokens} from '../../site/motor.js';

const substantivo = d => /(?:^|_)(?:art\d+|anexo\d+)/.test(d.id) &&
  d.texto.replace(/^#+[^\n]*\n?|^Tags:.*$/gm, '').replace(/^\s*-?\s*\*\*[^*]+\*\*\s*\{#[^}]+\}/, '').trim().length > 45;

// As pontuações de eixos distintos não são comparáveis. Reservar vagas por eixo
// evita que modalidades longas expulsem efluentes e resíduos do contexto da IA.
export function selecionarEvidencias(result, fatias, commit) {
  const byNorm = new Map(), byId = new Map(), refs = new Map();
  for (const f of fatias) {
    const ds = f.dispositivos.map(d => ({...d, norma:f.norma, arquivo:f.arquivo}));
    byNorm.set(f.norma, ds);
    for (const d of ds) byId.set(d.chave, d);
    for (const [k,v] of Object.entries(f.remissoes)) refs.set(k,v);
  }
  for (const f of fatias) for (const [k,v] of Object.entries(f.destinos)) {
    if (!byId.has(k)) byId.set(k,{...v,norma:k.split('#')[0]});
  }
  const lists = result.eixos.filter(e=>!e.nota).map(e=> {
    const query = new Set(tokens(e.busca));
    const indireto=e.id==='efluentes' && /rede|coletor|indiret/.test(e.busca);
    if(indireto) tokens('lançamento indireto').forEach(t=>query.add(t));
    const ranked = new Map();
    for (const [rank,n] of (e.normas||[]).slice(0,6).entries()) {
      if (n.situacao==='revogada') continue;
      const ds = byNorm.get(n.arquivo)||[];
      for (const [pos,b] of (n.trechos||[]).slice(0,5).entries()) {
        const pool = ds.filter(d=>substantivo(d) && ((d.linha_inicio>=b.linhas[0] && d.linha_inicio<=b.linhas[1]) || (indireto && /indiret|rede coletora/i.test(d.texto))));
        for (const d of pool) {
          const words = new Set(tokens(d.texto+' '+d.tags.join(' ')));
          const coverage = [...query].filter(w=>words.has(w)).length / Math.max(1,query.size);
          const s = 3*coverage + 1/(1+rank) + 1/(1+pos) + (indireto && /indiret|rede coletora/i.test(d.texto)?3:0);
          if (!ranked.has(d.chave)||s>ranked.get(d.chave).score) ranked.set(d.chave,{d,score:s,eixo:e.id});
        }
      }
    }
    return {eixo:e.id, items:[...ranked.values()].sort((a,b)=>b.score-a.score||a.d.chave.localeCompare(b.d.chave))};
  });
  // Pergunta tem prioridade, mas todos os eixos com evidência recebem uma vaga.
  lists.sort((a,b)=>Number(b.eixo==='pergunta')-Number(a.eixo==='pergunta'));
  const selected = new Map(), counts = new Map();
  for(let round=0;round<3 && selected.size<12;round++) for(const list of lists) {
    if(selected.size>=12) break;
    const item = list.items.find(x=>!selected.has(x.d.chave) && (counts.get(x.d.norma.replace(/-anexo\d+$/, ''))||0)<2);
    if(item) {
      selected.set(item.d.chave,{...item,papel:'principal'});
      const family=item.d.norma.replace(/-anexo\d+$/, '');
      counts.set(family,(counts.get(family)||0)+1);
    }
  }
  const primary=[...selected.values()];
  function add(key,papel,eixo) {
    const d=byId.get(key);
    if(d && !selected.has(key) && selected.size<40) selected.set(key,{d,papel,eixo});
  }
  // Primeiro, pais e caput: um inciso isolado não explica a quem a obrigação cabe.
  for(const {d,eixo} of primary) {
    let parent=d.pai;
    for(let i=0;parent && i<4;i++) {add(parent,'pai',eixo);parent=byId.get(parent)?.pai;}
    const article=d.id.match(/^(.*?art\d+(?:-[a-z])?)(?:_|$)/)?.[1];
    if(article) add(d.norma+'#'+article+'_cpt','caput',eixo);
  }
  // Disposições de âmbito e exceções iniciais fazem parte da leitura da norma.
  for(const {d,eixo} of primary) {
    for(const x of byNorm.get(d.norma)||[]) if(/^art[12]_(?:cpt|par\d+[a-z]*)$/.test(x.id)) add(x.chave,'ambito',eixo);
  }
  // Ressalvas e remissões se alternam por principal, sem rebaixar um principal
  // a contexto quando outro dispositivo remete a ele.
  for(const {d,eixo} of primary) {
    for(const key of refs.get(d.chave)||[]) add(key,'remissao',eixo);
    const article=d.id.match(/^(.*?art\d+(?:-[a-z])?)(?:_|$)/)?.[1];
    if(article) for(const x of byNorm.get(d.norma)||[]) {
      if(x.id.startsWith(article+'_par')) add(x.chave,'ressalva',eixo);
    }
  }
  let budget=44000;
  const evidencias=[];
  for(const {d,papel,eixo} of selected.values()) {
    const size=Math.min(d.texto.length,2500,budget);
    if(size<40) continue;
    const texto=d.texto.slice(0,size); budget-=size;
    evidencias.push({chave:d.chave,papel,eixo,texto,truncado:size<d.texto.length,
      funcao:d.funcao?{categorias:d.funcao.categorias,estado:d.funcao.estado}:null, tags:d.tags.slice(0,12),elegivel:true,arquivo:d.arquivo,linhas:[d.linha_inicio,d.linha_fim],
      url:'https://github.com/leoparreira21/base-legislacao-ambiental/blob/'+commit+'/'+d.arquivo+'#L'+d.linha_inicio+'-L'+d.linha_fim});
  }
  const lacunas=[];
  for(const list of lists) if(!evidencias.some(e=>e.eixo===list.eixo && e.papel==='principal')) {
    lacunas.push('Não foram recuperados dispositivos específicos para o eixo '+list.eixo+'. Isso não prova ausência de obrigação.');
  }
  if(evidencias.some(e=>e.truncado)) lacunas.push('Há dispositivos longos com texto parcial; confira a íntegra nas fontes.');
  if(selected.size>=40) lacunas.push('O contexto atingiu o limite de dispositivos; outras remissões e ressalvas podem não ter sido incluídas.');
  return {evidencias,lacunas};
}
