"""Conversor de Normas Regulamentadoras (NR) do MTE: PDF -> rascunho Markdown no padrão da base.

Uso:
  python scripts/conversor_nr/converter_nr.py ARQUIVO.pdf --nr 1 [--ano 1978] [--saida rascunho.md]
  python scripts/conversor_nr/converter_nr.py --conferir ARQUIVO.pdf normas/norma-regulamentadora-federal-1-1978.md

Gera o corpo (itens, títulos, intertítulos, alíneas, incisos, marcadores, anotações e anexos) e um
relatório de conferência no stderr (sequência da numeração, títulos deduzidos, parágrafos sem marcador).
O frontmatter sai com campos a preencher (TODO). O rascunho SEMPRE passa por revisão humana contra o PDF:
o conversor não decide redação vencida, vigência diferida nem erros do original.

Regras (README, seção "Normas Regulamentadoras"):
- item numerado 1.5.3.1 -> parágrafo `**Item 1.5.3.1** {#ite1-5-3-1}`;
- item numerado que só dá título (sem pontuação final, seguido de subitem, não é oração) -> cabeçalho
  com profundidade = nº de níveis (1.5 -> ##, 1.5.3 -> ###, 1.5.4.2 -> ####, mais -> #####);
- intertítulo sem número -> cabeçalho um nível abaixo do título em que está, ID `<título>_subN`;
- subitens em lista aninhada: alínea a) -> `_alia`; romano I. / I - -> `_incN` (filho da alínea anterior
  do mesmo item, ou do item); 1) -> `_iteN`; marcador gráfico (•, -, –) -> `_mrcN`;
- anexos: `## ANEXO I DA NR-01 – TÍTULO {#anexo1}`; itens `anexo1_ite2-1`; termos e definições
  (Termo: definição) -> `anexo1_linN`;
- anotações oficiais em itálico (letra menor) -> `*(...)*` com link para a portaria e tag de controle
  (#incluido / #redacao-alterada / #revogado).
"""
import argparse
import re
import sys
import unicodedata

import fitz  # PyMuPDF

# Ano da portaria que aprovou cada NR (nome do arquivo: norma-regulamentadora-federal-N-ANO).
ANO_NR = {n: 1978 for n in range(1, 29)}
ANO_NR.update({29: 1997, 30: 2002, 31: 2005, 32: 2005, 33: 2006, 34: 2011, 35: 2012, 36: 2013,
               37: 2018, 38: 2022})

ROMANOS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV',
           'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV']
ANOT_INI = '\x01'
ANOT_FIM = '\x02'
RX_NUM = re.compile(r'^(\d+(?:\.\d+)*)\.?$')
RX_ALINEA = re.compile(r'^([a-z]{1,2})\)\s*(.*)$', re.S)
RX_ROMANO = re.compile(r'^([IVXL]+)\s*(?:\.|-|–|\))\s*(.*)$', re.S)
RX_ARABICO = re.compile(r'^(\d+)\)\s*(.*)$', re.S)
RX_MARCADOR = re.compile(r'^[•▪●◦\-–]\s+(.*)$', re.S)
RX_ANEXO = re.compile(r'^ANEXO\s+([IVXL]+)\b(.*)$', re.I)
RX_TERMO = re.compile(r'^([A-ZÀ-Ú][^:]{1,140}):\s')
ORACAO = {'o', 'a', 'os', 'as', 'é', 'são', 'cabe', 'compete', 'deve', 'devem', 'para', 'quando', 'nos',
          'no', 'na', 'nas', 'ao', 'à', 'serão', 'será', 'fica', 'ficam', 'consideram-se', 'considera-se',
          'todo', 'toda', 'sempre', 'em', 'um', 'uma', 'este', 'esta', 'caso'}
RODAPE = re.compile(r'Este texto não substitui|^\s*\d+\s*$')


def sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def romano_int(r):
    return ROMANOS.index(r) + 1 if r in ROMANOS else None


# ------------------------------------------------------------------ leitura do PDF

def linhas_pdf(caminho):
    """Uma entrada por linha visual: dict(pag, x, y, spans=[(texto, negrito, italico, tamanho)]).
    Linha só com espaço vira separador ({'vazia': True})."""
    doc = fitz.open(caminho)
    saida = []
    for pn, pag in enumerate(doc):
        altura = pag.rect.height
        for b in pag.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                x0, y0, _, _ = ln['bbox']
                if y0 > altura - 55:          # rodapé e número da página
                    continue
                spans = [(s['text'], bool(s['flags'] & 16), bool(s['flags'] & 2), s['size']) for s in ln['spans']]
                texto = ''.join(s[0] for s in spans)
                if RODAPE.search(texto):
                    continue
                if not texto.strip():
                    saida.append({'vazia': True, 'pag': pn, 'y': y0})
                    continue
                saida.append({'vazia': False, 'pag': pn, 'x': x0, 'y': y0, 'spans': spans})
    return saida


def texto_linha(ln, corpo):
    """Texto da linha com a anotação (itálico de letra menor que o corpo) entre ANOT_INI/ANOT_FIM."""
    out, em_anot = [], False
    for t, _b, it, tam in ln['spans']:
        anot = tam < corpo - 0.8 and (it or t.strip() in '()')
        if t.strip() == '':
            out.append(t)
            continue
        if anot and not em_anot:
            out.append(ANOT_INI)
            em_anot = True
        elif not anot and em_anot:
            out.append(ANOT_FIM)
            em_anot = False
        out.append(t)
    if em_anot:
        out.append(ANOT_FIM)
    return ''.join(out)


def juntar(a, b):
    a = a.rstrip()
    b = b.lstrip()
    if not a:
        return b
    limpo = a.replace(ANOT_FIM, '')
    if limpo.endswith('-') and len(limpo) > 1 and limpo[-2] != ' ':
        return a + b
    return a + ' ' + b


def normalizar(t):
    t = re.sub(r'\(\s*' + ANOT_INI, ANOT_INI + '(', t)
    t = re.sub(ANOT_FIM + r'(\s*)' + ANOT_INI, r'\1', t)
    t = re.sub(r'[ \t]+', ' ', t).strip()
    return t


# ------------------------------------------------------------------ blocos

def classificar_inicio(ln, corpo=12.0):
    """Marcador no começo da linha: ('num', '1.5.3') se o número está em negrito; ('alinea', 'a'),
    ('romano', 'II'), ('arabico', '1'), ('marcador', ''), ou None."""
    sp = [s for s in ln['spans'] if s[0].strip()]
    if not sp:
        return None
    primeiro = sp[0][0].strip()
    m = re.match(r'^(\d+(?:\.\d+)*)\.?(?:\s|$)', primeiro)
    if m and sp[0][1]:
        return ('num', m.group(1))
    if all(s[2] and s[3] < corpo - 0.8 for s in sp):      # linha só de anotação: "2025)" não é marcador
        return None
    texto = ''.join(s[0] for s in ln['spans']).strip()
    for nome, rx in (('alinea', RX_ALINEA), ('romano', RX_ROMANO), ('arabico', RX_ARABICO)):
        mm = rx.match(texto)
        if mm:
            return (nome, mm.group(1))
    if RX_MARCADOR.match(texto):
        return ('marcador', '')
    return None


def todo_negrito(ln):
    return all(s[1] for s in ln['spans'] if s[0].strip())


def todo_anotacao(ln, corpo):
    return all(s[2] and s[3] < corpo - 0.8 for s in ln['spans'] if s[0].strip())


def continua_anotacao(texto, ln):
    """Linha toda em anotação que continua o parêntese aberto na linha anterior ou abre um novo
    parêntese colado ao dispositivo ("(incluída pela ...)" na linha de baixo)."""
    if texto.count('(') > texto.count(')'):
        return True
    return ''.join(s[0] for s in ln['spans']).lstrip().startswith('(')


def blocos(linhas, corpo):
    """Agrupa as linhas em parágrafos. Novo bloco: linha vazia, salto vertical, marcador no início,
    título em negrito ou caixa de anotação."""
    out = []
    atual = None
    ult = None
    for ln in linhas:
        if ln['vazia']:
            atual = None
            continue
        ini = classificar_inicio(ln, corpo)
        negrito = todo_negrito(ln)
        anot = todo_anotacao(ln, corpo)
        salto = ult is not None and ln['pag'] == ult['pag'] and ln['y'] - ult['y'] > corpo * 1.45
        novo = atual is None or salto or ini is not None
        if atual is not None and ult is not None and ln['pag'] != ult['pag'] and not novo:
            # quebra de página: parágrafo terminado em pontuação e linha nova com maiúscula = novo parágrafo
            ant = atual['texto'].replace(ANOT_INI, '').replace(ANOT_FIM, '').rstrip()
            prim = ''.join(s[0] for s in ln['spans']).lstrip()[:1]
            if re.search(r'[.;:]$', ant) and prim.isupper():
                novo = True
        if atual is not None and not novo:
            if negrito != atual['negrito'] and not atual['ini']:
                novo = True
            if anot != atual['anot'] and not (anot and continua_anotacao(atual['texto'], ln)):
                novo = True
        txt = texto_linha(ln, corpo)
        if not novo and atual['anot'] and anot and not atual['texto'].lstrip(ANOT_INI).startswith('('):
            atual['texto'] = atual['texto'].rstrip().rstrip(ANOT_FIM).rstrip() + '; ' + txt.lstrip().lstrip(ANOT_INI)
            ult = ln
            continue
        if novo:
            atual = {'ini': ini, 'negrito': negrito, 'anot': anot, 'texto': txt, 'pag': ln['pag'], 'x': ln['x']}
            out.append(atual)
        else:
            atual['texto'] = juntar(atual['texto'], txt)
        ult = ln
    for b in out:
        b['texto'] = normalizar(b['texto'])
    return out


# ------------------------------------------------------------------ links e anotações

ORGAOS = {'mtb': 'mtb', 'mte': 'mte', 'mtp': 'mtp', 'ssmt': 'ssmt', 'ssst': 'ssst', 'sit': 'sit',
          'seprt': 'seprt', 'dsst': 'dsst', 'mtps': 'mtps', 'stras': 'stras'}
RX_PORTARIA = re.compile(r'Portaria\s+(MTb|MTE|MTP|SSMT|SSST|SIT|SEPRT|DSST|MTPS)\s+n\.?\s*[º°o]\s*'
                         r'([\d.]+)\s*,?\s*de\s+\d{1,2}(?:º)?\s+de\s+\w+\s+de\s+(\d{4})', re.I)
RX_PORTARIA_CURTA = re.compile(r'Portaria\s+(MTb|MTE|MTP|SSMT|SSST|SIT|SEPRT|DSST|MTPS)\s+n\.?\s*[º°o]\s*'
                               r'([\d.]+)\s*/\s*(\d{2,4})', re.I)
RX_LEI = re.compile(r'\b(Lei|Decreto|Decreto-Lei)\s+(?:n\.?\s*[º°]\s*)?([\d.]+)/(\d{4})')
RX_NR = re.compile(r'\b(NR\s?-\s?0?(\d{1,2}))\b')
RX_NR_EXT = re.compile(r'(Norma Regulamentador(?:a|as|es)\s+n[º°]\s*0?(\d{1,2}))')


def slug_portaria(orgao, numero, ano):
    ano = int(ano)
    if ano < 100:
        ano += 2000 if ano < 50 else 1900
    return f"portaria-{ORGAOS[orgao.lower()]}-{numero.replace('.', '')}-{ano}"


def linkar(texto, nr_atual, relacoes):
    """Portarias e NRs viram wikilinks. Não mexe em links já existentes."""
    def port(m):
        s = slug_portaria(m.group(1), m.group(2), m.group(3))
        relacoes.add(s)
        return f'[[{s}|{m.group(0)}]]'


    def nr(m):
        n = int(m.group(2))
        if n == nr_atual or n not in ANO_NR:
            return m.group(0)
        s = f'norma-regulamentadora-federal-{n}-{ANO_NR[n]}'
        relacoes.add(s)
        return f'[[{s}|{m.group(1)}]]'

    def lei(m):
        tipo = {'lei': 'lei', 'decreto': 'decreto', 'decreto-lei': 'decreto-lei'}[m.group(1).lower()]
        s = f"{tipo}-federal-{m.group(2).replace('.', '')}-{m.group(3)}"
        relacoes.add(s)
        return f'[[{s}|{m.group(0)}]]'

    partes = re.split(r'(\[\[[^\]]*\]\])', texto)
    for i in range(0, len(partes), 2):
        t = RX_PORTARIA.sub(port, partes[i])
        sub = re.split(r'(\[\[[^\]]*\]\])', t)
        for j in range(0, len(sub), 2):
            sub[j] = RX_LEI.sub(lei, RX_NR_EXT.sub(nr, RX_NR.sub(nr, RX_PORTARIA_CURTA.sub(port, sub[j]))))
        partes[i] = ''.join(sub)
    return ''.join(partes)


def tag_controle(anot):
    a = sem_acento(anot.lower())
    if 'revogad' in a:
        return '#revogado'
    if re.search(r'\b(incluid|inserid|acrescentad)', a):
        return '#incluido'
    if re.search(r'\b(alterad|redacao dada|nova redacao)', a):
        return '#redacao-alterada'
    return ''


def anotacoes(texto, nr_atual, relacoes):
    """Troca ANOT_INI(...)ANOT_FIM por *(...)* com links; devolve (texto, tag de controle)."""
    tags = []

    def sub(m):
        corpo = m.group(1).strip()
        corpo = corpo[1:] if corpo.startswith('(') else corpo
        corpo = corpo[:-1] if corpo.endswith(')') else corpo
        t = tag_controle(corpo)
        if t:
            tags.append(t)
        return '*(' + corpo.strip() + ')*'

    texto = re.sub(ANOT_INI + r'(.*?)' + ANOT_FIM, sub, texto, flags=re.S)
    texto = texto.replace(ANOT_INI, '').replace(ANOT_FIM, '')
    tag = '#revogado' if '#revogado' in tags else ('#incluido' if '#incluido' in tags else
                                                     ('#redacao-alterada' if tags else ''))
    return texto, tag


# ------------------------------------------------------------------ montagem

class Conversor:
    def __init__(self, nr):
        self.nr = nr
        self.relacoes = set()
        self.saida = []
        self.relatorio = []
        self.anexo = None          # 'anexo2'
        self.anexo_rom = None      # 'II'
        self.item = None           # ('1.4.1', id)
        self.alinea = None         # id da alínea corrente
        self.romano = None         # id do inciso corrente
        self.cont = {}             # contadores de marcadores por pai
        self.titulo_aberto = None  # (id, nivel)
        self.subs = {}
        self.vistos = []           # números de itens, para a checagem de sequência
        self.modo_termos = False
        self.modo_termos_titulo = False
        self.rot_alinea = self.rot_romano = ''
        self.alinea_antes_romano = False

    def anexo_rom_ou(self):
        return self.anexo_rom or ''

    # ---- rótulos e ids
    def pref(self):
        return f'{self.anexo}_' if self.anexo else ''

    def rot_pref(self):
        return f'Anexo {self.anexo_rom}, item ' if self.anexo else 'Item '

    def id_item(self, num):
        return f"{self.pref()}ite{num.replace('.', '-')}"

    def emitir(self, s=''):
        self.saida.append(s)

    def fechar_paragrafo(self):
        if self.saida and self.saida[-1] != '':
            self.emitir('')

    def texto(self, t):
        t, tag = anotacoes(t, self.nr, self.relacoes)
        t = linkar(t, self.nr, self.relacoes)
        return t, tag

    # ---- tipos de bloco
    def titulo(self, num, texto, ident=None):
        nivel = min(num.count('.') + (3 if self.anexo else 1), 5) if num else None
        ident = ident or self.id_item(num)
        t, tag = self.texto(texto)
        self.fechar_paragrafo()
        self.emitir(f"{'#' * nivel} {num} {t} {{#{ident}}}".replace('  ', ' '))
        caixa = getattr(self, 'caixa', None)
        if caixa:
            c, tag_c = self.texto(ANOT_INI + caixa + ANOT_FIM)
            tag = tag or tag_c
            self.emitir('')
            self.emitir(c)
            self.caixa = None
        if tag:
            self.emitir('')
            self.emitir(f'Tags: {tag}')
        self.emitir('')
        self.titulo_aberto = (ident, nivel)
        self.modo_termos_titulo = bool(re.search(r'gloss|termos e defini', sem_acento(texto.lower())))
        if num:
            self.vistos.append(('A' if self.anexo else 'C') + self.anexo_rom_ou() + ':' + num)
        self.item = None
        self.alinea = self.romano = None
        self.relatorio.append(f'título  {num} {texto[:60]}')

    def intertitulo(self, texto):
        base, nivel = self.titulo_aberto or (self.anexo or 'corpo', 1)
        base = base.split('_sub')[0]
        n = self.subs.get(base, 0) + 1
        self.subs[base] = n
        t, _ = self.texto(texto)
        self.fechar_paragrafo()
        self.emitir(f"{'#' * min(nivel + 1, 5)} {t} {{#{base}_sub{n}}}")
        self.emitir('')
        self.item = None
        self.alinea = self.romano = None
        self.relatorio.append(f'intertít. {texto[:60]}')

    def item_numerado(self, num, texto):
        ident = self.id_item(num)
        t, tag = self.texto(texto)
        self.fechar_paragrafo()
        self.emitir(f"**{self.rot_pref()}{num}** {{#{ident}}} {tag + ' ' if tag else ''}{t}".rstrip())
        self.item = (num, ident)
        self.alinea = self.romano = None
        self.vistos.append(('A' if self.anexo else 'C') + self.anexo_rom_ou() + ':' + num)

    def sub(self, tipo, marca, texto):
        if not self.item:
            self.relatorio.append(f'AVISO subitem fora de item: {marca} {texto[:50]}')
            self.paragrafo(texto)
            return
        num, ident_item = self.item
        rot_item = f'{self.rot_pref()}{num}'
        if tipo == 'alinea':
            pai, rot_pai = (self.romano, self.rot_romano) if (self.romano and not self.alinea_antes_romano) \
                else (ident_item, rot_item)
            ident = f'{pai}_ali{marca}'
            rot = f'{rot_pai}, alínea "{marca}"'
            self.alinea, self.rot_alinea = ident, rot
            if pai == ident_item:
                self.romano = None
        elif tipo == 'romano':
            n = romano_int(marca) or 0
            if self.alinea:
                pai, rot_pai = self.alinea, self.rot_alinea
            else:
                pai, rot_pai = ident_item, rot_item
            ident = f'{pai}_inc{n}'
            rot = f'{rot_pai}, inciso {marca}'
            self.romano, self.rot_romano = ident, rot
            self.alinea_antes_romano = bool(self.alinea)
        else:  # arabico / marcador
            pai = self.romano or self.alinea or ident_item
            rot_pai = (self.rot_romano if self.romano else self.rot_alinea if self.alinea else rot_item)
            chave = (pai, tipo)
            n = int(marca) if tipo == 'arabico' else self.cont.get(chave, 0) + 1
            self.cont[chave] = n
            suf = 'ite' if tipo == 'arabico' else 'mrc'
            ident = f'{pai}_{suf}{n}'
            rot = f'{rot_pai}, {"item" if tipo == "arabico" else "marcador"} {n}'
        nivel = ident.count('_') - ident_item.count('_') - 1
        t, tag = self.texto(texto)
        self.emitir(f"{'  ' * nivel}- **{rot}** {{#{ident}}} {tag + ' ' if tag else ''}{t}".rstrip())

    def paragrafo(self, texto):
        t, tag = self.texto(texto)
        self.fechar_paragrafo()
        self.emitir(t)
        self.relatorio.append(f'AVISO parágrafo sem marcador: {texto[:70]}')

    def termo(self, texto):
        if self.modo_termos_titulo and self.titulo_aberto:
            base = self.titulo_aberto[0]
            num = base.split('ite', 1)[1].replace('-', '.') if 'ite' in base else ''
            rot = (f'Anexo {self.anexo_rom}, item {num}' if self.anexo else f'Item {num}') if num else base
        elif self.anexo:
            base, rot = self.anexo, f'Anexo {self.anexo_rom}'
        else:
            base, rot = 'glossario', 'Glossário'
        n = self.cont.get((base, 'lin'), 0) + 1
        self.cont[(base, 'lin')] = n
        t, tag = self.texto(texto)
        self.fechar_paragrafo()
        self.emitir(f"**{rot}, linha {n}** {{#{base}_lin{n}}} {tag + ' ' if tag else ''}{t}")

    def abrir_anexo(self, rom, titulo):
        self.anexo, self.anexo_rom = f'anexo{romano_int(rom)}', rom
        self.titulo_aberto = (self.anexo, 2)
        self.item = None
        self.alinea = self.romano = None
        self.modo_termos = False
        self.fechar_paragrafo()
        nome = f'ANEXO {rom} DA NR-{self.nr:02d}'
        self.emitir(f"## {nome}{' – ' + titulo if titulo else ''} {{#{self.anexo}}}")
        self.emitir('')
        if re.search(r'termos e defini|gloss', sem_acento(titulo.lower())):
            self.modo_termos = True

    # ---- laço principal
    def rodar(self, bls):
        i = 0
        self.alinea_antes_romano = False
        while i < len(bls):
            b = bls[i]
            prox = bls[i + 1] if i + 1 < len(bls) else None
            txt = b['texto']
            limpo = txt.replace(ANOT_INI, '').replace(ANOT_FIM, '')
            ma = RX_ANEXO.match(limpo)
            if ma and b['negrito']:
                titulo = ma.group(2).strip(' -–:')
                titulo = re.sub(r'^da\s+NR\s?-?\s?\d+\s*', '', titulo, flags=re.I).strip(' -–')
                if not titulo and prox and prox['negrito'] and not prox['ini']:
                    titulo = prox['texto']
                    i += 1
                self.abrir_anexo(ma.group(1).upper(), titulo)
                i += 1
                continue
            if b['anot'] and prox and prox['ini'] and prox['ini'][0] == 'num' and prox['negrito']:
                self.caixa = txt
                self.relatorio.append(f'caixa de anotação levada para baixo do título seguinte: {limpo[:60]}')
                i += 1
                continue
            if b['anot']:
                t, tag = self.texto(ANOT_INI + txt + ANOT_FIM)
                self.fechar_paragrafo()
                self.emitir(t)
                self.emitir('')
                self.relatorio.append(f'AVISO anotação solta (caixa?): {limpo[:70]}')
                i += 1
                continue
            ini = b['ini']
            if ini and ini[0] == 'num':
                num = ini[1]
                resto = re.sub(r'^\s*' + re.escape(num) + r'\.?\s*', '', txt)
                niveis = num.count('.') + 1
                minimo = 1 if self.anexo else 2
                if niveis <= minimo or self.eh_titulo(num, resto, prox):
                    self.titulo(num, resto)
                else:
                    self.item_numerado(num, resto)
            elif ini and self.item:
                texto = re.sub(r'^\s*(?:[a-z]{1,2}\)|[IVXL]+\s*(?:\.|-|–|\))|\d+\)|[•▪●◦\-–])\s*', '', txt, count=1)
                self.sub(ini[0], ini[1], texto)
            elif re.match(r'^Sum[áa]rio\b', limpo, re.I):
                self.relatorio.append(f'sumário omitido: {limpo[:60]}')
            elif (self.modo_termos or self.modo_termos_titulo) and self.saida \
                    and re.match(r'^(Observação|Nota|Exemplos?)\s*:', limpo):
                t, _ = self.texto(txt)
                self.saida[-1] += ' ' + t
                self.relatorio.append(f'observação anexada ao termo anterior: {limpo[:50]}')
            elif (self.modo_termos or self.modo_termos_titulo) and RX_TERMO.match(limpo):
                self.termo(txt)
            elif not b['negrito'] and prox and prox['ini'] and prox['ini'][0] == 'num' \
                    and not re.search(r'[.;:,]\s*$', limpo) and len(limpo.split()) <= 15:
                self.intertitulo(txt)
            elif b['negrito'] and not ini:
                self.intertitulo(txt)
            else:
                self.paragrafo(txt)
            i += 1
        return '\n'.join(self.saida).rstrip() + '\n'

    def eh_titulo(self, num, resto, prox):
        if re.search(r'[.;:,]\s*$', resto.replace(ANOT_FIM, '').strip()) or not resto.strip():
            return False
        if not (prox and prox['ini'] and prox['ini'][0] == 'num' and prox['ini'][1].startswith(num + '.')):
            return False
        palavras = resto.split()
        return len(palavras) <= 14 and sem_acento(palavras[0].lower()) not in {sem_acento(p) for p in ORACAO}


# ------------------------------------------------------------------ checagens

def checar_sequencia(numeros):
    """Número fora de ordem: depois de 1.5.3.1 espera-se 1.5.3.1.1, 1.5.3.2, 1.5.4 ou 1.6 (por contexto:
    corpo e cada anexo)."""
    avisos = []
    ant, ctx_ant = None, None
    for chave in numeros:
        ctx, n = chave.split(':')
        p = [int(x) for x in n.split('.')]
        if ctx != ctx_ant:
            ant, ctx_ant = None, ctx
        if ant is not None:
            ok = len(p) == len(ant) + 1 and p[:-1] == ant and p[-1] == 1
            k = len(p)
            if k <= len(ant) and p[:k - 1] == ant[:k - 1] and p[k - 1] == ant[k - 1] + 1:
                ok = True
            if not ok:
                avisos.append(f'SEQUÊNCIA {".".join(map(str, ant))} -> {n}')
        ant = p
    return avisos


def checar_listas(md):
    avisos = []
    ant = {}
    for ln in md.splitlines():
        m = re.search(r'\{#([^}]*_(ali|inc|ite|mrc)(\w+))\}', ln)
        if not m or not ln.lstrip().startswith('- '):
            continue
        ident, tipo, val = m.group(1), m.group(2), m.group(3)
        pai = ident.rsplit('_', 1)[0]
        n = ord(val) - 96 if tipo == 'ali' and len(val) == 1 else (int(val) if val.isdigit() else None)
        if n is None:
            continue
        esperado = ant.get((pai, tipo), 0) + 1
        if n != esperado:
            avisos.append(f'LISTA {ident}: esperado {esperado}')
        ant[(pai, tipo)] = n
    return avisos


def detectar_inicio(bls):
    """Pula capa, tabela de portarias e sumário: o corpo começa no primeiro título 'N.1 ...' em negrito
    que vem depois do sumário (o sumário repete os mesmos números sem negrito)."""
    for i, b in enumerate(bls):
        if b['ini'] and b['ini'][0] == 'num' and b['ini'][1].count('.') == 1 and b['ini'][1].endswith('.1') \
                and b['negrito']:
            return i
    for i, b in enumerate(bls):
        if b['ini'] and b['ini'][0] == 'num':
            return i
    return 0


def palavras_md(md):
    """Texto do Markdown sem rótulos, IDs, tags, sintaxe de link e seções editoriais."""
    md = md.split('\n---\n', 1)[1] if md.startswith('---') else md
    md = re.split(r'\n## (?:Histórico de alterações|Relação com normas superiores|Notas de transcrição)', md)[0]
    md = re.sub(r'\{#[^}]*\}', ' ', md)
    md = re.sub(r'\*\*[^*]+\*\*', ' ', md)
    md = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', md)
    md = re.sub(r'\[\[([^\]]*)\]\]', r'\1', md)
    md = re.sub(r'#(?:revogado|redacao-alterada|incluido|anexo-pendente)\b|^Tags:.*$', ' ', md, flags=re.M)
    md = re.sub(r'^#+ |^> .*$|^\s*- ', ' ', md, flags=re.M)
    md = md.replace('*(', '(').replace(')*', ')')
    return md.split()


def palavras_pdf(caminho):
    out = []
    for ln in linhas_pdf(caminho):
        if not ln['vazia']:
            out.append(''.join(s[0] for s in ln['spans']))
    texto = '\n'.join(out)
    texto = re.sub(r'(\S)-\n(\S)', r'\1-\2', texto)
    return texto.split()


def conferir(pdf, md_arq):
    """Diferenças de palavras entre o PDF e o corpo do Markdown (difflib). Rótulos, marcadores e
    sumário aparecem como diferença: o que importa é não sobrar palavra do texto normativo."""
    import difflib
    a, b = palavras_pdf(pdf), palavras_md(open(md_arq, encoding='utf-8').read())
    norm = lambda w: re.sub(r'[\W_]+', '', w.lower())
    sm = difflib.SequenceMatcher(None, [norm(w) for w in a], [norm(w) for w in b], autojunk=False)
    marcador = re.compile(r'^(\d+(\.\d+)*\.?|[a-z]{1,2}\)|[IVXL]+\.?|[a-z]|–|-)$')
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if all(marcador.match(w) for w in a[i1:i2] + b[j1:j2]):
            continue
        if True:
            print(f"{op:8} PDF: {' '.join(a[i1:i2])[:160]!r}\n         MD:  {' '.join(b[j1:j2])[:160]!r}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--conferir':
        conferir(sys.argv[2], sys.argv[3])
        return
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf')
    ap.add_argument('--nr', type=int, required=True)
    ap.add_argument('--ano', type=int)
    ap.add_argument('--corpo', type=float, default=12.0, help='tamanho da letra do corpo (anotação é menor)')
    ap.add_argument('--saida')
    a = ap.parse_args()
    ano = a.ano or ANO_NR.get(a.nr)
    arquivo = f'norma-regulamentadora-federal-{a.nr}-{ano}'

    bls = blocos(linhas_pdf(a.pdf), a.corpo)
    ini = detectar_inicio(bls)
    capa = [b['texto'].replace(ANOT_INI, '').replace(ANOT_FIM, '') for b in bls[:ini]]
    conv = Conversor(a.nr)
    corpo = conv.rodar(bls[ini:])

    portarias = sorted({s for s in conv.relacoes if s.startswith('portaria-')} |
                       {slug_portaria(m.group(1), m.group(2), m.group(3))
                        for t in capa for m in RX_PORTARIA.finditer(t)})
    citas = sorted(s for s in conv.relacoes if not s.startswith('portaria-'))
    fm = [
        '---',
        f'norma: Norma Regulamentadora nº {a.nr} (NR-{a.nr:02d})',
        f'arquivo: {arquivo}',
        'tipo: norma-regulamentadora',
        'esfera: federal',
        f'numero: {a.nr}',
        f'ano: {ano}',
        'data_assinatura: TODO',
        'publicacao: "TODO"',
        'orgao: Ministério do Trabalho e Emprego',
        'ementa: "TODO"',
        'situacao: vigente',
        'regulamenta: []',
        'altera: []',
        'alterado_por: [' + ', '.join(f'"[[{p}]]"' for p in portarias) + ']',
        'revoga: []',
        'revogado_por: []',
        'texto: compilado (atualizado até TODO)',
        'cita: [' + ', '.join(f'"[[{c}]]"' for c in citas) + ']',
        'tags: []',
        'fonte: "TODO"',
        '---',
        '',
        f'# NR {a.nr:02d} - TODO {{#{arquivo}}}',
        '',
        '> TODO ementa e aprovação.',
        '',
        '',
    ]
    md = '\n'.join(fm) + corpo
    md += '\n## Histórico de alterações {#historico-alteracoes}\n\nTODO (capa do PDF):\n\n' + \
          '\n'.join(f'- {c}' for c in capa) + '\n\n## Notas de transcrição {#notas-transcricao}\n\nTODO\n'
    if a.saida:
        open(a.saida, 'w', encoding='utf-8').write(md)
    else:
        sys.stdout.write(md)
    for r in conv.relatorio + checar_sequencia(conv.vistos) + checar_listas(md):
        print(r, file=sys.stderr)


if __name__ == '__main__':
    main()
