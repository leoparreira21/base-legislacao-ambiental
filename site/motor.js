/* Motor de busca da base de legislação ambiental.

   Módulo ES puro, sem DOM: o site (site/index.html) e a API do iatreports
   usam este mesmo arquivo, publicado no GitHub Pages ao lado de index.json.
   Mudou a regra de busca? Mude aqui, suba MOTOR_VERSAO e rode os testes
   (testes/motor.test.mjs). Mudou o formato de index.json? Suba FORMATO_INDICE.

   Uso:
     const m = criarMotor({indice, cnae, sinonimos, ambitos});
     m.buscaLivre({q:'usina de argamassa', cnaes:['2330399']});
     m.analiseCaso({campos:{atividade:'clínica odontológica', agua:'rede'}});
*/
export const MOTOR_VERSAO = '1.3.0';
export const FORMATO_INDICE = 1;
export const CATEGORIAS_FUNCAO = {enquadramento:'Específicas para enquadramento',licenciamento:'Específicas para licenciamento','obrigacoes-proibicoes':'Obrigações e proibições','limites-parametros':'Limites de parâmetros','normas-gerais':'Normas gerais'};
export const REPO = 'https://github.com/leoparreira21/base-legislacao-ambiental';

/* Opções do formulário de caso. O valor é a busca que o eixo faz. */
export const OPCOES_CASO = {
  modalidade: [
    {valor: '', rotulo: 'Não informado'},
    {valor: 'licenca previa', rotulo: 'Licença Prévia (LP)'},
    {valor: 'licenca instalacao', rotulo: 'Licença de Instalação (LI)'},
    {valor: 'licenca operacao', rotulo: 'Licença de Operação (LO)'},
    {valor: 'renovacao licenca operacao', rotulo: 'Renovação de LO (RLO)'},
    {valor: 'licenca ambiental simplificada', rotulo: 'Licença Ambiental Simplificada (LAS)'},
    {valor: 'licenca adesao compromisso', rotulo: 'LAC / adesão e compromisso'},
    {valor: 'ampliacao', rotulo: 'Ampliação'},
    {valor: 'regularizacao', rotulo: 'Regularização'},
    {valor: 'dispensa licenciamento', rotulo: 'Dispensa / baixo risco'},
  ],
  agua: [
    {valor: '', rotulo: 'Não informado'},
    {valor: 'rede', rotulo: 'Rede pública'},
    {valor: 'outorga poco agua subterranea', rotulo: 'Poço'},
    {valor: 'outorga captacao superficial', rotulo: 'Captação superficial'},
  ],
  efluentes: [
    {valor: '', rotulo: 'Não informado'},
    {valor: 'lancamento rede coletora esgoto', rotulo: 'Rede coletora de esgoto'},
    {valor: 'lancamento corpo receptor padrao', rotulo: 'Corpo hídrico'},
    {valor: 'infiltracao solo sumidouro', rotulo: 'Solo / fossa e sumidouro'},
    {valor: 'galeria pluvial', rotulo: 'Galeria pluvial'},
  ],
  localizacao: [
    {valor: 'manancial area protegida', rotulo: 'Não informado (triagem)'},
    {valor: 'manancial abastecimento', rotulo: 'Área de manancial'},
    {valor: 'carste karst', rotulo: 'Aquífero Karst'},
    {valor: 'preservacao permanente', rotulo: 'APP'},
    {valor: 'unidade conservacao amortecimento', rotulo: 'UC / zona de amortecimento'},
    {valor: '-', rotulo: 'Sem restrição conhecida'},
  ],
};
export const FILTROS_PADRAO = {esfera: '', listas: true, anexos: true};
export const AVISO = 'Candidatos para leitura. Presença na lista não prova aplicabilidade nem vigência: confira o dispositivo, as ressalvas e as remissões antes de concluir.';

/* ---------- texto ---------- */
const STOP = new Set('a o e as os de da do das dos em no na nos nas um uma uns umas por para pelo pela pelos pelas com sem que se ou ao aos à às sua seu suas seus como mais menos ser sao esta este isso essa esse entre sobre ate apos tipo outro outra outros outras qual quais'.split(' '));
export function normalizar(t){
  t=t.normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase();
  t=t.replace(/\b(\d{4})-(\d)\/(\d{2})\b/g,'$1$2$3');
  return (t.match(/[a-z0-9]+/g)||[]);
}
export function radical(w){
  if(/^\d/.test(w)||w.length<=3) return w;
  if(w.endsWith('oes')||w.endsWith('aes')) w=w.slice(0,-3)+'ao';
  else if(w.endsWith('ais')) w=w.slice(0,-3)+'al';
  else if(w.endsWith('eis')) w=w.slice(0,-3)+'el';
  else if(w.endsWith('ns')) w=w.slice(0,-2)+'m';
  else if(w.endsWith('res')||w.endsWith('zes')) w=w.slice(0,-2);
  else if(w.endsWith('s')&&!w.endsWith('ss')) w=w.slice(0,-1);
  if(w.length>4&&/[aoe]$/.test(w)) w=w.slice(0,-1);
  return w;
}
export const tokens=t=>normalizar(t).filter(w=>!STOP.has(w)).map(radical);
export function fmtCnae(id){return id.length===7?`${id.slice(0,4)}-${id[4]}/${id.slice(5)}`:id}

const GENERICO=new Set(tokens('ambiental ambientais estado parana procedimento procedimentos criterio criterios diretriz diretrizes definicao definicoes norma normas outra outras providencias dispoe estabelece estabelecer regulamenta altera institui lei resolucao instrucao normativa decreto conselho nacional federal estadual atividade atividades empreendimento empreendimentos ambito territorio controle aprova determina cumprimento unidade unidades publica publico operacao saude protecao gestao populacao instrumento basico bem estar geral gerais analise analises recurso recursos'));
const CNAE_GEN=new Set(tokens('fabricacao preparacao producao comercio atacadista varejista servico servicos atividade atividades outro outros outra outras especificado especificados anteriormente produto produtos artigo artigos exceto geral diverso diversos uso tipo parte partes peca pecas acessorio acessorios industria industrias industrial representante agente agentes comercial execucao fabricante usina usinas fabrica planta empresa loja deposito estabelecimento'));
const FATOR_TIPO=[1,.9,.3];
const PESO_TAG=2; // bônus do trecho marcado com a tag de um bloco, por radical da tag
const TIPO_TRECHO=['dispositivo','anexo','lista'];

/* Eixos da análise de caso: cada um vira uma busca curta e separada.
   campos: {atividade, cnae, modalidade, agua, efluentes, localizacao, residuos, outras} */
export function eixosCaso(campos){
  const v=k=>String(campos?.[k]??'').trim();
  const ativ=v('atividade'), mod=v('modalidade'), agua=v('agua'), efl=v('efluentes'), loc=v('localizacao'), res=v('residuos'), out=v('outras');
  const E=[];
  if(ativ) E.push({id:'atividade',t:'Atividade',d:'norma setorial e enquadramento',q:ativ,opc:'',listasCnae:true});
  E.push({id:'modalidade',t:'Competência e modalidade',d:mod?'regime geral e rito do requerimento':'regime geral',q:mod||'licenciamento ambiental competencia',opc:ativ});
  if(agua) E.push({id:'agua',t:'Água',d:'origem e outorga',q:agua,opc:ativ,nota:agua==='rede'?'Rede pública, isoladamente, não aciona as normas de outorga da base.':''});
  E.push({id:'efluentes',t:'Efluentes',d:efl?'tratamento e lançamento':'destino não informado: verificar',q:efl||'efluente lancamento tratamento',opc:ativ});
  E.push({id:'residuos',t:'Resíduos',d:'gerenciamento e destinação',q:res||'gerenciamento residuo',opc:ativ});
  if(loc&&loc!=='-') E.push({id:'localizacao',t:'Localização',d:'restrições territoriais',q:loc,opc:ativ});
  if(out) E.push({id:'outras',t:'Outras fontes',d:'emissões, riscos e alterações',q:out,opc:ativ});
  return E;
}

export function criarMotor({indice, cnae, sinonimos, ambitos, triagemHabilitada=true}){
  const DB=indice;
  if(!DB||!Array.isArray(DB.blocos)||!DB.docs) throw new Error('index.json inválido');
  if((DB.formato||1)!==FORMATO_INDICE) throw new Error(`index.json no formato ${DB.formato}; o motor ${MOTOR_VERSAO} lê o formato ${FORMATO_INDICE}`);
  const SINONIMOS=sinonimos?.sinonimos||sinonimos||{};
  const SETORIAL=ambitos?.ambitos||ambitos||{};

  /* ---------- índice ---------- */
  const IDX=[], DF=new Map();
  for(const b of DB.blocos){
    const [norma,l1,l2,id,ctx,tags,txt,k,funcao]=b;
    const tf=new Map(); const tt=tokens(txt);
    for(const w of tt) tf.set(w,(tf.get(w)||0)+1);
    const cx=new Set(tokens(ctx)), tg=new Set(tokens(tags.join(' ')));
    const todos=new Set([...tf.keys(),...cx,...tg]);
    for(const w of todos) DF.set(w,(DF.get(w)||0)+1);
    IDX.push({norma,l1,l2,id,ctx,tags,funcao,tset:new Set(tags),txt,k,tf,cx,tg,len:tt.length||1,norm:normalizar(txt).join(' '),seq:k===2?tt:null});
  }
  /* Tags da base, agrupadas pelos radicais (residuo-servico-saude e residuos-servico-saude
     são a mesma). Tag de uma palavra só genérica (#saude, #recurso) não vira bloco. */
  const TAGS=(()=>{
    const g=new Map();
    for(const b of DB.blocos) for(const tag of b[5]){
      const t=tokens(tag.replace(/-/g,' ')); if(!t.length) continue;
      if(t.length===1&&(GENERICO.has(t[0])||CNAE_GEN.has(t[0]))) continue;
      const k=t.join(' '); if(!g.has(k)) g.set(k,{t,tags:new Set()}); g.get(k).tags.add(tag);
    }
    return [...g.values()].map(x=>({t:x.t,tags:[...x.tags].sort()})).sort((a,b)=>b.t.length-a.t.length);
  })();
  const N=IDX.length, AVG=IDX.reduce((s,b)=>s+b.len,0)/N;
  const SYN=Object.entries(SINONIMOS).map(([k,v])=>({k:tokens(k),rot:k,alts:v.map(tokens)}))
      .sort((a,b)=>b.k.length-a.k.length);
  const idf=w=>{const d=DF.get(w)||0;return d?Math.log(1+(N-d+.5)/(d+.5)):0};

  /* conceitos: cada termo da busca (com seus sinônimos) */
  function conceitos(q,peso=1){
    const frases=[...q.matchAll(/"([^"]+)"/g)].map(m=>normalizar(m[1]).join(' ')).filter(Boolean);
    const resto=q.replace(/"[^"]*"/g,' ');
    const tk=tokens(resto); const out=[]; const usados=[];
    let i=0;
    while(i<tk.length){
      let m=null;
      for(const s of SYN){ if(s.k.length&&s.k.every((w,j)=>tk[i+j]===w)){m=s;break;} }
      if(m&&m.k.length>1){
        out.push({rot:m.rot,alts:[{t:m.k,p:1},...m.alts.map(a=>({t:a,p:.7}))],peso});usados.push(m.rot);i+=m.k.length;continue;
      }
      const w=tk[i]; const alts=[{t:[w],p:1}];
      if(m){m.alts.forEach(a=>alts.push({t:a,p:.7}));usados.push(m.rot);}
      if(!out.some(c=>c.alts[0].t.join(' ')===w)) out.push({rot:w,alts,peso});
      i++;
    }
    const uteis=out.filter(c=>!(c.alts.length===1&&c.alts[0].t.length===1&&(GENERICO.has(c.alts[0].t[0])||CNAE_GEN.has(c.alts[0].t[0]))));
    return {conceitos:comTags(uteis.length?uteis:out,new Set(tk)),frases,sinonimos:usados};
  }
  /* Blocos de tag: depois de gerados os blocos de palavras, cada tag da base cujas palavras
     estão todas na busca vira um bloco e absorve os blocos de palavras que cobre. Sem tag
     correspondente, os blocos ficam só com as palavras. Tag contida em outra maior fica de fora. */
  function comTags(base,termos){
    const achadas=TAGS.filter(x=>x.t.every(w=>termos.has(w)));
    const tags=achadas.filter(x=>!achadas.some(y=>y!==x&&y.t.length>x.t.length&&x.t.every(w=>y.t.includes(w))));
    if(!tags.length) return base;
    let livres=base; const blocos=[];
    for(const x of tags){
      const cobre=livres.filter(c=>c.alts[0].t.every(w=>x.t.includes(w)));
      livres=livres.filter(c=>!cobre.includes(c));
      blocos.push({rot:'#'+x.tags[0],tags:x.tags,t:x.t,cobre,peso:1,
        alts:[{t:x.t,p:1},...cobre.flatMap(c=>c.alts)].filter((a,i,l)=>l.findIndex(o=>o.t.join(' ')===a.t.join(' '))===i)});
    }
    return [...blocos,...livres];
  }
  function pontoTermo(b,w){
    const f=b.tf.get(w)||0; let s=0;
    if(f){s+=idf(w)*(f*2.2)/(f+1.2*(1-.75+.75*b.len/AVG));}
    if(b.cx.has(w)) s+=idf(w)*.5;
    if(b.tg.has(w)) s+=idf(w)*1.2;
    return s;
  }
  function melhor(b,c){
    let best=0;
    for(const a of c.alts){
      let s=0,todos=true;
      for(const w of a.t){const p=pontoTermo(b,w); if(!p){todos=false;break;} s+=p;}
      if(todos) best=Math.max(best,s*a.p);
    }
    return best;
  }
  // Bloco de tag: o trecho marcado com a tag conta o bloco inteiro e ganha o peso da tag;
  // sem a tag, valem as palavras que o bloco cobre, como antes.
  function pontoTag(b,c){
    const partes=c.cobre.length?c.cobre:[{alts:[{t:c.t,p:1}]}];
    let s=0,k=0;
    for(const p of partes){const v=melhor(b,p); if(v){s+=v;k++;}}
    if(c.tags.some(t=>b.tset.has(t))){s+=c.t.reduce((x,w)=>x+idf(w),0)*PESO_TAG;k=partes.length;}
    return {s,k,de:partes.length};
  }
  function pontuar(b,Q,minFrac=.6){
    for(const fr of Q.frases) if(!b.norm.includes(fr)) return 0;
    let soma=0,ok=0,acertos=0,total=0;
    for(const c of Q.conceitos){
      const r=c.tags?pontoTag(b,c):(v=>({s:v,k:v?1:0,de:1}))(melhor(b,c));
      if(r.s){soma+=r.s*c.peso;ok++;}
      acertos+=r.k; total+=r.de;
    }
    const n=Q.conceitos.length;
    if(n){
      const min=minFrac<1&&n>2?Math.ceil(n*minFrac):(minFrac<.5?1:n);
      if(ok<min) return 0;
      soma*=Math.pow(acertos/total,2);
    } else if(!Q.frases.length) return 0; else soma=1;
    return soma*FATOR_TIPO[b.k];
  }

  /* ---------- âmbito das normas ----------
     Regra fixa, que não muda com a quantidade de resultados:
     1. Norma setorial (ambitos.json) só entra se a atividade/consulta citar o setor dela.
     2. Demais normas só entram se a ementa ou o título citarem um termo da consulta.
     3. Dentro de uma norma admitida, mostram-se os trechos com termos da consulta.
     Se nada passar, a resposta é vazia: lacuna da base, não da busca. */
  const SET_TK=Object.fromEntries(Object.entries(SETORIAL).map(([k,v])=>[k,v.map(p=>({rot:p,t:tokens(p)}))]));
  const ESC_CACHE=new Map();
  function setorDe(nome){
    const d=DB.docs[nome]; return SET_TK[nome]||(d&&d.m?SET_TK[d.m]:null)||null;
  }
  function ementaDe(nome){
    if(ESC_CACHE.has(nome)) return ESC_CACHE.get(nome);
    const d=DB.docs[nome], mae=d.m?DB.docs[d.m]:null;
    const set=new Set(tokens([d.t,d.em,mae?.t||'',mae?.em||''].join(' ')).filter(w=>!GENERICO.has(w)));
    ESC_CACHE.set(nome,set); return set;
  }
  function termosDe(Q){
    const set=new Set(); Q.conceitos.forEach(c=>c.alts.forEach(a=>a.t.forEach(w=>set.add(w))));
    Q.frases.forEach(f=>tokens(f).forEach(w=>set.add(w))); return set;
  }
  // devolve o motivo da admissão, ou null
  function admite(nome,termos,termosAtiv,X){
    const setor=setorDe(nome);
    if(setor){
      const ref=new Set([...termos,...(termosAtiv||[]),...(X?X.termos:[])]);
      const p=setor.find(p=>p.t.every(w=>ref.has(w)));
      return p?`o âmbito da norma inclui «${p.rot}»`:null;
    }
    const em=ementaDe(nome), hit=[...termos].filter(w=>!GENERICO.has(w)&&em.has(w));
    return hit.length?`a ementa cita «${hit.slice(0,3).join('», «')}»`:null;
  }
  // X: expansão CNAE. listasCnae: se as listas de enquadramento podem admitir normas pelo CNAE
  function buscar(q,F=FILTROS_PADRAO,ativ='',X=null,listasCnae=true){
    const Q=conceitos(q), termos=new Set([...termosDe(Q),...tokens(q)]), termosAtiv=ativ?new Set([...termosDe(conceitos(ativ)),...tokens(ativ)]):null;
    const codigo=Q.conceitos.some(c=>/^\d{5,}$/.test(c.rot));
    const uteis=[...termos].filter(w=>!GENERICO.has(w)&&!CNAE_GEN.has(w));
    const motivos=new Map(), porNorma=new Map(), add=(n,b,s)=>{if(!porNorma.has(n))porNorma.set(n,[]);porNorma.get(n).push({b,s})};
    const ok=b=>{const d=DB.docs[b.norma];return !(F.categoria&&!b.funcao?.categorias.includes(F.categoria))&&!(F.esfera&&d.e!==F.esfera)&&!(!F.anexos&&d.m)};
    // 1) listas de enquadramento que citam o código, o termo de enquadramento ou todos os termos da busca
    const pelaLista=new Set();
    if(F.listas) for(const b of IDX){
      if(b.k!==2||!ok(b)) continue;
      let m=null,s=0;
      if(X&&listasCnae){
        const cod=[...X.codigos].find(c=>b.tf.has(c));
        if(cod){m=`a lista de atividades cita o CNAE ${fmtCnae(cod)}`;s=40;}
        else if(!temCodigo(b)){const g=X.ngr.find(g=>contem(b.seq,g.t)); if(g){m=`a lista de atividades cita «${g.rot}» (enquadramento da CNAE ${X.rot.join(', ')})`;s=15;}}
      }
      if(!m&&uteis.length&&uteis.every(w=>b.tf.has(w))){m=`a lista de atividades cita os termos buscados`;s=pontuar(b,Q,.01)/FATOR_TIPO[2];}
      if(!m) continue;
      if(!motivos.get(b.norma)) motivos.set(b.norma,m);
      pelaLista.add(b); add(b.norma,b,s);
    }
    // 2) âmbito (setor) e ementa; 3) trechos com os termos da busca
    for(const b of IDX){
      if(!ok(b)||pelaLista.has(b)) continue;
      if(!F.listas&&b.k===2) continue;
      if(!motivos.has(b.norma)) motivos.set(b.norma,codigo?'código citado no texto':admite(b.norma,termos,termosAtiv,X));
      if(!motivos.get(b.norma)) continue;
      if(b.k===2&&!codigo) continue; // linhas de lista só entram pela regra 1
      const s=pontuar(b,Q,.01); if(!s) continue;
      add(b.norma,b,s);
    }
    const grupos=[];
    for(const [norma,hs] of porNorma){
      hs.sort((x,y)=>y.s-x.s);
      const vistos=new Set(), top=[];
      for(const h of hs){const g=h.b.k===2?h.b.id.replace(/_lin\d+.*/,''):h.b.id+h.b.l1; if(vistos.has(g))continue; vistos.add(g); top.push(h.s); if(top.length===3)break;}
      grupos.push({norma,score:top[0]+.5*(top[1]||0)+.25*(top[2]||0),hits:hs,motivo:motivos.get(norma)});
    }
    grupos.sort((a,b)=>b.score-a.score);
    return {Q,grupos,X};
  }

  /* ---------- triagem CNAE (IBGE) ----------
     A atividade digitada é procurada na estrutura oficial da CNAE (descrições e
     lista de atividades de cada subclasse). As subclasses escolhidas acrescentam
     o código e os termos de enquadramento (classe, grupo, divisão, seção). */
  const CNAE=(cnae||[]).map(r=>{
    const [id,sub,cla,gru,did,div,sid,sec,ativs,comp,nao]=r;
    return {id,sub,cla,gru,did,div,sid,sec,comp,nao,
      sets:triagemHabilitada?[{n:3,t:new Set(tokens(sub))},{n:2,t:new Set(tokens(cla))},...ativs.map(a=>({n:1,t:new Set(tokens(a)),a}))]:[]};
  });
  const CNAE_POR_ID=new Map(CNAE.map(c=>[c.id,c]));
  const CNAE_DF=new Map(); for(const c of CNAE){const u=new Set(); c.sets.forEach(s=>s.t.forEach(w=>u.add(w))); u.forEach(w=>CNAE_DF.set(w,(CNAE_DF.get(w)||0)+1));}
  // Regra fixa: vence a maior cobertura de termos. Se só um termo casa, vale o termo mais raro na CNAE.
  function triagem(texto){
    if(!CNAE.length||!texto.trim()) return [];
    const cod=normalizar(texto).filter(w=>/^\d{7}$/.test(w));
    if(cod.length) return CNAE.filter(c=>cod.includes(c.id)).map(c=>({c,k:1,nivel:3,auto:true,via:'código informado'}));
    let termos=[...new Set(tokens(texto))].filter(w=>!CNAE_GEN.has(w)&&!GENERICO.has(w)&&w.length>1&&CNAE_DF.has(w));
    if(!termos.length) return [];
    const out=[];
    for(const c of CNAE){
      let best=null;
      for(const s of c.sets){
        const k=termos.filter(w=>s.t.has(w)).length; if(!k) continue;
        if(!best||k>best.k||(k===best.k&&s.n>best.s.n)) best={k,s};
      }
      if(best) out.push({c,k:best.k,nivel:best.s.n,hit:termos.filter(w=>best.s.t.has(w)),via:best.s.a?`atividade listada: ${best.s.a.toLowerCase()}`:best.s.n===3?'descrição da subclasse':'descrição da classe'});
    }
    const maxK=Math.max(0,...out.map(o=>o.k));
    let cs=out.filter(o=>o.k===maxK);
    if(maxK===1){ // um termo só: fica o mais raro
      const raro=termos.filter(w=>cs.some(o=>o.hit.includes(w))).sort((a,b)=>CNAE_DF.get(a)-CNAE_DF.get(b))[0];
      cs=cs.filter(o=>o.hit.includes(raro));
    }
    cs.sort((a,b)=>b.nivel-a.nivel);
    const topo=cs.filter(o=>o.nivel===cs[0].nivel);
    // marcação automática só quando é inequívoca: um único candidato no topo, descrito pela própria subclasse/classe
    // ou com todos os termos (2 ou mais) numa atividade listada
    if(topo.length===1&&maxK===termos.length&&(topo[0].nivel>=2||maxK>=2)) topo[0].auto=true;
    return cs.slice(0,10);
  }
  function palavras(txt){ // pares [radical, palavra original] sem stopwords
    return normalizar(txt).filter(w=>!STOP.has(w)).map(w=>[radical(w),w]);
  }
  function ngramas(txt){
    const p=palavras(txt), out=[];
    for(let i=0;i+1<p.length;i++){
      const [a,ao]=p[i],[b,bo]=p[i+1],c=p[i+2];
      if(b==='nao'&&c&&!CNAE_GEN.has(a)&&!CNAE_GEN.has(c[0])) out.push({t:[a,b,c[0]],rot:`${ao} nao ${c[1]}`});
      else if(a!=='nao'&&b!=='nao'&&!CNAE_GEN.has(a)&&!CNAE_GEN.has(b)&&!GENERICO.has(a)&&!GENERICO.has(b)) out.push({t:[a,b],rot:`${ao} ${bo}`});
    }
    return out;
  }
  function nucleo(txt){ // frase inteira da divisão sem as palavras genéricas
    const p=palavras(txt).filter(([r])=>!CNAE_GEN.has(r)&&!GENERICO.has(r));
    return p.length>=2?[{t:p.map(x=>x[0]),rot:p.map(x=>x[1]).join(' ')}]:[];
  }
  function expansao(ids){
    if(!ids.length) return null;
    const X={codigos:new Set(ids),termos:new Set(),ngr:[],rot:[]};
    for(const id of ids){
      const c=CNAE_POR_ID.get(id); if(!c) continue;
      [c.sub,c.cla,c.gru,c.div,c.sec].forEach(t=>tokens(t).forEach(w=>X.termos.add(w)));
      // só o par que abre cada descrição (núcleo da atividade) e a frase da divisão; pares só de objeto
      // ("veículos automotores") casariam atividades diferentes sobre o mesmo objeto
      for(const g of [...ngramas(c.sub).slice(0,1),...ngramas(c.cla).slice(0,1),...nucleo(c.div)])
        if(!X.ngr.some(h=>h.t.join(' ')===g.t.join(' '))) X.ngr.push(g);
      X.rot.push(fmtCnae(id));
    }
    return X;
  }
  const contem=(seq,g)=>{for(let i=0;i+g.length<=seq.length;i++){if(g.every((w,j)=>seq[i+j]===w))return true}return false};
  const temCodigo=b=>{for(const w of b.tf.keys()) if(/^\d{7}$/.test(w)) return true; return false};

  /* ---------- serialização (JSON da API e do site) ---------- */
  // faixas [início, fim) do texto a destacar: termos da busca (radicais), termos de enquadramento e frases
  function destaques(txt,Q,X){
    const alvo=new Set(); Q.conceitos.forEach(c=>c.alts.forEach(a=>a.t.forEach(w=>alvo.add(w))));
    if(X){X.ngr.forEach(g=>g.t.forEach(w=>w!=='nao'&&alvo.add(w)));}
    const frs=Q.frases, out=[];
    for(const m of txt.matchAll(/[A-Za-zÀ-ÿ0-9]+/g)){
      const n=normalizar(m[0])[0]; if(!n) continue;
      if(alvo.has(radical(n))||frs.some(f=>f.split(' ').includes(n))) out.push([m.index,m.index+m[0].length]);
    }
    return out;
  }
  function nomeNorma(n){
    const d=DB.docs[n]; if(!d.m) return d.t;
    const mae=DB.docs[d.m]; return (mae?mae.t+' — ':'')+d.t.replace(/^.*?–\s*/,'');
  }
  const urlTrecho=b=>`${REPO}/blob/${DB.commit}/${DB.docs[b.norma].f}#L${b.l1}-L${b.l2}`;
  const arred=x=>Math.round(x*1000)/1000;
  function trecho(h,Q,X){
    const b=h.b;
    return {id:b.id||null, rotulo:b.id||('L'+b.l1), contexto:b.ctx||'', tipo:TIPO_TRECHO[b.k],
      funcao:b.funcao||null, texto:b.txt, destaques:destaques(b.txt,Q,X), linhas:[b.l1,b.l2], url:urlTrecho(b), pontuacao:arred(h.s)};
  }
  // Uma norma do resultado. Linhas da mesma tabela: no máximo 2 (as demais ficam resumidas). Até maxTrechos.
  function grupo(g,Q,X,{maxTrechos=40}={}){
    const d=DB.docs[g.norma], mae=d.m?DB.docs[d.m]:null;
    const mostrados=[], tabs=new Map();
    for(const h of g.hits){
      if(h.b.k===2){const t=h.b.id.replace(/_lin\d+.*/,''); const c=tabs.get(t)||0; tabs.set(t,c+1); if(c>=2) continue;}
      mostrados.push(h);
    }
    return {arquivo:g.norma, titulo:d.t, nome:nomeNorma(g.norma), esfera:d.e||'', tipo:d.tp||'', situacao:d.s||'',
      anexoDe:d.m?{arquivo:d.m,titulo:mae?.t||d.m}:null, ementa:d.em||(mae?.em)||'',
      url:`${REPO}/blob/${DB.commit}/${d.f}`, motivo:g.motivo||'', pontuacao:arred(g.score),
      totalTrechos:g.hits.length, linhasResumidas:g.hits.length-mostrados.length,
      trechos:mostrados.slice(0,maxTrechos).map(h=>trecho(h,Q,X))};
  }
  function consulta(Q,X){
    return {termos:Q.conceitos.map(c=>({termo:c.rot,sinonimos:c.alts.slice(1).map(a=>a.t.join(' ')),tags:c.tags||[]})),
      frases:Q.frases,
      cnae:X?{codigos:[...X.codigos],rotulos:X.rot,termosEnquadramento:X.ngr.map(g=>g.rot)}:null};
  }
  function cnaeJSON(c){
    return {codigo:c.id, rotulo:fmtCnae(c.id), subclasse:c.sub, classe:c.cla, grupo:c.gru,
      divisao:{codigo:c.did,descricao:c.div}, secao:{codigo:c.sid,descricao:c.sec},
      compreende:c.comp||'', naoCompreende:c.nao||''};
  }
  const filtrosDe=f=>({categoria:f?.categoria||'', esfera:f?.esfera||'', listas:f?.listas!==false, anexos:f?.anexos!==false});
  const codigosValidos=ids=>[...new Set((ids||[]).map(x=>String(x).replace(/\D/g,'')))].filter(id=>CNAE_POR_ID.has(id));
  const pagina=(gs,limite,offset)=>gs.slice(offset,limite?offset+limite:undefined);

  /* ---------- operações de alto nível ---------- */
  // Candidatos CNAE para uma atividade ou código. "sugerido" = marcação automática inequívoca.
  function triagemCnae(texto){
    return triagem(String(texto||'')).map(o=>({...cnaeJSON(o.c), sugerido:!!o.auto, encontradoPor:o.via}));
  }
  function buscaLivre({q, cnaes=[], filtros, limiteNormas=0, offset=0, maxTrechos=40}={}){
    const texto=String(q||'').trim();
    const X=expansao(codigosValidos(cnaes)), F=filtrosDe(filtros);
    const r=buscar(texto,F,'',X);
    return {modo:'livre', consulta:{q:texto,...consulta(r.Q,X)}, filtros:F,
      total:{normas:r.grupos.length, trechos:r.grupos.reduce((s,g)=>s+g.hits.length,0)}, offset,
      normas:pagina(r.grupos,limiteNormas,offset).map(g=>grupo(g,r.Q,X,{maxTrechos}))};
  }
  function analiseCaso({campos={}, cnaes=[], filtros, maxTrechos=40}={}){
    const X=expansao(codigosValidos(cnaes)), F=filtrosDe(filtros);
    const eixos=eixosCaso(campos).map(e=>{
      const base={id:e.id, titulo:e.t, descricao:e.d, busca:e.q};
      if(e.nota) return {...base, nota:e.nota, normas:[]};
      const r=buscar(e.q,F,e.opc,X,!!e.listasCnae);
      return {...base, nota:'', consulta:consulta(r.Q,X), normas:r.grupos.map(g=>grupo(g,r.Q,X,{maxTrechos}))};
    });
    return {modo:'caso', campos, filtros:F, cnae:X?{codigos:[...X.codigos],rotulos:X.rot,termosEnquadramento:X.ngr.map(g=>g.rot)}:null, eixos};
  }
  function info(){
    return {commit:DB.commit, motor:MOTOR_VERSAO, formato:FORMATO_INDICE, arquivos:Object.keys(DB.docs).length, trechos:N};
  }

  return {
    // operações estáveis (contrato da API)
    info, triagemCnae, buscaLivre, analiseCaso,
    // baixo nível (usado pelo site e pelos testes)
    buscar, triagem, expansao, conceitos, destaques, grupo, nomeNorma, urlTrecho,
    DB, N,
  };
}
