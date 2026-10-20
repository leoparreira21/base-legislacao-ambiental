import {OPCOES_CASO} from './motor.js';
const API='https://legislacao-ambiental-api.leoparreira1007.workers.dev';
const $=id=>document.getElementById(id);
const fields=['atividade','modalidade','agua','efluentes','localizacao','residuos','outras'];
const labels={aplicavel:'Aplicável aos fatos informados',condicionada:'Aplicação condicionada',contextual:'Contexto para interpretação',nao_aplicavel:'Não aplicável aos fatos informados'};
let controller=null, generation=0, turns=[], backup=null;
const element=(tag,text,className)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;};
for(const name of ['modalidade','agua','efluentes','localizacao']) {
  const options=name==='localizacao'?[{valor:'',rotulo:'Não informado'},...OPCOES_CASO[name].slice(1)]:OPCOES_CASO[name];
  for(const o of options) {const option=element('option',o.rotulo);option.value=o.valor;$(name).append(option);}
}
if(matchMedia('(max-width:700px)').matches) $('case-details').open=false;
function fit(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,300)+'px';}
for(const el of document.querySelectorAll('textarea')) el.addEventListener('input',()=>fit(el));
function syncClear(){$('clear-question').hidden=!$('pergunta').value;}
$('pergunta').addEventListener('input',syncClear);
$('clear-question').onclick=()=>{$('pergunta').value='';fit($('pergunta'));syncClear();$('pergunta').focus();};
function error(message,field='pergunta') {
  $('chat-error').textContent=message;$('chat-error').hidden=false;
  if(field!=='pergunta') $('case-details').open=true;
  $(field).setAttribute('aria-invalid','true');$(field).setAttribute('aria-describedby',field==='atividade'?'activity-help chat-error':field==='cnaes'?'cnae-help chat-error':'question-help chat-error');
  $(field).focus();
}
function clearErrors(){for(const id of [...fields,'cnaes','pergunta'])$(id).removeAttribute('aria-invalid');$('chat-error').hidden=true;}
function busy(value) {
  $('send').disabled=value;$('send').textContent=value?'Consultando…':'Consultar a base ↗';
  $('cancel').hidden=!value;$('chat-form').setAttribute('aria-busy',String(value));
  for(const el of $('case-form').elements) el.disabled=value;
  for(const el of document.querySelectorAll('[data-example]'))el.disabled=value;
}
function sourceLink(url,title) {
  const a=element('a',title,'source');
  try {const u=new URL(url);if(u.protocol!=='https:'||u.hostname!=='github.com'||!u.pathname.startsWith('/leoparreira21/base-legislacao-ambiental/blob/'))return element('span','Fonte indisponível');a.href=u.href;}catch{return element('span','Fonte indisponível');}
  a.target='_blank';a.rel='noopener noreferrer';return a;
}
function titleKey(key) {
  const [norm,id]=key.split('#');
  const name=norm.replace(/-/g,' ').replace(/(\d+) (\d{4})$/,'nº $1/$2');
  const device=(id||'').replace(/^art(\d+)/,'Art. $1').replace('_cpt',' · caput').replace('_par1u',' · parágrafo único').replace(/_par(\d+)/,' · § $1').replace(/_inc(\d+)/,' · inciso $1').replace(/_ali([a-z])/,' · alínea $1').replace(/_/g,' · ');
  return name.charAt(0).toUpperCase()+name.slice(1)+' — '+device;
}
function renderAnswer(data,container) {
  const head=element('div',undefined,'answer-label');head.append(element('span',data.status==='analisado'?'DISPOSITIVOS E FUNDAMENTAÇÃO':'FONTES PARA CONFERÊNCIA'),element('span','Base '+(data.commit||'').slice(0,7)));container.append(head);
  for(const item of data.itens||[]) {
    const card=element('article',undefined,'evidence-card');
    card.append(element('span',labels[item.classificacao]||'Conferir','classification'),element('h3',titleKey(item.chave)),element('p',item.fundamentacao));
    const details=element('details');details.append(element('summary','Conferir citação e fonte'));
    for(const ev of item.evidencias||[]) {details.append(element('blockquote',ev.trecho),sourceLink(ev.fonte?.url||item.fonte.url,'Abrir '+ev.chave.split('#')[1]+' na fonte'));}
    card.append(details);
    if(item.verificar?.length) {
      card.append(element('p','O que conferir neste caso:','hint'));const list=element('ul');for(const v of item.verificar)list.append(element('li',v));card.append(list);
    }
    if(item.texto_parcial)card.append(element('p','Texto parcial no contexto da IA: leia a íntegra antes de concluir.','hint'));
    container.append(card);
  }
  for(const f of data.fontes||[]) {
    const card=element('article',undefined,'evidence-card');card.append(element('span','Candidato — sem conclusão da IA','classification'),element('h3',titleKey(f.chave)),element('blockquote',f.texto),sourceLink(f.url,'Conferir dispositivo na base'));container.append(card);
  }
  if(!data.itens?.length&&!data.fontes?.length) container.append(element('p','Não há dispositivos confirmados nesta resposta. Refine os dados e confira as lacunas abaixo.','empty'));
  if(data.lacunas?.length) {
    const gaps=element('section',undefined,'gaps');gaps.append(element('h3','O que ainda falta esclarecer'));const ul=element('ul');for(const g of data.lacunas)ul.append(element('li',g));gaps.append(ul);container.append(gaps);
  }
  const actions=element('div',undefined,'followups');
  for(const text of ['Quais condições preciso confirmar para aplicar esses dispositivos?','Quais dispositivos tratam especificamente dos efluentes deste caso?']) {
    const b=element('button',text,'btn ghost');b.type='button';b.onclick=()=>{$('pergunta').value=text;fit($('pergunta'));syncClear();$('pergunta').focus();};actions.append(b);
  }
  container.append(actions);
}
function renderTurns() {
  $('messages').replaceChildren();
  for(const turn of turns) {
    const section=element('section',undefined,'turn');const question=element('p',undefined,'question');question.append(element('small','SUA PERGUNTA'),document.createTextNode(turn.question));section.append(question);
    const facts=element('details');facts.append(element('summary','Dados usados nesta resposta'));const dl=element('dl',undefined,'hint');
    const nomes={atividade:'Atividade',modalidade:'Modalidade',agua:'Água',efluentes:'Efluentes',localizacao:'Localização',residuos:'Resíduos',outras:'Outros fatos'};
    for(const [key,value] of Object.entries(turn.campos)) {dl.append(element('dt',nomes[key]||key),element('dd',value||'Não informado'));}
    if(turn.cnaes.length)dl.append(element('dt','CNAEs'),element('dd',turn.cnaes.join(', ')));
    facts.append(dl);section.append(facts);
    renderAnswer(turn.data,section);$('messages').append(section);
  }
  $('intro').hidden=turns.length>0;$('export').hidden=!turns.length;
}
$('chat-form').addEventListener('submit',async e=> {
  e.preventDefault();if(controller) return;clearErrors();
  const campos=Object.fromEntries(fields.map(k=>[k,$(k).value.trim()]));
  if(campos.atividade.length<3)return error('Descreva a atividade com pelo menos 3 caracteres.','atividade');
  const cnaes=$('cnaes').value.split(/[,;\n]+/).map(x=>x.trim()).filter(Boolean);
  if(cnaes.length>12||cnaes.some(x=>!/^\d{7}$|^\d{4}-\d\/\d{2}$/.test(x)))return error('Use até 12 CNAEs no formato 8630-5/02 ou 8630502, separados por vírgula.','cnaes');
  const pergunta=$('pergunta').value.trim();if(pergunta.length<3)return error('Escreva sua pergunta com pelo menos 3 caracteres.');
  const current=++generation;controller=new AbortController();const signal=controller.signal;
  const timer=setTimeout(()=>controller?.abort('timeout'),180000);
  busy(true);$('chat-status').textContent='Buscando dispositivos, reunindo ressalvas e conferindo citações…';
  try {
    const response=await fetch(API+'/api/legislacao/chat',{method:'POST',headers:{'Content-Type':'application/json'},signal,
      body:JSON.stringify({campos,cnaes,pergunta,historico:turns.slice(-4).map(t=>t.question)})});
    let data;try{data=await response.json();}catch{throw Error('O serviço não retornou uma resposta válida. Tente novamente.');}
    if(!response.ok)throw Error(data.erro||'O serviço está indisponível. Tente novamente.');
    if(current!==generation)return;
    turns.push({question:pergunta,campos,cnaes,data});renderTurns();
    if($('pergunta').value.trim()===pergunta)$('pergunta').value='';fit($('pergunta'));syncClear();
    $('snapshot').textContent='Fontes conferidas no commit '+data.commit.slice(0,7)+'. Sem pesquisa externa.';
    $('chat-status').textContent='Consulta concluída. Leia os dispositivos e as condições indicadas.';
    const last=$('messages').lastElementChild;last.setAttribute('tabindex','-1');last.focus({preventScroll:true});last.scrollIntoView({behavior:'auto',block:'start'});
  } catch(e) {
    if(current!==generation)return;
    if(signal.aborted) {$('chat-status').textContent='Consulta interrompida. Sua pergunta foi preservada; você pode tentar novamente.';}
    else {error(navigator.onLine?e.message:'Você está sem conexão. Reconecte-se e envie novamente.');$('chat-status').textContent='Sua pergunta foi preservada.';}
  } finally {clearTimeout(timer);if(current===generation){controller=null;busy(false);}}
});
$('pergunta').addEventListener('keydown',e=>{if(e.ctrlKey&&e.key==='Enter'&&!e.isComposing){e.preventDefault();$('chat-form').requestSubmit();}});
$('cancel').onclick=()=>controller?.abort();
$('case-form').onsubmit=e=>e.preventDefault();
function snapshot(){return {values:Object.fromEntries([...fields,'cnaes','pergunta'].map(k=>[k,$(k).value])),turns:[...turns]};}
function apply(values){for(const [k,v] of Object.entries(values))$(k).value=v;for(const t of document.querySelectorAll('textarea'))fit(t);syncClear();}
function reset() {
  ++generation;controller?.abort();controller=null;busy(false);turns=[];
  apply(Object.fromEntries([...fields,'cnaes','pergunta'].map(k=>[k,''])));renderTurns();clearErrors();$('chat-status').textContent='';$('case-details').open=true;
}
$('new-case').onclick=()=>{backup=snapshot();reset();$('undo-case').hidden=false;$('atividade').focus();};
$('undo-case').onclick=()=>{if(!backup)return;reset();apply(backup.values);turns=backup.turns;renderTurns();backup=null;$('undo-case').hidden=true;$('chat-status').textContent='Caso anterior restaurado.';};
const examples={
  saude:{atividade:'Atividade médica ambulatorial com recursos para realização de exames complementares',cnaes:'8630-5/02',modalidade:'renovacao licenca operacao',agua:'rede',efluentes:'lancamento rede coletora esgoto',residuos:'Resíduos de serviços de saúde',pergunta:'Quais dispositivos específicos devo conferir para renovar a licença de operação deste ambulatório?'},
  industria:{atividade:'Usina de argamassa',cnaes:'2330-3/05',agua:'outorga poco agua subterranea',efluentes:'infiltracao solo sumidouro',pergunta:'Quais dispositivos da base tratam do licenciamento, da captação de água e dos efluentes desta atividade?'}
};
for(const b of document.querySelectorAll('[data-example]'))b.onclick=()=>{backup=snapshot();reset();apply(examples[b.dataset.example]);$('undo-case').hidden=false;$('chat-status').textContent='Exemplo preenchido. Ajuste os dados ao seu caso antes de consultar.';$('pergunta').focus();};
$('export').onclick=async()=>{
  const text=turns.map(t=>[
    'PERGUNTA: '+t.question,'DADOS: '+JSON.stringify(t.campos),'CNAEs: '+t.cnaes.join(', '),'BASE: '+t.data.commit,
    ...(t.data.itens||[]).flatMap(i=>[titleKey(i.chave)+' — '+labels[i.classificacao],i.fundamentacao,...i.evidencias.flatMap(e=>['“'+e.trecho+'”',e.fonte.url]),...(i.verificar||[]).map(v=>'Conferir: '+v)]),
    ...(t.data.fontes||[]).flatMap(f=>['Candidato sem conclusão: '+f.chave,f.texto,f.url]),
    'LACUNAS:',...(t.data.lacunas||[]),'Sugestões sujeitas a revisão técnica.'
  ].join('\n')).join('\n\n-----\n\n');
  try{await navigator.clipboard.writeText(text);$('chat-status').textContent='Consulta e fontes copiadas.';}catch{$('chat-status').textContent='O navegador bloqueou a cópia. Selecione o texto da consulta e copie manualmente.';}
};
window.addEventListener('beforeunload',e=>{if(turns.length||$('atividade').value||$('pergunta').value){e.preventDefault();e.returnValue='';}});
fetch(API+'/health',{signal:AbortSignal.timeout(10000)}).then(async r=>{if(!r.ok)throw Error();const d=await r.json();$('connection').textContent=d.chat?'Assistente conectado':'Assistente aguardando publicação';}).catch(()=>{$('connection').textContent='Conexão não confirmada';});
