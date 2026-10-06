#!/usr/bin/env python3
"""Recuperação lexical local, auditável. Não decide aplicabilidade nem vigência jurídica.

Termos são cumulativos, normalizados sem acentos; use várias consultas curtas.
Artigos são recuperados inteiros; anexos por dispositivo, com títulos de contexto.
Não há busca externa, modelo de linguagem, embeddings ou dependências adicionais.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import re
import subprocess
import unicodedata

RAIZ = Path(__file__).resolve().parents[1]
ID = re.compile(r'\{#([\w-]+)\}')
LINK = re.compile(r'\[\[([a-z0-9-]+)(?:#[\w-]+)?(?:\\?\|[^\]]*)?\]\]')
EDITORIAL = ('notas de transcricao', 'relacao com', 'relacao entre',
             'historico de alteracoes', 'sintese do conversor')


@lru_cache(maxsize=20000)
def normalizar(texto):
    texto = ''.join(c for c in unicodedata.normalize('NFKD', texto.casefold())
                    if not unicodedata.combining(c))
    texto = re.sub(r'\b(\d{4})-(\d)/(\d{2})\b', r'\1\2\3', texto)
    return ' '.join(re.findall(r'[a-z0-9]+', texto))


def texto_atual(texto):
    # Não descartar um artigo inteiro porque uma tag agregada diz #revogado.
    linhas = [l for l in texto.splitlines()
              if not (ID.search(l) and re.search(r'#revogado\b', l))
              and not re.match(r'>\s*Redação (?:original|anterior):', l)]
    return re.sub(r'~~.*?~~', '', '\n'.join(linhas), flags=re.S)


def ler_documento(caminho):
    texto = caminho.read_text(encoding='utf-8')
    if not texto.startswith('---\n') or '\n---\n' not in texto[4:]:
        raise ValueError(f'Frontmatter inválido: {caminho}')
    cab, corpo = texto[4:].split('\n---\n', 1)
    fm = dict(re.findall(r'^([a-z_]+):\s*(.*)$', cab, re.M))
    return texto, fm, corpo


def carregar(raiz=RAIZ, historico=False, interpretativo=False):
    documentos, blocos = {}, []
    for caminho in sorted((raiz / 'normas').rglob('*.md')):
        texto, fm, corpo = ler_documento(caminho)
        nome = caminho.stem
        documentos[nome] = {'arquivo': caminho.relative_to(raiz).as_posix(),
                            'metadados': fm,
                            'relacoes_saida': sorted(set(LINK.findall(texto)) - {nome})}
        if fm.get('situacao') == 'revogada' and not historico:
            continue
        comentario = fm.get('tipo_documento') == 'comentario'
        if comentario and not interpretativo:
            continue
        offset = len(texto[:len(texto)-len(corpo)].splitlines())
        titulos, bloco, inicio, editorial, artigo = {}, [], 0, False, False
        anexo_tecnico = 'tipo_anexo' in fm
        texto_anexo = False
        secao_editorial = False

        def fechar():
            if not bloco:
                return
            bruto = '\n'.join(bloco)
            atual = bruto if historico else texto_atual(bruto)
            if artigo and not historico and not any('_' in i for i in ID.findall(atual)):
                return  # artigo inteiramente revogado: não devolver só cabeçalho/tags
            natureza = 'interpretativo' if comentario or editorial else 'texto-normativo'
            if atual.strip() and (interpretativo or natureza != 'interpretativo'):
                blocos.append({'norma': nome, 'arquivo': caminho.relative_to(raiz).as_posix(),
                               'linha': inicio, 'linha_fim': inicio + len(bloco) - 1,
                               'ids': ID.findall(atual), 'natureza': natureza,
                               'situacao_cadastrada': fm.get('situacao', 'ver norma_mae'),
                               'contexto': list(titulos.values()), 'texto': atual})

        for numero, linha in enumerate(corpo.splitlines(), offset + 1):
            h = re.match(r'^(#{1,6})\s+(.+)', linha)
            ident = ID.search(linha)
            if h:
                fechar(); bloco = []; artigo = False
                nivel, titulo = len(h[1]), h[2]
                titulos = {n: v for n, v in titulos.items() if n < nivel}
                titulos[nivel] = titulo
                if nivel <= 2:
                    titulo_normal = normalizar(titulo)
                    texto_anexo = texto_anexo or titulo_normal.startswith('texto do anexo')
                    secao_editorial = secao_editorial or any(titulo_normal.startswith(e) for e in EDITORIAL)
                    editorial = secao_editorial or (anexo_tecnico and not texto_anexo)
                if nivel == 6 and ident and re.fullmatch(r'art\d+(?:-[a-z])?', ident[1]):
                    artigo = True
                if ident or editorial:
                    inicio = numero; bloco = [linha]
            elif ident and not artigo:
                fechar(); bloco = [linha]; inicio = numero
            elif bloco:
                bloco.append(linha)
        fechar()
    for nome, doc in documentos.items():
        doc['relacoes_entrada'] = sorted(n for n, d in documentos.items()
                                        if nome in d['relacoes_saida'])
        doc['pendentes'] = [n for n in doc['relacoes_saida'] if n not in documentos]
    return documentos, blocos


def buscar(blocos, consulta, norma=None, frase=False):
    q = normalizar(consulta)
    if not q:
        return []
    termos = set(q.split())
    achados = []
    for b in blocos:
        if norma and b['norma'] != norma:
            continue
        # Somente texto do bloco: frontmatter e título da norma não fazem cada
        # artigo parecer pertinente à atividade. Contexto é entregue para leitura.
        t = normalizar(b['texto'])
        if (q in t if frase else termos <= set(t.split())):
            achados.append(b)
    return sorted(achados, key=lambda b: (b['arquivo'], b['linha']))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('consulta', nargs='?', default='')
    p.add_argument('--norma', help='Nome de arquivo sem .md')
    p.add_argument('--frase', action='store_true')
    p.add_argument('--historico', action='store_true', help='Inclui revogadas e redações antigas; não reconstrói vigência numa data')
    p.add_argument('--interpretativo', action='store_true')
    p.add_argument('--inventario', action='store_true')
    p.add_argument('--limite', type=int, default=20, help='0 = todos; ordenação por arquivo/linha, sem ranking jurídico')
    p.add_argument('--offset', type=int, default=0)
    a = p.parse_args()
    if a.limite < 0 or a.offset < 0:
        p.error('limite e offset devem ser não negativos')
    docs, blocos = carregar(historico=a.historico, interpretativo=a.interpretativo)
    if a.norma and a.norma not in docs:
        p.error('norma não encontrada na base')
    encontrados = buscar(blocos, a.consulta, a.norma, a.frase)
    fim = a.offset + a.limite if a.limite else None
    selecionados = encontrados[a.offset:fim]
    sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    sujo = bool(subprocess.run(['git', 'status', '--porcelain', '--', 'normas'], cwd=RAIZ, capture_output=True, text=True).stdout.strip())
    for b in selecionados:
        b['url'] = None if not sha or sujo else f'https://github.com/leoparreira21/base-legislacao-ambiental/blob/{sha}/{b["arquivo"]}#L{b["linha"]}-L{b["linha_fim"]}'
    print(json.dumps({'aviso': 'Candidatos para leitura; presença não prova aplicabilidade ou vigência. Leia ressalvas, pais e remissões.',
                      'commit': sha, 'corpus_modificado': sujo, 'total': len(encontrados),
                      'offset': a.offset, 'truncado': a.offset + len(selecionados) < len(encontrados),
                      'documentos': docs if a.inventario else {n: docs[n] for n in sorted({b['norma'] for b in selecionados})},
                      'resultados': selecionados}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
