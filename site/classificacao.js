import {CATEGORIAS_FUNCAO, REPO} from './motor.js';
const $=id=>document.getElementById(id), revisions=new Map();
let data, rows=[], page=0, dirty=false;
const SIZE=30;
const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
const norm=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const current=d=>revisions.get(d.chave)||d.funcao;
function error(message){$('erro').hidden=!message;$('erro').textContent=message;}
function filter(){
  const q=norm($('consulta').value.trim()), category=$('categoria').value, state=$('estado').value;
  rows=data.dispositivos.filter(d=>(!$('norma').value||d.chave.split('#')[0]===$('norma').value)&&
    (!q||norm(d.chave+' '+d.texto).includes(q))&&(!category||current(d).categorias.includes(category))&&
    (!state||(state==='desatualizada'?d.funcao.revisao_desatualizada&&!revisions.has(d.chave):current(d).estado===state)));
  page=0;render();
}
function render(){
  const frag=document.createDocumentFragment();
  for(const d of rows.slice(page*SIZE,(page+1)*SIZE)){
    const f=current(d), card=node('article',undefined,'norma');card.append(node('h2',d.chave));
    card.append(node('p',f.estado==='revisada'?'Revisão registrada':'Sugestão automática · pendente de revisão','hint'));
    if(d.funcao.revisao_desatualizada&&!revisions.has(d.chave))card.append(node('p','A redação mudou: a revisão anterior não foi aplicada.','hint'));
    const source=node('a','Conferir texto na fonte ↗');source.href=REPO+'/blob/'+data.commit+'/'+d.arquivo+'#L'+d.linha_inicio+'-L'+d.linha_fim;source.target='_blank';source.rel='noopener';card.append(source,node('p',d.texto,'review-text'));
    const reasons=node('details');reasons.append(node('summary','Motivos da pré-classificação'));
    for(const [c,signals] of Object.entries(d.funcao.motivos))reasons.append(node('p',CATEGORIAS_FUNCAO[c]+': '+signals.join('; ')));
    card.append(reasons);
    const field=node('fieldset'), choices=node('div',undefined,'checks');field.append(node('legend','Categorias funcionais deste dispositivo'));
    for(const [id,title] of Object.entries(CATEGORIAS_FUNCAO)){
      const label=node('label'), input=node('input');input.type='checkbox';input.value=id;input.checked=f.categorias.includes(id);label.append(input,document.createTextNode(title));choices.append(label);
    }
    field.append(choices);card.append(field);
    const button=node('button','Confirmar revisão','btn');button.type='button';button.onclick=()=>{
      const categories=[...choices.querySelectorAll('input:checked')].map(e=>e.value);
      if(!categories.length){error('Selecione ao menos uma categoria para '+d.chave);return;}
      revisions.set(d.chave,{categorias:categories,texto_sha256:d.funcao.texto_sha256,estado:'revisada'});dirty=true;error('');
      button.textContent='Revisão confirmada · exporte para guardar';updateStatus();
    };card.append(button);frag.append(card);
  }
  if(!rows.length)frag.append(node('p','Nenhum dispositivo corresponde aos filtros.','empty'));
  $('resultados').replaceChildren(frag);$('anterior').disabled=page===0;$('proxima').disabled=(page+1)*SIZE>=rows.length;
  $('pagina').textContent=rows.length?`${page+1} / ${Math.ceil(rows.length/SIZE)}`:'0 / 0';updateStatus();
}
function updateStatus(){
  $('status').textContent=`${data.dispositivos.length} dispositivos elegíveis · ${rows.length} no filtro · ${revisions.size} revisões prontas para exportar.`;
}
for(const id of ['consulta','norma','categoria','estado'])$(id).addEventListener(id==='consulta'?'input':'change',()=>{if(data)filter();});
$('anterior').onclick=()=>{page--;render();};$('proxima').onclick=()=>{page++;render();};
$('exportar').onclick=()=>{
  const output=Object.fromEntries([...revisions].sort().map(([key,r])=>[key,{categorias:r.categorias,texto_sha256:r.texto_sha256}]));
  const url=URL.createObjectURL(new Blob([JSON.stringify(output,null,2)+'\n'],{type:'application/json'})), a=node('a');
  a.href=url;a.download='classificacao-revisada.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);dirty=false;
};
$('importar').onchange=async()=>{
  const file=$('importar').files[0];if(!file||!data)return;
  try{
    if(file.size>20_000_000)throw Error('Arquivo maior que 20 MB.');
    const input=JSON.parse(await file.text()), byId=new Map(data.dispositivos.map(d=>[d.chave,d])), pending=[];
    if(!input||Array.isArray(input)||typeof input!=='object')throw Error('Objeto JSON esperado.');
    for(const [key,r] of Object.entries(input)){
      const d=byId.get(key);
      if(!d||!r||r.texto_sha256!==d.funcao.texto_sha256)throw Error('ID inexistente ou redação diferente: '+key);
      if(!Array.isArray(r.categorias)||!r.categorias.length||new Set(r.categorias).size!==r.categorias.length||r.categorias.some(c=>!Object.hasOwn(CATEGORIAS_FUNCAO,c)))throw Error('Categorias inválidas: '+key);
      pending.push([key,{categorias:r.categorias,texto_sha256:r.texto_sha256,estado:'revisada'}]);
    }
    for(const [key,r] of pending)revisions.set(key,r);dirty=true;error('');filter();
  }catch(e){error('Não foi possível importar: '+e.message);}
  $('importar').value='';
};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
try{
  const response=await fetch('./classificacao.json');if(!response.ok)throw Error('HTTP '+response.status);data=await response.json();
  if(data.formato!=='funcional/1'||!Array.isArray(data.dispositivos)||!/^[a-f0-9]{40}$/.test(data.commit))throw Error('Formato de classificação inválido');
  for(const [id,title] of Object.entries(CATEGORIAS_FUNCAO)){const option=node('option',title);option.value=id;$('categoria').append(option);}
  for(const id of [...new Set(data.dispositivos.map(d=>d.chave.split('#')[0]))].sort()){const option=node('option',id);option.value=id;$('norma').append(option);}
  for(const d of data.dispositivos)if(d.funcao.estado==='revisada')revisions.set(d.chave,d.funcao);
  $('exportar').disabled=false;filter();
}catch(e){$('status').textContent='Falha ao carregar a classificação.';error(e.message+' · Recarregue a página para tentar novamente.');}
