"""Conversor de textos compilados (Planalto/Câmara) para o padrão da base.
Entrada: lista de parágrafos (strings) do corpo, já sem os tachados.
"""
import re, json, collections

ROM = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
def rom(s):
    t = 0
    for i, c in enumerate(s):
        v = ROM[c]
        if i + 1 < len(s) and ROM[s[i + 1]] > v: t -= v
        else: t += v
    return t

def ordn(n):  # rótulo do número
    return f'{n}º' if re.fullmatch(r'\d', n) else n

# ---------------------------------------------------------------- normas citadas
MESES = 'janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro'
RE_NORMA = re.compile(
    r'(?P<tipo>Lei Complementar|Lei Delegada|Lei|Decreto-Lei|Decreto-lei|Decreto Legislativo|Decreto|Medida Provis[óo]ria|'
    r'Emenda Constitucional de Revis[ãa]o|Emenda Constitucional)\s+'
    r'(?:n[º°o]s?\.?\s*|N[º°o]\s*)(?P<num>\d{1,3}(?:\.\d{3})*(?:-[A-Z0-9]+)?)'
    r'(?P<data>\s*,?\s*(?:de\s+)?(?:(?:\d{1,2}[º°o]?\s*(?:de\s+)?(?:' + MESES + r')\s+de\s+)|(?:\d{1,2}[./]\d{1,2}[./]\s*))?'
    r'(?P<ano>\d{4}|\d{2})(?!\d))?')

def slug_norma(tipo, num, ano):
    num = num.replace('.', '').lower()
    if len(ano) == 2:
        ano = ('19' if int(ano) > 30 else '20') + ano
    t = tipo.lower()
    if t.startswith('lei complementar'): base = 'lei-complementar-federal'
    elif t.startswith('lei delegada'): base = 'lei-delegada-federal'
    elif t == 'lei': base = 'lei-federal'
    elif t.startswith('decreto-lei'): base = 'decreto-lei-federal'
    elif t.startswith('decreto legislativo'): base = 'decreto-legislativo-federal'
    elif t == 'decreto': base = 'decreto-federal'
    elif t.startswith('medida'): base = 'medida-provisoria'
    elif 'revis' in t: base = 'emenda-constitucional-revisao-federal'
    else: base = 'emenda-constitucional-federal'
    return f'{base}-{num}-{ano}'

def protect(s):
    """Separa trechos já em [[...]] para não ligar duas vezes."""
    parts = re.split(r'(\[\[.*?\]\])', s)
    return parts

def link_normas(s, proprio, citadas):
    out = []
    for part in protect(s):
        if part.startswith('[['):
            out.append(part); continue
        def rep(m):
            if not m.group('ano'):
                return m.group(0)
            sl = slug_norma(m.group('tipo'), m.group('num'), m.group('ano'))
            if sl == proprio:
                return m.group(0)
            citadas.add(sl)
            txt = m.group(0).rstrip(' ,')
            tail = m.group(0)[len(txt):]
            return f'[[{sl}|{txt}]]{tail}'
        out.append(RE_NORMA.sub(rep, part))
    return ''.join(out)

# ---------------------------------------------------------------- anotações
ANN_RE = re.compile(r'^\s*[“"]?(Reda[çc][ãa]o|reda[çc][ãa]o|Inclu[íi]d|Revogad|Renumerad|Vide|Regulament|Acrescid|Acrescentad|Promulga|'
                    r'Produ[çc][ãa]o de efeito|Vig[êe]ncia|Retificad|Transformad|Suprimid|Express[ãa]o|Execu[çc][ãa]o|Mantid|'
                    r'Convertid|Restabelecid|Declarad|Revigorad|Em vigor|Inconstitucion|Suspens|Prorrogad|Dispositivo|'
                    r'Par[áa]grafo|Inciso|Al[íi]nea|Artigo|Arts?\.|Caput|Item|Se[çc][ãa]o|Cap[íi]tulo|T[íi]tulo|Numera|Nova reda|'
                    r'Texto|ADIN|ADI |ADC |ADPF|Vetad|Veto|Derrubad|Ver |Referendo|Primitivo|Publica|Partes? vetad|Emenda|Lei n|Vigente|Efeitos|Eficácia|Com reda|'
                    r'Nota de rodap|Vide|vide|Este|Esta|Nº|N°|Atualizado|Acr[eé]scimo|Revoga|Alterad|Modificad|Sem efeito|Tornad|Republica|Subst)')
BARE = ('Vigência', 'Regulamento', 'Produção de efeito', 'Produção de efeitos', 'Mensagem de veto', 'Vide', 'Promulgação', 'Promulgação partes vetadas')

def split_annot(t):
    t = t.strip()
    anns = []
    while True:
        t = t.rstrip()
        hit = False
        for b in BARE:
            pre = t[:-len(b)].rstrip()
            if t.endswith(' ' + b) and (pre.endswith((')', '.', ';', ':')) or (len(pre) > 3 and pre == pre.upper())):
                anns.insert(0, b); t = t[:-len(b)]; hit = True; break
        if hit: continue
        if t.endswith(')') or t.endswith(').') or t.endswith(');'):
            end = t.rfind(')')
            trail = t[end + 1:]
            depth = 0; i = end
            while i >= 0:
                if t[i] == ')': depth += 1
                elif t[i] == '(':
                    depth -= 1
                    if depth == 0: break
                i -= 1
            if i < 0: break
            inner = t[i + 1:end]
            if ANN_RE.match(inner) and not re.match(r'^\s*VETADO', inner):
                anns.insert(0, inner.strip() + ('' if not trail.strip() else ''))
                t = t[:i] + ('' if not trail.strip() else '')
                hit = True
        if not hit: break
    return t.strip(), anns

def kinds_of(ann):
    """[(tipo, trecho da norma)] para cada norma citada na anotação."""
    res = []
    if ann.startswith('Nota de rodapé'):
        return [('vid', slug_norma(m.group('tipo'), m.group('num'), m.group('ano')), m.group(0).rstrip(' ,')) for m in RE_NORMA.finditer(ann) if m.group('ano')]
    last = None
    for m in RE_NORMA.finditer(ann):
        before = ann[:m.start()].lower()
        cands = [(before.rfind(k), v) for k, v in [('redação', 'alt'), ('redacao', 'alt'), ('incluíd', 'inc'), ('incluid', 'inc'),
                 ('acrescid', 'inc'), ('acrescentad', 'inc'), ('revogad', 'rev'), ('renumerad', 'ren'), ('transformad', 'ren'),
                 ('vide', 'vid'), ('convertid', 'conv'), ('mantid', 'vid'), ('vetad', 'vid'), ('promulga', 'vid'),
                 ('restabelecid', 'alt'), ('suprimid', 'rev'), ('declarad', 'vid'), ('produção de efeito', 'vid'), ('retificad', 'vid'), ('regulament', 'vid')]]
        cands = [c for c in cands if c[0] >= 0]
        k = max(cands)[1] if cands else (last or 'vid')
        if k == 'conv': k = last or 'vid'
        last = k
        if m.group('ano'):
            res.append((k, slug_norma(m.group('tipo'), m.group('num'), m.group('ano')), m.group(0).rstrip(' ,')))
    return res

# ---------------------------------------------------------------- reconhecimento
RE_HEAD = re.compile(r'^(PARTE|LIVRO|T[IÍ]TULO|CAP[IÍ]TULO|Cap[íi]tulo|SE[ÇC][ÃA]O|SUBSE[ÇC][ÃA]O|Se[çc][ãa]o|Subse[çc][ãa]o)\s+'
                     r'([IVXLC]+(?:-[A-Z])?|[ÚU]NIC[OA]|GERAL|ESPECIAL|COMPLEMENTAR)\b\.?\s*[-–]?\s*(.*)$')
RE_ART = re.compile(r'^Art\.?\s*(\d+(?:\.\d{3})?)\s*([º°o](?![a-zà-ú]))?((?:-|\.)[A-Za-z]{1,2}(?![a-zà-ú]))?\s*\.?\s*[-–]?\s*(.*)$')
RE_ARTS = re.compile(r'^Arts?\.\s*(\d+)\s*[º°o]?\s*(a|e)\s*(\d+)\s*[º°o]?(-[A-Z])?\.?\s*(.*)$')
RE_PAR = re.compile(r'^§\s*(\d+)\s*([º°o])?(-[A-Z]{1,2})?\s*\.?\s*[-–]?\s*(.*)$')
RE_PU = re.compile(r'^Par[áa]gr[áa]fo [úu]nico\s*\.?\s*[-–]?\s*(.*)$', re.I)
RE_INC = re.compile(r'^([IVXLC]+)(-[A-Z]{1,2})?\s*[-–—](?![A-Z]{1,2}\b)\s*(.*)$')
RE_INC2 = re.compile(r'^([IVXLC]+)(-[A-Z]{1,2})?\s+(?=[a-zà-ú(])(.*)$')
RE_ALI = re.compile(r'^([a-z])(-[A-Z])?\s?\)\s*(.*)$')
RE_ITE = re.compile(r'^(\d+)\s*(?:[.)]|(?=\s[-–]))\s*[-–]?\s*(.*)$')

class N:
    def __init__(s, kind, ident, label, text='', anns=None):
        s.kind, s.id, s.label, s.text = kind, ident, label, text
        s.anns = anns or []
        s.kids = []
        s.extra = []   # parágrafos soltos acrescentados

def art_id(num, suf, prefix=''):
    n = num.replace('.', '')
    sfx = ''
    if suf:
        sfx = '-' + suf.strip('-.').lower()
    return f'{prefix}art{n}{sfx}'

def art_label(num, suf, ordc):
    base = num + ('º' if (ordc or re.fullmatch(r'\d', num)) and re.fullmatch(r'\d', num) else '')
    if suf:
        base += ('-' + suf.strip('-.').upper()) if suf.startswith('-') else suf
    return 'Art. ' + base

class Parser:
    def __init__(s, cfg):
        s.cfg = cfg
        s.items = []         # ('head', nivel, texto, id, anns) | ('art', N) | ('raw', texto)
        s.art = None
        s.ids = collections.Counter()
        s.log = []
        s.prefix = ''
        s.head_open = None   # cabeçalho aguardando título
        s.label_prefix = ''

    def reg(s, node, parent):
        s.revtexto(node)
        pend = getattr(s, 'pend', None)
        if pend and pend[0].id == node.id:
            oldn, par, k = pend
            s.pend = None
            node.kids = oldn.kids + node.kids
            if not hasattr(s, 'parents'): s.byid, s.parents = {}, {}
            for kk in oldn.kids:
                s.parents[kk.id] = [node]
            if par is parent:
                parent.kids.insert(k, node)
            else:
                parent.kids.append(node)
        else:
            parent.kids.append(node)
        if not hasattr(s, 'byid'): s.byid, s.parents = {}, {}
        s.byid[node.id] = node
        s.parents[node.id] = [parent]

    def revtexto(s, node):
        if s.cfg.get('revogado_remove_texto') and node.text.strip() and any(re.match(r'^[“"]?(Revogad|[A-Za-zÁ-ú“” ]{0,40} revogad)', a) and not a.startswith('Nota de rodapé') for a in node.anns):
            s.log.append(f'texto de dispositivo revogado removido: {node.id}')
            s.revogados_com_texto = getattr(s, 'revogados_com_texto', []) + [(node.id, node.text)]
            node.text = ''

    def newid(s, i):
        s.ids[i] += 1
        old = s.byid.get(i) if hasattr(s, 'byid') else None
        if s.cfg.get('dup_ultima') and s.ids[i] > 1:
            # lei revogada por inteiro e toda tachada (ex.: Lei 8.666/1993): não há como separar a redação anterior
            # da última; cada nova entrada de mesmo número substitui a anterior (fica a última redação)
            s.ids[i] -= 1
            s.substituidos = getattr(s, 'substituidos', 0) + 1
            if old is not None:
                for par in s.parents.get(i, []):
                    if old in par.kids:
                        s.pend = (old, par, par.kids.index(old))
                        par.kids.remove(old)
            return i
        def vazio(n):
            return not n.text.strip() and not n.extra and all(vazio(k) for k in n.kids)
        if s.ids[i] > 1 and old is not None and vazio(old):
            # dispositivo revogado (só rótulo e anotação) seguido da entrada atual de mesmo número: fica a atual
            s.log.append(f'revogado duplicado substituído pela entrada seguinte: {i}')
            for par in s.parents.get(i, []):
                if old in par.kids: par.kids.remove(old)
            s.ids[i] -= 1
            s.pending_anns = [a for a in old.anns]
            return i
        if s.ids[i] > 1:
            s.log.append(f'ID duplicado: {i}')
            i2 = f'{i}-dup{s.ids[i]}'
            return i2
        return i

    def add_head(s, kind, num, rest):
        k = kind.upper().replace('Í', 'I').replace('Ç', 'C').replace('Ã', 'A')
        lv = s.cfg['niveis'].get(k, 5)
        s.art = None
        cab = f'{kind.upper() if kind.isupper() else kind} {num}'
        if lv == 'prefixo':
            s.parte = cab
            s.head_open = None
            return
        if getattr(s, 'parte', None):
            cab = f'{s.parte} – {cab}'
            s.parte = None
        s.items.append(['head', lv, cab, rest, []])
        s.head_open = s.items[-1]

    def start_art(s, num, ordc, suf, text, anns):
        mrv = re.match(r'^[.\s]*(Revogad[oa]s?\b[^()]*?)[:;.]?\s*$', text or '')
        if mrv:
            s.log.append(f'Art. {num}: "{text}" sem parênteses no original, tratado como anotação de revogação')
            anns = [mrv.group(1)] + list(anns); text = ''
        ident = s.newid(art_id(num, suf, s.prefix))
        lab = art_label(num, suf, ordc)
        a = N('art', ident, lab)
        a.num = num
        herdados = []
        if s.cfg.get('dup_ultima'):
            for k in range(len(s.items) - 1, -1, -1):
                it = s.items[k]
                if it[0] == 'art' and it[1].id == ident:
                    herdados = it[1].kids[1:]
                    del s.items[k]
                    break
        s.items.append(('art', a))
        s.art = a
        s.head_open = None
        c = N('cpt', s.newid(ident + '_cpt'), f'{s.label_prefix}{lab}, caput', text, anns)
        s.revtexto(c)
        a.kids.append(c)
        if herdados:
            a.kids += herdados
            if not hasattr(s, 'parents'): s.byid, s.parents = {}, {}
            for kk in herdados:
                s.parents[kk.id] = [a]
        s.cur_par = c
        s.cur_inc = None
        s.cur_ali = None
        s.cur_ite = None
        s.last = c

    def feed(s, p):
        t = p.strip()
        if not t:
            return
        mm = re.match(r'^([IVXLCl](?:\s?[IVXLCl])*)(\s*[-–—]\s)', t)
        if mm and ('l' in mm.group(1) or ' ' in mm.group(1)):
            novo = mm.group(1).replace('l', 'I').replace(' ', '')
            if re.fullmatch(r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})', novo):
                s.log.append(f'numeral do inciso grafado "{mm.group(1)}" no original, lido como {novo}')
                t = novo + t[mm.end(1):]
        if re.match(r'^S eção\b', t):
            s.log.append('"S eção" no original, lido como "Seção"')
            t = 'Seção' + t[6:]
        # bloco citado (nova redação de outra norma), entre aspas
        if s.art is not None and (getattr(s, 'in_quote', False) or re.match(r'^[“"]\s*(Art\.|§|[IVXLC]+\s*[-–]|[a-z]\)|\.{5}|CAP[IÍ]TULO|T[IÍ]TULO|Se[çc][ãa]o)', t)):
            host = s.last
            novo = re.match(r'^[“"]\s*Art\.\s*([\d.]+[º°o]?(?:-[A-Z])?)', t)
            if not getattr(s, 'in_quote', False) or novo:
                host.alts = getattr(host, 'alts', [])
                host.alts.append({'id': f'{host.id}_alt{len(host.alts) + 1}', 'art': novo.group(1).rstrip('.') if novo else '', 'paras': []})
            ps = host.alts[-1]['paras']
            if ps and not re.match(r'^([“"]|Art\.|§|Par[áa]grafo|[IVXLC]+\s*[-–]|[a-z]\)|\d+\s*[.)-]|\.{5})', t):
                ps[-1] = ps[-1] + ' ' + t
            else:
                ps.append(t)
            s.in_quote = not re.search(r'[”"]\s*(\(NR\))?\s*[.;]?\s*(\([^)]*\)\s*)*$', t)
            return
        m = RE_HEAD.match(t)
        if m and (not s.art or True):
            kind, num, rest = m.group(1), m.group(2), m.group(3)
            core, anns = split_annot(rest)
            s.add_head(kind, num, core)
            if s.head_open is not None:
                s.head_open[4].extend(anns)
            return
        if s.head_open is not None and not RE_ART.match(t) and not RE_ARTS.match(t):
            core, anns = split_annot(t)
            if core:
                h = s.head_open
                h[3] = (h[3] + ' ' + core).strip() if h[3] else core
            h = s.head_open
            h[4].extend(anns)
            return
        core, anns = split_annot(t)
        if not core and anns:   # parágrafo só de anotação
            tgt = s.last if s.art else None
            if tgt is not None:
                tgt.anns.extend(anns)
            else:
                s.items.append(('raw', ' '.join(f'({a})' for a in anns)))
            return
        m = RE_ARTS.match(core)
        if m:
            a1, a2 = int(m.group(1)), int(m.group(3))
            rest, anns2 = split_annot(m.group(5))
            if rest.strip('. ') == '' and (anns or anns2):
                lista = [(str(n), None) for n in ((a1, a2) if m.group(2) == 'e' else range(a1, a2 + 1))]
                if m.group(4):
                    lista.append((str(a2), m.group(4)))
                for n, suf in lista:
                    s.start_art(n, None, suf, '', list(anns2 + anns))
                return
        m = RE_ART.match(core)
        if m and not re.match(r'^\d', m.group(4) or ''):
            num, ordc, suf, txt = m.group(1), m.group(2), m.group(3), m.group(4)
            if suf and suf.startswith('.') and not s.cfg.get('art_letra_ponto'):
                suf = None
            s.start_art(num, ordc, suf, txt, anns)
            return
        if s.art is None:
            s.items.append(('raw', t))
            return
        a = s.art
        L = a.kids[0].label.rsplit(', caput', 1)[0]
        m = RE_PAR.match(core)
        if m:
            n, suf = m.group(1), m.group(3)
            pid = s.newid(f'{a.id}_par{n}' + ('-' + suf.strip('-').lower() if suf else ''))
            lab = f'{L}, § {n}{"º" if len(n) == 1 else ""}' + (suf.upper() if suf else '')
            node = N('par', pid, lab, m.group(4), anns)
            s.reg(node, a); s.cur_par = node; s.cur_inc = s.cur_ali = s.cur_ite = None; s.last = node
            return
        m = RE_PU.match(core)
        if m:
            pid = s.newid(f'{a.id}_par1u')
            node = N('par', pid, f'{L}, parágrafo único', m.group(1), anns)
            s.reg(node, a); s.cur_par = node; s.cur_inc = s.cur_ali = s.cur_ite = None; s.last = node
            return
        m = RE_INC.match(core)
        m2 = None if m else RE_INC2.match(core)
        if m2:
            base = rom(re.sub(r'-.*', '', s.cur_inc.num)) if s.cur_inc else 0
            if rom(m2.group(1)) == base + 1 or (m2.group(2) and rom(m2.group(1)) == base):
                m = m2
                s.log.append(f'inciso sem travessão: {core[:50]}')
        if m:
            n, suf = m.group(1), m.group(2)
            par = s.cur_par
            pid = s.newid(f'{par.id}_inc{rom(n)}' + ('-' + suf.strip('-').lower() if suf else ''))
            node = N('inc', pid, f'{par.label}, inciso {n}{suf or ""}', m.group(3), anns)
            node.num = n + (suf or '')
            if s.cur_inc and not suf and rom(n) != rom(re.sub(r'-.*', '', s.cur_inc.num)) + 1:
                s.log.append(f'sequência de inciso: {pid} após {s.cur_inc.id}')
            if not s.cur_inc and not suf and rom(n) != 1:
                s.log.append(f'inciso inicial {n}: {pid}')
            s.reg(node, par); s.cur_inc = node; s.cur_ali = s.cur_ite = None; s.last = node
            return
        m = RE_ALI.match(core)
        if m:
            n = m.group(1)
            par = s.cur_inc or s.cur_par
            pid = s.newid(f'{par.id}_ali{n}' + ('-' + m.group(2).strip('-').lower() if m.group(2) else ''))
            node = N('ali', pid, f'{par.label}, alínea "{n}{m.group(2) or ""}"', m.group(3), anns)
            node.num = n
            if s.cur_ali and ord(n) != ord(s.cur_ali.num) + 1 and not m.group(2):
                s.log.append(f'sequência de alínea: {pid} após {s.cur_ali.id}')
            s.reg(node, par); s.cur_ali = node; s.cur_ite = None; s.last = node
            return
        m = RE_ITE.match(core)
        if m and (s.cur_ali or s.cur_inc or s.cur_par):
            n = m.group(1)
            exp = int(s.cur_ite.num) + 1 if s.cur_ite else 1
            if int(n) == exp:
                par = s.cur_ali or s.cur_inc or s.cur_par
                pid = s.newid(f'{par.id}_ite{n}')
                node = N('ite', pid, f'{par.label}, item {n}', m.group(2), anns)
                node.num = n
                s.reg(node, par); s.cur_ite = node; s.last = node
                return
        # parágrafo sem marcador: continua o último dispositivo
        s.log.append(f'sem marcador (unido a {s.last.id}): {t[:80]}')
        s.last.extra.append((core, anns))

# ---------------------------------------------------------------- links internos
EXT = re.compile(r'^[^;]{0,90}?\b(da Lei|do Decreto|da Medida|do C[óo]digo|da Consolida|do Estatuto|do Regimento|da Emenda|'
                 r'da Constitui|do Ato das Disposi|desta Constitui|deste Ato|deste C[óo]digo|desta Lei|do Ato|da Conven|do Tratado|da Resolu)')

def link_interno(s, ids, ctx, ext_cf=None):
    """ctx: 'corpo' ou 'adct' (CF). ext_cf: ids da CF quando a norma é outra (liga 'da Constituição')."""
    spans = [(m.start(), m.end()) for m in re.finditer(r'\[\[.*?\]\]', s)]
    def inside(p):
        return any(a <= p < b for a, b in spans)
    res = []
    pos = 0
    for m in re.finditer(r'\b(arts?\.|artigos?)\s+((?:\d+(?:\.\d{3})?\s*[º°o]?(?:-[A-Z])?(?:\s*(?:,|e|a|ou)\s+(?=\d))?)+)', s):
        if inside(m.start()):
            continue
        res.append(s[pos:m.start()])
        after = re.sub(r'\[\[[^|\]]*\|', '', s[m.end():m.end() + 300]).replace(']]', '')
        e = EXT.match(after)
        if e:
            w = e.group(1)
            if w.startswith('desta Constitui'): alvo = ('', '') if ctx in ('corpo', 'adct') else None
            elif w.startswith('deste Ato'): alvo = ('', 'adct_') if ctx in ('corpo', 'adct') else None
            elif w.startswith('do Ato'):
                alvo = ('', 'adct_') if ctx in ('corpo', 'adct') else (('constituicao-federal-1988', 'adct_') if ext_cf else None)
            elif w.startswith('da Constitui'):
                alvo = ('', '') if ctx in ('corpo', 'adct') else (('constituicao-federal-1988', '') if ext_cf else None)
            elif w in ('deste Código', 'deste Codigo', 'desta Lei'):
                alvo = ('', '')
            else:
                alvo = None
        else:
            alvo = ('', '')
        if alvo is None:
            res.append(m.group(0)); pos = m.end(); continue
        arq, pfx = alvo
        pool = ext_cf if arq else ids
        def rn(mm):
            num = mm.group(1).replace('.', '')
            suf = mm.group(3)
            i = f'{pfx}art{num}' + (('-' + suf.strip('-').lower()) if suf else '')
            if i in pool:
                return f'[[{arq}#{i}|{mm.group(0)}]]'
            return mm.group(0)
        nums = re.sub(r'(\d+(?:\.\d{3})?)(\s*[º°o])?(-[A-Z])?', rn, m.group(2))
        res.append(m.group(1) + ' ' + nums)
        pos = m.end()
    res.append(s[pos:])
    return ''.join(res)

# ---------------------------------------------------------------- renderização
KIND_TXT = {'alt': 'nova redação', 'inc': 'incluído', 'rev': 'revogado', 'ren': 'renumerado'}
CTRL = {'alt': '#redacao-alterada', 'inc': '#incluido', 'rev': '#revogado'}

class Render:
    def __init__(s, cfg, parser):
        s.cfg, s.p = cfg, parser
        s.citadas = set()
        s.alteradoras = collections.OrderedDict()   # slug -> nome
        s.hist = []   # (slug, nome, id, label, tipo)
        s.ids = set()
        for it in parser.items:
            if it[0] == 'art':
                s._ids(it[1])
        s.tags_usadas = set()

    def _ids(s, n):
        s.ids.add(n.id)
        for k in n.kids: s._ids(k)

    def links(s, t, ctx):
        t = s.cfg.get('pre', lambda x: x)(t)
        for a, b in s.cfg.get('manual', []):
            t = t.replace(a, b)
        t = link_normas(t, s.cfg['arquivo'], s.citadas)
        t = link_interno(t, s.ids, ctx, s.cfg.get('ids_cf'))
        return t

    def ann_md(s, n, ctx):
        out = []
        ctrl = []
        for a in n.anns:
            ks = kinds_of(a)
            for k, sl, nome in ks:
                if k in ('alt', 'inc', 'rev', 'ren') and sl != s.cfg['arquivo']:
                    s.alteradoras.setdefault(sl, nome)
                    s.hist.append((sl, nome, n.id, n.label, k))
                    if k in CTRL and CTRL[k] not in ctrl: ctrl.append(CTRL[k])
            low = a.lower()
            if not ks:
                if low.startswith('revogad') and '#revogado' not in ctrl: ctrl.append('#revogado')
                elif (low.startswith('incluíd') or low.startswith('acrescid')) and '#incluido' not in ctrl: ctrl.append('#incluido')
                elif 'redação dada' in low and '#redacao-alterada' not in ctrl: ctrl.append('#redacao-alterada')
            out.append(f'*({s.links(a, ctx)})*')
        return ctrl, ' '.join(out)

    def disp(s, n, ctx, depth, tags):
        ctrl, anns = s.ann_md(n, ctx)
        txt = s.links(n.text, ctx) if n.text else ''
        if re.fullmatch(r'\(?revogad[oa]s?\.?\)?[.;]?', n.text.strip(), re.I):
            if '#revogado' not in ctrl: ctrl.append('#revogado')
        if not txt and any('#revogado' == c for c in ctrl):
            pass
        tg = ctrl + [t for t in tags.get(n.id, []) if t not in ctrl]
        s.tags_usadas.update(tg)
        bits = [f'**{n.label}** {{#{n.id}}}'] + tg + ([txt] if txt else []) + ([anns] if anns else [])
        line = ' '.join(bits)
        for core, an in n.extra:
            n2 = N('x', '', '', core, an)
            _, a2 = s.ann_md(n2, ctx)
            line += ' ' + s.links(core, ctx) + (' ' + a2 if a2 else '')
        if n.kind in ('cpt', 'par'):
            lines = [line]
        else:
            lines = ['  ' * (depth - 1) + '- ' + line]
        for alt in getattr(n, 'alts', []):
            alvo = re.findall(r'\[\[([a-z0-9-]+)\|([^\]]+)\]\]', txt)
            nome = alvo[0][1] if alvo else ''
            lab = 'Nova redação' + (f' – {nome}' if nome else '') + (f', art. {alt["art"]}' if alt['art'] else '')
            lines += ['', f'> **{lab}** {{#{alt["id"]}}}']
            for k, ptxt in enumerate(alt['paras']):
                if k: lines.append('>')
                lines.append('> ' + link_normas(ptxt, s.cfg['arquivo'], s.citadas))
            lines.append('')
        for k in n.kids:
            lines += s.disp(k, ctx, depth + 1 if n.kind not in ('cpt', 'par') else 1, tags)
        return lines

    def mover_anotacoes(s, a):
        # Câmara: "(Artigo acrescido ...)" no fim do último inciso vale para o artigo; idem Parágrafo/Inciso/Caput
        pais = {}
        def walk(n, p):
            pais[id(n)] = p
            for k in n.kids: walk(k, n)
        for k in a.kids: walk(k, a)
        alvo_kind = [(r'^Artigo\b', 'cpt'), (r'^[“"]?Caput\b', 'cpt'), (r'^Par[áa]grafo\b', 'par'), (r'^Inciso\b', 'inc'), (r'^Al[íi]nea\b', 'ali')]
        def todos(n):
            yield n
            for k in n.kids: yield from todos(k)
        for k in a.kids:
            for n in list(todos(k)):
                for an in list(n.anns):
                    for rx, kind in alvo_kind:
                        if re.match(rx, an) and n.kind != kind:
                            if kind == 'cpt':
                                dest = a.kids[0]
                            else:
                                dest = pais.get(id(n))
                                while dest is not None and getattr(dest, 'kind', None) != kind:
                                    dest = pais.get(id(dest))
                            if dest is not None and dest is not n:
                                n.anns.remove(an); dest.anns.append(an)
                                s.p.log.append(f'anotação "{an[:40]}…" movida de {n.id} para {dest.id}')
                            break

    def art(s, a, ctx, tags):
        if s.cfg.get('camara'):
            s.mover_anotacoes(a)
        out = [f'###### {a.heading} {{#{a.id}}}' if hasattr(a, 'heading') else f'###### {a.kids[0].label.rsplit(", caput",1)[0].split(", ")[-1]} {{#{a.id}}}']
        at = tags.get(a.id, [])
        s.tags_usadas.update(at)
        out.append('Tags: ' + ' '.join(at) if at else 'Tags:')
        start = len(s.hist)
        body = []
        for i, k in enumerate(a.kids):
            ls = s.disp(k, ctx, 1, tags)
            if k.kind == 'par' or k.kind == 'cpt':
                body.append('')
            body += ls
        # linha Alterações
        por = collections.OrderedDict()
        for sl, nome, i, lab, k in s.hist[start:]:
            rel = lab.split(', ', 1)[1] if ', ' in lab else lab
            if lab.startswith('ADCT, '): rel = lab.split(', ', 2)[2] if lab.count(', ') >= 2 else lab
            if rel.startswith('caput, '): rel = rel[7:]
            por.setdefault(sl, [nome, collections.OrderedDict()])[1].setdefault(KIND_TXT[k], []).append(rel)
        if por:
            parts = []
            for sl, (nome, ks) in por.items():
                parts.append(f'[[{sl}|{nome}]] (' + '; '.join(f'{k}: {", ".join(v)}' for k, v in ks.items()) + ')')
            out.append('Alterações: ' + '; '.join(parts))
        return out + body + ['']

    def body(s, tags, ctx_of=lambda a: 'corpo'):
        out = []
        for it in s.p.items:
            if it[0] == 'head':
                _, lv, cab, tit, anns = it[:5]
                tit, an2 = split_annot(tit)
                n = N('h', '', '', '', an2 + list(anns))
                _, am = s.ann_md(n, 'corpo')
                h = f'{cab} – {tit}' if tit else cab
                hid = it[5] if len(it) > 5 else None
                out.append('#' * lv + ' ' + h + (f' {{#{hid}}}' if hid else '') + (f' {am}' if am else ''))
                out.append('')
            elif it[0] == 'art':
                out += s.art(it[1], ctx_of(it[1]), tags)
            else:
                out.append(s.links(it[1], 'corpo')); out.append('')
        return out

    def historico(s):
        rows = ['| Norma | Dispositivo | Alteração |', '|---|---|---|']
        for sl, nome, i, lab, k in s.hist:
            rows.append(f'| [[{sl}\\|{nome}]] | [[#{i}\\|{lab}]] | {KIND_TXT[k].capitalize()} |')
        return rows
