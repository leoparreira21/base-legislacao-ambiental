import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from conv import *

SP = os.environ.get('CONV_TRAB', os.getcwd())   # pasta de trabalho: pdf/, <json>.json, <norma>.log.json
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ids_existentes(arq):
    f = f'{REPO}/normas/{arq}.md'
    if not os.path.exists(f): return set()
    return set(re.findall(r'\{#([\w-]+)\}', open(f, encoding='utf-8').read()))

RE_MARK = re.compile(r'^(Art\.\s*\d+(?:\.\d{3})?\s*[º°o]?(?:-[A-Z]{1,2})?\.?|§\s*\d+\s*[º°o]?(?:-[A-Z])?\.?|Par[áa]grafo [úu]nico\.?|[IVXLC]+(?:-[A-Z])?\s*[-–]|[a-z]\))')

RE_MARKTOK = re.compile(r'^(Art\.|§|Parágrafo|[IVXLC]+(?:-[A-Z])?$|[a-z]\)$)')

def segmentos(toks):
    segs = [[]]
    for k, t in enumerate(toks):
        w = t.lstrip('~')
        if segs[-1] and RE_MARKTOK.match(w):
            prev = toks[k - 1].lstrip('~')
            nxt = toks[k + 1].lstrip('~') if k + 1 < len(toks) else ''
            ok = re.search(r'[.;:)]$', prev) and (not re.fullmatch(r'[IVXLC]+(?:-[A-Z])?', w) or nxt in ('-', '–'))
            if ok:
                segs.append([])
        segs[-1].append(t)
    return segs

def paragraphs(cfg):
    P = json.load(open(f"{SP}/{cfg['json']}.json"))
    out = []
    drop = []
    revog = []
    parcial = []
    for i, r in enumerate(P):
        if r['s'] == 0 or i in cfg.get('forcar_manter', ()):
            out.append(r); continue
        for toks in segmentos(r['st'].split(' ')):
            keep = ' '.join(t for t in toks if not t.startswith('~'))
            struck = ' '.join(t[1:] for t in toks if t.startswith('~'))
            if not struck:
                r2 = dict(r); r2['t'] = keep; out.append(r2); continue
            core, anns = split_annot(keep)
            resto = RE_MARK.sub('', core.strip()).strip(' -–.;:,')
            nst = sum(1 for t in toks if t.startswith('~'))
            if resto and len(resto.split()) <= 2 and nst >= 8:
                parcial.append((i, 'sobra de tachado descartada', struck[:120], resto))
                resto = ''
            if not resto:
                anns = list(dict.fromkeys(anns))
                if any(a.lower().startswith(('revogad', 'suprimid')) for a in anns):
                    m = RE_MARK.match(struck) or RE_MARK.match(keep) or re.match(r'^([IVXLC]+)(?=\s*\()', keep)
                    if m:
                        mk = m.group(1) + (' -' if re.fullmatch(r'[IVXLC]+', m.group(1)) else '')
                        r2 = dict(r); r2['t'] = mk + ' ' + ' '.join(f'({a})' for a in anns)
                        out.append(r2); revog.append((i, struck[:120], r2['t'])); continue
                    drop.append((i, struck + ' || ' + keep)); parcial.append((i, 'revogação sem marcador', struck[:120], keep)); continue
                drop.append((i, struck + (' || ' + keep if keep else ''))); continue
            r2 = dict(r); r2['t'] = keep
            out.append(r2); parcial.append((i, 'palavras tachadas removidas', struck[:200], keep[:200]))
    cfg['_revog'] = revog; cfg['_parcial'] = parcial
    return out, drop

def fm_list(xs):
    return '[' + ', '.join(f'"[[{x}]]"' for x in xs) + ']'

def build(cfg):
    P, drop = paragraphs(cfg)
    texts = [r['t'].strip() for r in P]
    ini = next(i for i, t in enumerate(texts) if re.match(cfg['preambulo_re'], t))
    fins = [i for i, t in enumerate(texts) if i > ini and re.match(cfg.get('fecho_re', r'^Brasília,'), t)]
    fim = fins[-1] if cfg.get('fecho_ultimo') else fins[0]
    npre = cfg.get('preambulo_n', 1)
    pre = re.sub(r'\s{2,}', ' ', ' '.join(texts[ini:ini + npre]))
    exc = cfg.get('excluir', lambda texts: set())(texts)
    cfg['_excluidos'] = [texts[i] for i in sorted(exc)]
    corpo = [t for i, t in enumerate(texts[ini + npre:fim], ini + npre) if i not in exc]
    corpo = [re.sub(r'^(?:o\s+)+(§\s*\d+)\s', r'\1º ', t) for t in corpo]   # ordinal sobrescrito fora de lugar
    corpo = [re.sub(r'^o (Art\.\s*\d+)\s', r'\1o ', t) for t in corpo]
    corpo = [re.sub(r'(§\s*\d+|Art\.\s*\d+) o\b', r'\1o', t) for t in corpo]
    corpo = [cfg.get('fix', lambda x: x)(t) for t in corpo]
    # vários artigos no mesmo parágrafo ("Art. 430. (Revogado ...) Art. 431. (Revogado ...)")
    corpo = [x for t in corpo for x in (re.split(r'(?<=[):.])\s+(?=Art\.\s*\d)', t) if t.startswith('Art') else [t])]
    sp = cfg.get('split')
    if sp:
        corpo = [x for t in corpo for x in sp(t)]
    pr = Parser(cfg)
    pr.prefix = ''
    for t in corpo:
        if cfg.get('adct_re') and re.match(cfg['adct_re'], t):
            pr.prefix = 'adct_'; pr.label_prefix = 'ADCT, '
            pr.items.append(['head', 2, cfg['adct_titulo'], '', [], 'adct'])
            pr.art = None; pr.head_open = None
            _, an = split_annot(t)
            pr.items[-1][4].extend(an)
            continue
        if cfg.get('pular') and cfg['pular'](t):
            continue
        pr.feed(t)
    for it in pr.items:
        if it[0] == 'art':
            a = it[1]
            a.heading = a.kids[0].label.rsplit(', caput', 1)[0].replace('ADCT, ', '') + (' (ADCT)' if a.id.startswith('adct_') else '')
    # IDs de cabeçalho (opcional)
    rd = Render(cfg, pr)
    tags = cfg.get('tags', {})
    if callable(tags): tags = tags(pr)
    body = rd.body(tags, ctx_of=lambda a: 'adct' if a.id.startswith('adct_') else 'corpo')
    # fecho e assinaturas
    rest = texts[fim:]
    fecho = rest[0]
    assin = []
    for t in rest[1:]:
        if t.startswith('Este texto não substitui') or t == '*':
            break
        assin.append(t)
    assin = cfg.get('assinaturas', lambda a: a)(assin)
    cita = sorted(set(cfg.get('cita_extra', [])) | rd.citadas - {cfg['arquivo']})
    alter = [x for x in rd.alteradoras if x != cfg['arquivo']]
    fmd = collections.OrderedDict(cfg['fm'])
    # relações recíprocas declaradas por normas da base
    import glob
    rec = {'regulamenta': 'regulamentado_por', 'altera': 'alterado_por', 'revoga': 'revogado_por'}
    extra = collections.defaultdict(set)
    for f in glob.glob(f'{REPO}/normas/*.md'):
        nome = os.path.basename(f)[:-3]
        if nome == cfg['arquivo']: continue
        head = open(f, encoding='utf-8').read().split('\n---\n', 1)[0]
        for campo, recip in rec.items():
            mm = re.search(rf'^{campo}: (.*)$', head, re.M)
            if mm and f'[[{cfg["arquivo"]}]]' in mm.group(1):
                extra[recip].add(nome)
    for recip, nomes in extra.items():
        atuais = set(re.findall(r'\[\[([a-z0-9-]+)\]\]', fmd.get(recip, '[]')))
        if recip == 'alterado_por':
            cfg.setdefault('alterado_por_extra', [])
            cfg['alterado_por_extra'] = sorted(set(cfg['alterado_por_extra']) | nomes)
        else:
            fmd[recip] = fm_list(sorted(atuais | nomes))
    fmd['alterado_por'] = fm_list(sorted(set(alter) | set(cfg.get('alterado_por_extra', []))))
    fmd['cita'] = fm_list(cita)
    alltags = sorted(t.lstrip('#') for t in rd.tags_usadas)
    fmd['tags'] = '[' + ', '.join(alltags) + ']'
    order = ['norma', 'arquivo', 'tipo', 'esfera', 'numero', 'ano', 'data_assinatura', 'data_publicacao', 'publicacao', 'vigencia',
             'orgao', 'ementa', 'apelido', 'situacao', 'texto', 'regulamenta', 'regulamentado_por', 'altera', 'alterado_por', 'revoga',
             'revogado_por', 'cita', 'tags', 'fonte']
    lines = ['---']
    for k in order:
        if k in fmd: lines.append(f'{k}: {fmd[k]}')
    lines.append('---')
    lines.append('')
    lines.append(f"# {cfg['titulo']} {{#{cfg['arquivo']}}}")
    lines.append('')
    lines.append(f"> **Ementa:** {rd.links(cfg['ementa_md'], 'corpo')}")
    lines.append('')
    if cfg.get('cabecalho'):
        lines.append('> ' + rd.links(cfg['cabecalho'], 'corpo'))
        lines.append('')
    lines.append(f"**Preâmbulo** {{#preambulo}} {rd.links(pre, 'corpo')}")
    lines.append('')
    lines += body
    lines.append('---')
    lines.append('')
    lines.append(f'**Fecho** {{#fecho}} {fecho}')
    lines.append('')
    lines += cfg.get('assin_md', lambda a: [f'- {x}' for x in a])(assin)
    lines.append('')
    lines.append('---')
    lines.append('')
    if cfg.get('apos_assinatura'):
        lines += cfg['apos_assinatura'](rd, texts[fim:])
    lines.append('## Relação com outras normas {#relacao-normas-superiores}')
    lines.append('')
    lines.append('Observação do conversor (não é texto normativo):')
    lines.append('')
    lines += [rd.links(x, 'corpo') if not x.startswith('!') else x[1:] for x in cfg['relacao']]
    lines.append('')
    if rd.hist:
        lines.append('## Histórico de alterações {#historico-alteracoes}')
        lines.append('')
        lines += rd.historico()
        lines.append('')
    lines.append('## Notas de transcrição {#notas-transcricao}')
    lines.append('')
    lines += cfg['notas'](rd, pr, drop)
    md = '\n'.join(lines).rstrip() + '\n'
    md = re.sub(r'\n{3,}', '\n\n', md)
    out = f"{REPO}/normas/{cfg['arquivo']}.md"
    open(out, 'w', encoding='utf-8').write(md)
    json.dump({'log': pr.log, 'drop': drop}, open(f"{SP}/{cfg['arquivo']}.log.json", 'w'), ensure_ascii=False, indent=1)
    print(cfg['arquivo'], 'artigos', sum(1 for i in pr.items if i[0] == 'art'), 'log', len(pr.log), 'tachados', len(drop),
          'citadas', len(rd.citadas), 'alteradoras', len(alter))
    return pr, rd, drop
