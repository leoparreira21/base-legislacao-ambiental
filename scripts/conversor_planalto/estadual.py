"""Auxiliares para converter normas estaduais (CEMA, CERH...) usando o conversor do Planalto como base."""
import re, os, sys, json
C = '/home/claude/base-legislacao-ambiental/scripts/conversor_planalto'
sys.path.insert(0, C)
from make import *

MES = 'janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro'
TIPOS = [
    (r'Lei Estadual', 'lei-estadual'), (r'Lei Federal', 'lei-federal'), (r'Lei Complementar Federal', 'lei-complementar-federal'),
    (r'Lei Complementar', 'lei-complementar-federal'),
    (r'Decreto Estadual', 'decreto-estadual'), (r'Decreto Federal', 'decreto-federal'),
    (r'Resolu[çc][ãa]o CONAMA', 'resolucao-conama'), (r'Resolu[çc][ãa]o SEMA', 'resolucao-sema'),
    (r'Resolu[çc][ãa]o CEMA', 'resolucao-cema'), (r'Resolu[çc][ãa]o CERH', 'resolucao-cerh'),
    (r'Resolu[çc][ãa]o SEDEST', 'resolucao-sedest'),
]
TIPO_RE = '|'.join(f'(?P<t{i}>{rx})' for i, (rx, _) in enumerate(TIPOS))
ANO = r'(?P<ano>\d{1,2}\.?\d{3}|\d{4}|\d{2})'
RE_E = re.compile(
    r'(?P<pre>(?:(?:art\.|arts\.|artigo|artigos)\s+(?P<a>\d+)\s*[º°o]?(?P<par>,?\s*§\s*(?P<pn>\d+)\s*[º°o]?)?\s*,?\s+(?:da|do|dos|das)\s+))?'
    r'(?P<tipo>' + TIPO_RE + r')\s*(?:n[º°o]\.?s?\s*|n\.[º°o]\s*|N[º°o]\s*)?(?P<num>\d{1,3}(?:\.\d{3})+|\d+)'
    r'(?P<data>(?:\s*,?\s*(?:de\s+)?\d{1,2}[º°o]?\s*(?:de\s+)?(?:' + MES + r')\s+de\s+|\s*[/]\s*|\s*,\s*de\s+)' + ANO + r'(?!\d))?', re.I)

CITADAS = []

def _slug(m):
    for i, (_, base) in enumerate(TIPOS):
        if m.group(f't{i}'):
            break
    num = str(int(m.group('num').replace('.', '')))
    ano = m.group('ano')
    if not ano: return None
    ano = ano.replace('.', '')
    if len(ano) == 2: ano = ('19' if int(ano) > 30 else '20') + ano
    return f'{base}-{num}-{ano}'

def link_estadual(t, proprio=''):
    parts = re.split(r'(\[\[.*?\]\])', t)
    out = []
    for p in parts:
        if p.startswith('[['):
            out.append(p); continue
        def rep(m):
            sl = _slug(m)
            if not sl or sl == proprio: return m.group(0)
            if sl not in CITADAS: CITADAS.append(sl)
            txt = m.group(0)
            tail = ''
            alvo = sl
            if m.group('a'):
                alvo += f'#art{m.group("a")}' + (f'_par{m.group("pn")}' if m.group('pn') else '')
            return f'[[{alvo}|{txt}]]'
        out.append(RE_E.sub(rep, p))
    return ''.join(out)

def post_considerandos(path):
    s = open(path, encoding='utf-8').read()
    lines = s.split('\n')
    out = []; n = 0; dentro = False
    for ln in lines:
        if ln.startswith('**Preâmbulo**'): dentro = True
        if dentro and re.match(r'^Considerando\b', ln):
            n += 1
            out.append(f'- **Considerando {n}** {{#preambulo_cons{n}}} {ln}')
            continue
        if dentro and ln.strip() == 'RESOLVE:': dentro = False
        out.append(ln)
    s = '\n'.join(out)
    s = re.sub(r'\n(- \*\*Considerando \d+\*\*[^\n]*)\n\n(?=- \*\*Considerando)', r'\n\1\n', s)
    s = s.replace('\nesfera: estadual\n', '\nesfera: estadual\nuf: PR\n', 1)
    open(path, 'w', encoding='utf-8').write(s)
    return n

# ---- separação de dispositivos colados no mesmo parágrafo (PDF do portal junta linhas contíguas)
def _rom(s):
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}; t = 0
    for i, c in enumerate(s):
        t += -v[c] if i + 1 < len(s) and v[s[i + 1]] > v[c] else v[c]
    return t

def split_dispositivos(t):
    """Quebra o parágrafo antes de incisos (I - ), alíneas (a) ) e parágrafos (§ N) que seguem a sequência esperada."""
    cuts = []
    last_inc = 0; last_ali = 0; last_par = 0
    m0 = re.match(r'^([IVXLC]+)\s*[-–]\s', t)
    if m0: last_inc = _rom(m0.group(1))
    m0 = re.match(r'^([a-z])\)\s', t)
    if m0: last_ali = ord(m0.group(1)) - 96
    m0 = re.match(r'^§\s*(\d+)', t)
    if m0: last_par = int(m0.group(1))
    for m in re.finditer(r'(?<=[;:.)])\s+(?:e\s+|ou\s+)?(?=(?:([IVXLC]+)\s*[-–]\s|([a-z])\)\s|§\s*(\d+)\s*[º°o]?\s|(Parágrafo único)))', t):
        rest = t[m.end():]
        mi = re.match(r'([IVXLC]+)\s*[-–]\s', rest)
        ma = re.match(r'([a-z])\)\s', rest)
        mp = re.match(r'§\s*(\d+)', rest)
        if mi:
            n = _rom(mi.group(1))
            if n == last_inc + 1:
                last_inc = n; last_ali = 0; cuts.append(m.end())
        elif ma:
            n = ord(ma.group(1)) - 96
            if n == last_ali + 1:
                last_ali = n; cuts.append(m.end())
        elif mp:
            n = int(mp.group(1))
            if n == last_par + 1:
                last_par = n; last_inc = 0; last_ali = 0; cuts.append(m.end())
        elif rest.startswith('Parágrafo único'):
            last_inc = 0; last_ali = 0; cuts.append(m.end())
    out = []; p = 0
    for c in cuts:
        out.append(t[p:c].strip()); p = c
    out.append(t[p:].strip())
    return [x for x in out if x]
