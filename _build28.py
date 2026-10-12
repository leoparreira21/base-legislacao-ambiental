import pymupdf,re,pathlib,json
pdf=r'C:\Users\leo_p\Downloads\acrescentar à base legislação ambiental\IN 28 2026.pdf'
d=pymupdf.open(pdf)
def cleaned_pages(start,stop):
    result=[]
    mark=re.compile(r'^(?:Art\.?\s*\d+(?!\s*[º°]?\s+d[oa]\b)\s*[º°]?\.?|CAP[IÍ]TULO\s+[IVXLCDM]+|Se[cç][aã]o\s+[IVXLCDM]+|Subse[cç][aã]o\s+[IVXLCDM]+|Par[aá]grafo [uú]nico|§\s*\d+|[IVXLCDM]+\s*[-–—]|[a-z]\s*[).]|\d+\s*[).])',re.I)
    for pi in range(start,stop):
        raw=d[pi].get_text()
        raw=re.sub(r'(?m)^Rua Engenheiros Rebouças,.*(?:\n|$)','',raw)
        raw=re.sub(r'(?m)^\s*(?:Assinatura Qualificada realizada.*|Documento assinado nos termos.*|A autenticidade deste documento.*|https?://www\.eprotocolo\.pr\.gov\.br.*|[0-9a-f]{32})\s*$','',raw)
        raw=re.sub(r'(?m)^\s*\d{1,3}a?\s*$','',raw)
        cur=''
        for rawline in raw.splitlines():
            x=rawline.strip()
            if not x:
                if cur: result.append(re.sub(r'\s+',' ',cur).strip()); cur=''
                continue
            if mark.match(x) and cur:
                result.append(re.sub(r'\s+',' ',cur).strip());cur=''
            if not cur: cur=x
            elif cur.endswith('-') and not cur.endswith(' -') and x[:1].islower(): cur=cur[:-1]+x
            else: cur+=' '+x
        if cur: result.append(re.sub(r'\s+',' ',cur).strip())
    return result
blocks=cleaned_pages(0,71)
# Exclude electronic appendix/signature material after Article 106 and the appendix list.
cut=next(i for i,b in enumerate(blocks) if b.startswith('RELAÇÃO DOS ANEXOS'))
blocks=blocks[:cut]
def wikify(t):
    mapping=[(r'Decreto Estadual nº 13\.433','decreto-estadual-13433-2026'),(r'Lei Estadual nº 10\.066','lei-estadual-10066-1992'),(r'Lei Estadual nº 20\.070','lei-estadual-20070-2019'),(r'Decreto Estadual nº 3\.813','decreto-estadual-3813-2020'),(r'Decreto Estadual nº 11\.977','decreto-estadual-11977-2022'),(r'Decreto Estadual nº 9\.541','decreto-estadual-9541-2025'),(r'Lei Estadual nº 22\.252','lei-estadual-22252-2024'),(r'Lei Estadual nº 19\.857','lei-estadual-19857-2019'),(r'Lei Federal nº 6\.938','lei-federal-6938-1981'),(r'Lei Federal nº 12\.651','lei-federal-12651-2012'),(r'Lei Federal nº 9\.605','lei-federal-9605-1998'),(r'Lei nº 9\.605','lei-federal-9605-1998'),(r'Decreto Regulamentador n\.?º 6\.514','decreto-federal-6514-2008'),(r'Resolução CONAMA n\.?º 273','resolucao-conama-273-2000'),(r'Resolução CONAMA nº 362','resolucao-conama-362-2005'),(r'Resolução CONAMA nº 237','resolucao-conama-237-1997'),(r'Resolução CONAMA nº 307','resolucao-conama-307-2002'),(r'Resolução CONAMA nº 006','resolucao-conama-6-1986'),(r'Resolução CEMA n° 100 de 2017','resolucao-cema-100-2017'),(r'Resolução SEDEST n\.?º 003/2020','resolucao-sedest-3-2020'),(r'Decreto Estadual nº 8\.680','decreto-estadual-8680-2013'),(r'Decreto Estadual nº 1\.940','decreto-estadual-1940-1996'),(r'Decreto Estadual nº 6\.674','decreto-estadual-6674-2002'),(r'Instrução Normativa nº 39','instrucao-normativa-iat-39-2025'),(r'Instrução Normativa IBAMA nº 13','instrucao-normativa-ibama-13-2021'),(r'Portaria IAP nº 212/2019','portaria-iap-212-2019'),(r'Portaria IAP nº 159/2015','portaria-iap-159-2015'),(r'Lei Federal nº 6\.496/77','lei-federal-6496-1977'),(r'Lei nº 6\.496/77','lei-federal-6496-1977')]
    for pat,slug in mapping:
        t=re.sub(pat,lambda m:'[['+slug+'|'+m.group(0)+']]' if '[[' not in m.group(0) else m.group(0),t,flags=re.I)
    t=re.sub(r'(?i)\bArt\.?\s*(\d+)º(?!\|)',lambda m:'[[#art'+m.group(1)+'|'+m.group(0)+']]',t)
    return t
pretext='\n\n'.join(blocks[:next(i for i,b in enumerate(blocks) if b.startswith('RESOLVE'))])
pretext=pretext[pretext.lower().find('o diretor-presidente'):]
rest=blocks[next(i for i,b in enumerate(blocks) if b.startswith('RESOLVE'))+1:]
out=['---','norma: Instrução Normativa IAT nº 28/2026','arquivo: instrucao-normativa-iat-28-2026','tipo: instrucao-normativa','esfera: estadual','orgao: Instituto Água e Terra - IAT','uf: PR','numero: 28','ano: 2026','data_assinatura: 2026-09-10','ementa: "Estabelece definições, critérios, diretrizes e procedimentos, para o licenciamento ambiental de Posto Revendedor, Ponto de Abastecimento, Instalação de Sistema Retalhista de Combustível – TRR, Posto Flutuante e Base de Distribuição de Combustíveis."','situacao: vigente','publicacao: "Data e número do DIOE desta publicação não constam do PDF fornecido."','vigencia: "Na data da publicação; art. 106 torna sem efeito a IN IAT nº 39/2025, publicada no DIOE nº 11893, de 30/04/2025."','regulamenta: []','altera: []','alterado_por: []','revoga: ["[[instrucao-normativa-iat-39-2025]]"]','revogado_por: []','cita: ["[[decreto-estadual-13433-2026]]", "[[decreto-estadual-3813-2020]]", "[[decreto-estadual-11977-2022]]", "[[decreto-estadual-9541-2025]]", "[[decreto-estadual-8680-2013]]", "[[decreto-estadual-1940-1996]]", "[[decreto-estadual-6674-2002]]", "[[decreto-federal-6514-2008]]", "[[lei-estadual-10066-1992]]", "[[lei-estadual-19857-2019]]", "[[lei-estadual-20070-2019]]", "[[lei-estadual-22252-2024]]", "[[lei-federal-6496-1977]]", "[[lei-federal-6938-1981]]", "[[lei-federal-9605-1998]]", "[[lei-federal-12651-2012]]", "[[resolucao-cema-100-2017]]", "[[resolucao-conama-237-1997]]", "[[resolucao-conama-273-2000]]", "[[resolucao-conama-307-2002]]", "[[resolucao-conama-362-2005]]", "[[resolucao-conama-6-1986]]", "[[resolucao-sedest-3-2020]]", "[[instrucao-normativa-ibama-13-2021]]", "[[instrucao-normativa-iat-39-2025]]", "[[portaria-iap-212-2019]]", "[[instrucao-normativa-iat-28-2026-anexo2]]", "[[instrucao-normativa-iat-28-2026-anexo3]]", "[[instrucao-normativa-iat-28-2026-anexo4]]", "[[instrucao-normativa-iat-28-2026-anexo5]]", "[[instrucao-normativa-iat-28-2026-anexo6]]", "[[instrucao-normativa-iat-28-2026-anexo9]]"]','tags: [area-contaminada, app, ampliacao, autorizacao-ambiental, baixo-potencial-poluidor, condicionante, csaO, dbo, dqo, efluente, enquadramento, estudo-ambiental, licenciamento-ambiental, monitoramento, outorga, pgrs, pcpa, posto-combustivel, prazo, rap, regularizacao, renovacao, residuo-solido, risco-ambiental, sancao, tanque, taxa-ambiental, vigencia]','fonte: "PDF IN 28 2026.pdf fornecido pelo usuário; 118 páginas; assinatura e publicação no DIOE desta edição não informadas no PDF. Art. 106 cita a IN nº 39/2025 publicada no DIOE nº 11893, de 30/04/2025."','texto: compilado (atualizado até 2026-09-10)','---','','# Instrução Normativa IAT nº 28, de 10 de setembro de 2026 {#instrucao-normativa-iat-28-2026}','','> **Súmula:** Estabelece definições, critérios, diretrizes e procedimentos, para o licenciamento ambiental de Posto Revendedor, Ponto de Abastecimento, Instalação de Sistema Retalhista de Combustível – TRR, Posto Flutuante, Base de Distribuição de Combustíveis.','', '**Preâmbulo** {#preambulo} '+wikify(pretext),'','RESOLVE','']
art_occ={}; chapter_occ={}; section_occ={}; article_blocks=[]; headings=[]
article_re=re.compile(r'^Art\.?\s*(\d+)(?!\s*[º°]?\s+d[oa]\b)\s*[º°]?\.?\s*(.*)$',re.I)
def is_heading(x): return bool(re.match(r'^(?:CAP[IÍ]TULO\s+[IVXLCDM]+|Se[cç][aã]o\s+[IVXLCDM]+|Subse[cç][aã]o\s+[IVXLCDM]+)\b',x,re.I))
# determine actual document segments
current=None
for b in rest:
    m=article_re.match(b)
    if m:
        if current: article_blocks.append(current)
        current=[m.group(1),m.group(2),[]]
    elif is_heading(b):
        if current: article_blocks.append(current); current=None
        headings.append(b)
    elif current is not None: current[2].append(b)
if current: article_blocks.append(current)
# headings emitted in source order by walking again
def article_id(n):
    c=art_occ.get(n,0);art_occ[n]=c+1;return 'art'+n+('-a' if c else '')
def roman_num(x):
    vals={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}; n=0; prev=0
    for ch in x[::-1]:
        v=vals.get(ch,0); n+=-v if v<prev else v; prev=max(prev,v)
    return n
def suffix(n):
    z=''
    while n:
        n,rem=divmod(n-1,26);z=chr(97+rem)+z
    return '-' + z
def render_article(n,caput,devs):
    aid=article_id(n); out.extend([f'###### Art. {n}º'+(' (repetido no original)' if aid.endswith('-a') else '')+f' {{#{aid}}}','','Tags: #posto-combustivel #licenciamento-ambiental #area-contaminada',''])
    if devs and re.match(r'^Art\.?\s*\d+\s*[º°]?\.?\s+d[oa]\s+presente Instrução Normativa',devs[0],re.I):
        caput=(caput+' '+devs.pop(0)).strip()
    # Attach sequence numbers and hierarchical paths to all recognized legal/list markers.
    inc_counts={}; para_counts={}; item_counts={}; current_parent=aid+'_cpt'; current_para=None; last_inc_label=None; alpha_base=None
    if caput: out.append(f'**Art. {n}º, caput** {{#{aid}_cpt}} '+wikify(caput))
    skip_table=(n=='6')
    for b in devs:
        if skip_table:
            if b.lower().startswith('parágrafo único'):
                skip_table=False
            else: continue
        m=re.match(r'^Parágrafo único\.?\s*(.*)$',b,re.I)
        if m:
            para_counts['u']=para_counts.get('u',0)+1;pid=aid+'_par1u'+(suffix(para_counts['u']-1) if para_counts['u']>1 else '')
            out.extend(['',f'**Art. {n}º, parágrafo único** {{#{pid}}} '+wikify(m.group(1))]);current_parent=pid;current_para=pid;alpha_base=None;continue
        m=re.match(r'^§\s*(\d+)\s*[º°o]?\.?\s*(.*)$',b)
        if m:
            k=m.group(1);para_counts[k]=para_counts.get(k,0)+1;pid=aid+f'_par{k}'+(suffix(para_counts[k]-1) if para_counts[k]>1 else '')
            out.extend(['',f'**Art. {n}º, § {k}º** {{#{pid}}} '+wikify(m.group(2))]);current_parent=pid;current_para=pid;alpha_base=None;continue
        m=re.match(r'^([IVXLCDM]+)\s*[-–—]\s*(.*)$',b)
        if m:
            lab=m.group(1).upper(); pos=roman_num(lab);key=lab;inc_counts[key]=inc_counts.get(key,0)+1
            par=current_para or aid+'_cpt';iid=par+f'_inc{pos}'+(suffix(inc_counts[key]-1) if inc_counts[key]>1 else '')
            out.extend(['',f'- **Art. {n}º, '+('§ '+re.search(r'_par(\d+)',par).group(1)+'º, ' if '_par' in par and re.search(r'_par(\d+)',par) else 'caput, ')+'inciso '+lab+(' (repetido no original)' if inc_counts[key]>1 else '')+f'** {{#{iid}}} '+wikify(m.group(2))]);current_parent=iid;alpha_base=iid;last_inc_label=lab;continue
        m=re.match(r'^([a-z])\s*[).]\s*(.*)$',b)
        if m:
            lab=m.group(1); parent=alpha_base or current_parent; key=parent+'_ali'+lab; item_counts[key]=item_counts.get(key,0)+1
            iid=key+(suffix(item_counts[key]-1) if item_counts[key]>1 else '')
            out.extend([f'  - **alínea "{lab}"** {{#{iid}}} '+wikify(m.group(2))]);current_parent=iid;continue
        m=re.match(r'^(\d+)\s*[.)]\s*(.*)$',b)
        if m:
            lab=m.group(1);parent=current_parent;key=parent+'_ite'+lab;item_counts[key]=item_counts.get(key,0)+1;iid=key+(suffix(item_counts[key]-1) if item_counts[key]>1 else '')
            out.extend([f'    - **item {lab}** {{#{iid}}} '+wikify(m.group(2))]);current_parent=iid;alpha_base=iid;continue
        m=re.match(r'^([ivxlcdm]+)\s*\.\s*(.*)$',b,re.I)
        if m:
            lab=m.group(1).lower();parent=current_parent; iid=parent+'_ite'+str(roman_num(lab.upper()));out.extend([f'      - **subitem {lab}** {{#{iid}}} '+wikify(m.group(2))]);current_parent=iid;continue
        out.extend(['',wikify(b)])
    out.append('')
    return aid

# output in source order; headings are carried from positions in source blocks, therefore collect with source chronology instead.
out.clear()
# reconstruct preamble from earlier prefix + parsed legal stream
out=['---','norma: Instrução Normativa IAT nº 28/2026','arquivo: instrucao-normativa-iat-28-2026','tipo: instrucao-normativa','esfera: estadual','orgao: Instituto Água e Terra - IAT','uf: PR','numero: 28','ano: 2026','data_assinatura: 2026-09-10','ementa: "Estabelece definições, critérios, diretrizes e procedimentos, para o licenciamento ambiental de postos e instalações de armazenamento e distribuição de combustíveis."','situacao: vigente','publicacao: "Data e número do DIOE desta publicação não constam do PDF fornecido."','vigencia: "Na data da publicação; art. 106 torna sem efeito a IN IAT nº 39/2025, publicada no DIOE nº 11893, de 30/04/2025."','regulamenta: []','altera: []','alterado_por: []','revoga: ["[[instrucao-normativa-iat-39-2025]]"]','revogado_por: []','cita: ["[[decreto-estadual-13433-2026]]", "[[decreto-estadual-3813-2020]]", "[[decreto-estadual-11977-2022]]", "[[decreto-estadual-9541-2025]]", "[[decreto-estadual-8680-2013]]", "[[decreto-estadual-1940-1996]]", "[[decreto-estadual-6674-2002]]", "[[decreto-federal-6514-2008]]", "[[lei-estadual-10066-1992]]", "[[lei-estadual-19857-2019]]", "[[lei-estadual-20070-2019]]", "[[lei-estadual-22252-2024]]", "[[lei-federal-6496-1977]]", "[[lei-federal-6938-1981]]", "[[lei-federal-9605-1998]]", "[[lei-federal-12651-2012]]", "[[resolucao-cema-100-2017]]", "[[resolucao-conama-237-1997]]", "[[resolucao-conama-273-2000]]", "[[resolucao-conama-307-2002]]", "[[resolucao-conama-362-2005]]", "[[resolucao-conama-6-1986]]", "[[resolucao-sedest-3-2020]]", "[[instrucao-normativa-ibama-13-2021]]", "[[instrucao-normativa-iat-39-2025]]", "[[portaria-iap-212-2019]]", "[[instrucao-normativa-iat-28-2026-anexo2]]", "[[instrucao-normativa-iat-28-2026-anexo3]]", "[[instrucao-normativa-iat-28-2026-anexo4]]", "[[instrucao-normativa-iat-28-2026-anexo5]]", "[[instrucao-normativa-iat-28-2026-anexo6]]", "[[instrucao-normativa-iat-28-2026-anexo9]]"]','tags: [area-contaminada, app, ampliacao, autorizacao-ambiental, baixo-potencial-poluidor, condicionante, dbo, dqo, efluente, enquadramento, estudo-ambiental, licenciamento-ambiental, monitoramento, outorga, pgrs, pcpa, posto-combustivel, prazo, rap, regularizacao, renovacao, residuo-solido, risco-ambiental, sancao, taxa-ambiental, vigencia]','fonte: "PDF IN 28 2026.pdf fornecido pelo usuário; 118 páginas. Dados de publicação desta edição não constam do PDF; assinatura qualificada eProtocolo conforme arquivo. Art. 106 cita publicação anterior da IN 39/2025 no DIOE nº 11893."','texto: compilado (atualizado até 2026-09-10)','---','','# Instrução Normativa IAT nº 28, de 10 de setembro de 2026 {#instrucao-normativa-iat-28-2026}','','> **Súmula:** Estabelece definições, critérios, diretrizes e procedimentos, para o licenciamento ambiental de Posto Revendedor, Ponto de Abastecimento, Instalação de Sistema Retalhista de Combustível – TRR, Posto Flutuante, Base de Distribuição de Combustíveis.','', '**Preâmbulo** {#preambulo} '+wikify(pretext),'','RESOLVE','']
# render body in source sequence
chapter_counts={}; sec_counts={}; idx=0; i=0
while i<len(rest):
    b=rest[i]
    ch=re.match(r'^CAP[IÍ]TULO\s+([IVXLCDM]+)\s*(.*)$',b,re.I)
    if ch:
        num=ch.group(1).upper();chapter_counts[num]=chapter_counts.get(num,0)+1;aid='cap'+str(roman_num(num))+(suffix(chapter_counts[num]-1) if chapter_counts[num]>1 else '')
        out.extend(['',f'## CAPÍTULO {num} {ch.group(2)} {{#{aid}}}','']);i+=1;continue
    sec=re.match(r'^(Se[cç][aã]o|Subse[cç][aã]o)\s+([IVXLCDM]+)\s*(.*)$',b,re.I)
    if sec:
        num=sec.group(2).upper(); sec_counts[num]=sec_counts.get(num,0)+1; aid='sec'+num.lower()+(suffix(sec_counts[num]-1) if sec_counts[num]>1 else '')
        out.extend(['',f'### {sec.group(1)} {num} {sec.group(3)} {{#{aid}}}','']);i+=1;continue
    m=article_re.match(b)
    if m:
        n,cap=m.group(1),m.group(2); dev=[]; i+=1
        while i<len(rest) and not article_re.match(rest[i]) and not is_heading(rest[i]): dev.append(rest[i]);i+=1
        render_article(n,cap,dev);continue
    i+=1
# Type 3 table in Art. 6, visually checked against PDF page 9.
art6=next(i for i,x in enumerate(out) if x.startswith('###### Art. 6º'))
tab=['','**Art. 6º, Tabela I** {#art6_tab1}','','- **Art. 6º, Tabela I, linha 1** {#art6_tab1_lin1} Modalidade: Dispensa de Licenciamento Ambiental–DLAM | Critérios: Ponto de abastecimento com instalações aéreas de até 15.000 L de volume total da tancagem destinadas exclusivamente ao abastecimento do detentor das instalações. Não se enquadram nessa modalidade qualquer associação em forma de empresa, cooperativa, condomínio, clube ou assemelhado que comercialize combustíveis em especial para veículos de passeio. | Tipo de empreendimento: Ponto de Abastecimento com instalações aéreas de até 15.000 L de volume total da tancagem.','- **Art. 6º, Tabela I, linha 2** {#art6_tab1_lin2} Modalidade: Licenciamento Trifásico–LP,LI e LO | Critérios: Empreendimentos ou atividades que não se enquadrem nas modalidades anteriores. | Tipo de empreendimento: Ponto de Abastecimento, Posto Revendedor, Base de Distribuição, Instalação de Sistema Retalhista – TRR, Posto Flutuante.','']
insert=next(i for i,x in enumerate(out) if x.startswith('**Art. 6º, parágrafo único')) if any(x.startswith('**Art. 6º, parágrafo único') for x in out) else next(i for i,x in enumerate(out) if x.startswith('**Art. 6º, caput'))+1
out[insert:insert]=tab
# Annexes 1, 7 and 8 are templates; II, III, IV, V, VI, IX are separate type 2.
out+=['','### ANEXO I – Declaração de uso/finalidade do combustível armazenado para DLAM {#anexo1}','Modelo de declaração de uso/finalidade do combustível armazenado para DLAM.','', '### ANEXO II – Termo de referência para projeto executivo de remoção de componentes e desmobilização de sistemas de armazenamento subterrâneo e aéreo de combustíveis {#anexo2}','[[instrucao-normativa-iat-28-2026-anexo2|Texto do Anexo II]]','', '### ANEXO III – Termo de referência para elaboração do Memorial de Caracterização do Empreendimento – MCE {#anexo3}','[[instrucao-normativa-iat-28-2026-anexo3|Texto do Anexo III]]','', '### ANEXO IV – Termo de referência para elaboração do Relatório Ambiental Preliminar – RAP {#anexo4}','[[instrucao-normativa-iat-28-2026-anexo4|Texto do Anexo IV]]','', '### ANEXO V – Diretrizes para elaboração e apresentação do Projeto de Controle de Poluição Ambiental {#anexo5}','[[instrucao-normativa-iat-28-2026-anexo5|Texto do Anexo V]]','', '### ANEXO VI – Termo de referência para elaboração do Plano de Gerenciamento de Resíduos Sólidos {#anexo6}','[[instrucao-normativa-iat-28-2026-anexo6|Texto do Anexo VI]]','', '### ANEXO VII – Ocorrência de fase livre {#anexo7}','Modelo de declaração de ocorrência de fase livre.','', '### ANEXO VIII – Ficha de vistoria de infraestrutura {#anexo8}','Modelo de ficha de vistoria de infraestrutura.','', '### ANEXO IX – Roteiro para inspeção de tanques aéreos de armazenamento de combustíveis e suas tubulações {#anexo9}','[[instrucao-normativa-iat-28-2026-anexo9|Texto do Anexo IX]]','', '## Relação com normas superiores','', '- O art. 106 torna sem efeito a IN IAT nº 39, de 29/04/2025, publicada no DIOE nº 11893, de 30/04/2025. O arquivo da IN 39/2025 não existe no acervo; a relação está registrada, mas não é possível preencher relação recíproca ou atualizar seu texto.','', '## Notas de transcrição','', '- Rodapés com endereço institucional, paginação e assinaturas eletrônicas foram removidos. O PDF contém 118 páginas; o texto normativo termina no art. 106 e é seguido pelos nove anexos.','- O art. 6º contém tabela de enquadramento; as duas linhas foram conferidas visualmente na página 9, repetindo células mescladas para tornar cada linha autossuficiente. A grafia “Licenciamento Trifásico–LP,LI e LO” foi preservada.','- As formas “Parágrafo único”, a grafia “dada Lei Federal” no art. 104 e demais erros de redação foram mantidos.','- O Anexo VIII é modelo de ficha de vistoria; o Anexo I é modelo de declaração; o Anexo VII é formulário de comunicação. Seus campos em branco não foram transcritos.','- Os Anexos II, III, IV, V, VI e IX são termos de referência/diretrizes e foram separados em arquivos próprios.','- Publicação da edição em análise e data de assinatura qualificada não foram identificadas na extração consultada; a vigência reproduz o art. 106 sem presumir a data de publicação.','']
pathlib.Path('normas/instrucao-normativa-iat-28-2026.md').write_text('\n'.join(out),encoding='utf-8')
