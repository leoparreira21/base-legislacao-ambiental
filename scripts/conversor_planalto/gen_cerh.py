import sys, re
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from estadual import link_estadual, post_considerandos, REPO
def norm(t): return re.sub(r'\s+',' ',t).strip()
def region(txt, a, b):
    s=open(__import__('os').environ.get('CONV_TXT','/home/claude/work/txt')+'/'+txt).read()
    s=s[s.index(a):s.index(b)]
    s=re.sub(r'Assinatura Avançada realizada por:.*?código: \w+\n','',s,flags=re.S)
    return s
def build(n, txt, sumula, ementa_md, cons_start, resolve_txt, arts, anexo_blocks, relacao, notas, extra_fm):
    ARQ=f'resolucao-cerh-{n}-2026'; L=lambda t: link_estadual(t, ARQ)
    pre = region(txt, 'O CONSELHO ESTADUAL', 'Considerando')
    cons = re.sub(r'\n\d+[a-z]?\n\d+\n','\n',region(txt, 'Considerando', 'RESOLVE:'))
    cons = [norm(c) for c in re.split(r'\n(?=Considerando)', cons.replace('\n\n','\n')) if c.strip()]
    cons = [re.sub(r'^(\d+)\s*','',c) for c in cons]
    cons = [c for c in cons if not re.fullmatch(r'[\d\sa]*',c)]
    out=['---',f'norma: Resolução CERH nº {n}/2026',f'arquivo: {ARQ}','tipo: resolucao','esfera: estadual','uf: PR',
     'orgao: Conselho Estadual de Recursos Hídricos – CERH/PR',f'numero: {n}','ano: 2026','data_assinatura: 2026-04-14','data_publicacao: 2026-04-14',
     'publicacao: "Diário Oficial do Estado, edição especial (número não consta do PDF enviado); data de publicação a conferir"',
     'vigencia: na data da publicação (art. 3º)' if n=='43' else 'vigencia: na data da publicação (art. 2º)',
     f'ementa: "{sumula}"','situacao: vigente','regulamenta: []','regulamentado_por: []','altera: []','alterado_por: []','revoga: []','revogado_por: []',
     'cita: []','tags: []',
     'fonte: "PDF da edição especial do Diário Oficial do Estado enviado por Leo (documento assinado no e-protocolo, protocolo 24.813.216-7); inclui documentos do processo anexados à resolução"','---','',
     f'# Resolução CERH nº {n}, de 14 de abril de 2026 {{#resolucao-cerh-{n}-2026}}','',f'> **Ementa:** {sumula}','',
     '**Preâmbulo** {#preambulo} '+L(norm(pre)),'']
    for i,c in enumerate(cons,1): out.append(f'- **Considerando {i}** {{#preambulo_cons{i}}} '+L(c))
    out+=['','RESOLVE:','']
    for i,(rot,txt_) in enumerate(arts,1):
        out+=[f'###### Art. {i}º {{#art{i}}}','',f'**Art. {i}º, caput** {{#art{i}_cpt}} '+L(txt_),'']
    out+=['---','','**Fecho** {#fecho} Curitiba, 14 de abril de 2026.','',
     f'**Assinaturas** {{#assinaturas}} {extra_fm.get("assin","EVERTON LUIZ DA COSTA SOUZA")} – Secretário de Estado do Desenvolvimento Sustentável – Presidente do Conselho Estadual de Recursos Hídricos','','---','']
    out+=anexo_blocks
    out+=['## Relação com outras normas {#relacao-outras-normas}','','Observação do conversor (não é texto normativo):','']+relacao+['']
    out+=['## Notas de transcrição {#notas-transcricao}','']+notas
    p=f'{REPO}/normas/{ARQ}.md'
    s='\n'.join(out)+'\n'
    body=s.split('\n---\n',1)[1]
    links=sorted(set(re.findall(r'\[\[([a-z0-9-]+)[#|\]]',body))-{ARQ})
    s=s.replace('cita: []','cita: ['+', '.join(f'"[[{l}]]"' for l in links)+']',1)
    open(p,'w').write(s); print(ARQ,'consid',len(cons),'cita',links)
