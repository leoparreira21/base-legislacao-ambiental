#!/usr/bin/env python3
"""Gera a versão HTML de consulta de cada norma da base (dispositivos com recolher/expandir).

Uso:
  python scripts/gerar_html.py              # grava em html/
  python scripts/gerar_html.py PASTA        # grava em outra pasta (o site usa _site/html)

Lê normas/*.md, normas/anexos/*.md e normas/comentarios/*.md e grava um HTML por arquivo,
mais um index.html com a lista. Cada HTML é autossuficiente (CSS e JS embutidos).

Como a página se comporta:
  - Ao abrir, mostra só o título, a ementa e os índices do primeiro nível (títulos ou
    capítulos; sem capítulos, os artigos).
  - Cada índice (<details>) abre o próprio texto e os índices dos dispositivos ligados a ele:
    capítulo -> seções -> artigos -> caput e parágrafos -> incisos -> alíneas -> itens.
    O caput não tem índice próprio: o texto dele aparece ao abrir o artigo.
  - Linhas de anexo (IDs ..._linN) aparecem direto ao abrir o anexo, sem índice por linha.
  - Botão de três estados: "Expandir tudo" -> "Recolher artigos" (só índices de artigos,
    com títulos, capítulos e seções abertos) -> "Recolher tudo" (volta aos capítulos).
  - Endereço com #id (ex.: lei-federal-12305-2010.html#art3_cpt_inc7) abre o caminho até
    o dispositivo; os links [[norma#id]] do Markdown viram links entre as páginas.

A hierarquia vem do padrão do README: cabeçalhos ## a ###### e IDs LexML dos dispositivos.
"""
import html
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTAS = [RAIZ / 'normas', RAIZ / 'normas' / 'anexos', RAIZ / 'normas' / 'comentarios']

RE_CABECALHO = re.compile(r'^(#{1,6})\s+(.*?)\s*(?:\{#([^}]+)\}\s*(.*?))?\s*$')
RE_ANEXO = re.compile(r'^ANEXO(?!S)\b', re.I)
RE_GRUPO_ANEXOS = re.compile(r'^ANEXOS\b', re.I)
EDITORIAIS = {'sintese', 'sintese-conversor', 'notas-transcricao', 'fontes', 'observacoes'}
RE_ID_CITACAO = re.compile(r'\s*\{#([^}]+)\}')
RE_DISP = re.compile(r'^(\s*)(?:[-*]\s+)?\*\*(.+?)\*\*\s*\{#([^}]+)\}\s*(.*)$')
RE_TAGS_INICIO = re.compile(r'^(?:#[\w-]+\s+)+')
RE_TAG_SOLTA = re.compile(r'(?<![\w/&#])#[a-z][\w-]*(?=\s|$)')


class No:
    def __init__(self, tipo, ident, rotulo, nivel=0):
        self.tipo = tipo          # 'raiz', 'sec' (título/capítulo/seção), 'art', 'disp', 'cpt', 'lin'
        self.id = ident
        self.rotulo = rotulo
        self.nivel = nivel        # nível do cabeçalho (2 a 6)
        self.conteudo = []        # ('html', str) ou ('no', No)
        self.revogado = False

    def filhos(self):
        return [c for k, c in self.conteudo if k == 'no']

    def tem_artigo(self):
        # artigos (ou itens numerados, nas NRs) abaixo deste cabeçalho
        return any(f.tipo in ('art', 'disp') or (f.tipo == 'sec' and f.tem_artigo()) for f in self.filhos())


# ---------------------------------------------------------------- Markdown inline

def ler_frontmatter(texto):
    if not texto.startswith('---\n'):
        return {}, texto
    fim = texto.find('\n---', 4)
    if fim < 0:
        return {}, texto
    fm = {}
    for linha in texto[4:fim].splitlines():
        m = re.match(r'^(\w+):\s*(.*)$', linha)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm, texto[fim + 4:].lstrip('\n')


class Conversor:
    def __init__(self, existentes, arquivo, pasta_md, saida, anexos=None):
        self.existentes = existentes
        self.anexos = anexos or {}     # arquivo do anexo -> (norma-mãe, id do título do anexo nela)
        self.arquivo = arquivo
        self.pasta_md = pasta_md
        self.saida = saida

    def link(self, m):
        alvo, texto = m.group(1), m.group(2)
        alvo = alvo.replace('\\', '')
        norma, _, frag = alvo.partition('#')
        norma = norma.strip()
        rotulo = texto if texto is not None else (alvo.lstrip('#') or alvo)
        if not norma:
            if self.arquivo in self.anexos and frag == 'texto-anexo':
                frag = self.anexos[self.arquivo][1]
            elif self.arquivo in self.anexos and frag in EDITORIAIS:
                frag = f'{self.anexos[self.arquivo][1]}-{frag}'
            return f'<a href="#{frag}">{rotulo}</a>'
        if norma in self.anexos:       # o anexo fica dentro da página da norma-mãe
            mae, ancora = self.anexos[norma]
            if frag == 'texto-anexo':
                frag = ancora
            elif frag in EDITORIAIS:
                frag = f'{ancora}-{frag}'
            return f'<a href="{mae}.html#{frag or ancora}">{rotulo}</a>'
        if norma in self.existentes:
            return f'<a href="{norma}.html' + (f'#{frag}' if frag else '') + f'">{rotulo}</a>'
        return f'<span class="pendente" title="Norma ainda não incluída na base: {norma}">{rotulo}</span>'

    def imagem(self, m):
        alt, src = m.group(1), m.group(2)
        if not re.match(r'^[a-z]+:', src):
            # sempre relativo a html/ na raiz: vale no repositório e no site (_site/html + _site/normas/...)
            src = os.path.relpath(self.pasta_md / html.unescape(src), RAIZ / 'html').replace(os.sep, '/')
        return f'<img src="{html.escape(src)}" alt="{alt}" loading="lazy">'

    def inline(self, t):
        # escapes do Markdown (\*, \|, \_ ...): guardados antes da formatação e devolvidos sem a barra
        t = re.sub(r'\[\[[^\]]*\]\]', lambda m: m.group(0).replace('\\|', '|'), t)   # [[norma#id\|rótulo]] em tabelas
        t = re.sub(r'\\([\\*_#|\[\]()~`>-])', lambda m: f'\x00{ord(m.group(1))}\x00', t)
        t = html.escape(t, quote=False)
        t = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)', self.imagem, t)
        t = re.sub(r'\[\[([^\]|]+?)(?:(?<!\\)\|([^\]]+))?\]\]', self.link, t)
        t = re.sub(r'(?<!!)\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', t)
        t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'~~(.+?)~~', r'<del>\1</del>', t)
        t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
        t = re.sub(r'\x00(\d+)\x00', lambda m: html.escape(chr(int(m.group(1))), quote=False), t)
        return t

    def tabela(self, linhas):
        def celulas(l):
            return dividir_celulas(l.strip().strip('|'), r'\|')
        corpo = [l for l in linhas if not re.match(r'^\s*\|?\s*:?-{2,}', l)]
        if not corpo:
            return ''
        cab, resto = celulas(corpo[0]), corpo[1:]
        h = '<div class="tabela"><table><thead><tr>' + ''.join(f'<th>{self.inline(c)}</th>' for c in cab) + '</tr></thead><tbody>'
        for l in resto:
            h += '<tr>' + ''.join(f'<td>{self.inline(c)}</td>' for c in celulas(l)) + '</tr>'
        return h + '</tbody></table></div>'


RE_LINHA_TABELA = re.compile(r'_tab\d+(_lin\d+[a-z-]*)$')
RE_CAB_TABELA = re.compile(r'(_tab\d+)_cab$')
RE_OBS_TABELA = re.compile(r'(_tab\d+)_obs\d*$')
RE_CHAVE = re.compile(r'^([^:\[\]]{1,140}?):\s+(.*)$', re.S)


def dividir_celulas(texto, sep=r' \| '):
    """Divide pelo separador, sem cortar [[norma|rótulo]] nem "\\|"."""
    partes, buf, prof, i = [], '', 0, 0
    rx = re.compile(sep)
    while i < len(texto):
        if texto.startswith('[[', i):
            prof += 1; buf += '[['; i += 2; continue
        if texto.startswith(']]', i):
            prof = max(0, prof - 1); buf += ']]'; i += 2; continue
        m = rx.match(texto, i)
        if prof == 0 and m and (i == 0 or texto[i - 1] != '\\'):
            partes.append(buf.strip()); buf = ''; i = m.end(); continue
        buf += texto[i]; i += 1
    partes.append(buf.strip())
    return partes


def celulas_linha(texto):
    """'Porte: Micro | Área (ha): até 10' -> [('Porte', 'Micro'), ('Área (ha)', 'até 10')]; sem chave -> (None, texto).
    Chave curta depois de uma chave com grupo herda o grupo: 'CLASSE — I: X | II: X' -> 'CLASSE — II'."""
    saida, grupo = [], None
    for parte in dividir_celulas(texto):
        if not parte:
            continue
        m = RE_CHAVE.match(parte)
        if not m:
            saida.append((None, parte))
            continue
        chave = m.group(1).strip()
        if ' — ' in chave:
            grupo = chave.rsplit(' — ', 1)[0]
        elif grupo and len(chave) <= 5:
            chave = f'{grupo} — {chave}'
        else:
            grupo = None
        saida.append((chave, m.group(2).strip()))
    return saida


# ---------------------------------------------------------------- árvore

ROTULO_CURTO = [
    (re.compile(r'^inciso\s+(.+)$', re.I), r'\1'),
    (re.compile(r'^alínea\s+"?([^"]+)"?$', re.I), r'\1)'),
    (re.compile(r'^item\s+(.+)$', re.I), r'item \1'),
]


def rotulo_curto(rotulo):
    ultimo = rotulo.split(', ')[-1].strip()
    for rx, sub in ROTULO_CURTO:
        if rx.match(ultimo):
            return rx.sub(sub, ultimo)
    if ultimo.lower() == 'parágrafo único':
        return 'Parágrafo único'
    return ultimo


def montar(corpo, conv):
    raiz = No('raiz', None, '')
    titulo, cabecalho = '', []
    titulo_id = None
    pilha = [raiz]               # cabeçalhos abertos
    por_id = {}
    dono = raiz                  # nó que recebe texto solto
    tabela = []
    inicio = True                # ainda no cabeçalho da página (título e ementa)

    def despeja_tabela():
        if tabela:
            dono.conteudo.append(('html', conv.tabela(tabela)))
            tabela.clear()

    for linha in corpo.splitlines():
        if linha.lstrip().startswith('|'):
            tabela.append(linha)
            continue
        despeja_tabela()
        s = linha.strip()
        if not s:
            continue

        m = RE_CABECALHO.match(linha)
        if m and not linha.startswith(' '):
            nivel, texto, ident = len(m.group(1)), m.group(2), m.group(3)
            if nivel == 1:
                titulo = texto
                titulo_id = ident
                continue
            inicio = False
            while pilha[-1] is not raiz and pilha[-1].nivel >= nivel:
                pilha.pop()
            if RE_ANEXO.match(texto):
                # "### ANEXO I" logo depois do último artigo não pertence ao último capítulo:
                # sobe para o nível da norma, ou fica sob o título de grupo "ANEXOS", se houver
                while pilha[-1] is not raiz and not (pilha[-1].nivel == 2 and RE_GRUPO_ANEXOS.match(pilha[-1].rotulo)):
                    pilha.pop()
            tipo = 'art' if nivel == 6 else 'sec'
            no = No(tipo, ident, texto, nivel)
            if m.group(4):          # algo depois do {#id}, ex.: link para o comentário
                no.extra = conv.inline(m.group(4))
            pilha[-1].conteudo.append(('no', no))
            pilha.append(no)
            if ident:
                por_id[ident] = no
            dono = no
            continue

        if s.startswith('Tags:'):
            continue

        if inicio and s.startswith('>'):
            mid = RE_ID_CITACAO.search(s)
            txt = conv.inline(RE_ID_CITACAO.sub('', s.lstrip('> ')).strip())
            cabecalho.append(f'<span id="{html.escape(mid.group(1))}">{txt}</span>' if mid else txt)
            continue

        m = RE_DISP.match(linha)
        if m:
            inicio = False
            rotulo, ident, texto = m.group(2), m.group(3), m.group(4)
            revogado = '#revogado' in texto.split('(')[0] if texto else False
            texto = RE_TAGS_INICIO.sub('', texto).strip()
            texto = RE_TAG_SOLTA.sub('', texto).strip()
            container = pilha[-1]
            if re.match(r'(fecho|assinatura)', ident):
                container = raiz          # fecho e assinaturas ficam no nível da norma
            elif container.tipo == 'art' and not ident.startswith('art'):
                container = pilha[-2]     # bloco depois do último artigo não pertence a ele
            pai = None
            for cand_id in ancestrais(ident):
                cand = por_id.get(cand_id)
                if cand is not None and getattr(cand, 'tabela', None):
                    continue          # linha de tabela não tem filhos: o pai é o da tabela
                if cand is not None and dentro(cand, container):
                    pai = cand
                    break
            if pai is None:
                pai = container
            if re.search(r'_lin\d+[a-z-]*$', ident):
                tipo = 'lin'
            elif ident.endswith('_cpt') and pai.tipo == 'art':
                tipo = 'cpt'
            else:
                tipo = 'disp'
            no = No(tipo, ident, rotulo)
            no.revogado = revogado
            mtab = RE_LINHA_TABELA.search(ident) if tipo == 'lin' else None
            mcab = RE_CAB_TABELA.search(ident)
            if not mcab and rotulo.endswith('cabeçalho'):
                mcab = re.search(r'(_tab\d+)$', ident)
            mobs = RE_OBS_TABELA.search(ident)
            if mobs:
                # observações da tabela: linha final de largura inteira
                tipo = 'lin'
                no = No(tipo, ident, rotulo)
                no.tabela = ident[:mobs.end(1)]
                no.celulas = [(None, conv.inline(texto))]
                no.revogado = revogado
            elif mcab:
                # cabeçalho explícito da tabela: só aparece se as linhas não trouxerem as colunas
                tipo = 'lin'
                no = No(tipo, ident, rotulo)
                no.tabela = ident[:mcab.end(1)]
                no.cab = [conv.inline(c) for c in dividir_celulas(re.sub(r'\s*\([^)]*\)\s*$', '', texto))]
                no.celulas = []
                no.revogado = revogado
            elif mtab:
                # linha de tabela "Coluna: valor | Coluna: valor": vira linha de <table> no render
                no.tabela = ident[:mtab.start(1)]
                no.celulas = [(conv.inline(k) if k else None, conv.inline(v)) for k, v in celulas_linha(texto)]
            elif texto:
                no.conteudo.append(('html', f'<p class="texto">{conv.inline(texto)}</p>'))
            pai.conteudo.append(('no', no))
            no.pai = pai
            por_id[ident] = no
            dono = no
            continue

        # texto solto: continua o último nó. Um {#id} na linha (bloco de nova redação, linha de anexo
        # sem rótulo, ex.: "- Nome; {#anexo4_lin25}") vira o id do parágrafo, para os links chegarem nele.
        texto = s
        mid = RE_ID_CITACAO.search(texto)
        ida = f' id="{html.escape(mid.group(1))}"' if mid else ''
        if mid:
            texto = RE_ID_CITACAO.sub('', texto, count=1).strip()
        if texto.startswith('>'):
            frag = f'<blockquote{ida}>{conv.inline(texto.lstrip("> ").strip())}</blockquote>'
        elif texto.startswith('Alterações:'):
            frag = f'<p class="nota"{ida}>{conv.inline(texto)}</p>'
        elif re.match(r'^[-*]\s+', texto):
            recuo = (len(linha) - len(linha.lstrip())) // 2
            frag = f'<p class="item r{min(recuo, 4)}"{ida}>{conv.inline(re.sub(r"^[-*]\s+", "", texto))}</p>'
        else:
            frag = f'<p{ida}>{conv.inline(texto)}</p>'
        if inicio:
            cabecalho.append(conv.inline(texto))
        else:
            dono.conteudo.append(('html', frag))
    despeja_tabela()
    raiz.id_titulo = titulo_id
    return titulo, cabecalho, raiz


def ancestrais(ident):
    """IDs candidatos a pai, do mais próximo ao mais distante.
    art5_par2_inc3 -> art5_par2, art5; nas NRs, ite13-1-3-1 -> ite13-1-3, ite13-1."""
    partes = ident.split('_')
    while len(partes) > 1:
        partes.pop()
        yield '_'.join(partes)
    if partes[0].startswith('ite'):
        pedacos = partes[0].split('-')
        while len(pedacos) > 1:
            pedacos.pop()
            yield '-'.join(pedacos)


def dentro(no, container):
    """O nó está na subárvore do cabeçalho aberto (para não ligar a dispositivo de outro artigo)?"""
    while no is not None:
        if no is container:
            return True
        no = getattr(no, 'pai', None)
    return False


def marcar_pais(no):
    for f in no.filhos():
        if not hasattr(f, 'pai'):
            f.pai = no
        marcar_pais(f)


NOMES_NIVEL = [('parágrafo', '§§'), ('§', '§§'), ('inciso', 'incisos'), ('alínea', 'alíneas'), ('item', 'itens'),
               ('caput', 'caput'), ('tabela', 'tabelas'), ('nota', 'notas'), ('pena', 'pena')]


def nome_nivel(rotulo):
    ultimo = rotulo.split(', ')[-1].strip().lower()
    for inicio, nome in NOMES_NIVEL:
        if ultimo.startswith(inicio):
            return nome
    return 'outros'


def niveis_do_artigo(art):
    """Nomes dos dispositivos em cada profundidade do artigo: [['incisos', '§§'], ['incisos dos §§'], ...].
    Tipo que já apareceu num nível acima leva o nome do pai (incisos dos §§) para não confundir."""
    tipos = []      # tipos puros por profundidade
    niveis = []

    def walk(no, p, nome_pai):
        for f in no.filhos():
            if f.tipo == 'disp':
                while len(niveis) < p:
                    niveis.append([])
                    tipos.append(set())
                nome = nome_nivel(f.rotulo)
                tipos[p - 1].add(nome)
                rotulo = nome
                if nome_pai and any(nome in t for t in tipos[:p - 1]):
                    rotulo = f"{nome} {'das' if nome_pai == 'alíneas' else 'dos'} {nome_pai}"
                if rotulo not in niveis[p - 1]:
                    niveis[p - 1].append(rotulo)
                walk(f, p + 1, nome)
            else:
                walk(f, p, nome_pai)
    walk(art, 1, None)
    return niveis


def controle_niveis(art):
    """Seletor de níveis do artigo: 'Índices' fecha tudo; cada botão seguinte abre o texto até aquele nível."""
    niveis = niveis_do_artigo(art)
    if not niveis:
        return ''
    botoes = '<button type="button" data-nivel="0" title="Só os índices do caput e dos parágrafos">Índices</button>'
    for i, nomes in enumerate(niveis, 1):
        rotulo = ', '.join(nomes[:-1]) + ' e ' + nomes[-1] if len(nomes) > 1 else nomes[0]
        ativo = ' class="ativo"' if i == len(niveis) else ''
        botoes += f'<button type="button" data-nivel="{i}"{ativo} title="Abre o texto até: {rotulo}">{rotulo}</button>'
    return f'<div class="niveis" role="group" aria-label="Níveis do artigo"><span>Abrir até:</span>{botoes}</div>'


def render_conteudo(conteudo, prof):
    """Renderiza o conteúdo de um nó; linhas consecutivas da mesma tabela viram uma <table>."""
    partes, i = [], 0
    while i < len(conteudo):
        k, c = conteudo[i]
        if k == 'no' and getattr(c, 'tabela', None):
            linhas = [c]
            i += 1
            while i < len(conteudo) and conteudo[i][0] == 'no' and getattr(conteudo[i][1], 'tabela', None) == c.tabela:
                linhas.append(conteudo[i][1])
                i += 1
            partes.append(render_tabela(linhas, prof))
            continue
        partes.append(c if k == 'html' else render(c, prof))
        i += 1
    return ''.join(partes)


def montar_blocos(linhas):
    """Separa as linhas em blocos com o mesmo cabeçalho.
    - linha só com colunas já conhecidas: entra no bloco (célula ausente fica vazia);
    - mesma quantidade de colunas, só a primeira com outro nome (PARÂMETROS -> PARÂMETROS INORGÂNICOS):
      novo bloco, com subcabeçalho;
    - colunas novas (cabeçalho em dois níveis achatado, ex.: "Método — Aspersão"): somam-se ao bloco."""
    blocos = []
    for ln in linhas:
        chaves = [ch for ch, _ in ln.celulas if ch is not None]
        b = blocos[-1] if blocos else None
        if not chaves:
            if b is None:
                b = {'colunas': [], 'linhas': []}
                blocos.append(b)
        elif b is None or not b['colunas']:
            if b is None:
                b = {'colunas': [], 'linhas': []}
                blocos.append(b)
            b['colunas'] = list(dict.fromkeys(chaves))
        elif set(chaves) <= set(b['colunas']):
            pass
        elif len(chaves) == len(b['colunas']) and chaves[1:] == b['colunas'][1:]:
            b = {'colunas': list(dict.fromkeys(chaves)), 'linhas': []}
            blocos.append(b)
        else:
            b['colunas'] += [ch for ch in dict.fromkeys(chaves) if ch not in b['colunas']]
        b['linhas'].append(ln)
    return blocos


def juntar_linhas(linhas):
    """Reúne linhas que a conversão separou: mesma informação nas colunas comuns e colunas novas
    (Porte: Micro | Área: <10 | Aspersão: DLAM  +  Porte: Micro | Área: <10 | Localizada: DLAM)."""
    juntas = []
    for ln in linhas:
        valores = {ch: v for ch, v in ln.celulas if ch is not None}
        if juntas and valores:
            ant = juntas[-1]
            comuns = set(ant['valores']) & set(valores)
            novas = set(valores) - set(ant['valores'])
            if comuns and novas and all(ant['valores'][ch] == valores[ch] for ch in comuns) and not ant['livre']:
                for ch in novas:
                    ant['valores'][ch] = valores[ch]
                    ant['ids'][ch] = ln.id
                ant['nos'].append(ln)
                continue
        livre = ' '.join(v for ch, v in ln.celulas if ch is None)
        juntas.append({'valores': valores, 'ids': {}, 'livre': livre, 'nos': [ln]})
    return juntas


def cabecalho_tabela(colunas):
    """Cabeçalho da tabela. Colunas "Grupo — Sub — Item" viram várias linhas de <th>,
    com o grupo em colspan sobre as colunas dele e rowspan nas colunas de nível único."""
    partes = [c.split(' — ') for c in colunas]
    niveis = max(len(p) for p in partes)
    linhas = []
    for nv in range(niveis):
        tr, i = '', 0
        while i < len(partes):
            p = partes[i]
            if len(p) <= nv:
                i += 1
                continue
            if len(p) == nv + 1:
                rs = f' rowspan="{niveis - nv}"' if niveis - nv > 1 else ''
                tr += f'<th{rs}>{p[nv]}</th>'
                i += 1
                continue
            n = 1
            while i + n < len(partes) and len(partes[i + n]) > nv + 1 and partes[i + n][:nv + 1] == p[:nv + 1]:
                n += 1
            cs = f' colspan="{n}"' if n > 1 else ''
            tr += f'<th{cs}>{p[nv]}</th>'
            i += n
        linhas.append(f'<tr class="cab">{tr}</tr>')
    return ''.join(linhas)


def mesclar_colunas(linhas):
    """Células iguais seguidas nas primeiras colunas viram uma célula com rowspan (como na publicação).
    Cada coluna só mescla dentro dos grupos já mesclados da coluna anterior; a última coluna nunca mescla."""
    if not linhas or not linhas[0]['celulas']:
        return
    ncol = len(linhas[0]['celulas'])
    grupos = [(0, len(linhas))]
    for c in range(ncol - 1):
        novos = []
        for ini, fim in grupos:
            k = ini
            while k < fim:
                v = linhas[k]['celulas'][c][1]
                n = 1
                while k + n < fim and v and linhas[k + n]['celulas'][c][1] == v and not linhas[k + n]['celulas'][c][0]:
                    n += 1
                if n > 1:
                    linhas[k]['celulas'][c][2] = n
                    for r in range(k + 1, k + n):
                        linhas[r]['celulas'][c][2] = 0      # coberta pelo rowspan
                    novos.append((k, k + n))
                k += n
        if not novos:
            break
        grupos = novos


def render_tabela(linhas, prof):
    linhas_html, depois = [], []
    cabs = [ln for ln in linhas if getattr(ln, 'cab', None) is not None]
    linhas = [ln for ln in linhas if getattr(ln, 'cab', None) is None]
    id_tabela = ''
    if cabs:
        id_tabela = f' id="{html.escape(cabs[0].id)}"'
        if not any(ch for ln in linhas for ch, _ in ln.celulas):   # sem colunas nas linhas: usa o cabeçalho
            linhas_html.append('<tr class="cab">' + ''.join(f'<th>{c}</th>' for c in cabs[0].cab) + '</tr>')
    blocos = montar_blocos(linhas)
    largura = max([len(b['colunas']) for b in blocos] + [len(c.cab) for c in cabs] + [1])
    for b in blocos:
        if b['colunas']:
            linhas_html.append(cabecalho_tabela(b['colunas']))
        trechos, corrida = [], []     # linhas de dados seguidas (mescláveis) e linhas de largura inteira
        for j in juntar_linhas(b['linhas']):
            primeiro = j['nos'][0]
            rev = ' class="revogado"' if all(n.revogado for n in j['nos']) else ''
            titulo = html.escape(' / '.join(n.rotulo for n in j['nos']))
            attrs = f' id="{html.escape(primeiro.id)}"{rev} title="{titulo}"'
            if not j['valores']:
                if corrida:
                    trechos.append(corrida); corrida = []
                trechos.append({'attrs': attrs, 'largura': f'<td colspan="{largura}">{j["livre"]}</td>'})
            else:
                cols = b['colunas']
                celulas = []
                for n_col, ch in enumerate(cols):
                    v = j['valores'].get(ch, '')
                    if n_col == len(cols) - 1 and j['livre']:
                        v = (v + ' ' + j['livre']).strip()
                    ida = f' id="{html.escape(j["ids"][ch])}"' if ch in j['ids'] else ''
                    celulas.append([ida, v, 1])
                corrida.append({'attrs': attrs, 'celulas': celulas, 'revogado': bool(rev)})
            for n in j['nos']:          # notas e linhas soltas que vinham depois da linha
                if n.conteudo:
                    depois.append(render_conteudo(n.conteudo, prof))
        if corrida:
            trechos.append(corrida)
        for t in trechos:
            if isinstance(t, dict):
                linhas_html.append(f'<tr{t["attrs"]}>{t["largura"]}</tr>')
                continue
            seg = []                     # linha revogada separa os trechos mescláveis
            for r in t + [None]:
                if r is None or r['revogado']:
                    mesclar_colunas(seg)
                    seg = []
                else:
                    seg.append(r)
            for r in t:
                tds = ''.join(f'<td{ida}{f" rowspan={chr(34)}{rs}{chr(34)}" if rs > 1 else ""}>{v}</td>'
                              for ida, v, rs in r['celulas'] if rs)
                linhas_html.append(f'<tr{r["attrs"]}>{tds}</tr>')
    return f'<div class="tabela"{id_tabela}><table><tbody>' + ''.join(linhas_html) + '</tbody></table></div>' + ''.join(depois)


def tem_art(no):
    return any(f.tipo == 'art' or (f.tipo == 'sec' and tem_art(f)) for f in no.filhos())


def render(no, prof=0):
    """prof: profundidade do dispositivo dentro do artigo (1 = parágrafos e incisos do caput)."""
    if no.tipo == 'art':
        prof_filhos = 1
    elif no.tipo == 'disp':
        prof_filhos = prof + 1
    else:
        prof_filhos = prof
    corpo = render_conteudo(no.conteudo, prof_filhos)
    ida = f' id="{html.escape(no.id)}"' if no.id else ''
    rev = ' revogado' if no.revogado else ''
    if no.tipo == 'raiz':
        return corpo
    if no.tipo == 'cpt':
        return f'<div class="cpt{rev}"{ida}>{corpo}</div>'
    if no.tipo == 'lin':
        return f'<div class="lin{rev}"{ida}>{corpo}</div>'
    if no.tipo == 'sec':
        if RE_ANEXO.match(no.rotulo) or RE_GRUPO_ANEXOS.match(no.rotulo):
            # anexo: em "Recolher artigos" só fica aberto se tiver artigos (ex.: regulamento anexo)
            classe = 'sec anexo estrutura' if tem_art(no) else 'sec anexo'
        else:
            classe = 'sec estrutura' if no.tem_artigo() else 'sec extra'
        extra = f' <span class="extra">{no.extra}</span>' if getattr(no, 'extra', '') else ''
        return (f'<details class="{classe} n{no.nivel}"{ida}><summary>{rotulo_html(no.rotulo)}{extra}</summary>'
                f'<div class="corpo">{corpo}</div></details>')
    if no.tipo == 'art':
        return (f'<details class="art{rev}"{ida}><summary>{rotulo_html(no.rotulo)}</summary>'
                f'<div class="corpo">{controle_niveis(no)}{corpo}</div></details>')
    titulo = html.escape(no.rotulo)
    dp = f' data-p="{prof}"' if prof else ''
    return (f'<details class="disp{rev}"{ida}{dp}><summary title="{titulo}">{html.escape(rotulo_curto(no.rotulo))}</summary>'
            f'<div class="corpo">{corpo}</div></details>')


def rotulo_html(t):
    return html.escape(t, quote=False).replace('**', '')


# ---------------------------------------------------------------- página

CSS = """
:root{--fundo:#fbfaf7;--texto:#1f2328;--suave:#6a6f76;--linha:#e3e0d8;--realce:#1d5f8a;--realce-fundo:#e8f1f7;--revogado:#9a9a9a;--marca:#fff3c4}
@media (prefers-color-scheme:dark){:root{--fundo:#16181b;--texto:#e4e4e2;--suave:#9aa0a6;--linha:#30343a;--realce:#7cb8e0;--realce-fundo:#1c2a35;--revogado:#777;--marca:#4a4120}}
*{box-sizing:border-box}
body{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.6 Georgia,"Times New Roman",serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 80px}
header h1{font-size:1.5rem;line-height:1.3;margin:0 0 12px}
header .ementa{color:var(--suave);font-style:italic;margin:0 0 6px}
.situacao{display:inline-block;font:600 .75rem system-ui,sans-serif;text-transform:uppercase;letter-spacing:.05em;color:#fff;background:#a33;border-radius:4px;padding:2px 8px;margin-bottom:8px}
.barra{position:sticky;top:0;z-index:2;background:var(--fundo);padding:10px 0;margin:12px 0 8px;border-bottom:1px solid var(--linha);display:flex;gap:12px;align-items:center}
.barra button{font:600 .9rem system-ui,sans-serif;padding:8px 16px;border-radius:6px;border:1px solid var(--realce);background:var(--realce);color:var(--fundo);cursor:pointer;min-width:160px}
.barra a{font:.85rem system-ui,sans-serif;color:var(--suave)}
details{margin:2px 0}
summary{cursor:pointer;list-style:none;padding:3px 6px;border-radius:4px;font-family:system-ui,sans-serif}
summary::-webkit-details-marker{display:none}
summary::before{content:"";display:inline-block;width:0;height:0;border-style:solid;border-width:5px 0 5px 7px;border-color:transparent transparent transparent var(--suave);margin:0 .5em 1px .1em;transition:transform .15s}
details[open]>summary::before{transform:rotate(90deg)}
summary:hover{background:var(--realce-fundo)}
.corpo{margin-left:1.1em;padding-left:10px;border-left:1px solid var(--linha)}
.sec>summary{font-weight:700;text-transform:none}
.sec.n2>summary{font-size:1.05rem}
.sec.extra>summary{font-weight:500;color:var(--suave)}
.sec.anexo>summary{font-weight:700;color:var(--texto)}
.art>summary{font-weight:600;color:var(--realce)}
.disp>summary{display:inline-block;font-size:.92rem;color:var(--realce)}
.disp[open]>summary{float:left;margin-right:6px;line-height:1.6;padding-top:0;padding-bottom:0}
.disp[open]>.corpo{margin-left:0;padding-left:0;border-left:none;display:flow-root}
.disp[open]>.corpo>.texto:first-child{margin-top:0}
.disp[open]>.corpo>details{margin-left:1.6em}
p{margin:4px 0}
.texto{margin:2px 0 6px}
.lin{margin:3px 0}
.nota{font:.8rem/1.4 system-ui,sans-serif;color:var(--suave);margin:6px 0}
.item{padding-left:1em}
.item.r1{padding-left:2em}.item.r2{padding-left:3em}.item.r3{padding-left:4em}.item.r4{padding-left:5em}
.revogado>summary,.revogado .texto{color:var(--revogado)}
del{color:var(--revogado)}
blockquote{margin:6px 0;padding:4px 12px;border-left:3px solid var(--linha);color:var(--suave)}
a{color:var(--realce)}
.pendente{border-bottom:1px dotted var(--suave)}
.extra{font-weight:400;font-size:.85rem}
.tabela{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;font:.85rem/1.4 system-ui,sans-serif}
th,td{border:1px solid var(--linha);padding:4px 8px;vertical-align:top;text-align:left}
th{background:var(--realce-fundo);font-weight:600}
tr.revogado td{color:var(--revogado);text-decoration:line-through}
td.alvo,tr.alvo td{background:var(--marca)}
img{max-width:100%;height:auto}
code{font-size:.85em}
.alvo{background:var(--marca);border-radius:4px}
.niveis{display:flex;flex-wrap:wrap;gap:4px;align-items:center;margin:4px 0 8px;font:.78rem system-ui,sans-serif;color:var(--suave)}
.niveis span{margin-right:2px}
.niveis button{font:inherit;padding:2px 8px;border-radius:10px;border:1px solid var(--linha);background:transparent;color:var(--suave);cursor:pointer}
.niveis button:hover{border-color:var(--realce);color:var(--realce)}
.niveis button.ativo{background:var(--realce-fundo);border-color:var(--realce);color:var(--realce);font-weight:600}
"""

JS = """
(function(){
  var btn=document.getElementById('alternar'), estado=0;
  var rotulos=['Expandir tudo','Recolher artigos','Recolher tudo'];
  btn.addEventListener('click',function(){
    var todos=document.querySelectorAll('main details');
    if(estado===0){todos.forEach(function(d){d.open=true;});}
    else if(estado===1){todos.forEach(function(d){d.open=d.classList.contains('estrutura');});}
    else{todos.forEach(function(d){d.open=false;});}
    estado=(estado+1)%3; btn.textContent=rotulos[estado];
  });
  // abrir um artigo abre todos os dispositivos dele, com os textos
  function nivel(art,n){
    art.querySelectorAll('details.disp[data-p]').forEach(function(d){d.open=n<0||(+d.dataset.p)<=n;});
    art.querySelectorAll('.niveis button').forEach(function(b){
      var bn=+b.dataset.nivel, max=art.querySelectorAll('.niveis button').length-1;
      b.classList.toggle('ativo', n<0 ? bn===max : bn===n);
    });
  }
  document.addEventListener('toggle',function(e){
    var d=e.target; if(d.classList&&d.classList.contains('art')&&d.open) nivel(d,-1);
  },true);
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.niveis button'); if(!b) return;
    nivel(b.closest('details.art'),+b.dataset.nivel);
  });
  function irPara(){
    var id=decodeURIComponent(location.hash.slice(1)); if(!id) return;
    var el=document.getElementById(id); if(!el) return;
    for(var p=el; p; p=p.parentElement){ if(p.tagName==='DETAILS') p.open=true; }
    document.querySelectorAll('.alvo').forEach(function(e){e.classList.remove('alvo');});
    el.classList.add('alvo'); el.scrollIntoView({block:'center'});
  }
  window.addEventListener('hashchange',irPara); irPara();
})();
"""


def pagina(titulo, cabecalho, corpo, fm, titulo_id=None):
    situacao = '<div class="situacao">Revogada</div>' if fm.get('situacao') == 'revogada' else ''
    cab = ''.join(f'<p class="ementa">{c}</p>' for c in cabecalho)
    if not cab and fm.get('ementa'):
        cab = f'<p class="ementa">{html.escape(fm["ementa"])}</p>'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(re.sub(r'<[^>]+>', '', titulo))}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<header>{situacao}<h1{f' id="{html.escape(titulo_id)}"' if titulo_id else ''}>{titulo}</h1>{cab}</header>
<div class="barra"><button id="alternar" type="button">Expandir tudo</button><a href="index.html">Todas as normas</a></div>
{corpo}
</main>
<script>{JS}</script>
</body>
</html>
"""


def indice(itens):
    lis = ''.join(
        f'<li><a href="{a}.html">{html.escape(n)}</a>' + (f'<br><small>{html.escape(e)}</small>' if e else '') + '</li>'
        for a, n, e in itens)
    return f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Normas da base</title><style>{CSS} li{{margin:10px 0}} small{{color:var(--suave)}}</style></head>
<body><main><header><h1>Base de Legislação Ambiental</h1>
<p class="ementa">Consulta direta das normas, com dispositivos que abrem e fecham.</p></header>
<ul>{lis}</ul></main></body></html>
"""


def arquivos():
    lista = []
    for pasta in PASTAS:
        lista += sorted(pasta.glob('*.md'))
    return lista


def numero_anexo(arquivo):
    m = re.search(r'-anexo(\d+)', arquivo)
    return int(m.group(1)) if m else 0


def achar(no, ident):
    if no.id == ident:
        return no
    for f in no.filhos():
        r = achar(f, ident)
        if r is not None:
            return r
    return None


def encaixar_anexo(raiz_mae, mae, ancora, raiz_anexo):
    """Põe o texto do anexo dentro do título "ANEXO N {#anexoN}" da norma-mãe.
    A seção "Texto do anexo" é desfeita (o texto entra direto); síntese e notas do anexo
    entram como subseções. O link "Texto do Anexo N", que apontaria para o próprio lugar, sai."""
    destino = achar(raiz_mae, ancora)
    if destino is None:          # sem título para o anexo: entra no fim da norma
        destino = No('sec', ancora, 'Anexo', 2)
        raiz_mae.conteudo.append(('no', destino))
    proprio = re.compile(rf'^<p><a href="{re.escape(mae)}\.html#{re.escape(ancora)}">[^<]*</a>\.?</p>$')
    destino.conteudo = [(k, c) for k, c in destino.conteudo if not (k == 'html' and proprio.match(c))]
    for k, c in raiz_anexo.conteudo:
        if k == 'no' and c.tipo == 'sec' and c.rotulo.lower().startswith('texto do anexo'):
            destino.conteudo += c.conteudo
        else:
            if k == 'no' and c.tipo == 'sec':
                prefixar(c, ancora)
            destino.conteudo.append((k, c))


def prefixar(no, ancora):
    """Seções editoriais do anexo (sintese, notas-transcricao) repetem IDs da norma-mãe: viram anexoN-sintese."""
    if no.tipo == 'sec' and no.id and not no.id.startswith('anexo'):
        no.id = f'{ancora}-{no.id}'
    for f in no.filhos():
        prefixar(f, ancora)


def main():
    saida = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ / 'html'
    saida.mkdir(parents=True, exist_ok=True)
    fontes = arquivos()
    paginas = [f for f in fontes if f.parent.name != 'anexos']
    existentes = {f.stem for f in paginas}

    # anexos: cada um vai para a página da norma-mãe (campo norma_mae), na posição do título dele
    anexos, por_mae = {}, {}
    for f in fontes:
        if f.parent.name != 'anexos':
            continue
        fm, corpo = ler_frontmatter(f.read_text(encoding='utf-8'))
        mae = re.sub(r'^\[\[|\]\]$', '', fm.get('norma_mae', '')).split('|')[0].split('#')[0]
        if mae not in existentes:
            paginas.append(f)        # norma-mãe fora da base: o anexo continua com página própria
            existentes.add(f.stem)
            continue
        anexos[f.stem] = (mae, f'anexo{numero_anexo(f.stem)}')
        por_mae.setdefault(mae, []).append((f, corpo))

    itens = []
    for f in paginas:
        fm, corpo = ler_frontmatter(f.read_text(encoding='utf-8'))
        conv = Conversor(existentes, f.stem, f.parent, saida, anexos)
        titulo, cabecalho, raiz = montar(corpo, conv)
        marcar_pais(raiz)
        for fa, corpo_a in sorted(por_mae.get(f.stem, []), key=lambda x: numero_anexo(x[0].stem)):
            conv_a = Conversor(existentes, fa.stem, fa.parent, saida, anexos)
            _, _, raiz_a = montar(corpo_a, conv_a)
            marcar_pais(raiz_a)
            encaixar_anexo(raiz, f.stem, anexos[fa.stem][1], raiz_a)
        titulo_html = conv.inline(titulo) if titulo else html.escape(fm.get('norma') or f.stem)
        (saida / f'{f.stem}.html').write_text(pagina(titulo_html, cabecalho, render(raiz), fm, getattr(raiz, 'id_titulo', None)), encoding='utf-8')
        if f.parent.name == 'normas':
            itens.append((f.stem, fm.get('norma') or f.stem, fm.get('ementa', '')))
    # apaga páginas que não existem mais (normas que saíram da base, anexos agora dentro da norma)
    for velho in saida.glob('*.html'):
        if velho.stem not in existentes and velho.name != 'index.html':
            velho.unlink()
    (saida / 'index.html').write_text(indice(itens), encoding='utf-8')
    print(f'{len(paginas)} páginas em {saida} ({len(anexos)} anexos dentro das normas)')


if __name__ == '__main__':
    main()
